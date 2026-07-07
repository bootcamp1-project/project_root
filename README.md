# 🧩 블록 코딩 로봇 교육 플랫폼

> **ROS 2 Humble 기반 TurtleBot3 블록 코딩 교육 플랫폼**

웹 기반 블록 코딩 환경과 ROS 2를 연동하여 TurtleBot3를 제어할 수 있는 교육용 플랫폼입니다. 사용자는 Scratch 방식의 블록을 드래그 앤 드롭하여 프로그램을 작성하고, 웹 브라우저를 통해 실행하면 TurtleBot3가 해당 프로그램을 실시간으로 수행합니다.

본 프로젝트는 단순히 블록 명령을 순차적으로 실행하는 것이 아니라, **Runtime Tree Interpreter**를 적용하여 반복문과 조건문의 중첩 구조를 런타임에 직접 해석하도록 설계되었습니다. 또한 LiDAR 기반 장애물 감지와 Runtime Skip & Branch 기능을 적용하여 실행 중에도 주변 환경 변화에 유연하게 대응할 수 있도록 구현하였습니다.

---

# 📖 프로젝트 개요

초등학생을 대상으로 하는 블록 코딩 교육에서는 사용자가 작성한 프로그램이 실제 로봇의 움직임으로 이어질 때 학습 효과가 높아집니다. 본 프로젝트는 웹 애플리케이션과 ROS 2 기반 TurtleBot3를 연동하여 사용자가 작성한 블록 프로그램을 실제 하드웨어에서 실행할 수 있는 교육 플랫폼을 구현하는 것을 목표로 하였습니다.

웹에서 작성한 블록 프로그램은 Nested JSON Tree 형태로 변환되어 `rosbridge_server`를 통해 ROS 2로 전달됩니다. Interpreter Node는 해당 JSON Tree를 런타임에 해석하여 TurtleBot3의 이동 명령으로 변환하고, 실행 상태를 웹으로 다시 전달하여 현재 실행 중인 블록을 실시간으로 표시합니다.

또한 LiDAR 센서를 이용한 장애물 감지 기능과 Runtime Skip & Branch 구조를 적용하여 장애물이 감지되더라도 프로그램 전체를 종료하지 않고 현재 이동 블록만 중단한 뒤 다음 실행 흐름으로 자연스럽게 이어질 수 있도록 구현하였습니다.

---

# 🎯 개발 목표

본 프로젝트의 주요 목표는 다음과 같습니다.

- Scratch 방식의 블록 코딩 인터페이스 제공
- TurtleBot3와 웹 애플리케이션의 실시간 연동
- ROS 2 기반 Runtime Interpreter 구현
- 반복문 및 조건문의 중첩 구조 지원
- LiDAR 기반 안전한 주행 환경 구축
- 초등학생도 쉽게 사용할 수 있는 교육용 플랫폼 구현

---

# ✨ 주요 기능

## 1. 블록 기반 프로그래밍

- Drag & Drop 방식의 블록 편집기
- 반복문(Repeat) 지원
- 조건문(If) 지원
- 반복문과 조건문의 중첩 구조 지원
- 프로그램 실행 및 정지 기능

---

## 2. Runtime Tree Interpreter

웹에서 생성된 Nested JSON Tree를 Runtime에 직접 해석하는 Interpreter를 구현하였습니다.

기존처럼 프로그램을 모두 펼쳐(Loop Unrolling) 실행하는 방식이 아니라 실행 시점마다 현재 노드를 해석하여 다음 실행 블록을 결정하는 구조를 적용하였습니다.

주요 특징은 다음과 같습니다.

- Stack 기반 실행 구조
- Runtime Tree Parsing
- Nested Block 지원
- 실시간 실행 흐름 제어
- Runtime Skip & Branch 지원

---

## 3. 실시간 ROS 2 연동

웹과 TurtleBot3는 `rosbridge_server`를 이용하여 통신합니다.

웹 애플리케이션은 WebSocket을 통해 프로그램을 ROS 2로 전달하며 Interpreter Node는 이를 해석하여 `/cmd_vel` 명령으로 변환합니다.

또한 현재 실행 중인 연산자를 `/run_state` Topic으로 웹에 전달하여 실행 중인 블록을 실시간으로 표시합니다.

---

## 4. LiDAR 기반 장애물 감지

LiDAR 데이터를 이용하여 전방과 후방의 장애물을 감지합니다.

장애물이 일정 거리 이내로 접근하면 현재 이동 블록을 중단하고 프로그램의 다음 실행 흐름으로 이동하도록 구현하여 프로그램 전체가 종료되지 않도록 하였습니다.

주요 기능은 다음과 같습니다.

- 전방 장애물 감지
- 후방 장애물 감지
- Runtime Skip
- Runtime Branch
- 안전 정지 기능

---

## 5. 실행 상태 시각화

Interpreter Node는 현재 실행 중인 Operator 정보를 `/run_state` Topic으로 송신합니다.

웹에서는 해당 정보를 이용하여 실행 중인 블록을 실시간으로 하이라이트하여 사용자가 프로그램의 진행 상황을 쉽게 확인할 수 있도록 구현하였습니다.

---

## 6. 실행 중 안전 기능

실행 중 발생할 수 있는 오류를 방지하기 위해 다음 기능을 적용하였습니다.

- Web UI Lock
- Program Drop
- Emergency Stop
- LiDAR Safety Check
- Runtime Skip & Branch
- 초기 Latch 처리

---
# 🏗 시스템 아키텍처

본 프로젝트는 웹 애플리케이션, ROS 2 미들웨어, TurtleBot3 하드웨어로 구성된 분산 시스템이다. 사용자가 웹에서 작성한 블록 프로그램은 JSON Tree 형태로 변환되어 `rosbridge_server`를 통해 ROS 2로 전달되며, Interpreter Node가 이를 실시간으로 해석하여 로봇을 제어한다.

```text
                    Web Browser
         (HTML / CSS / JavaScript)

                     │
                     │ WebSocket
                     ▼
             rosbridge_server
                     │
                     ▼
             /program (JSON Tree)
                     │
                     ▼
          Interpreter Node (ROS2)
      Runtime Tree Interpreter Engine
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    /cmd_vel      /run_state    /buzzer
        │                           │
        ▼                           ▼
   TurtleBot3                 Buzzer Node

                     ▲
                     │
          /scan (LaserScan)
                     │
             LiDAR Sensor
                     │
                     ▼
          Ultrasonic Node
```

---

# ⚙ 시스템 동작 과정

전체 시스템은 다음 순서로 동작한다.

### ① 블록 프로그램 작성

사용자는 웹 브라우저에서 Drag & Drop 방식으로 블록을 조립하여 프로그램을 작성한다.

지원하는 블록은 다음과 같다.

- 앞으로 이동
- 뒤로 이동
- 좌회전
- 우회전
- 대기
- 반복문
- 조건문
- 부저

---

### ② 프로그램 직렬화

작성된 블록은 실행 버튼을 누르는 순간 Nested JSON Tree 형태로 직렬화된다.

예시

```json
[
  {
    "op":"repeat",
    "count":3,
    "children":[
      {
        "op":"forward",
        "time":2
      },
      {
        "op":"if_front"
      }
    ]
  }
]
```

---

### ③ rosbridge 통신

웹 브라우저는 rosbridge_server와 WebSocket으로 연결된다.

프로그램은 `/program` Topic으로 Publish된다.

```
Web Browser

↓

WebSocket

↓

rosbridge_server

↓

ROS2 Topic
```

---

### ④ Runtime Tree Interpreter

Interpreter Node는 프로그램을 미리 펼치지 않는다.

대신 Runtime에 현재 노드를 읽으면서 Stack 기반으로 실행한다.

이를 통해

- Repeat
- If
- Nested Repeat
- Nested If

구조를 모두 지원한다.

---

### ⑤ TurtleBot3 제어

Interpreter는 현재 실행 중인 블록을 TurtleBot3의 이동 명령으로 변환한다.

대표적으로 사용하는 Topic은 다음과 같다.

| Topic | 역할 |
|--------|------|
| /cmd_vel | 이동 명령 |
| /run_state | 현재 실행 블록 |
| /buzzer | 부저 출력 |

---

### ⑥ LiDAR 장애물 감지

Ultrasonic Node는 LiDAR 데이터를 분석하여 전방과 후방의 최단 거리를 계산한다.

Interpreter Node는 해당 정보를 이용하여 장애물을 감지한다.

장애물이 감지되면

- 현재 이동 블록 종료
- Runtime Skip
- 다음 블록 실행

순으로 처리한다.

---

# 📂 프로젝트 구조

프로젝트는 다음과 같은 구조로 구성되어 있다.

```text
project_root/
│
├── README.md
├── PLAN.md
├── INTERFACE.md
├── PROJECT_GUIDE.md
├── DAILY_LOG.md
├── TEST.md
├── REPORT.md
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
│           │    └── bringup.launch.py
│           │
│           └── block_robot/
│                ├── interpreter_node.py
│                ├── ultrasonic_node.py
│                ├── buzzer_node.py
│                └── __init__.py
│
├── images/
│   ├── block_robot_architecture.png
│   ├── rosgraph_update.png 
│
└── media/
    └── 블록코딩시연영.mp4
```

---

# 📁 주요 디렉터리 설명

| 디렉터리 | 설명 |
|-----------|------|
| web | 블록 코딩 웹 애플리케이션 |
| ros2_ws | ROS2 Workspace |
| launch | ROS2 Launch 파일 |
| block_robot | 핵심 ROS2 패키지 |
| images | 프로젝트 이미지 |
| media | 실행 영상 및 스크린샷 |

---

# 🛠 기술 스택

## Operating System

- Ubuntu 22.04 LTS

## Middleware

- ROS 2 Humble

## Programming Language

- Python 3
- HTML5
- CSS3
- JavaScript (ES6)

## Communication

- rosbridge_server
- WebSocket
- ROS 2 Topic

## Hardware

- TurtleBot3 Burger
- LDS-01 / LDS-02 LiDAR
- OpenCR

## ROS2 Package

- rclpy
- geometry_msgs
- sensor_msgs
- std_msgs
- rosbridge_server

---
# 🚀 설치 및 실행 방법

## 1. 개발 환경

| 항목 | 내용 |
|------|------|
| OS | Ubuntu 22.04 LTS |
| ROS | ROS 2 Humble |
| Python | Python 3.10 이상 |
| Web | HTML5 / CSS3 / JavaScript (ES6) |
| Hardware | TurtleBot3 Burger |
| Communication | rosbridge_server (WebSocket) |

---

## 2. 패키지 빌드

ROS2 Workspace에서 패키지를 빌드합니다.

```bash
cd ~/ros2_ws

colcon build --packages-select block_robot

source install/setup.bash
```

---

## 3. TurtleBot3 Bringup

터틀봇 라즈베리파이에서 기본 노드를 실행합니다.

```bash
export TURTLEBOT3_MODEL=burger

ros2 launch turtlebot3_bringup robot.launch.py
```

---

## 4. rosbridge_server 실행

웹 애플리케이션과 ROS2를 연결하기 위해 rosbridge_server를 실행합니다.

```bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

기본적으로 **9090 포트(WebSocket)** 에서 대기합니다.

---

## 5. Block Robot 실행

PC에서 Interpreter 및 센서 노드를 실행합니다.

```bash
source ~/ros2_ws/install/setup.bash

ros2 launch block_robot bringup.launch.py
```

실행되는 노드는 다음과 같습니다.

- interpreter_node
- ultrasonic_node
- buzzer_node

---

## 6. Web Server 실행

웹 애플리케이션은 정적 파일 서버를 통해 실행합니다.

```bash
cd ~/ros2_ws/src/block_robot/web

python3 -m http.server 8000
```

---

## 7. 웹 접속

브라우저에서 다음 주소로 접속합니다.

```text
http://localhost:8000/blocks.html
```

다른 장치에서 접속하는 경우에는 PC의 IP 주소를 사용합니다.

```text
http://192.168.xxx.xxx:8000/blocks.html
```

---

# ▶ 실행 순서

아래 순서를 권장합니다.

```text
① TurtleBot3 Bringup

↓

② rosbridge_server

↓

③ block_robot Bringup

↓

④ Web Server

↓

⑤ Browser 접속

↓

⑥ 프로그램 실행
```

---

# 📄 프로젝트 문서

프로젝트의 모든 개발 과정은 아래 문서에 정리되어 있습니다.

| 문서 | 설명 |
|------|------|
| README.md | 프로젝트 소개 및 실행 방법 |
| PLAN.md | 프로젝트 기획 및 요구사항 분석 |
| INTERFACE.md | ROS2 Topic 및 JSON 프로토콜 명세 |
| PROJECT_GUIDE.md | 개발 및 운영 가이드 |
| DAILY_LOG.md | 개발 일지 |
| TEST.md | 테스트 결과 및 검증 |
| REPORT.md | 최종 프로젝트 보고서 |

---

# 📸 프로젝트 결과

본 프로젝트는 다음 기능을 구현하였습니다.

- Scratch 방식의 블록 코딩 인터페이스
- ROS2 기반 TurtleBot3 제어
- Runtime Tree Interpreter
- Nested JSON Tree 실행
- Runtime Skip & Branch
- LiDAR 기반 장애물 감지
- 실시간 실행 상태 하이라이트
- Web ↔ ROS2 실시간 통신

---

# 👥 Team

| 이름 | 담당 분야 |
|------|-----------|
| 박준서 | 프로젝트 관리 및 시스템 설계 |
| **박정호** | **Full Stack 개발, Runtime Tree Interpreter, ROS2 연동, 시스템 통합, 테스트 및 문서화** |
| 김건호 | Web Front-End |
| 윤태환 | ROS2 제어 |
| 김민찬 | LiDAR 및 하드웨어 |
| 김성수 | Build 및 통합 테스트 |

---

# 📌 향후 개선 사항

향후 다음과 같은 기능을 추가하여 교육 플랫폼을 더욱 발전시킬 수 있습니다.

- 프로그램 저장 및 불러오기
- 실행 경로 시각화
- 2D/3D 시뮬레이터 연동
- 미션 기반 교육 콘텐츠
- 다양한 ROS2 모바일 로봇 지원

---

# 📜 License

본 프로젝트는 교육 목적의 팀 프로젝트로 개발되었습니다.

```
Copyright (c) 2026 Block Team

This project was developed for educational purposes.
```
