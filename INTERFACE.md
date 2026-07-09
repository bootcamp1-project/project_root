# 📡 INTERFACE.md

# 블록 코딩 로봇 교육 플랫폼 인터페이스 명세서

> ROS 2 Humble 기반 TurtleBot3 블록 코딩 교육 플랫폼의 통신 인터페이스 정의
> AI 자연어 기반 블록 프로그램 생성 기능 포함

---

# 1. 문서 목적

본 문서는 웹 애플리케이션, AI 서비스, ROS 2 노드 간의 데이터 교환 규격을 정의한다.

웹 기반 블록 코딩 환경과 ROS 2 기반 TurtleBot3 간의 통신 구조를 표준화하고, AI 자연어 입력을 통한 블록 프로그램 생성 과정까지 포함하여 각 시스템이 독립적으로 개발되더라도 동일한 데이터 규격을 사용할 수 있도록 하는 것을 목표로 한다.

본 플랫폼은 다음 기능을 지원한다.

* 웹 기반 블록 코딩 프로그램 작성
* AI 자연어 입력 기반 블록 프로그램 자동 생성
* JSON Tree 기반 프로그램 데이터 전달
* ROS 2 Interpreter를 통한 로봇 제어
* 실행 상태 Web Highlight 표시
* 장애물 감지 및 Runtime Skip 처리

---

# 2. 시스템 구성

```text
                         User

                          │

                          ▼

                ┌─────────────────┐
                │   AI Panel      │
                │ Natural Language │
                └────────┬────────┘
                         │
                         │ Prompt
                         ▼
                ┌─────────────────┐
                │   AI Service    │
                │ JSON Tree 생성  │
                └────────┬────────┘
                         │
                         │ JSON Tree
                         ▼

┌────────────────────────────────────────┐
│            Web Application             │
│                                        │
│  Blockly Editor                        │
│  Program Manager                       │
│  Run Highlight                        │
└────────────────┬───────────────────────┘
                 │
                 │ WebSocket
                 ▼

        ┌─────────────────┐
        │ rosbridge_server │
        └────────┬────────┘
                 │
                 ▼

              ROS 2 Topics

                 │

                 ▼

          Interpreter Node

        ┌────────┼────────┐
        │        │        │
        ▼        ▼        ▼

     cmd_vel  run_state  buzzer

        │

        ▼

    TurtleBot3


        ▲

        │

 obstacle_dist

        │

 Ultrasonic Node
```

---

# 3. 통신 방식

웹 애플리케이션과 ROS 2는 **rosbridge_server(WebSocket)** 를 이용하여 통신한다.

AI 기능은 웹 애플리케이션 내부의 프로그램 생성 과정에 포함되며, 생성된 결과는 기존 Blockly 프로그램과 동일한 JSON Tree 형식으로 처리된다.

---

## 3.1 AI → Web

사용자가 AI Panel에 자연어 명령을 입력한다.

```
사용자 입력

↓

AI Panel

↓

AI Service

↓

JSON Tree 생성

↓

Blockly Workspace 반영
```

예시 입력

```
앞으로 3초 이동하고
오른쪽으로 회전한 뒤
다시 앞으로 이동해줘.
```

AI는 해당 명령을 분석하여 블록 프로그램 구조(JSON Tree)를 생성한다.

---

## 3.2 Web → ROS2

웹에서 작성되거나 AI가 생성한 블록 프로그램은 JSON Tree 형태로 전달된다.

```
JSON Tree

↓

/program

↓

Interpreter Node

↓

cmd_vel

↓

TurtleBot3
```

---

## 3.3 ROS2 → Web

Interpreter 실행 상태는 Web으로 전달된다.

```
현재 실행 중인 블록

↓

/run_state

↓

rosbridge_server

↓

Web

↓

Block Highlight
```

---

# 4. Topic 목록

| Topic                | Type                  | Publisher   | Subscriber      | 설명                 |
| -------------------- | --------------------- | ----------- | --------------- | ------------------ |
| /program             | std_msgs/String       | Web         | Interpreter     | 블록 프로그램(JSON Tree) |
| /cmd_vel             | geometry_msgs/Twist   | Interpreter | TurtleBot3      | 이동 명령              |
| /run_state           | std_msgs/String       | Interpreter | Web             | 현재 실행 블록           |
| /buzzer              | std_msgs/Int32        | Interpreter | Buzzer Node     | 부저 제어              |
| /scan                | sensor_msgs/LaserScan | TurtleBot3  | Ultrasonic Node | LiDAR 원본 데이터       |
| /obstacle_dist/front | std_msgs/Float32      | Ultrasonic  | Interpreter     | 전방 거리              |
| /obstacle_dist/rear  | std_msgs/Float32      | Ultrasonic  | Interpreter     | 후방 거리              |

---

# 5. 데이터 흐름

## 5.1 일반 블록 실행 흐름

```text
Web

↓

Blockly Workspace

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

---

## 5.2 AI 기반 프로그램 생성 흐름

```text
User

↓

AI Panel

↓

Natural Language Prompt

↓

AI Service

↓

JSON Tree 생성

↓

Blockly Workspace

↓

사용자 실행

↓

rosbridge_server

↓

Interpreter

↓

TurtleBot3
```

---

## 5.3 실행 상태 전달 흐름

```text
Interpreter

↓

/run_state

↓

rosbridge_server

↓

Web

↓

현재 실행 Block Highlight
```

---

# 6. 프로그램(JSON) 구조

Interpreter는 프로그램을 JSON Tree 형태로 입력받는다.

AI가 생성한 프로그램 역시 동일한 JSON Tree 규격을 사용한다.

---

## 기본 구조

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

## 반복문 예시

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

## 조건문 예시

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

## 중첩 구조 예시

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

이어서 **INTERFACE.md v1.5 Part 2 (7~14장)** 입니다.

---

# 7. 실행 상태(run_state)

Interpreter는 현재 실행 중인 블록 정보를 `/run_state` Topic을 통해 Web으로 전달한다.

웹 애플리케이션은 전달받은 `op` 값을 기준으로 현재 실행 중인 블록을 Highlight 한다.

---

## 실행 상태 데이터 예시

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

---

## 실행 상태 흐름

```text
Interpreter

↓

실행 Node 확인

↓

/run_state Publish

↓

rosbridge_server

↓

Web Application

↓

해당 Block Highlight
```

---

# 8. 명령(Operation) 정의

AI 생성 프로그램과 Blockly 프로그램은 동일한 Operation 규격을 사용한다.

| op       | 설명    |
| -------- | ----- |
| forward  | 전진    |
| backward | 후진    |
| left     | 좌회전   |
| right    | 우회전   |
| wait     | 대기    |
| buzzer   | 부저    |
| repeat   | 반복문   |
| if_front | 전방 조건 |
| if_rear  | 후방 조건 |

---

# 9. Runtime Interpreter 동작

Interpreter는 전달받은 JSON Tree를 미리 펼치지 않고 Runtime에서 직접 해석한다.

AI가 생성한 JSON Tree 또한 동일한 방식으로 실행된다.

---

## 실행 과정

```text
Stack Push

↓

현재 Node 확인

↓

Operation 실행

↓

Children 존재 여부 확인

↓

Child Node Stack Push

↓

다음 Node 실행

↓

Stack Empty

↓

프로그램 종료
```

---

## 특징

* 반복문 중첩 지원
* 조건문 중첩 지원
* AI 생성 프로그램 동일 실행 지원
* Runtime 상태 추적 가능
* 실행 중 장애물 판단 가능

---

# 10. 장애물 감지

Interpreter는 `/obstacle_dist/front`와 `/obstacle_dist/rear` Topic을 구독한다.

장애물이 설정된 임계 거리 이내로 감지되면 현재 실행 중인 이동 명령을 제어한다.

---

## 처리 과정

```text
장애물 감지

↓

현재 이동 Block 확인

↓

이동 명령 종료

↓

cmd_vel = 0 전송

↓

다음 Block 실행
```

---

## 장애물 처리 목적

* 로봇 충돌 방지
* 교육 환경에서 안전한 동작 보장
* AI 생성 프로그램 실행 시 예외 상황 대응

---

# 11. 예외 처리

| 상황             | 처리                |
| -------------- | ----------------- |
| 잘못된 JSON       | 프로그램 실행 중단        |
| WebSocket 종료   | 프로그램 종료           |
| Emergency Stop | cmd_vel = 0       |
| 장애물 감지         | Runtime Skip      |
| 빈 프로그램         | 실행하지 않음           |
| AI 생성 실패       | JSON 변환 실패 메시지 출력 |
| AI 응답 형식 오류    | 프로그램 실행 전 검증      |

---

# 12. 인터페이스 규칙

* 모든 프로그램 데이터는 JSON Tree 형태로 전달한다.
* Blockly 작성 프로그램과 AI 생성 프로그램은 동일한 JSON 규격을 사용한다.
* Web과 ROS2는 rosbridge_server를 통해 연결한다.
* 실행 상태는 `/run_state` Topic으로 전달한다.
* Interpreter는 Runtime에서 Tree 구조를 해석한다.
* 장애물 감지는 LiDAR 기반 데이터를 활용한다.
* AI는 프로그램 생성 역할만 담당하며 실제 로봇 제어는 ROS2 Interpreter가 담당한다.
* AI 생성 결과는 실행 전 Web 화면에서 확인 및 수정 가능하다.
* Emergency Stop은 프로그램 실행 중 언제든 동작할 수 있어야 한다.

---

# 13. AI 인터페이스

## 13.1 AI 입력

사용자는 AI Panel을 통해 자연어 형태로 로봇 동작을 요청한다.

| 항목    | 내용            |
| ----- | ------------- |
| 입력 방식 | 자연어 Prompt    |
| 입력 위치 | AI Panel      |
| 처리 방식 | AI Service 분석 |
| 출력 결과 | JSON Tree     |

---

## 13.2 AI 입력 예시

사용자 입력

```text
앞으로 2초 이동하고
장애물이 있으면 오른쪽으로 돌아줘.
```

---

AI 변환 결과 예시

```json
[
    {
        "op":"forward",
        "time":2
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
```

---

## 13.3 AI 처리 흐름

```text
Natural Language

↓

AI Service

↓

Command Analysis

↓

Operation Mapping

↓

JSON Tree 생성

↓

Blockly Workspace 적용

↓

사용자 실행

↓

Interpreter 실행
```

---

## 13.4 AI 인터페이스 특징

* 사용자는 블록을 직접 조립하지 않고 자연어로 프로그램 생성 가능
* 생성 결과는 기존 Blockly 구조와 호환
* Interpreter 수정 없이 AI 기능 확장 가능
* 사용자가 생성 결과를 확인 후 실행 가능

---

# 14. 인터페이스 변경 이력

| 버전       | 내용                                               |
| -------- | ------------------------------------------------ |
| v1.0     | 기본 Topic 정의                                      |
| v1.1     | JSON Tree 구조 추가                                  |
| v1.2     | Runtime Interpreter 명세 추가                        |
| v1.3     | Runtime Skip 및 장애물 처리 명세 추가                      |
| v1.4 | AI Panel 기반 자연어 → Blockly JSON Tree 생성 기능 추가 |
| v1.5     | 최종 인터페이스 문서 정리                                   |


---

