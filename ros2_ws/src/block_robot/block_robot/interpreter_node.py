#!/usr/bin/env python3
"""interpreter_node: 중첩 반복문 및 실시간 IF 제어 흐름 완벽 통합 엔진"""
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool, Float32
from geometry_msgs.msg import Twist

OBSTACLE_M = 0.20      # 장애물 제한 거리 (20cm)
TURN_90_SEC = 3.2      # 90도 회전 시간
LINEAR_SPEED = 0.10    # 전진/후진 속도 (m/s)
ANGULAR_SPEED = 0.5    # 회전 속도 (rad/s)

class InterpreterNode(Node):
    def __init__(self):
        super().__init__('interpreter_node')
        
        self.sub_prog = self.create_subscription(String, '/program', self.on_program, 10)
        self.sub_stop = self.create_subscription(Bool, '/run_stop', self.on_stop, 10)
        
        self.sub_front = self.create_subscription(Float32, '/obstacle_dist/front', self.on_dist_front, 10)
        self.sub_rear = self.create_subscription(Float32, '/obstacle_dist/rear', self.on_dist_rear, 10)
        
        self.pub_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        self.pub_buzzer = self.create_publisher(Bool, '/buzzer', 10)
        self.pub_state = self.create_publisher(String, '/run_state', 10)
        
        self.program = []        
        self.remain = 0.0        
        self.cur = None          
        
        self.dist_front = 999.0  
        self.dist_rear = 999.0   
        self.is_running = False  
        
        self.timer = self.create_timer(0.1, self.tick)
        self.get_logger().info('★ [반복문 내 IF문 패치] 하이브리드 트리 런타임 엔진 탑재 완료!')

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
        if msg.data and self.is_running:
            self.abort('사용자 중지')

    def on_dist_front(self, msg):
        self.dist_front = float(msg.data)
        
    def on_dist_rear(self, msg):
        self.dist_rear = float(msg.data)

    def abort(self, reason):
        self.program = []
        self.cur = None
        self.remain = 0.0
        self.is_running = False
        self.pub_vel.publish(Twist())
        self.send_state('aborted', reason=reason)

    def next_block(self):
        """반복문 내부에 IF문이나 다른 제어 블록이 중첩되어도 런타임에 실시간으로 한 단계씩 해석합니다."""
        while self.program:
            block = self.program.pop(0)
            op = block.get('op')
            
            # 1. 런타임 반복문 해석: 자식 블록들을 개수만큼 풀어 헤쳐 대기열 맨 앞에 주입 (중첩 구조 보존)
            if op == 'repeat':
                count = int(block.get('count', 1))
                inner_blocks = block.get('blocks', []) # blocks.html 규격과 연동
                unrolled = []
                for _ in range(count):
                    unrolled.extend(json.loads(json.dumps(inner_blocks)))
                self.program = unrolled + self.program
                continue # 루프를 다시 돌려 방금 풀린 첫 번째 블록을 해석함
                
            # 2. 런타임 IF문 해석: 반복문 안에서 차례가 돌아온 '바로 지금 이 순간' 센서값을 체크!
            elif op == 'if':
                cond = block.get('cond')
                if cond == 'front_obstacle' and self.dist_front < OBSTACLE_M:
                    then_blocks = block.get('then', [])
                    self.program = json.loads(json.dumps(then_blocks)) + self.program
                continue # 조건이 맞지 않으면 자식을 풀지 않고 그냥 패스함

            self.cur = block
            break
        
        if not self.cur:
            if self.is_running:
                self.is_running = False
                self.pub_vel.publish(Twist()) 
                self.send_state('done')
            return

        # 동작 시간 세팅
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
            
            # 주행 중에 벽을 보면 현재 명령 블록만 스킵하고 제어권을 즉시 다음 블록(IF 등)으로 이양
            if op == 'forward' and self.dist_front < OBSTACLE_M:
                self.get_logger().warn(f"⚠️ [주행 중 탈출] 전방 장애물 감지! 다음 블록으로 이동합니다. (거리: {self.dist_front:.2f}m)")
                self.pub_vel.publish(Twist()) 
                self.cur = None 
                return
            elif op == 'backward' and self.dist_rear < OBSTACLE_M:
                self.get_logger().warn(f"⚠️ [주행 중 탈출] 후방 장애물 감지! 다음 블록으로 이동합니다. (거리: {self.dist_rear:.2f}m)")
                self.pub_vel.publish(Twist())
                self.cur = None
                return

            # 모터 제어
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
