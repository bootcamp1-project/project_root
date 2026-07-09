#!/usr/bin/env python3
"""interpreter_node_fixed.py

블록 코딩 웹(v5/v6)에서 발행하는 /program(JSON)을 실행하는 ROS 2 노드입니다.
- forward/backward/turn_left/turn_right/wait/buzzer 실행
- repeat, if(front_obstacle) 중첩 처리
- 전/후방 장애물 감지 시 즉시 정지
- IF 블록이 바로 다음에 있으면 IF의 then 블록으로 제어 이동
- IF 블록이 없으면 /run_state에 aborted + reason='장애물 감지' 발행
"""

import copy
import json
import math
from typing import Any, Dict, List, Optional

import rclpy
from rclpy.node import Node
from rclpy.time import Time
from std_msgs.msg import Bool, Float32, String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Range

OBSTACLE_M = 0.20       # 장애물 제한 거리: 20 cm
TURN_90_SEC = 3.4       # 제자리 90도 회전에 필요한 시간. 로봇에 맞게 조정
LINEAR_SPEED = 0.10     # m/s
ANGULAR_SPEED = 0.50    # rad/s
TICK_SEC = 0.10
SENSOR_STALE_SEC = 0.80 # 이 시간보다 오래된 센서값은 무시

VALID_OPS = {
    'forward', 'backward', 'turn_left', 'turn_right',
    'wait', 'buzzer', 'repeat', 'if'
}


class InterpreterNode(Node):
    def __init__(self) -> None:
        super().__init__('interpreter_node')

        self.sub_prog = self.create_subscription(String, '/program', self.on_program, 10)
        self.sub_stop = self.create_subscription(Bool, '/run_stop', self.on_stop, 10)

        self.sub_front = self.create_subscription(Float32, '/obstacle_dist/front', self.on_dist_front, 10)
        self.sub_rear = self.create_subscription(Float32, '/obstacle_dist/rear', self.on_dist_rear, 10)

        # 여러 실습 코드와 호환되도록 자주 쓰는 장애물 토픽도 함께 구독합니다.
        self.sub_obs1 = self.create_subscription(Bool, '/obstacle', self.on_bool_obstacle, 10)
        self.sub_obs2 = self.create_subscription(Bool, '/front_obstacle', self.on_bool_obstacle, 10)
        self.sub_obs3 = self.create_subscription(Bool, '/obstacle_detected', self.on_bool_obstacle, 10)
        self.sub_range1 = self.create_subscription(Range, '/range', self.on_range_obstacle, 10)
        self.sub_range2 = self.create_subscription(Range, '/ultrasonic_range', self.on_range_obstacle, 10)

        self.pub_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        self.pub_buzzer = self.create_publisher(Bool, '/buzzer', 10)
        self.pub_state = self.create_publisher(String, '/run_state', 10)

        self.program: List[Dict[str, Any]] = []
        self.cur: Optional[Dict[str, Any]] = None
        self.remain = 0.0
        self.is_running = False

        self.dist_front_float = 999.0
        self.dist_front_range = 999.0
        self.dist_rear_float = 999.0
        self.obs_bool = False

        now = self.get_clock().now()
        self.front_float_stamp = now
        self.front_range_stamp = now
        self.rear_float_stamp = now
        self.obs_bool_stamp = now

        self.timer = self.create_timer(TICK_SEC, self.tick)
        self.get_logger().info('✅ interpreter_node_fixed 실행됨: 블록 실행 + 장애물 정지 + IF 흐름 처리')

    # ---------- 유틸 ----------
    def _age(self, stamp: Time) -> float:
        return (self.get_clock().now() - stamp).nanoseconds / 1e9

    def _fresh(self, stamp: Time) -> bool:
        return self._age(stamp) <= SENSOR_STALE_SEC

    @property
    def dist_front(self) -> float:
        values: List[float] = []
        if self.obs_bool and self._fresh(self.obs_bool_stamp):
            values.append(0.0)
        if self._fresh(self.front_float_stamp):
            values.append(self.dist_front_float)
        if self._fresh(self.front_range_stamp):
            values.append(self.dist_front_range)
        return min(values) if values else 999.0

    @property
    def dist_rear(self) -> float:
        return self.dist_rear_float if self._fresh(self.rear_float_stamp) else 999.0

    def stop_robot(self) -> None:
        self.pub_vel.publish(Twist())

    def send_state(self, status: str, **kwargs: Any) -> None:
        msg = String()
        msg.data = json.dumps({'state': status, **kwargs}, ensure_ascii=False)
        self.pub_state.publish(msg)

    def sanitize_program(self, blocks: Any) -> List[Dict[str, Any]]:
        """웹/파일에서 온 JSON을 안전하게 정규화합니다."""
        if not isinstance(blocks, list):
            return []
        out: List[Dict[str, Any]] = []
        for raw in blocks:
            if not isinstance(raw, dict):
                continue
            op = str(raw.get('op', '')).strip()
            if op not in VALID_OPS:
                continue

            if op == 'repeat':
                count = int(float(raw.get('count', 1)))
                count = max(1, min(20, count))
                inner = raw.get('blocks', raw.get('children', []))
                out.append({'op': 'repeat', 'count': count, 'blocks': self.sanitize_program(inner)})
            elif op == 'if':
                cond = raw.get('cond', 'front_obstacle')
                then_blocks = raw.get('then', raw.get('blocks', raw.get('children', [])))
                out.append({'op': 'if', 'cond': cond, 'then': self.sanitize_program(then_blocks)})
            elif op in ('forward', 'backward'):
                sec = self._clamp_float(raw.get('sec', 3.0), 0.1, 30.0, 3.0)
                out.append({'op': op, 'sec': sec})
            elif op == 'wait':
                sec = self._clamp_float(raw.get('sec', 1.0), 0.1, 30.0, 1.0)
                out.append({'op': op, 'sec': sec})
            else:
                out.append({'op': op})
        return out

    @staticmethod
    def _clamp_float(value: Any, lo: float, hi: float, default: float) -> float:
        try:
            v = float(value)
            if not math.isfinite(v):
                return default
            return max(lo, min(hi, v))
        except Exception:
            return default

    # ---------- 구독 콜백 ----------
    def on_program(self, msg: String) -> None:
        if self.is_running:
            self.get_logger().warn('실행 중 새 프로그램은 무시합니다. 먼저 멈춤을 누르세요.')
            return
        try:
            parsed = json.loads(msg.data)
            self.program = self.sanitize_program(parsed)
        except Exception as e:
            self.get_logger().error(f'프로그램 JSON 파싱 실패: {e}')
            self.abort('데이터 오류')
            return

        self.cur = None
        self.remain = 0.0
        if not self.program:
            self.send_state('done')
            return

        self.is_running = True
        self.send_state('running', total=len(self.program))
        self.get_logger().info(f'프로그램 시작: {len(self.program)}개 블록')

    def on_stop(self, msg: Bool) -> None:
        if msg.data:
            self.abort('사용자 중지')

    def on_dist_front(self, msg: Float32) -> None:
        v = float(msg.data)
        if math.isfinite(v):
            self.dist_front_float = v
            self.front_float_stamp = self.get_clock().now()

    def on_dist_rear(self, msg: Float32) -> None:
        v = float(msg.data)
        if math.isfinite(v):
            self.dist_rear_float = v
            self.rear_float_stamp = self.get_clock().now()

    def on_bool_obstacle(self, msg: Bool) -> None:
        self.obs_bool = bool(msg.data)
        self.obs_bool_stamp = self.get_clock().now()

    def on_range_obstacle(self, msg: Range) -> None:
        r = float(msg.range)
        if math.isfinite(r) and msg.range_min <= r <= msg.range_max:
            self.dist_front_range = r
            self.front_range_stamp = self.get_clock().now()

    # ---------- 실행 엔진 ----------
    def abort(self, reason: str) -> None:
        self.program = []
        self.cur = None
        self.remain = 0.0
        was_running = self.is_running
        self.is_running = False
        self.stop_robot()
        # 실행 중이 아니더라도 웹 UI에 확실히 표시되도록 상태를 발행합니다.
        self.send_state('aborted', reason=reason)
        if was_running:
            self.get_logger().warn(f'프로그램 중지: {reason}')

    def peek_next_command(self) -> Optional[Dict[str, Any]]:
        """repeat 내부를 펼쳐서 실제 다음 실행 블록을 미리 봅니다."""
        temp_prog = copy.deepcopy(self.program)
        while temp_prog:
            b = temp_prog.pop(0)
            op = b.get('op')
            if op == 'repeat':
                count = int(b.get('count', 1))
                blocks = copy.deepcopy(b.get('blocks', []))
                temp_prog = blocks * max(0, count) + temp_prog
                continue
            return b
        return None

    def next_is_obstacle_if(self) -> bool:
        nxt = self.peek_next_command()
        return bool(nxt and nxt.get('op') == 'if' and nxt.get('cond', 'front_obstacle') == 'front_obstacle')

    def next_block(self) -> None:
        self.cur = None

        while self.program:
            block = self.program.pop(0)
            op = block.get('op')

            if op == 'repeat':
                count = int(block.get('count', 1))
                inner = copy.deepcopy(block.get('blocks', []))
                expanded: List[Dict[str, Any]] = []
                for _ in range(max(0, count)):
                    expanded.extend(copy.deepcopy(inner))
                self.program = expanded + self.program
                continue

            if op == 'if':
                cond = block.get('cond', 'front_obstacle')
                if cond == 'front_obstacle' and self.dist_front < OBSTACLE_M:
                    then_blocks = copy.deepcopy(block.get('then', []))
                    self.program = then_blocks + self.program
                    self.get_logger().warn(f'IF 실행: 전방 장애물 {self.dist_front:.2f}m, then 블록 {len(then_blocks)}개')
                else:
                    self.get_logger().info(f'IF 통과: 전방 장애물 없음({self.dist_front:.2f}m)')
                continue

            self.cur = block
            break

        if self.cur is None:
            if self.is_running:
                self.is_running = False
                self.stop_robot()
                self.send_state('done')
            return

        op = self.cur.get('op')
        if op in ('forward', 'backward'):
            self.remain = float(self.cur.get('sec', 3.0))
        elif op in ('turn_left', 'turn_right'):
            self.remain = TURN_90_SEC
        elif op == 'wait':
            self.remain = float(self.cur.get('sec', 1.0))
        elif op == 'buzzer':
            self.pub_buzzer.publish(Bool(data=True))
            self.remain = 0.5
        else:
            self.remain = 0.1

        self.send_state('block', op=op, left=len(self.program))

    def tick(self) -> None:
        if not self.is_running:
            return

        if self.cur is None:
            self.next_block()

        if self.cur is None:
            return

        op = self.cur.get('op')
        cmd = Twist()

        # 장애물 안전 처리: 이동 블록보다 먼저 검사합니다.
        if op == 'forward' and self.dist_front < OBSTACLE_M:
            self.stop_robot()
            if self.next_is_obstacle_if():
                self.get_logger().warn(f'⚠️ 전방 장애물 {self.dist_front:.2f}m: 다음 IF 블록으로 제어 이동')
                self.cur = None
                self.remain = 0.0
                self.send_state('block', op='if', reason='장애물 감지')
            else:
                self.get_logger().warn(f'🛑 전방 장애물 {self.dist_front:.2f}m: IF 없음, 즉시 정지')
                self.abort('장애물 감지')
            return

        if op == 'backward' and self.dist_rear < OBSTACLE_M:
            self.stop_robot()
            self.get_logger().warn(f'🛑 후방 장애물 {self.dist_rear:.2f}m: 즉시 정지')
            self.abort('장애물 감지')
            return

        if op == 'forward':
            cmd.linear.x = LINEAR_SPEED
        elif op == 'backward':
            cmd.linear.x = -LINEAR_SPEED
        elif op == 'turn_left':
            cmd.angular.z = ANGULAR_SPEED
        elif op == 'turn_right':
            cmd.angular.z = -ANGULAR_SPEED
        # wait/buzzer는 Twist() 그대로 발행되어 정지 상태를 유지합니다.

        self.pub_vel.publish(cmd)
        self.remain -= TICK_SEC

        if self.remain <= 0.0:
            self.cur = None
            self.stop_robot()
            if op == 'buzzer':
                self.pub_buzzer.publish(Bool(data=False))


def main() -> None:
    rclpy.init()
    node = InterpreterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
