# 📡 INTERFACE.md

# 블록 코딩 로봇 교육 플랫폼 인터페이스 명세서

> ROS 2 Humble 기반 TurtleBot3 블록 코딩 교육 플랫폼의 통신 인터페이스 정의

---

# 1. 문서 목적

본 문서는 웹 애플리케이션과 ROS 2 노드 간의 데이터 교환 규격을 정의한다.

인터페이스를 표준화하여 프론트엔드와 ROS2 노드가 독립적으로 개발되더라도 동일한 프로토콜을 사용할 수 있도록 하는 것을 목표로 한다.

---

# 2. 시스템 구성

```text
Web Browser
      │
      │ WebSocket
      ▼
rosbridge_server
      │
      ▼
ROS2 Topics
      │
      ▼
Interpreter Node
      │
 ┌────┼────┐
 │    │    │
 ▼    ▼    ▼
cmd_vel
run_state
buzzer

      ▲
      │
obstacle_dist
      ▲
      │
Ultrasonic Node
```

---

# 3. 통신 방식

웹과 ROS2는 **rosbridge_server(WebSocket)** 를 이용하여 통신한다.

### Web → ROS2

프로그램 실행 명령

JSON Tree

↓

`/program`

↓

Interpreter Node

---

### ROS2 → Web

현재 실행 중인 블록

↓

`/run_state`

↓

Web Highlight

---

# 4. Topic 목록

| Topic | Type | Publisher | Subscriber | 설명 |
|--------|------|-----------|------------|------|
| /program | std_msgs/String | Web | Interpreter | 블록 프로그램(JSON) |
| /cmd_vel | geometry_msgs/Twist | Interpreter | TurtleBot3 | 이동 명령 |
| /run_state | std_msgs/String | Interpreter | Web | 현재 실행 블록 |
| /buzzer | std_msgs/Int32 | Interpreter | Buzzer Node | 부저 제어 |
| /scan | sensor_msgs/LaserScan | TurtleBot3 | Ultrasonic Node | LiDAR 원본 데이터 |
| /obstacle_dist/front | std_msgs/Float32 | Ultrasonic | Interpreter | 전방 거리 |
| /obstacle_dist/rear | std_msgs/Float32 | Ultrasonic | Interpreter | 후방 거리 |

---

# 5. 데이터 흐름

```text
Web

↓

JSON Tree 생성

↓

rosbridge_server

↓

/program

↓

Interpreter

↓

cmd_vel

↓

TurtleBot3
```

실행 상태는 다음과 같이 역방향으로 전달된다.

```text
Interpreter

↓

/run_state

↓

rosbridge_server

↓

Web

↓

현재 블록 Highlight
```

---

# 6. 프로그램(JSON) 구조

Interpreter는 프로그램을 JSON Tree 형태로 입력받는다.

예시

```json
[
  {
    "op":"forward",
    "time":2
  },
  {
    "op":"left",
    "time":1
  }
]
```

---

반복문 예시

```json
{
  "op":"repeat",
  "count":3,
  "children":[
      {
          "op":"forward",
          "time":1
      }
  ]
}
```

---

조건문 예시

```json
{
  "op":"if_front",
  "children":[
      {
          "op":"right"
      }
  ]
}
```

---

중첩 구조 예시

```json
{
    "op":"repeat",
    "count":2,
    "children":[
        {
            "op":"forward"
        },
        {
            "op":"if_front",
            "children":[
                {
                    "op":"right"
                }
            ]
        }
    ]
}
```

---

# 7. 실행 상태(run_state)

Interpreter는 현재 실행 중인 블록을 Web으로 전달한다.

예시

```json
{
    "op":"forward"
}
```

또는

```json
{
    "op":"left"
}
```

웹에서는 전달받은 op를 이용하여 해당 블록을 Highlight한다.

---

# 8. 명령(Operation) 정의

| op | 설명 |
|----|------|
| forward | 전진 |
| backward | 후진 |
| left | 좌회전 |
| right | 우회전 |
| wait | 대기 |
| buzzer | 부저 |
| repeat | 반복문 |
| if_front | 전방 조건 |
| if_rear | 후방 조건 |

---

# 9. Runtime Interpreter 동작

Interpreter는 프로그램을 미리 펼치지 않는다.

Tree 구조를 Runtime에 직접 해석한다.

실행 순서는 다음과 같다.

```text
Stack Push

↓

현재 Node 실행

↓

Children 존재 여부 확인

↓

Stack Push

↓

다음 Node 실행

↓

Stack Empty

↓

종료
```

이를 통해 반복문과 조건문의 중첩 구조를 지원한다.

---

# 10. 장애물 감지

Interpreter는 `/obstacle_dist/front`와 `/obstacle_dist/rear` Topic을 구독한다.

임계 거리 이내로 장애물이 감지되면

```
현재 이동 블록 종료

↓

속도 0 전송

↓

다음 블록 실행
```

과정을 수행한다.

---

# 11. 예외 처리

| 상황 | 처리 |
|------|------|
| 잘못된 JSON | 프로그램 실행 중단 |
| WebSocket 종료 | 프로그램 종료 |
| Emergency Stop | cmd_vel = 0 |
| 장애물 감지 | Runtime Skip |
| 빈 프로그램 | 실행하지 않음 |

---

# 12. 인터페이스 규칙

- 모든 프로그램은 JSON Tree 형태로 전송한다.
- Web과 ROS2는 rosbridge_server를 통해 연결한다.
- 실행 상태는 `/run_state` Topic으로 전달한다.
- Interpreter는 Runtime에 Tree를 해석한다.
- 장애물 감지는 LiDAR 데이터를 기반으로 수행한다.
- Emergency Stop은 언제든 프로그램 실행을 중단할 수 있어야 한다.

---

# 13. 인터페이스 변경 이력

| 버전 | 내용 |
|------|------|
| v1.0 | 기본 Topic 정의 |
| v1.1 | JSON Tree 구조 추가 |
| v1.2 | Runtime Interpreter 명세 추가 |
| v1.3 | Runtime Skip 및 장애물 처리 명세 추가 |
| v1.4 | 최종 인터페이스 문서 정리 |

---
