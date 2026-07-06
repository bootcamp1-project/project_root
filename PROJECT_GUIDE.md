# 🧩 블록 코딩 로봇 교육 플랫폼

> ROS 2와 웹 기반 블록 코딩을 이용한 초등학생 대상 로봇 교육 프로젝트

---

## 📖 프로젝트 소개

아이가 웹에서 블록을 조합하여 프로그램을 만들면 TurtleBot이 순서대로 실행합니다.

### 주요 기능

- 블록 코딩으로 프로그램 작성
- 블록 순차 실행
- 현재 실행 블록 하이라이트
- 라이다(LiDAR) 센서를 이용한 안전 정지
- 실행 중 정지 버튼
- 사용자 테스트 기반 UX 개선

---

## 🏗 시스템 구조

```text
Web App
    │
    ▼
interpreter_node (웹소켓 서버 내장)
    ├── /cmd_vel
    ├── /buzzer
    └── /run_state
          ▲
          │
  LiDAR Node (ultrasonic_node.py)
```

---

## 📂 프로젝트 구조

```text
project-root/
├── README.md
├── PLAN.md
├── INTERFACE.md
├── DAILY_LOG.md
├── TEST.md
├── REPORT.md
├── web/
├── ros2_ws/
├── images/
└── media/
```

---

## ⚙ 실행 환경

- Ubuntu 22.04
- ROS 2 Humble
- Python 3
- HTML / CSS / JavaScript
- rosbridge_suite

---

## 🚀 실행 방법

### 1. 터틀봇 기본 노드 실행 (터틀봇 라즈베리파이에서 실행)

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_bringup robot.launch.py
```

### 2. 블록 코딩 통합 노드 실행 (PC에서 실행)

```bash
ros2 launch block_robot bringup.launch.py
```

interpreter_node, ultrasonic_node, buzzer_node와 웹 서버가 함께 실행되며, 웹 앱은 별도의 rosbridge 없이 interpreter_node에 내장된 웹소켓 서버를 통해 직접 통신합니다.

### 3. 웹앱 접속

브라우저에서 아래 주소로 접속합니다. (실제 환경에 맞게 IP 변경)

```text
http://localhost:8000
```

---

## 📄 문서

| 문서 | 내용 |
| --- | --- |
| PLAN.md | 프로젝트 계획 |
| INTERFACE.md | ROS 토픽 정의 |
| DAILY_LOG.md | 개발 일지 |
| TEST.md | 테스트 결과 |
| REPORT.md | 최종 보고서 |
