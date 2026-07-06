#!/usr/bin/env python3
"""HC-SR04 배선 단독 테스트 (ROS 없이). 파이에서 직접 실행:
   python3 test_ultrasonic.py
"""
import RPi.GPIO as GPIO
import time

TRIG_PIN = 23
ECHO_PIN = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.output(TRIG_PIN, False)

print("센서 안정화 대기...")
time.sleep(1)

try:
    for i in range(10):
        # 트리거 전 echo 핀 초기 상태 확인
        print(f"[{i}] 트리거 전 ECHO 핀 상태: {GPIO.input(ECHO_PIN)}")

        GPIO.output(TRIG_PIN, True)
        time.sleep(0.00001)
        GPIO.output(TRIG_PIN, False)

        start_wait = time.time()
        while GPIO.input(ECHO_PIN) == 0:
            if time.time() - start_wait > 0.03:
                print(f"[{i}] ECHO가 HIGH로 안 올라옴 (타임아웃) -> 배선/전원 확인 필요")
                break
        else:
            pulse_start = time.time()
            stop_wait = time.time()
            while GPIO.input(ECHO_PIN) == 1:
                if time.time() - stop_wait > 0.03:
                    print(f"[{i}] ECHO가 계속 HIGH -> 이상")
                    break
            pulse_end = time.time()
            dist = (pulse_end - pulse_start) * 343.0 / 2.0
            print(f"[{i}] 거리: {dist*100:.1f} cm")

        time.sleep(0.5)
finally:
    GPIO.cleanup()
