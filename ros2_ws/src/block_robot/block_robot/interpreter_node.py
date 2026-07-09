#!/usr/bin/env python3
"""interpreter_node: 중첩 반복문 및 실시간 IF 제어 흐름 완벽 통합 엔진"""
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool, Float32
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Range

OBSTACLE_M = 0.20      # 장애물 제한 거리 (20cm)
TURN_90_SEC = 3.4      # 90도 회전 시간
LINEAR_SPEED = 0.10    # 전진/후진 속도 (m/s)
ANGULAR_SPEED = 0.5    # 회전 속도 (rad/s)

class InterpreterNode(Node):
    def __init__(self):
        super().__init__('interpreter_node')
        
        self.sub_prog = self.create_subscription(String, '/program', self.on_program, 10)
        self.sub_stop = self.create_subscription(Bool, '/run_stop', self.on_stop, 10)
        
        self.sub_front = self.create_subscription(Float32, '/obstacle_dist/front', self.on_dist_front, 10)
        self.sub_rear = self.create_subscription(Float32, '/obstacle_dist/rear', self.on_dist_rear, 10)
        
        # [수정] 웹에서 일괄 처리하던 안전 감지를 Backend로 이관. Race Condition 방지용 다중 센서 구독 추가.
        self.sub_obs1 = self.create_subscription(Bool, '/obstacle', self.on_bool_obstacle, 10)
        self.sub_obs2 = self.create_subscription(Bool, '/front_obstacle', self.on_bool_obstacle, 10)
        self.sub_obs3 = self.create_subscription(Bool, '/obstacle_detected', self.on_bool_obstacle, 10)
        self.sub_range1 = self.create_subscription(Range, '/range', self.on_range_obstacle, 10)
        self.sub_range2 = self.create_subscription(Range, '/ultrasonic_range', self.on_range_obstacle, 10)
        
        self.pub_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        self.pub_buzzer = self.create_publisher(Bool, '/buzzer', 10)
        self.pub_state = self.create_publisher(String, '/run_state', 10)
        
        self.program = []        
        self.remain = 0.0        
        self.cur = None          
        
        self.dist_front_float = 999.0  
        self.dist_front_range = 999.0
        self.obs_bool = False
        
        self.dist_rear_float = 999.0   
        self.is_running = False  
        
        self.timer = self.create_timer(0.1, self.tick)
        self.get_logger().info('★ [통합 패치 완료] 웹 프론트엔드 v5 규격 반영 및 실시간 트리 런타임 엔진')

    @property
    def dist_front(self):
        """다중 센서 간의 값 덮어쓰기 버그를 방지하고 통합된 거리 값 제공"""
        if self.obs_bool:
            return 0.0
        return min(self.dist_front_float, self.dist_front_range)

    @property
    def dist_rear(self):
        return self.dist_rear_float

    def send_state(self, status, **kwargs):
        msg = String()
        msg.data = json.dumps({'state': status, **kwargs}, ensure_ascii=False)
        self.pub_state.publish(msg)

    def on_program(self, msg):
        if self.is_running:
            return
        try:
            self.program = json.loads(msg.data)
            if not self.program:
                self.send_state('done')
                return
            self.is_running = True
            self.cur = None
            self.send_state('running', total=len(self.program))
        except Exception as e:
            self.get_logger().error(f'프로그램 파싱 실패: {e}')
            self.abort('데이터 오류')

    def on_stop(self, msg):
        # [수정] 사용자의 수동 개입은 항시 '사용자 중지'로 명확히 처리합니다.
        if not (msg.data and self.is_running):
            return
        self.abort('사용자 중지')

    def on_dist_front(self, msg):
        self.dist_front_float = float(msg.data)
        
    def on_dist_rear(self, msg):
        self.dist_rear_float = float(msg.data)

    def on_bool_obstacle(self, msg):
        self.obs_bool = msg.data

    def on_range_obstacle(self, msg):
        if msg.range <= OBSTACLE_M:
            self.dist_front_range = msg.range
        else:
            self.dist_front_range = msg.range # 정상 추적 유지

    def abort(self, reason):
        if not self.is_running:
            self.pub_vel.publish(Twist())
            return
        self.program = []
        self.cur = None
        self.remain = 0.0
        self.is_running = False
        self.pub_vel.publish(Twist())
        self.send_state('aborted', reason=reason)

    def peek_next_command(self):
        """[수정] 대기열(self.program)에서 반복문 내부까지 풀어가며 실제 다음에 실행될 명령어를 깊이 탐색"""
        if not self.program:
            return None
        temp_prog = json.loads(json.dumps(self.program))
        while temp_prog:
            b = temp_prog[0]
            op = b.get('op')
            if op == 'repeat':
                temp_prog.pop(0)
                count = int(b.get('count', 1))
                if count > 0:
                    blocks = b.get('blocks', [])
                    unrolled = []
                    for _ in range(count):
                        unrolled.extend(json.loads(json.dumps(blocks)))
                    temp_prog = unrolled + temp_prog
                continue
            return b
        return None

    def next_is_obstacle_if(self):
        """실제 다음 블록이 '만약 앞 장애물' 조건 블록인지 정확히 탐색합니다."""
        nxt = self.peek_next_command()
        return nxt is not None and nxt.get('op') == 'if' and nxt.get('cond') == 'front_obstacle'

    def next_block(self):
        """런타임에 실시간으로 해석합니다."""
        while self.program:
            block = self.program.pop(0)
            op = block.get('op')
            
            if op == 'repeat':
                count = int(block.get('count', 1))
                inner_blocks = block.get('blocks', [])
                unrolled = []
                for _ in range(count):
                    unrolled.extend(json.loads(json.dumps(inner_blocks)))
                self.program = unrolled + self.program
                continue
                
            elif op == 'if':
                cond = block.get('cond')
                if cond == 'front_obstacle' and self.dist_front < OBSTACLE_M:
                    then_blocks = block.get('then', [])  
                    self.program = json.loads(json.dumps(then_blocks)) + self.program
                continue

            self.cur = block
            break
        
        if not self.cur:
            if self.is_running:
                self.is_running = False
                self.pub_vel.publish(Twist()) 
                self.send_state('done')
            return

        op = self.cur['op']
        if op in ('forward', 'backward'):
            self.remain = float(self.cur.get('sec', 3.0))
        elif op in ('turn_left', 'turn_right'):
            self.remain = TURN_90_SEC
        elif op == 'wait':
            self.remain = float(self.cur.get('sec', 1.0))
        elif op == 'buzzer':
            buz = Bool()
            buz.data = True
            self.pub_buzzer.publish(buz)
            self.remain = 0.5  
            
        self.send_state('block', op=op, left=len(self.program))

    def tick(self):
        cmd = Twist()
        if not self.is_running:
            return
            
        if self.cur is None:
            self.next_block()
            
        if self.cur is not None:
            op = self.cur['op']
            
            if op == 'forward' and self.dist_front < OBSTACLE_M:
                self.pub_vel.publish(Twist())
                if self.next_is_obstacle_if(): 
                    self.get_logger().warn(f"⚠️ [주행 중 탈출] 전방 장애물 감지! IF 블록으로 제어를 넘깁니다. (거리: {self.dist_front:.2f}m)")
                    self.cur = None
                    return
                else:
                    self.get_logger().warn(f"🛑 전방 장애물 감지! IF 블록이 없어 프로그램을 정지합니다. (거리: {self.dist_front:.2f}m)")
                    self.abort('장애물 감지')
                    return
                    
            elif op == 'backward' and self.dist_rear < OBSTACLE_M:
                self.pub_vel.publish(Twist())
                self.get_logger().warn(f"🛑 후방 장애물 감지! 프로그램을 정지합니다. (거리: {self.dist_rear:.2f}m)")
                self.abort('장애물 감지')
                return

            if op == 'forward': cmd.linear.x = LINEAR_SPEED
            elif op == 'backward': cmd.linear.x = -LINEAR_SPEED
            elif op == 'turn_left': cmd.angular.z = ANGULAR_SPEED
            elif op == 'turn_right': cmd.angular.z = -ANGULAR_SPEED

            self.remain -= 0.1
            if self.remain <= 0:
                self.cur = None
                
        self.pub_vel.publish(cmd)

def main():
    rclpy.init()
    node = InterpreterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
