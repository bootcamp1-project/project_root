#!/usr/bin/env python3
"""ultrasonic_node: 라이다(LDS-03) 사각지대 제거 버전 (전/후방 각각 90도 부채꼴 감시)"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from sensor_msgs.msg import LaserScan
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class UltrasonicNode(Node):
    def __init__(self):
        super().__init__('ultrasonic_node')
        
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
        self.get_logger().info('🚀 [사각지대 제로 패치] 앞/뒤 좌우 45도 대각선 영역까지 모두 감시합니다!')

    def scan_callback(self, msg):
        if not msg.ranges:
            return

        # 정면 및 대각선 사각지대 포함 (0도 기준 좌우 45도 -> 총 90도 범위)
        front_ranges = msg.ranges[0:45] + msg.ranges[315:360]
        
        # 후면 및 대각선 사각지대 포함 (180도 기준 좌우 45도 -> 135 ~ 225도 범위)
        rear_ranges = msg.ranges[135:225]
        
        # 유효한 거리(m)만 필터링 (센서 측정 최소/최대값 사이의 데이터만 인정)
        valid_front = [r for r in front_ranges if msg.range_min < r < msg.range_max]
        valid_rear = [r for r in rear_ranges if msg.range_min < r < msg.range_max]

        msg_f = Float32()
        msg_r = Float32()
        
        # 감시 범위 내에서 가장 가까운 장애물 거리를 발행
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
