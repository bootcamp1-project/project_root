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
        
        # 구독자 및 발행자 설정
        self.sub_prog = self.create_subscription(String, '/program', self.on_program, 10)
        self.sub_stop = self.create_subscription(Bool, '/run_stop', self.on_stop, 10)
        self.sub_dist = self.create_subscription(Float32, '/obstacle_dist', self.on_dist, 10)
        
        self.pub_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        self.pub_buzzer = self.create_publisher(Bool, '/buzzer', 10)
        self.pub_state = self.create_publisher(String, '/run_state', 10)
        
        # 상태 변수 초기화
        self.program = []        
        self.remain = 0.0        
        self.cur = None          
        self.dist = 999.0        
        self.is_running = False  
        
        self.timer = self.create_timer(0.1, self.tick)
        self.get_logger().info('★ 완벽하게 패치된 interpreter_node가 시작되었습니다.')

    def send_state(self, status, **kwargs):
        msg = String()
        msg.data = json.dumps({'state': status, **kwargs}, ensure_ascii=False)
        self.pub_state.publish(msg)

    def on_program(self, msg):
        if self.is_running:
            self.get_logger().warn('이미 블록 프로그램이 실행 중입니다! 명령을 무시합니다.')
            return
        try:
            raw_program = json.loads(msg.data)
            self.program = self.preprocess_program(raw_program)
            if not self.program:
                self.send_state('done')
                return
            self.is_running = True
            self.cur = None
            self.send_state('running', total=len(self.program))
        except Exception as e:
            self.get_logger().error(f'프로그램 파싱 실패: {e}')
            self.abort('데이터 오류')

    def preprocess_program(self, blocks):
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
        if msg.data and self.is_running:
            self.abort('사용자 중지')

    def on_dist(self, msg):
        self.dist = float(msg.data)

    def abort(self, reason):
        self.program = []
        self.cur = None
        self.remain = 0.0
        self.is_running = False
        self.pub_vel.publish(Twist())
        self.send_state('aborted', reason=reason)

    def next_block(self):
        if not self.program:
            if self.cur is not None or self.is_running:
                self.cur = None
                self.is_running = False
                self.pub_vel.publish(Twist()) # 완전히 끝나면 모터 정지 명령 명시
                self.send_state('done')
            return

        self.cur = self.program.pop(0)
        op = self.cur['op']
        
        if op == 'forward':
            self.remain = float(self.cur.get('sec', 1))
        elif op in ('turn_left', 'turn_right'):
            self.remain = TURN_90_SEC
        elif op == 'wait':
            self.remain = float(self.cur.get('sec', 1))
        elif op == 'buzzer':
            # 주행 모터가 서는 타이밍에 맞춰 부저 노드로 엣지 신호 전달
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
            
            if self.dist < OBSTACLE_M:
                self.abort('장애물 감지')
                return

            # [★ 패치 핵심]: 각 op 타입별 속도를 정확히 격리 지정하여 명령 꼬임 차단
            if op == 'forward':
                cmd.linear.x = LINEAR_SPEED
                cmd.angular.z = 0.0
            elif op == 'turn_left':
                cmd.linear.x = 0.0
                cmd.angular.z = ANGULAR_SPEED
            elif op == 'turn_right':
                cmd.linear.x = 0.0
                cmd.angular.z = -ANGULAR_SPEED
            elif op == 'wait' or op == 'buzzer':
                # 부저가 울리거나 대기할 때는 물리 제어 명령을 확실히 0으로 잠금
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0

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
