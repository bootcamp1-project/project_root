# 📡 ROS2 Topic Interface
 
> 블록 코딩 로봇 교육 플랫폼의 ROS 2 토픽 인터페이스 정의서

---

# 1. 시스템 개요

웹 애플리케이션에서 작성한 블록 프로그램을 ROS 2로 전달하고, Interpreter Node가 이를 해석하여 TurtleBot3를 제어한다.

실행 상태는 다시 웹으로 전달되어 현재 실행 중인 블록을 표시하며, 초음파 센서는 장애물을 감지하여 안전 정지를 수행한다.

---

# 2. Topic Interface

| Topic | Message Type | Publisher | Subscriber | Rate | Type | QoS |
|--------|--------------|-----------|------------|------|------|------|
| `/program` | `std_msgs/msg/String` | Web App | Interpreter Node | Event | Edge | RELIABLE |
| `/run_stop` | `std_msgs/msg/Bool` | Web App | Interpreter Node | Event | Edge | RELIABLE |
| `/run_state` | `std_msgs/msg/String` | Interpreter Node | Web App | Event | Edge | RELIABLE |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Interpreter Node | TurtleBot3 | 10 Hz | Continuous | RELIABLE |
| `/obstacle_dist` | `std_msgs/msg/Float32` | Ultrasonic Node | Interpreter Node | 10 Hz | Continuous | RELIABLE |
| `/buzzer` | `std_msgs/msg/Bool` | Interpreter Node | Buzzer Node | Event | Edge | RELIABLE |

---

# 3. Block Specification

웹에서는 블록을 JSON 배열 형태로 전송한다.

## Forward

```json
{
  "op":"forward",
  "sec":3
}
```

3초 동안 전진한다.

---

## Turn Left

```json
{
  "op":"turn_left"
}
```

좌측으로 약 90° 회전한다.

---

## Turn Right

```json
{
  "op":"turn_right"
}
```

우측으로 약 90° 회전한다.

---

## Wait

```json
{
  "op":"wait",
  "sec":2
}
```

2초 동안 대기한다.

---

## Buzzer

```json
{
  "op":"buzzer"
}
```

부저를 약 0.5초 동안 울린다.

---

# 4. Program Format

웹에서 Interpreter Node로 전달하는 전체 프로그램 예시이다.

```json
[
  {
    "op":"forward",
    "sec":3
  },
  {
    "op":"turn_left"
  },
  {
    "op":"forward",
    "sec":2
  },
  {
    "op":"buzzer"
  },
  {
    "op":"wait",
    "sec":1
  }
]
```

---

# 5. Run State Format

Interpreter Node는 현재 실행 상태를 JSON 문자열로 전송한다.

## 실행 시작

```json
{
    "state":"running",
    "total":5
}
```

---

## 블록 실행 중

```json
{
    "state":"block",
    "op":"forward",
    "left":4
}
```

| 항목 | 설명 |
|------|------|
| state | 현재 상태 |
| op | 실행 중인 블록 |
| left | 남은 블록 개수 |

---

## 실행 완료

```json
{
    "state":"done"
}
```

---

## 실행 중단

```json
{
    "state":"aborted",
    "reason":"장애물 감지"
}
```

또는

```json
{
    "state":"aborted",
    "reason":"사용자 중지"
}
```

---

# 6. Data Flow

```text
Web App
    │
    │  /program
    ▼
Interpreter Node
    │
    ├──────────────▶ /cmd_vel
    │
    ├──────────────▶ /buzzer
    │
    └──────────────▶ /run_state
            ▲
            │
   /obstacle_dist
            ▲
            │
 Ultrasonic Node
```

---

# 7. Safety Policy

## 장애물 감지

- 거리 20cm 이하에서 즉시 정지
- 모든 이동 명령 중단
- `/run_state`에 중단 이유 전송

---

## 긴급 정지

웹의 Stop 버튼 클릭 시

- 모든 블록 제거
- 속도 0으로 설정
- 상태를 `aborted`로 변경

---

## 프로그램 실행 중

- 새로운 `/program`은 무시한다.
- 실행 완료 후에만 새로운 프로그램을 수신한다.

---

# 8. QoS Policy

| Topic | QoS |
|---------|------|
| /program | RELIABLE |
| /run_stop | RELIABLE |
| /run_state | RELIABLE |
| /cmd_vel | RELIABLE |
| /obstacle_dist | RELIABLE |
| /buzzer | RELIABLE |

---

# 9. Interface Version

Version : **1.0**

Last Update : Day 1

Status : Approved
