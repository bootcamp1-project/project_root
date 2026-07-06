#!/usr/bin/env python3
"""buzzer_node: /buzzer (Bool) 수신 시 터틀봇3 처음 켜질 때 나는 부팅음(Value 2) 출력"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from turtlebot3_msgs.msg import Sound

class BuzzerNode(Node):
    def __init__(self):
        super().__init__('buzzer_node')
        self.sub = self.create_subscription(Bool, '/buzzer', self.on_buzzer, 10)
        self.pub_sound = self.create_publisher(Sound, '/sound', 10)
        self.get_logger().info('★ 터틀봇3 처음 켜질 때 나는 음(Value 2) 세팅 완료!')

    def on_buzzer(self, msg):
        if not msg.data:
            return
            
        sound_msg = Sound()
        # ★ 핵심: 1번(단음) 대신 2번을 넣어야 우리가 아는 그 부팅 멜로디가 나옵니다!
        sound_msg.value = 2
        
        self.pub_sound.publish(sound_msg)
        self.get_logger().info('🔔 [부저 노드] 처음 켜질 때 나는 멜로디(Value: 2) 발행 성공!')

def main():
    rclpy.init()
    node = BuzzerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
