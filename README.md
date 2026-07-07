# 🧩 블록 코딩 로봇 교육 플랫폼

> **ROS 2 Humble 기반 TurtleBot3 블록 코딩 교육 플랫폼**  
> 웹에서 작성한 중첩 블록 프로그램을 런타임에 실시간 해석하여 TurtleBot3를 제어하는 프로젝트입니다.

---

## 📖 프로젝트 소개

본 프로젝트는 **초등학생을 위한 블록 코딩 기반 로봇 제어 시스템**입니다.

사용자는 웹 브라우저에서 Scratch 형태의 블록을 조립하여 프로그램을 작성하고 실행할 수 있으며, 프로그램은 **중첩된 JSON 트리(Nested JSON Tree)** 형태로 ROS 2에 전달됩니다.

Interpreter Node는 이를 미리 평탄화(Unrolling)하지 않고 **실행 시점(Runtime)** 에 직접 해석하여 반복문과 조건문을 처리합니다. 또한 주행 중 센서 데이터를 실시간으로 반영하여 프로그램의 흐름을 변경할 수 있습니다.

---

## ✨ 주요 기능

### 🧱 블록 기반 프로그래밍

- Drag & Drop 방식의 블록 조립
- 반복문(`repeat`)
- 조건문(`if`)
- 반복문 내부 조건문 등 중첩 구조 지원

---

### ⚙️ Runtime Tree Interpreter

기존처럼 블록을 모두 펼쳐서 실행하지 않고,

- Nested JSON Tree 수신
- Stack 기반 Runtime Interpreter
- 실행 시점에 현재 블록 해석
- 반복 및 조건문 실시간 처리

방식으로 동작합니다.

---

### 🚧 Runtime Skip & Branch

주행 중 장애물이 발견되면 프로그램 전체를 종료하지 않습니다.

```
앞으로 이동
      │
장애물 감지
      │
현재 이동 블록 Skip
      │
다음 조건문 실행
```

이를 통해 실행 흐름을 자연스럽게 이어갈 수 있습니다.

---

### 📡 90° LiDAR Sector Scan

기존의 좁은 감지 각도 대신

- 전방 ±45°
- 후방 ±45°

총 **90° 부채꼴 영역**을 스캔하여 대각선 방향 장애물 감지 성능을 향상시켰습니다.

---

### 🎨 실시간 실행 하이라이트

Interpreter에서 현재 실행 중인 Operator(op)를 `/run_state` 토픽으로 전송하여

- 현재 실행 중인 블록
- 실제 TurtleBot3 동작

을 웹 화면과 실시간으로 동기화합니다.

---

### 🔒 실행 중 안전 제어

실행 중 프로그램 변경으로 인한 충돌을 방지하기 위해

- Web UI 편집 Lock
- Robot Program Drop

방식을 적용하였습니다.

---

### 🔔 비동기 초기 안정화

블록이 변경되는 순간 발생할 수 있는 센서 오작동을 방지하기 위해 초기 Latch 구간을 적용하여 안정성을 높였습니다.

---

# 🏗 시스템 아키텍처

```text
             Web Application
     (Drag & Drop Block Editor)
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
                 ▲
                 │
      /obstacle_dist/front
      /obstacle_dist/rear
                 ▲
                 │
      Ultrasonic (LiDAR) Node
```

---

# 📂 프로젝트 구조

```text
project_root/
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
│           ├── package.xml
│           ├── setup.py
│           ├── launch/
│           │   └── bringup.launch.py
│           └── block_robot/
│               ├── interpreter_node.py
│               ├── ultrasonic_node.py
│               └── buzzer_node.py
│
├── images/
└── media/
```

---

# ⚙️ 개발 환경

| 항목 | 내용 |
|------|------|
| OS | Ubuntu 22.04 LTS |
| Middleware | ROS 2 Humble |
| Language | Python 3 |
| Front-End | HTML5 / CSS3 / JavaScript (ES6) |
| Robot | TurtleBot3 Burger |
| Sensor | LDS-03 LiDAR |
| Communication | rosbridge_suite (WebSocket) |

---

# 🚀 실행 방법

## 1. 패키지 빌드

```bash
cd ~/ros2_ws

colcon build --packages-select block_robot

source install/setup.bash
```

---

## 2. TurtleBot3 Bringup

라즈베리파이에서 실행합니다.

```bash
export TURTLEBOT3_MODEL=burger

ros2 launch turtlebot3_bringup robot.launch.py
```

---

## 3. ROS 2 노드 실행

```bash
ros2 launch block_robot bringup.launch.py
```

실행되는 노드

- interpreter_node
- ultrasonic_node
- buzzer_node

---

## 4. 웹 서버 실행

```bash
cd ~/ros2_ws/src/block_robot/web

python3 -m http.server 8000
```

---

## 5. 브라우저 접속

```
http://localhost:8000/blocks.html
```

또는

```
http://<PC_IP>:8000/blocks.html
```

---

# 📡 주요 ROS 2 토픽

| Topic | 설명 |
|--------|------|
| `/program` | 블록 프로그램 전송 |
| `/cmd_vel` | TurtleBot3 이동 명령 |
| `/buzzer` | 부저 제어 |
| `/run_state` | 현재 실행 중인 Operator |
| `/obstacle_dist/front` | 전방 장애물 거리 |
| `/obstacle_dist/rear` | 후방 장애물 거리 |

---

# 📚 프로젝트 문서

| 문서 | 설명 |
|------|------|
| **PLAN.md** | 요구사항 분석 및 개발 계획 |
| **INTERFACE.md** | ROS 2 인터페이스 및 JSON 프로토콜 |
| **DAILY_LOG.md** | 개발 일지 및 트러블슈팅 |
| **TEST.md** | 통합 테스트 결과 |
| **REPORT.md** | 최종 프로젝트 보고서 |
| **PROJECT_GUIDE.md** | 프로젝트 빌드 및 실행 가이드 |

---

# 👥 Team

| 이름 | 담당 |
|------|------|
| 박준서 | 팀장 |
| 박정호 | 프로젝트 총괄 및 시스템 설계 Runtime Tree Interpreter, ROS2, Full Stack |
| 김건호 | 블록 UI 및 JSON 직렬화 |
| 윤태환 | Interpreter 구조 개선 및 주행 로직 |
| 김민찬 | LiDAR 및 Buzzer Node |
| 김성수 | Build 및 Launch 환경 구성 |

---

# 🎯 프로젝트 성과

- Runtime Tree Interpreter 구현
- Nested Loop / If 실시간 해석
- Runtime Skip & Branch 지원
- LiDAR 90° Sector Scan 적용
- Web-ROS2 실시간 상태 동기화
- 실행 중 UI Lock 및 Program Drop 적용
- ROS 2와 웹 기반 블록 코딩 교육 플랫폼 구현

---

# 📄 License

This project was developed for educational purposes.
