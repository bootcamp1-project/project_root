# 🧩 블록 코딩 로봇 교육 플랫폼

> ROS 2와 웹 기반 블록 코딩을 이용한 초등학생 대상 로봇 교육 프로젝트

---

## 📖 프로젝트 소개

아이가 웹에서 블록을 조합하여 프로그램을 만들면 TurtleBot이 순서대로 실행합니다.

### 주요 기능

- 블록 코딩으로 프로그램 작성
- 블록 순차 실행
- 현재 실행 블록 하이라이트
- 초음파 센서를 이용한 안전 정지
- 실행 중 정지 버튼
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
    ├── /cmd_vel
    ├── /buzzer
    └── /run_state
          ▲
          │
  Ultrasonic Node
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

### 1. rosbridge 실행

```bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

### 2. ROS 노드 실행

```bash
ros2 run robot_interpreter interpreter_node
```

### 3. 웹 실행

```bash
cd web
python3 -m http.server 8000
```

브라우저에서 아래 주소로 접속합니다.

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
