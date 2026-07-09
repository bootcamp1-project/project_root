#!/usr/bin/env python3
"""ultrasonic_node_fixed.py

LaserScan(/scan)을 읽어서 전방/후방 장애물 최단 거리를 발행합니다.
기존 코드처럼 ranges 인덱스를 0~359도라고 가정하지 않고,
angle_min / angle_increment를 이용해 실제 각도를 계산합니다.
"""

import math
from typing import Iterable, List, Optional

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool, Float32

OBSTACLE_M = 0.20      # 20 cm 이내면 장애물 True
FRONT_HALF_DEG = 45.0  # 정면 기준 좌우 45도 = 총 90도
REAR_HALF_DEG = 45.0   # 후면 기준 좌우 45도 = 총 90도


def normalize_angle(rad: float) -> float:
    """각도를 -pi ~ pi 범위로 정규화합니다."""
    return math.atan2(math.sin(rad), math.cos(rad))


def min_or_default(values: Iterable[float], default: float = 999.0) -> float:
    vals = list(values)
    return float(min(vals)) if vals else float(default)


class UltrasonicNode(Node):
    def __init__(self) -> None:
        super().__init__('ultrasonic_node')

        self.pub_front = self.create_publisher(Float32, '/obstacle_dist/front', 10)
        self.pub_rear = self.create_publisher(Float32, '/obstacle_dist/rear', 10)
        self.pub_front_bool = self.create_publisher(Bool, '/front_obstacle', 10)
        self.pub_obstacle_bool = self.create_publisher(Bool, '/obstacle', 10)

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self.sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, qos_profile)
        self.get_logger().info('✅ ultrasonic_node_fixed 실행됨: LaserScan 실제 각도 기반 전/후방 감시')

    def valid_range(self, msg: LaserScan, r: float) -> bool:
        return math.isfinite(r) and msg.range_min < r < msg.range_max

    def scan_callback(self, msg: LaserScan) -> None:
        if not msg.ranges or msg.angle_increment == 0.0:
            return

        front_half = math.radians(FRONT_HALF_DEG)
        rear_half = math.radians(REAR_HALF_DEG)
        front_values: List[float] = []
        rear_values: List[float] = []

        for i, r in enumerate(msg.ranges):
            if not self.valid_range(msg, float(r)):
                continue
            angle = normalize_angle(msg.angle_min + i * msg.angle_increment)

            # 전방: 0도 주변
            if abs(angle) <= front_half:
                front_values.append(float(r))

            # 후방: +180도 또는 -180도 주변
            if abs(abs(angle) - math.pi) <= rear_half:
                rear_values.append(float(r))

        front_min = min_or_default(front_values)
        rear_min = min_or_default(rear_values)

        self.pub_front.publish(Float32(data=front_min))
        self.pub_rear.publish(Float32(data=rear_min))

        front_hit = front_min < OBSTACLE_M
        self.pub_front_bool.publish(Bool(data=front_hit))
        self.pub_obstacle_bool.publish(Bool(data=front_hit))


def main() -> None:
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
