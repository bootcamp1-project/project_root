# 📡 ROS2 Topic Interface

> 블록 코딩 로봇 교육 플랫폼의 ROS 2 토픽 인터페이스 정의서

---

## 1. 시스템 개요

웹 애플리케이션에서 중첩 조립한 블록 프로그램(JSON Tree)을 ROS 2로 전달하면, Interpreter Node가 이를 런타임에 실시간으로 해석하여 TurtleBot3를 제어한다.

실행 상태는 실시간으로 웹으로 역전파되어 현재 구동 중인 블록을 직관적으로 표시한다. 라이다(LiDAR) 센서는 대각선 사각지대를 포함한 전/후방 90도 범위를 철벽 감시하며, 주행 중 장애물 발견 시 현재 블록을 즉시 탈출(Skip)하고 하위 조건 분기 블록으로 제어권을 부드럽게 이양한다.

---

## 2. Topic Interface

| Topic | Message Type | Publisher | Subscriber | Rate | Type | QoS |
|--------|--------------|-----------|------------|------|------|------|
| `/program` | `std_msgs/msg/String` | Web App | Interpreter Node | Event | Edge | RELIABLE |
| `/run_stop` | `std_msgs/msg/Bool` | Web App | Interpreter Node | Event | Edge | RELIABLE |
| `/run_state` | `std_msgs/msg/String` | Interpreter Node | Web App | Event | Edge | RELIABLE |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Interpreter Node | TurtleBot3 | 10 Hz | Continuous | RELIABLE |
| `/obstacle_dist/front` | `std_msgs/msg/Float32` | Ultrasonic Node (LiDAR) | Interpreter Node | 10 Hz | Continuous | RELIABLE |
| `/obstacle_dist/rear` | `std_msgs/msg/Float32` | Ultrasonic Node (LiDAR) | Interpreter Node | 10 Hz | Continuous | RELIABLE |
| `/buzzer` | `std_msgs/msg/Bool` | Interpreter Node | Buzzer Node | Event | Edge | RELIABLE |

> **호환성 노트:** LiDAR(LDS-03)의 360도 전방위 스캔 데이터를 전/후방 부채꼴 영역으로 가공하여 스캔하며, 시스템 호환성을 유지하기 위해 노드 파일명은 기존대로 `ultrasonic_node.py`를 유지한다.

---

## 3. Block Specification

웹에서는 블록을 중첩이 가능한 JSON 트리 구조 형태로 직렬화하여 전송한다.

### Forward

```json
{
  "op": "forward",
  "sec": 3.0
}
```

지정한 시간(초) 동안 전진한다 (시간 미지정 시 기본 3.0초).

### Backward

```json
{
  "op": "backward",
  "sec": 3.0
}
```

지정한 시간(초) 동안 후진한다 (시간 미지정 시 기본 3.0초).

### Turn Left

```json
{
  "op": "turn_left"
}
```

좌측으로 약 90° 회전한다. (제자리 회전 시간 상수 `TURN_90_SEC = 3.4`로 실제 구동 사양 보정 완료)

### Turn Right

```json
{
  "op": "turn_right"
}
```

우측으로 약 90° 회전한다. (제자리 회전 시간 상수 `TURN_90_SEC = 3.4`로 실제 구동 사양 보정 완료)

### Wait

```json
{
  "op": "wait",
  "sec": 1.0
}
```

지정한 시간 동안 대기한다.

### Buzzer

```json
{
  "op": "buzzer"
}
```

부저를 약 0.5초 동안 울린다.

### Repeat (반복하기)

```json
{
  "op": "repeat",
  "count": 2,
  "blocks": [
    { "op": "forward", "sec": 3.0 }
  ]
}
```

내부에 중첩된 자식 블록들(`blocks`)을 지정한 횟수(`count`)만큼 실시간 루프로 반복 실행한다.

### If (만약에)

```json
{
  "op": "if",
  "cond": "front_obstacle",
  "then": [
    { "op": "backward", "sec": 3.0 }
  ]
}
```

해당 블록 차례가 온 런타임 순간에 조건(`cond`)을 검사하여 참(장애물 거리 20cm 미만)일 경우 내부 자식 블록들(`then`)을 대기열에 주입하여 실행한다.

---

## 4. Program Format (Nested Tree 구조)

**[중요 변경]** 기존의 웹앱 단 선형 평탄화(Loop Unrolling) 전송 방식을 전면 무효화하고, 스크래치 고유의 실시간 논리 제어를 위해 중첩 트리(Nested JSON Tree) 형태로 프로그램을 전송한다.

```json
[
  {
    "op": "repeat",
    "count": 2,
    "blocks": [
      {
        "op": "if",
        "cond": "front_obstacle",
        "then": [
          { "op": "backward", "sec": 3.0 }
        ]
      },
      {
        "op": "forward",
        "sec": 3.0
      }
    ]
  }
]
```

Interpreter Node는 이 트리를 기억하고 있다가, 주행 중에 실시간 한 단계씩 스택 구조로 깨서 해석(Runtime Parsing)을 수행한다.

---

## 5. Run State Format

Interpreter Node는 현재 실행 상태를 JSON 문자열로 웹에 실시간 송신한다. 웹앱은 이 토픽을 다이렉트로 매핑하여 시각적인 블록 반짝임 동기화(하이라이트)를 구현한다.

### 실행 시작

```json
{
  "state": "running",
  "total": 5
}
```

### 블록 실행 중

```json
{
  "state": "block",
  "op": "forward",
  "left": 4
}
```

| 항목 | 설명 |
|------|------|
| `state` | 현재 상태 |
| `op` | 현재 하드웨어가 실제로 수행 중인 동작 연산자 |
| `left` | 대기열에 남은 잔여 블록 개수 |

### 실행 완료

```json
{
  "state": "done"
}
```

### 실행 중단 (치명적 예외 상황 발생 시)

```json
{
  "state": "aborted",
  "reason": "사용자 중지"
}
```

> **주의:** 주행 중 벽 발견 시에는 전체 중단(`aborted`) 대신 아래의 안전 정책에 의거해 실시간 탈출 분기를 탑재함.

---

## 6. Data Flow

```
      Web App (JSON 트리 빌드 및 UI 동적 매핑)
           │
           │  /program (중첩 Tree)
           ▼
     Interpreter Node (실시간 런타임 스택 제어 엔진)
           │
           ├──────────────▶ /cmd_vel (바퀴 모터 구동)
           │
           ├──────────────▶ /buzzer (멜로디 제어)
           │
           └──────────────▶ /run_state (현재 실행 op 다이렉트 전송)
                 ▲
                 │ /obstacle_dist/front, /obstacle_dist/rear
                 │ (90도 부채꼴 스캔 최적 거리 데이터)
                 │
      Lidar Node (ultrasonic_node.py) [사각지대 제로 패치 완료]
```

---

## 7. Safety Policy

### 주행 중 실시간 조건 탈출 (Runtime Skip & Branch)

- **실시간 도중하차:** `forward`(전진) 또는 `backward`(후진) 블록 실행 도중, 해당 진행 방향의 부채꼴 감시 범위 내에서 거리 임계값(20cm) 이하가 감지되면 전체 프로그램을 강제 강등시키는 대신 현재 주행 블록만 즉시 탈출(Skip) 처리한다.
- **제어권 부드러운 이양:** 전진 블록이 스킵(`self.cur = None`)되면 다음 틱에서 대기열 하단에 위치한 [만약에] 블록이 즉시 깨어나게 되며, 실시간 센서 조건이 참이 되므로 내부에 조립된 피하기(후진, 회전 등) 시퀀스가 자연스럽게 이어지도록 설계되었다.

### 대각선 사각지대(Blind Spot) 방어 정책

- **부채꼴 스캔망 전개:** 기존의 일직선(10°) 스캔에서 정면(0°) 및 후면(180°) 기준 좌우 45°씩 총 90°의 광폭 부채꼴 방어막 영역을 설정함.
- **사각지대 소멸:** 로봇이 경사지게 진입하거나 회전 반경 내에 벽이 대각선으로 걸릴 때 발생하는 물리 충돌 결함을 원천 차단하고, 감시 영역 내 최단 거리를 추출하여 실시간 연동한다.

### 오작동 및 긴급 정지 이중 방어

- **초기 간섭 차단 Latch:** 새로운 블록이 트리에서 막 해석되어 인가되는 첫 0.1초의 비동기 주기 동안, 센서 토픽의 미세 노이즈나 타이밍 비싱크로 긴급 제동 시퀀스가 오작동하는 현상을 `just_changed` 플래그로 완벽하게 래치(Latch) 차단 유예한다.
- **웹-로봇 이중 잠금:** 프로그램이 실행 중일 때는 웹 단의 전체 편집 UI가 락(Lock) 상태가 되어 조작이 차단되고, 로봇 단에서도 실행 상태일 때 유입되는 신규 `/program` 토픽은 내부적으로 완전 무시(Drop) 처리하여 시스템 꼬임을 상호 방어한다.

---

## 8. QoS Policy

| Topic | QoS |
|-------|-----|
| `/program` | RELIABLE |
| `/run_stop` | RELIABLE |
| `/run_state` | RELIABLE |
| `/cmd_vel` | RELIABLE |
| `/obstacle_dist/front` | RELIABLE |
| `/obstacle_dist/rear` | RELIABLE |
| `/buzzer` | RELIABLE |

---

## 9. Interface Version

- **Version:** 1.2
- **Last Update:** Day 5 (중첩 JSON 트리 인터프리터 탑재, 주행 중 실시간 블록 탈출 및 제어 이양 메커니즘, 라이다 90도 사각지대 제로 패치 전면 반영)
- **Status:** Final Approved
