# 🧩 블록 코딩 로봇 교육 플랫폼

> ROS 2와 웹 기반 블록 코딩을 이용한 초등학생 대상 로봇 교육 프로젝트
 
---

## 📖 프로젝트 소개

본 프로젝트는 **초등학생을 위한 블록 코딩 기반 로봇 제어 시스템**을 개발하는 것을 목표로 합니다.

사용자는 스마트폰 또는 태블릿의 웹 애플리케이션에서 블록을 조합하여 프로그램을 작성하고, 실행 버튼을 누르면 TurtleBot이 작성된 순서대로 동작합니다.

실행 중에는 현재 실행 중인 블록을 화면에서 확인할 수 있으며, 초음파 센서를 통해 장애물을 감지하면 즉시 안전하게 정지합니다.

프로젝트는 ROS 2와 웹 기술을 연동하여 인터프리터 기반 블록 실행 구조를 구현하고, 사용자 중심의 UI/UX 설계를 목표로 합니다.

---

## 🎯 주요 기능

- 블록 코딩 프로그램 작성
- 블록 순차 실행(Interpreter)
- 실행 블록 하이라이트
- 장애물 감지 시 자동 정지
- 실행 중 긴급 정지 버튼
- 사용자 테스트 기반 UX 개선

---

## 🏗 시스템 구조

```text
      Web App
          │
          ▼
  rosbridge_server
          │
          ▼
  interpreter_node
      │        │
      │        ├── /buzzer
      │
      └── /cmd_vel
          │
          ▼
      TurtleBot3
          ▲
          │
 /obstacle_dist
          ▲
          │
 Ultrasonic Node
```

---

## 📂 프로젝트 구조

```text
project_root/
├── README.md              # 프로젝트 소개 + 터틀봇 구동 및 웹앱 실행 방법
├── PLAN.md                # Day 1: 프로젝트 계획서
├── INTERFACE.md           # Day 1: 토픽 인터페이스 정의서 (/program, /run_state 등)
├── DAILY_LOG.md           # Day 2~4: 일일 스탠드업 로그 (누적)
├── TEST.md                # Day 3~4: 테스트 시나리오 및 결과 (주행 및 스피커 우회 테스트)
├── REPORT.md              # Day 5: 최종 보고서 (KPT 포함)
├── PROJECT_GUIDE.md       # 프로젝트 운영 가이드
│
├── web/
│   └── blocks.html        # 스크롤바 최적화 + 노트북 스피커 부저 연동형 블록코딩 웹앱
│
├── ros2_ws/
│   └── src/
│       └── block_robot/   # 핵심 ROS 2 블록 제어 패키지
│           ├── package.xml        # turtlebot3_msgs 의존성이 추가된 패키지 설정 파일
│           ├── setup.py           # 노드 실행 파일 및 런치 엔트리포인트 등록 설정
│           ├── setup.cfg
│           └── block_robot/
│               ├── __init__.py
│               ├── interpreter_node.py # [핵심] JSON 순차 실행 및 모터/부저 제어 뇌 노드
│               ├── buzzer_node.py      # /buzzer 토픽을 OpenCR 사운드로 중계하는 부저 노드
│               └── ultrasonic_node.py  # HC-SR04 초음파 센서 값 발행 노드
│
├── images/                # 아키텍처 및 시스템 데이터 흐름 다이어그램 (상대 경로 참조)
└── media/                 # 터틀봇 Burger 주행 및 웹앱 연동 시연 영상, 스크린샷
```

---

## ⚙ 개발 환경

- Ubuntu 22.04
- ROS 2 Humble
- Python 3
- HTML
- CSS
- JavaScript
- rosbridge_suite
- TurtleBot3

---

## 🚀 실행 방법

### 1. rosbridge 실행

```bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

### 2. Interpreter 실행

```bash
ros2 run robot_interpreter interpreter_node
```

### 3. 웹 실행

```bash
cd web
python3 -m http.server 8000
```

브라우저 접속

```
http://localhost:8000
```

---

## 📄 프로젝트 문서

| 문서 | 설명 |
|------|------|
| PLAN.md | 프로젝트 계획서 |
| INTERFACE.md | ROS2 인터페이스 정의 |
| DAILY_LOG.md | 개발 일지 |
| TEST.md | 테스트 결과 |
| REPORT.md | 최종 보고서 |
| PROJECT_GUIDE.md | 프로젝트 운영 가이드 |

---

## 👥 Team

| 이름 | 역할 |
|------|------|
| 박준서 | 팀장 |
| 박정호 | 팀원 |
| 김건호 | 팀원 |
| 윤태환 | 팀원 |
| 김민찬 | 팀원 |
| 김성수 | 팀원 |

---

## 📜 License

This project was developed for educational purposes.
