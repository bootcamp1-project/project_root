# 📊 REPORT.md

# 블록 코딩 로봇 교육 플랫폼 최종 보고서

> ROS 2 Humble 기반 TurtleBot3 블록 코딩 교육 플랫폼

---

# 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 프로젝트명 | 블록 코딩 로봇 교육 플랫폼 |
| 개발 기간 | 5일 (40시간) |
| 개발 환경 | Ubuntu 22.04 LTS, ROS 2 Humble |
| 개발 언어 | Python, HTML5, CSS3, JavaScript |
| 하드웨어 | TurtleBot3 Burger |

---

# 2. 프로젝트 소개

본 프로젝트는 웹 기반 블록 코딩 환경과 ROS 2 기반 TurtleBot3를 연동하여 초등학생도 쉽게 사용할 수 있는 교육용 로봇 제어 플랫폼을 구현하는 것을 목표로 하였다.

사용자는 웹 브라우저에서 블록을 조합하여 프로그램을 작성하고, 실행 버튼을 누르면 프로그램이 JSON Tree 형태로 변환되어 `rosbridge_server`를 통해 ROS 2로 전달된다. Interpreter Node는 이를 런타임에 해석하여 TurtleBot3를 제어하며, 현재 실행 중인 블록은 실시간으로 웹 화면에 표시된다.

또한 LiDAR 기반 장애물 감지 기능과 Runtime Skip 구조를 적용하여 장애물이 감지되면 현재 이동 블록만 중단하고 다음 실행 흐름으로 자연스럽게 이어지도록 구현하였다.

---

# 3. 개발 목표

본 프로젝트의 주요 목표는 다음과 같다.

- 웹 기반 블록 코딩 환경 구축
- TurtleBot3 실시간 제어
- ROS2 기반 Runtime Interpreter 구현
- 반복문 및 조건문의 중첩 구조 지원
- LiDAR 기반 안전 주행
- 웹과 로봇의 실시간 상태 동기화

---

# 4. 시스템 구성

```text
Web Browser
      │
      ▼
rosbridge_server
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
Ultrasonic Node
      ▲
      │
LiDAR
```

---

# 5. 주요 구현 기능

## 5.1 블록 코딩 UI

- Drag & Drop 방식의 블록 편집기
- 프로그램 실행 및 정지
- 현재 실행 블록 하이라이트

## 5.2 Runtime Interpreter

- JSON Tree 기반 실행
- Stack 기반 Runtime Parsing
- 반복문 및 조건문 중첩 지원

## 5.3 ROS2 연동

- rosbridge_server 기반 WebSocket 통신
- `/program`, `/cmd_vel`, `/run_state` Topic 활용
- 웹과 ROS2 간 실시간 데이터 교환

## 5.4 LiDAR 기반 안전 기능

- 전방·후방 장애물 감지
- Runtime Skip
- Emergency Stop

---

# 6. 구현 결과

| 기능 | 결과 |
|------|------|
| 블록 편집기 | ✅ |
| TurtleBot3 제어 | ✅ |
| rosbridge 통신 | ✅ |
| Runtime Interpreter | ✅ |
| 반복문 | ✅ |
| 조건문 | ✅ |
| 중첩 구조 | ✅ |
| Highlight | ✅ |
| Emergency Stop | ✅ |
| LiDAR 감지 | ✅ |

---

# 7. 역할 분담

| 이름 | 담당 | 주요 수행 내용 |
|------|------|----------------|
| 박준서 | 프로젝트 관리 | 일정 관리 및 프로젝트 총괄 |
| **박정호** | **Full Stack 개발** | **웹 UI 설계, ROS2 연동, Runtime Interpreter 구현, JSON Tree 설계, 시스템 통합, 테스트 및 문서화** |
| 김건호 | Web | 블록 편집기 구현 |
| 윤태환 | ROS2 | 주행 제어 및 Interpreter 보조 |
| 김민찬 | Hardware | LiDAR 및 부저 제어 |
| 김성수 | Integration | 빌드 및 통합 테스트 |

---

# 8. 개발 과정

### Day 1

- 요구사항 분석
- 시스템 설계
- 개발 환경 구축

### Day 2

- Web UI 구현
- ROS2 Node 구현
- TurtleBot3 기본 제어

### Day 3

- rosbridge 연동
- 전체 시스템 통합
- Highlight 구현

### Day 4

- 반복문 및 조건문 구현
- Nested Block 지원
- 사용자 테스트

### Day 5

- Runtime Skip 구현
- 시스템 안정화
- 문서 작성

---

# 9. 트러블슈팅

| 문제 | 원인 | 해결 |
|------|------|------|
| WebSocket 연결 실패 | rosbridge 미실행 | rosbridge_server 실행 절차 추가 |
| Highlight 불일치 | 실행 상태 동기화 문제 | `/run_state` 기반 갱신 |
| 중첩 블록 오류 | Stack 처리 미흡 | Runtime Interpreter 개선 |
| 장애물 감지 시 프로그램 종료 | 전체 종료 로직 | Runtime Skip 적용 |
| 실행 중 프로그램 수정 | UI 잠금 미적용 | Web UI Lock 추가 |

---

# 10. 테스트 결과

| 테스트 | 결과 |
|---------|------|
| Web 실행 | ✅ |
| ROS2 통신 | ✅ |
| TurtleBot3 제어 | ✅ |
| 반복문 | ✅ |
| 조건문 | ✅ |
| 중첩 구조 | ✅ |
| Highlight | ✅ |
| Emergency Stop | ✅ |
| LiDAR | ✅ |

모든 필수 기능이 정상적으로 동작하는 것을 확인하였다.

---

# 11. KPT 회고

## Keep

- 웹과 ROS2를 안정적으로 연동하였다.
- Runtime Interpreter를 구현하여 중첩 구조를 지원하였다.
- 팀원 간 역할을 분담하여 개발 일정을 계획대로 진행하였다.

## Problem

- 프로그램 저장 및 불러오기 기능은 구현하지 못하였다.
- 실행 경로 시각화 기능은 제외하였다.

## Try

- LocalStorage를 이용한 프로그램 저장 기능 추가
- 실행 경로 시각화 기능 구현
- 3D 시뮬레이터 연동
- 다양한 ROS2 기반 로봇 지원

---

# 12. 결론

본 프로젝트를 통해 웹 기반 블록 코딩 환경과 ROS 2 기반 TurtleBot3를 연동한 교육용 로봇 플랫폼을 구현하였다.

웹에서 작성한 블록 프로그램을 JSON Tree 형태로 변환하여 `rosbridge_server`를 통해 ROS 2에 전달하고, Runtime Interpreter가 이를 실시간으로 해석하여 로봇을 제어하는 구조를 구현하였다. 또한 LiDAR 기반 장애물 감지와 Runtime Skip 기능을 적용하여 실제 환경에서도 안정적으로 동작하는 시스템을 구축하였다.

이번 프로젝트를 통해 웹 개발, ROS 2, 로봇 제어, 실시간 통신, 시스템 통합 등 다양한 기술을 활용한 프로젝트 수행 경험을 쌓을 수 있었으며, 향후 교육용 로봇 플랫폼으로 확장할 수 있는 기반을 마련하였다.
