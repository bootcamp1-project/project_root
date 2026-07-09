# 🛠 PROJECT_GUIDE.md

# 블록 코딩 로봇 교육 플랫폼 운영 가이드

> ROS 2 Humble 기반 TurtleBot3 블록 코딩 교육 플랫폼 설치 및 실행 매뉴얼

---

# 1. 문서 목적

본 문서는 프로젝트를 처음 실행하는 사용자를 위한 운영 가이드이다.

개발 환경 구축부터 패키지 빌드, TurtleBot3 실행, 웹 애플리케이션 실행, 시스템 종료까지 전체 과정을 설명한다.

---

# 2. 개발 환경

| 항목 | 내용 |
|------|------|
| OS | Ubuntu 22.04 LTS |
| ROS | ROS 2 Humble |
| Python | Python 3.10 |
| Robot | TurtleBot3 Burger |
| Sensor | LDS LiDAR |
| Browser | Google Chrome |

---

# 3. 프로젝트 구조

```text
project_root/

README.md
PLAN.md
INTERFACE.md
PROJECT_GUIDE.md
DAILY_LOG.md
TEST.md
REPORT.md

web/
    blocks.html

ros2_ws/
└── src/
    └── block_robot/
        ├── launch/
        ├── package.xml
        ├── setup.py
        └── block_robot/
            ├── interpreter_node.py
            ├── ultrasonic_node.py
            └── buzzer_node.py
```

---

# 4. 실행 전 확인 사항

다음 항목을 확인한다.

- TurtleBot3 전원 ON
- OpenCR 연결 확인
- ROS_DOMAIN_ID 확인
- 동일 네트워크 연결
- LiDAR 정상 동작 확인

---

# 5. Workspace Build

ROS2 Workspace에서 패키지를 빌드한다.

```bash
cd ~/ros2_ws

colcon build --packages-select block_robot

source install/setup.bash
```

빌드 오류가 발생하면

```bash
rm -rf build install log

colcon build
```

를 수행한다.

---

# 6. TurtleBot3 Bringup

라즈베리파이에서 실행한다.

```bash
export TURTLEBOT3_MODEL=burger

ros2 launch turtlebot3_bringup robot.launch.py
```

정상 실행 시

- /cmd_vel
- /scan
- /tf

등의 Topic이 생성된다.

---

# 7. Block Robot Bringup

웹과 ROS2 통신을 위한 rosbridge_server는 bringup.launch.py 실행 시 자동으로 실행된다.

별도의 rosbridge 실행 과정은 필요하지 않다.

기본 포트

```
9090
```

WebSocket 주소

```
ws://<PC_IP>:9090
```

---

# 8. Block Robot 실행

새 터미널에서 실행한다.

```bash
cd ~/ros2_ws

source install/setup.bash

ros2 launch block_robot bringup.launch.py
```

실행되는 노드

- rosbridge_server
- interpreter_node
- ultrasonic_node
- buzzer_node

---

# 9. 웹 서버 실행

프로젝트 web 디렉터리에서

```bash
cd ~/ros2_ws/src/block_robot/web

python3 -m http.server 8000
```

실행한다.

---

# 10. 브라우저 접속

PC

```
http://localhost:8000/blocks.html
```

스마트폰

```
http://192.168.xxx.xxx:8000/blocks.html
```

---

# 11. 실행 순서

반드시 아래 순서를 따른다.

```text
① TurtleBot3 Bringup

↓

② Block Robot Bringup
   (rosbridge_server 자동 실행)

↓

③ HTTP Server

↓

④ Browser 접속

↓

⑤ Connect

↓

⑥ Program Execute
```

---

# 12. 종료 순서

프로그램 종료는 다음 순서를 권장한다.

```text
Browser 종료

↓

bringup.launch 종료

↓

rosbridge_server 종료

↓

TurtleBot3 종료
```

---

# 13. 사용 방법

## 프로그램 작성

웹에서 블록을 Drag & Drop으로 배치한다.

지원 블록

- Forward
- Backward
- Left
- Right
- Wait
- Buzzer
- Repeat
- If

---

## 프로그램 실행

Execute 버튼을 누르면

AI Prompt

↓

AI Service

↓

JSON Tree 

↓

Blockly Workspace

↓

rosbridge_server

↓

Interpreter

↓

TurtleBot3

순으로 실행된다.

---

## 긴급 정지

Emergency Stop 버튼을 누르면

```
cmd_vel = 0
```

을 즉시 전송하여 로봇을 정지시킨다.

---

# 14. 시스템 구성

```text
User

↓

AI Panel

↓

AI Service

↓

JSON Tree

↓

Web Application

↓

rosbridge_server

↓

Interpreter Node

↓

cmd_vel

↓

TurtleBot3

↑

LiDAR

↓

Ultrasonic Node
```

---

# 15. 확인해야 할 Topic

```bash
ros2 topic list
```

주요 Topic

```
/program

/cmd_vel

/run_state

/buzzer

/scan

/obstacle_dist/front

/obstacle_dist/rear
```

---

# 16. 통신 확인

Topic 확인

```bash
ros2 topic echo /run_state
```

속도 확인

```bash
ros2 topic echo /cmd_vel
```

LiDAR 확인

```bash
ros2 topic echo /scan
```

---

# 17. Troubleshooting

## WebSocket 연결 실패

확인

```bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

포트 확인

```
9090
```

---

## 웹 접속 불가

확인

```bash
python3 -m http.server 8000
```

브라우저

```
http://localhost:8000
```

---

## TurtleBot3 움직이지 않음

확인

```bash
ros2 topic list
```

```
/cmd_vel
```

존재 여부 확인

---

## LiDAR 인식 실패

확인

```bash
ros2 topic echo /scan
```

LaserScan 데이터 확인

---

## Interpreter 실행 실패

다시 Build

```bash
colcon build

source install/setup.bash
```

---

# 18. 유지보수

패키지 수정 후

```bash
colcon build

source install/setup.bash
```

반드시 다시 수행한다.

---

# 19. 참고 문서

| 문서 | 설명 |
|------|------|
| README.md | 프로젝트 소개 |
| PLAN.md | 프로젝트 기획 |
| INTERFACE.md | 통신 규격 |
| DAILY_LOG.md | 개발 일지 |
| TEST.md | 테스트 |
| REPORT.md | 최종 보고서 |

---

# 20. 버전

| Version | 내용 |
|----------|------|
| v1.0 | 초기 운영 가이드 |
| v1.1 | rosbridge 추가 |
| v1.2 | Runtime Interpreter 추가 |
| v1.3 | LiDAR 및 Runtime Skip 추가 |
| v1.4 | AI 코딩 보조 기능 추가 및 실행 과정 변경 |
| v1.5 | 최종 운영 문서 |
