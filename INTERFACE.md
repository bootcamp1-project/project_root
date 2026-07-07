# 📡 ROS2 Topic Interface
 
> 블록 코딩 로봇 교육 플랫폼의 ROS 2 토픽 인터페이스 정의서
---
# 1. 시스템 개요
웹 애플리케이션에서 작성한 블록 프로그램을 ROS 2로 전달하고, Interpreter Node가 이를 해석하여 TurtleBot3를 제어한다.
실행 상태는 다시 웹으로 전달되어 현재 실행 중인 블록을 표시하며, 라이다(LiDAR) 센서는 로봇의 진행 방향(전방/후방)에서 장애물을 감지하여 안전 정지를 수행한다.
---
# 2. Topic Interface
| Topic | Message Type | Publisher | Subscriber | Rate | Type | QoS |
|--------|--------------|-----------|------------|------|------|------|
| `/program` | `std_msgs/msg/String` | Web App | Interpreter Node | Event | Edge | RELIABLE |
| `/run_stop` | `std_msgs/msg/Bool` | Web App | Interpreter Node | Event | Edge | RELIABLE |
| `/run_state` | `std_msgs/msg/String` | Interpreter Node | Web App | Event | Edge | RELIABLE |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Interpreter Node | TurtleBot3 | 10 Hz | Continuous | RELIABLE |
| `/obstacle_dist/front` | `std_msgs/msg/Float32` | Ultrasonic Node (LiDAR) | Interpreter Node | 10 Hz | Continuous | RELIABLE |
| `/obstacle_dist/rear` | `std_msgs/msg/Float32` | Ultrasonic Node (LiDAR) | Interpreter Node | 10 Hz | Continuous | RELIABLE |
| `/buzzer` | `std_msgs/msg/Bool` | Interpreter Node | Buzzer Node | Event | Edge | RELIABLE |

> LiDAR(LDS-03)를 전/후방 두 방향으로 나누어 스캔하며, 호환성을 위해 노드 파일명은 기존대로 `ultrasonic_node.py`를 유지한다 (`README.md` 프로젝트 구조 참고).

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
## Backward
```json
{
  "op":"backward",
  "sec":3
}
```
3초 동안 후진한다.
---
## Turn Left
```json
{
  "op":"turn_left"
}
```
좌측으로 약 90° 회전한다. (제자리 회전 시간 상수 `TURN_90_SEC = 3.1`로 보정됨)
---
## Turn Right
```json
{
  "op":"turn_right"
}
```
우측으로 약 90° 회전한다. (제자리 회전 시간 상수 `TURN_90_SEC = 3.1`로 보정됨)
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
    "op":"backward",
    "sec":1
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
반복 블록은 웹앱(JS) 단에서 실제 실행 순서대로 완전히 평탄화(Unrolling)한 뒤 위와 같은 단일 배열 형태로 전송한다. 예를 들어 `[3번 반복: 앞으로, 부저]`는 `[앞으로, 부저, 앞으로, 부저, 앞으로, 부저]`로 변환되어 전달된다.
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
   /obstacle_dist/front, /obstacle_dist/rear
            ▲
            │
  Lidar Node (ultrasonic_node.py)
```
---
# 7. Safety Policy
## 장애물 감지 (전진/후진 중에만 적용)
- `forward`(전진) 또는 `backward`(후진) 블록 실행 중, 진행 방향 기준 거리 20cm 이하 감지 시 즉시 정지
- 모든 이동 명령 중단
- `/run_state`에 중단 이유 전송

> **주의:** `turn_left`/`turn_right`(회전) 블록 실행 중에는 주변 지형지물에 의한 오검측 리스크가 커서 장애물 검사를 수행하지 않는다. 이는 개발 중 실차 테스트로 확인된 정책이며, 상세 근거는 `TEST.md` 2.3, `REPORT.md` 7번을 참고한다.
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
- 실행 중에는 웹앱 UI도 잠금(Lock) 상태가 되어, 사용자가 편집 화면을 조작하더라도 새 프로그램이 전송되지 않는다 (이중 방어, `REPORT.md` 7번 참고).
---
# 8. QoS Policy
| Topic | QoS |
|---------|------|
| /program | RELIABLE |
| /run_stop | RELIABLE |
| /run_state | RELIABLE |
| /cmd_vel | RELIABLE |
| /obstacle_dist/front | RELIABLE |
| /obstacle_dist/rear | RELIABLE |
| /buzzer | RELIABLE |
---
# 9. Interface Version
Version : **1.1**
Last Update : Day 3 (전/후방 장애물 토픽 분리, 후진 블록 및 회전 중 정지 제외 정책 반영)
Status : Approved
