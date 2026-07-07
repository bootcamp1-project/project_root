# 🧩 프로젝트 가이드 (PROJECT_GUIDE.md)

> ROS 2 Humble 및 웹 기반 런타임 트리 해석(Interpreter) 엔진을 활용한 초등학생 대상 로봇 교육 플랫폼 프로젝트 가이드라인

---

# 📖 프로젝트 소개

아동이 웹 인터페이스에서 스크래치 방식의 중중첩 반복문 및 조건문 블록을 조립하면, TurtleBot3 하드웨어가 이를 런타임에 실시간으로 해석하여 움직입니다.

기존의 **Loop Unrolling(선형 평탄화)** 방식은 모든 블록을 미리 펼쳐 전송하기 때문에 실행 중 조건 변화에 대응하기 어려웠습니다. 본 프로젝트는 **런타임 트리 해석기(Hybrid Interpreter)** 를 적용하여 실행 도중 센서값을 즉시 반영하고, 조건문과 반복문의 흐름을 실시간으로 제어하는 교육 플랫폼을 구현했습니다.

---

# 🚀 주요 핵심 기술 (Day 5)

## 1. 런타임 트리 해석기 (Hybrid Interpreter)

- Nested JSON Tree를 그대로 수신
- 실행 시점에 현재 블록을 해석
- 스택(Stack) 기반 실행 엔진
- 반복문과 조건문의 중중첩 구조를 실시간 처리

---

## 2. Runtime Skip & Branch

주행 중 장애물을 만나면 전체 프로그램을 종료하지 않습니다.

예시

```
앞으로
↓
장애물 감지
↓
현재 전진 블록 Skip
↓
다음 if 블록 실행
```

이를 통해 로봇은 실행 중에도 자연스럽게 분기합니다.

---

## 3. 90° 광폭 부채꼴 라이다 스캔

기존

- 전방 ±10°
- 후방 ±10°

문제

- 대각선 충돌 발생

개선

- 좌측 45°
- 우측 45°

총 **90° 부채꼴 스캔**을 수행하여 사각지대를 제거했습니다.

---

## 4. 실시간 실행 하이라이트

실행 중인 Operator(op)를

```
Interpreter
    ↓
/run_state
    ↓
Web UI
```

로 역전파하여

- 현재 실행 블록
- 실제 로봇 동작

을 항상 1:1로 동기화합니다.

DOM 인덱스 기반이 아닌 **Operator ID 기반 매핑**을 사용하여 실행 중 분기와 Skip 이후에도 하이라이트가 정확히 유지됩니다.

---

## 5. 트래픽 이중 보호

### Web

- 실행 중 블록 편집 Lock

### Robot

- 실행 중 새로운 프로그램 Drop

이를 통해 실행 중 프로그램 꼬임을 방지합니다.

---

# 🏗 시스템 아키텍처

```text
               Web Application
      (Nested JSON Tree Builder)
                 │
                 │  /program
                 ▼
      Interpreter Node
(Runtime Tree Interpreter Engine)
                 │
      ┌──────────┼───────────┐
      │          │           │
      ▼          ▼           ▼
   /cmd_vel   /buzzer    /run_state
      ▲                      │
      │                      │
      └──────┬───────────────┘
             │
   /obstacle_dist/front
   /obstacle_dist/rear
             ▲
             │
      Ultrasonic Node
 (90° Sector Scan Filter)
```

---

# 📂 프로젝트 구조

```text
project-root/
│
├── README.md
├── PLAN.md
├── INTERFACE.md
├── DAILY_LOG.md
├── TEST.md
├── REPORT.md
├── PROJECT_GUIDE.md
│
├── web/
│   └── blocks.html
│
├── ros2_ws/
│   └── src/
│       └── block_robot/
│           ├── block_robot/
│           │   ├── __init__.py
│           │   ├── interpreter_node.py
│           │   ├── ultrasonic_node.py
│           │   └── buzzer_node.py
│           │
│           └── launch/
│               └── bringup.launch.py
│
├── images/
└── media/
```

---

# ⚙ 실행 환경

| 항목 | 내용 |
|------|------|
| OS | Ubuntu 22.04 LTS |
| Middleware | ROS 2 Humble |
| Language | Python 3 |
| Front-End | HTML5 / CSS3 / JavaScript (ES6) |
| Robot | TurtleBot3 Burger |
| 통신 | rosbridge_suite(WebSocket) |

---

# 🚀 실행 방법

## 1. TurtleBot3 Bringup

터틀봇 라즈베리파이에서 실행

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_bringup robot.launch.py
```

---

## 2. Interpreter Node 실행

PC

```bash
cd ~/ros2_ws

colcon build --packages-select block_robot

source install/setup.bash

ros2 launch block_robot bringup.launch.py
```

실행되는 노드

- interpreter_node
- ultrasonic_node
- buzzer_node

---

## 3. Web Server 실행

별도의 터미널

```bash
cd ~/ros2_ws/src/block_robot/web

python3 -m http.server 8000
```

---

## 4. 브라우저 접속

```
http://localhost:8000/blocks.html
```

실제 TurtleBot3와 연결하는 경우

```
http://<PC_IP>:8000/blocks.html
```

형태로 접속합니다.

---

# 📡 주요 ROS 2 인터페이스

| Topic | 설명 |
|--------|------|
| /program | Web → Interpreter 프로그램 전송 |
| /cmd_vel | 로봇 이동 명령 |
| /buzzer | 비프음 재생 |
| /run_state | 현재 실행 중인 Operator |
| /obstacle_dist/front | 전방 거리 |
| /obstacle_dist/rear | 후방 거리 |

---

# ⚠️ 운영 시 주의사항

- 실행 중에는 Web UI가 자동으로 Lock됩니다.
- 실행 중 새로운 프로그램은 Robot에서 무시(Drop)됩니다.
- HTTP 서버는 Launch 파일에 포함하지 않고 별도 프로세스로 실행합니다.
- rosbridge WebSocket 서버(9090)가 먼저 실행되어 있어야 합니다.

---

# 📄 프로젝트 문서

| 문서 | 내용 |
|------|------|
| README.md | 프로젝트 소개 |
| PLAN.md | 요구사항 및 개발 계획 |
| INTERFACE.md | ROS2 인터페이스 및 JSON 프로토콜 |
| DAILY_LOG.md | 개발 일지 및 트러블슈팅 |
| TEST.md | 통합 테스트 및 UX 검증 |
| REPORT.md | 최종 기술 보고서 |

---

# 🎯 프로젝트 성과

- Runtime Tree Interpreter 구현
- Nested Loop 실시간 실행
- Runtime Skip & Branch 지원
- 90° 부채꼴 장애물 감지
- Web UI 실시간 하이라이트
- Operator 기반 실행 동기화
- Web/Robot 이중 보호 구조
- ROS2와 WebSocket 기반 실시간 제어 플랫폼 완성
