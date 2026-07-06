#!/usr/bin/env python3
"""ultrasonic_node: HC-SR04 초음파 센서로 거리 측정 -> /obstacle_dist (Float32, 10Hz)"""
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

TRIG_PIN = 23
ECHO_PIN = 24
MAX_WAIT = 0.03        
PUBLISH_HZ = 10.0

try:
    import RPi.GPIO as GPIO
    HW_AVAILABLE = True
except (ImportError, RuntimeError):
    HW_AVAILABLE = False


class UltrasonicNode(Node):
    def __init__(self):
        super().__init__('ultrasonic_node')
        self.pub = self.create_publisher(Float32, '/obstacle_dist', 10)

        if HW_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(TRIG_PIN, GPIO.OUT)
            GPIO.setup(ECHO_PIN, GPIO.IN)
            GPIO.output(TRIG_PIN, False)
            time.sleep(0.3)
            self.get_logger().info('HC-SR04 초기화 완료')
        else:
            self.get_logger().warn('RPi.GPIO를 사용할 수 없음 -> 더미 값 발행')

        self.timer = self.create_timer(1.0 / PUBLISH_HZ, self.tick)

    def measure_once(self):
        if not HW_AVAILABLE:
            return None
        GPIO.output(TRIG_PIN, True)
        time.sleep(0.00001)
        GPIO.output(TRIG_PIN, False)

        start = time.time()
        timeout = start + MAX_WAIT
        while GPIO.input(ECHO_PIN) == 0:
            start = time.time()
            if start > timeout:
                return None

        stop = time.time()
        timeout = stop + MAX_WAIT
        while GPIO.input(ECHO_PIN) == 1:
            stop = time.time()
            if stop > timeout:
                return None

        elapsed = stop - start
        distance_m = (elapsed * 343.0) / 2.0
        return distance_m

    def tick(self):
        msg = Float32()
        if HW_AVAILABLE:
            d = self.measure_once()
            msg.data = float(d) if d is not None else 999.0
        else:
            msg.data = 999.0
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = UltrasonicNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if HW_AVAILABLE:
            GPIO.cleanup()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
