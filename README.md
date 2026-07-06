# 🧩 블록 코딩 로봇 교육 플랫폼

> ROS 2와 웹 기반 블록 코딩을 이용한 초등학생 대상 로봇 교육 프로젝트
 
---

## 📖 프로젝트 소개

본 프로젝트는 **초등학생을 위한 블록 코딩 기반 로봇 제어 시스템**을 개발하는 것을 목표로 합니다.

사용자는 스마트폰 또는 태블릿의 웹 애플리케이션에서 블록을 조합하여 프로그램을 작성하고, 실행 버튼을 누르면 TurtleBot이 작성된 순서대로 동작합니다.

실행 중에는 현재 실행 중인 블록을 화면에서 실시간으로 확인할 수 있으며, **360도 라이다(LiDAR) 센서를 통해 전진 및 후진 시 장애물을 감지하면 즉시 안전하게 정지**합니다.

프로젝트는 ROS 2와 웹 기술을 연동하여 인터프리터 기반 블록 실행 구조를 구현하고, 사용자 중심의 UI/UX 설계와 100% 안전한 주행 환경 제공을 목표로 합니다.

---

## 🎯 주요 기능

- **블록 코딩 프로그램 작성:** 직관적인 Drag & Drop 기반 UI
- **블록 순차 실행(Interpreter):** 앞으로, 뒤로, 회전, 대기, 소리 등
- **실행 블록 하이라이트:** 현재 로봇이 수행 중인 명령을 웹 화면에 실시간 표시
- **지능형 양방향 장애물 감지:** 라이다(LDS-03) 센서를 활용해 로봇 진행 방향(전방/후방 20cm)의 장애물 감지 시 자동 정지
- **웹 브라우저 피드백:** 비상 정지 시 스마트폰/PC에서 귀여운 배너 알림 및 경고음 출력
- **실행 중 긴급 정지 버튼:** 언제든 사용자가 로봇을 멈출 수 있는 하드 스톱 기능

---

## 🏗 시스템 구조

```text
        Web App (스마트폰/PC 브라우저)
          │
          ▼
    rosbridge_server (WebSocket)
          │
          ▼
   interpreter_node (핵심 뇌 노드)
      │        │
      │        ├── /buzzer
      │
      └── /cmd_vel
          │
          ▼
      TurtleBot3 (모터 구동부)
          ▲
          │
 /obstacle_dist/front & rear
          ▲
          │
 LiDAR Node (ultrasonic_node.py)
📂 프로젝트 구조Plaintextproject_root/
├── README.md              # 프로젝트 소개 + 터틀봇 구동 및 웹앱 실행 방법
├── PLAN.md                # Day 1: 프로젝트 계획서
├── INTERFACE.md           # Day 1: 토픽 인터페이스 정의서 (/program, /run_state 등)
├── DAILY_LOG.md           # Day 2~4: 일일 스탠드업 로그 (누적)
├── TEST.md                # Day 3~4: 테스트 시나리오 및 결과 (주행 및 스피커 우회 테스트)
├── REPORT.md              # Day 5: 최종 보고서 (KPT 포함)
├── PROJECT_GUIDE.md       # 프로젝트 운영 가이드
│
├── web/
│   └── blocks.html        # 모바일 최적화 UI + 브라우저 자체 경고음 내장 웹앱
│
├── ros2_ws/
│   └── src/
│       └── block_robot/   # 핵심 ROS 2 블록 제어 패키지
│           ├── package.xml        # turtlebot3_msgs 등 의존성이 추가된 패키지 설정 파일
│           ├── setup.py           # 노드 실행 파일 및 런치 엔트리포인트 등록 설정
│           ├── launch/
│           │   └── bringup.launch.py # 웹서버, rosbridge, 핵심 노드를 한 번에 켜는 통합 런치 파일
│           └── block_robot/
│               ├── __init__.py
│               ├── interpreter_node.py # [핵심] JSON 순차 실행 및 양방향 안전 정지 로직 포함
│               ├── buzzer_node.py      # /buzzer 토픽을 OpenCR 사운드로 중계하는 부저 노드
│               └── ultrasonic_node.py  # 라이다(LDS-03) 전/후방 거리 스캔 노드 (호환성을 위해 기존 파일명 유지)
│
├── images/                # 아키텍처 및 시스템 데이터 흐름 다이어그램
└── media/                 # 터틀봇 주행 및 웹앱 연동 시연 영상, 스크린샷
⚙ 개발 환경Ubuntu 22.04ROS 2 HumblePython 3HTML / CSS / JavaScript (웹 오디오 API 활용)rosbridge_suiteTurtleBot3 (LDS-03 LiDAR 센서 활용)🚀 실행 방법본 프로젝트는 편의성을 위해 통합 런치 파일을 제공합니다. 아래 과정을 통해 한 번에 전체 시스템을 구동할 수 있습니다.1. 패키지 빌드Bashcd ~/ros2_ws
colcon build --packages-select block_robot
source install/setup.bash
2. 하드웨어 기본 노드 실행 (터틀봇 라즈베리파이에서 실행)Bashexport TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_bringup robot.launch.py
3. 블록 코딩 통합 런치 파일 실행 (PC 터미널에서 실행)아래 명령어 하나로 rosbridge_server, interpreter_node, ultrasonic_node, buzzer_node, 그리고 웹 서버(포트 8000)가 동시에 실행됩니다.Bashros2 launch block_robot bringup.launch.py
4. 웹앱 접속스마트폰 또는 노트북의 브라우저에서 아래 주소로 접속합니다. (실제 환경에 맞게 IP 변경)Plaintexthttp://localhost:8000/blocks.html
또는 http://[노트북_IP]:8000/blocks.html📄 프로젝트 문서문서설명PLAN.md프로젝트 계획서INTERFACE.mdROS 2 인터페이스 정의DAILY_LOG.md개발 일지TEST.md테스트 결과REPORT.md최종 보고서PROJECT_GUIDE.md프로젝트 운영 가이드👥 Team이름역할박준서팀장박정호팀원김건호팀원윤태환팀원김민찬팀원김성수팀원📜 LicenseThis project was developed for educational purposes.
