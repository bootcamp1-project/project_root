#!/usr/bin/env python3
"""ultrasonic_node: 라이다(LDS-03)로 전방/후방 거리 동시 측정"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from sensor_msgs.msg import LaserScan
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class UltrasonicNode(Node):
    def __init__(self):
        super().__init__('ultrasonic_node')
        
        # 전방과 후방 거리를 각각 발행할 2개의 퍼블리셔 생성
        self.pub_front = self.create_publisher(Float32, '/obstacle_dist/front', 10)
        self.pub_rear = self.create_publisher(Float32, '/obstacle_dist/rear', 10)

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            qos_profile
        )
        self.get_logger().info('🚀 [전/후방 감시] 라이다 센서가 앞뒤를 모두 감시합니다!')

    def scan_callback(self, msg):
        if not msg.ranges:
            return

        # 정면 (0도 기준 좌우 5도)
        front_ranges = msg.ranges[0:5] + msg.ranges[355:360]
        # 후방 (180도 기준 좌우 5도 -> 175도 ~ 185도)
        rear_ranges = msg.ranges[175:185]
        
        # 유효한 거리(m)만 필터링
        valid_front = [r for r in front_ranges if msg.range_min < r < msg.range_max]
        valid_rear = [r for r in rear_ranges if msg.range_min < r < msg.range_max]

        msg_f = Float32()
        msg_r = Float32()
        
        msg_f.data = float(min(valid_front)) if valid_front else 999.0
        msg_r.data = float(min(valid_rear)) if valid_rear else 999.0

        self.pub_front.publish(msg_f)
        self.pub_rear.publish(msg_r)

def main():
    rclpy.init()
    node = UltrasonicNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
