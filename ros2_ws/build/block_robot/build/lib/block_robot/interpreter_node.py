#!/usr/bin/env python3
"""interpreter_node: 블록 프로그램(JSON) 순차 실행 + 안전 중단 및 이중 방어 적용"""
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool, Float32
from geometry_msgs.msg import Twist

OBSTACLE_M = 0.20      # 장애물 제한 거리 (20cm)
TURN_90_SEC = 3.1      # 90도 회전 시간 (실측 보정 값)
LINEAR_SPEED = 0.10    # 전진 속도 (m/s)
ANGULAR_SPEED = 0.5    # 회전 속도 (rad/s)

class InterpreterNode(Node):
    def __init__(self):
        super().__init__('interpreter_node')
        
        # 구독자(Subscribers) 및 발행자(Publishers) 설정
        self.sub_prog = self.create_subscription(String, '/program', self.on_program, 10)
        self.sub_stop = self.create_subscription(Bool, '/run_stop', self.on_stop, 10)
        self.sub_dist = self.create_subscription(Float32, '/obstacle_dist', self.on_dist, 10)
        
        self.pub_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        self.pub_buzzer = self.create_publisher(Bool, '/buzzer', 10)
        self.pub_state = self.create_publisher(String, '/run_state', 10)
        
        # 상태 변수 초기화
        self.program = []        # 실행할 블록 큐
        self.remain = 0.0        # 현재 블록의 남은 시간 (초)
        self.cur = None          # 현재 실행 중인 블록
        self.dist = 999.0        # 초음파 거리 초기화
        self.is_running = False  # 실행 중 중복 수신 방어를 위한 플래그 (이중 방어)
        
        # 10Hz 주기 타이머 (0.1초 마다 tick 실행)
        self.timer = self.create_timer(0.1, self.tick)
        self.get_logger().info('★ 개선된 interpreter_node가 성공적으로 시작되었습니다.')

    def send_state(self, status, **kwargs):
        """웹 UI로 실행 상태를 역전파하는 엣지 메시지 발행"""
        msg = String()
        msg.data = json.dumps({'state': status, **kwargs}, ensure_ascii=False)
        self.pub_state.publish(msg)

    def on_program(self, msg):
        """
        웹 앱으로부터 블록 프로그램(JSON 배열)을 수신
        [한계 해결 ③] 이미 실행 중(is_running=True)이면 새로운 프로그램 요청을 방어(무시)합니다.
        """
        if self.is_running:
            self.get_logger().warn('이미 블록 프로그램이 실행 중입니다! 명령을 무시합니다.')
            return

        try:
            raw_program = json.loads(msg.data)
            
            # [한계 해결 ②] 반복 블록(repeat) 처리 (해석기 내부에서 Loop 펼치기 구현)
            self.program = self.preprocess_program(raw_program)
            
            if not self.program:
                self.send_state('done')
                return

            self.is_running = True
            self.cur = None
            self.send_state('running', total=len(self.program))
            self.get_logger().info(f'새 프로그램 수신: 총 {len(self.program)}개 블록 실행 시작')
        except Exception as e:
            self.get_logger().error(f'프로그램 파싱 실패: {e}')
            self.abort('데이터 오류')

    def preprocess_program(self, blocks):
        """반복(repeat) 블록이 포함되어 있을 경우 이를 순차 리스트로 펼쳐주는 헬퍼 함수"""
        flat_list = []
        for block in blocks:
            if block.get('op') == 'repeat':
                count = int(block.get('count', 1))
                inner_blocks = block.get('blocks', [])
                for _ in range(count):
                    flat_list.extend(self.preprocess_program(inner_blocks))
            else:
                flat_list.append(block)
        return flat_list

    def on_stop(self, msg):
        """[M5] 빨간 정지 버튼 누를 시 즉시 안전하게 중단"""
        if msg.data and self.is_running:
            self.abort('사용자 중지')

    def on_dist(self, msg):
        """초음파 센서 거리 업데이트"""
        self.dist = float(msg.data)

    def abort(self, reason):
        """안전하게 로봇을 세우고 모든 상태를 초기화하며 UI에 사유 전달"""
        self.program = []
        self.cur = None
        self.remain = 0.0
        self.is_running = False
        
        # 즉시 정지 명령 발행
        stop_cmd = Twist()
        self.pub_vel.publish(stop_cmd)
        
        # UI 잠금 해제 및 경고 전달
        self.send_state('aborted', reason=reason)
        self.get_logger().error(f'🚨 프로그램 중단 사유: {reason}')

    def next_block(self):
        """큐에서 다음 블록을 꺼내어 초기 설정을 진행"""
        if not self.program:
            if self.cur is not None or self.is_running:
                self.cur = None
                self.is_running = False
                self.send_state('done')  # [한계 해결 ①] 명확한 done 상태 전송으로 UI 잠금 해제 유도
                self.get_logger().info('🎉 모든 블록 동작을 완주했습니다.')
            return

        self.cur = self.program.pop(0)
        op = self.cur['op']
        
        # 블록 종류별 대기/동작 시간 설정
        if op == 'forward':
            self.remain = float(self.cur.get('sec', 1))
        elif op in ('turn_left', 'turn_right'):
            self.remain = TURN_90_SEC
        elif op == 'wait':
            self.remain = float(self.cur.get('sec', 1))
        elif op == 'buzzer':
            # 부저 엣지 신호 발생
            buz = Bool()
            buz.data = True
            self.pub_buzzer.publish(buz)
            self.remain = 0.5  # 트러블슈팅: 부저 지속 시간 보장
            
        # [M3] 현재 실행 중인 블록 정보를 UI로 역전파 (하이라이트용)
        self.send_state('block', op=op, left=len(self.program))

    def tick(self):
        """10Hz 주기로 실행되는 핵심 제어 루프"""
        cmd = Twist()
        
        # 실행 중이 아니라면 대기
        if not self.is_running:
            return

        # 현재 실행 블록이 없으면 가져오기
        if self.cur is None:
            self.next_block()
            
        if self.cur is not None:
            op = self.cur['op']
            
            # [M4 / 트러블슈팅 해결] 전진(forward) 뿐만 아니라 회전 중에도 안전을 위해 장애물 검사 통합 진행
            # 만약 회전 중에는 검사하고 싶지 않다면 `if op == 'forward' and self.dist < OBSTACLE_M:` 으로 수정 가능합니다.
            if self.dist < OBSTACLE_M:
                self.abort('장애물 감지')
                return

            # 블록 타입별 실제 속도 명령 할당
            if op == 'forward':
                cmd.linear.x = LINEAR_SPEED
            elif op == 'turn_left':
                cmd.angular.z = ANGULAR_SPEED
            elif op == 'turn_right':
                cmd.angular.z = -ANGULAR_SPEED
            elif op == 'wait' or op == 'buzzer':
                # 이동 정지 상태 유지
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0

            # 시간 차감 (10Hz이므로 0.1초씩 차감)
            self.remain -= 0.1
            if self.remain <= 0:
                self.cur = None  # 다음 tick에서 next_block()이 호출되도록 초기화
                
        # 터틀봇에게 주기적으로 연속 물리 명령 발행 (10Hz)
        self.pub_vel.publish(cmd)

def main():
    rclpy.init()
    node = InterpreterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # 종료 시 터틀봇이 계속 움직이는 것을 방지하기 위해 안전하게 정지 명령 발행
        stop_node = rclpy.create_node('stop_publisher')
        stop_pub = stop_node.create_publisher(Twist, '/cmd_vel', 10)
        stop_pub.publish(Twist())
        
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
