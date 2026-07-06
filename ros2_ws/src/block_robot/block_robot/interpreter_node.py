#!/usr/bin/env python3
"""interpreter_node: 블록 프로그램 순차 실행 + 전/후방 안전 방어"""
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool, Float32
from geometry_msgs.msg import Twist

OBSTACLE_M = 0.20      # 장애물 제한 거리 (20cm)
TURN_90_SEC = 3.4      # 90도 회전 시간 (실측 보정 값)
LINEAR_SPEED = 0.10    # 전진/후진 속도 (m/s)
ANGULAR_SPEED = 0.5    # 회전 속도 (rad/s)

class InterpreterNode(Node):
    def __init__(self):
        super().__init__('interpreter_node')
        
        self.sub_prog = self.create_subscription(String, '/program', self.on_program, 10)
        self.sub_stop = self.create_subscription(Bool, '/run_stop', self.on_stop, 10)
        
        # 전방/후방 거리 각각 구독
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
        self.get_logger().info('★ 완벽 패치: [전/후방 장애물 회피] 지능이 추가되었습니다!')

    def send_state(self, status, **kwargs):
        msg = String()
        msg.data = json.dumps({'state': status, **kwargs}, ensure_ascii=False)
        self.pub_state.publish(msg)

    def on_program(self, msg):
        if self.is_running:
            self.get_logger().warn('이미 실행 중입니다!')
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
        if not self.program:
            if self.cur is not None or self.is_running:
                self.cur = None
                self.is_running = False
                self.pub_vel.publish(Twist()) 
                self.send_state('done')
            return

        self.cur = self.program.pop(0)
        op = self.cur['op']
        
        if op in ('forward', 'backward'):
            self.remain = float(self.cur.get('sec', 1))
        elif op in ('turn_left', 'turn_right'):
            self.remain = TURN_90_SEC
        elif op == 'wait':
            self.remain = float(self.cur.get('sec', 1))
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
            
            # [핵심] 앞으로 갈 때는 앞을, 뒤로 갈 때는 뒤를 검사!
            if op == 'forward' and self.dist_front < OBSTACLE_M:
                self.get_logger().warn(f"🚨 전방 장애물 감지! (거리: {self.dist_front:.2f}m)")
                self.abort('장애물 감지') # HTML 호환성을 위해 에러명 '장애물 감지' 유지
                return
            elif op == 'backward' and self.dist_rear < OBSTACLE_M:
                self.get_logger().warn(f"🚨 후방 장애물 감지! (거리: {self.dist_rear:.2f}m)")
                self.abort('장애물 감지') # HTML 호환성을 위해 에러명 '장애물 감지' 유지
                return

            # 속도 및 회전 부여
            if op == 'forward':
                cmd.linear.x = LINEAR_SPEED
                cmd.angular.z = 0.0
            elif op == 'backward':
                cmd.linear.x = -LINEAR_SPEED
                cmd.angular.z = 0.0
            elif op == 'turn_left':
                cmd.linear.x = 0.0
                cmd.angular.z = ANGULAR_SPEED
            elif op == 'turn_right':
                cmd.linear.x = 0.0
                cmd.angular.z = -ANGULAR_SPEED
            elif op == 'wait' or op == 'buzzer':
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
