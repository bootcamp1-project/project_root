# 📅 DAILY_LOG.md

# 블록 코딩 로봇 교육 플랫폼 개발 일지

> 프로젝트 기간 : 5일 (40시간)

---

# 프로젝트 개요

본 프로젝트는 ROS 2 Humble 기반 TurtleBot3와 웹 기반 블록 코딩 환경을 연동하여 초등학생을 위한 교육용 로봇 제어 플랫폼을 개발하는 것을 목표로 진행하였다.

프로젝트는 총 5일 동안 요구사항 분석부터 시스템 설계, 구현, 통합 테스트, 문서화까지 수행하였다.

---

# Day 1 - 프로젝트 기획 및 시스템 설계

## 목표

- 프로젝트 요구사항 분석
- 시스템 아키텍처 설계
- 역할 분담
- 개발 환경 구축

---

## 수행 내용

### 요구사항 분석

프로젝트 기능을 Must / Should / Could 항목으로 분류하였다.

#### Must

- 블록 코딩 UI
- TurtleBot3 제어
- ROS2 통신
- 장애물 감지
- 긴급 정지
- 프로그램 저장

#### Should

- 반복문
- 조건문
- 중첩 구조

#### Could


- 실행 경로 시각화
- 시뮬레이터

---

### 시스템 구조 설계

웹과 ROS2 사이를 rosbridge_server를 이용한 WebSocket 통신으로 구성하였다.

```
Web

↓

rosbridge_server

↓

Interpreter

↓

TurtleBot3
```

---

### 통신 방식 정의

프로그램은 JSON Tree 형태로 전송하도록 결정하였다.

예시

```json
[
    {
        "op":"forward",
        "time":2
    }
]
```

---

### 개발 환경 구축

구성한 환경

- Ubuntu 22.04
- ROS2 Humble
- TurtleBot3 Burger
- Python 3
- HTML
- CSS
- JavaScript

---

## 담당 업무

### 박정호

- 시스템 구조 설계 참여
- JSON Tree 구조 설계
- Runtime Interpreter 구조 검토
- Web ↔ ROS2 통신 구조 설계

---

## 발생한 문제

### 문제

웹과 ROS2를 어떤 방식으로 연결할지 결정되지 않았다.

### 해결

rosbridge_server를 사용하여 WebSocket 통신을 구성하기로 결정하였다.

---

## 결과

- 시스템 구조 확정
- 통신 방식 확정
- 역할 분담 완료
- 개발 환경 구축 완료

---

### 윤태환 

- 주제 선정 및 프로젝트 제안서 작성

---

# Day 2 - 기본 기능 구현

## 목표

- Web UI 구현
- ROS2 Node 구현
- TurtleBot3 제어 확인

---

## 수행 내용

### Web

- Drag & Drop UI 구현
- 블록 생성
- 블록 삭제
- 실행 버튼 구현

---

### ROS2

구현한 Node

- interpreter_node
- ultrasonic_node
- buzzer_node

---

### Interpreter

기본 기능 구현

- JSON 수신
- 순차 실행
- cmd_vel Publish

---

### TurtleBot3

다음 동작을 확인하였다.

- 전진
- 후진
- 좌회전
- 우회전

---

## 담당 업무

### 박정호

- Interpreter Node 구현
- WebSocket 연동
- JSON 파싱
- cmd_vel 제어
- UI / UX 테스트

---

## 발생한 문제

### 문제

웹에서 ROS2로 데이터가 전달되지 않았다.

### 원인

rosbridge 연결 실패

### 해결

WebSocket 주소와 Topic 이름을 수정하여 해결하였다.

---

## 결과

- Web ↔ ROS2 연동 성공
- TurtleBot3 제어 성공
- 기본 블록 실행 성공

---

### 윤태환

- 테스트 지원자 모집 및 산출물 테스트

##결과 

- 산출물 전체 동작 확인 및 문제접 검출


# Day 3 - 시스템 통합

## 목표

- Web
- ROS2
- TurtleBot3

전체 시스템 통합

---

## 수행 내용

### rosbridge 통신

WebSocket 연결 완료

---

### 프로그램 실행

JSON Tree

↓

Interpreter

↓

cmd_vel

↓

TurtleBot3

정상 확인

---

### Highlight

/run_state Topic을 이용하여

현재 실행 블록 표시 기능 구현

---

## 담당 업무

### 박정호

- 시스템 통합
- run_state 구현
- Highlight 기능 구현
- rosbridge 디버깅

---

## 발생한 문제

### 문제

Highlight가 실제 실행 순서와 맞지 않았다.

### 해결

실행 상태를 기준으로 UI를 갱신하도록 수정하였다.

---

## 결과

- 전체 파이프라인 동작
- Highlight 정상 동작

---

### 윤태환 

- 발표자료 작성 및 프로젝트 문서 보완
---
### 문서화

수정 및 작성 문서

- README
- PROJECT_GUIDE
- 블록 코딩 로봇 교육 플랫폼 최종 보고서.pdf / .pptx



# Day 4 - 기능 고도화

## 목표

- Repeat
- If
- Nested Block
- UI 개선
- Ai 기능 추가

---

## 수행 내용

### 반복문

Repeat Block 구현

---

### 조건문

If Block 구현

---

### Nested Block

Repeat 내부 If

If 내부 Repeat

구조 지원

---

### UI 개선

- UI Lock
- Emergency Stop
- 사용자 피드백 반영

---

### Ai기능 추가

- 자연어 명령 인식
- Ai 블록 자동 생성
- 반복 / If 블록 자동 구성
- 생성 블록 미리보기
- Ai 블록 추가 / 전체 교체 가능
- Ai 패널 접기 / 펼치기

  ---

## 담당 업무

### 박정호

- Runtime Interpreter 개선
- Nested Tree 처리
- UI 개선 참여
- 통합 테스트 

---

## 발생한 문제

### 문제

중첩 블록 실행 시 순서가 꼬였다.

### 해결

Stack 기반 실행 구조로 변경하였다.

---

## 결과

- Nested Block 지원
- Runtime Interpreter 개선

---

### 윤태환 

- 전체 문서 검토 및 수정,보완
- Ai활용내용 추가 
---
### 문서화

수정 문서

- README
- PLAN
- INTERFACE
- PROJECT_GUIDE
- DAILY_LOG
- TEST
- REPORT

---



# Day 5 - 최종 통합 및 검증

## 목표

- 시스템 안정화
- 테스트
- 문서 작성

---

## 수행 내용

### Runtime Skip

장애물이 감지되면

현재 이동 블록만 종료하도록 구현하였다.

---

### LiDAR

전방·후방 장애물 감지

---

### 문서화

작성 문서

- README
- PLAN
- INTERFACE
- PROJECT_GUIDE
- DAILY_LOG
- TEST
- REPORT

---

## 담당 업무

### 박정호

- Runtime Skip 구현
- 시스템 안정화
- 통합 테스트
- 문서 작성
- 최종 발표 자료 정리

---

## 발생한 문제

### 문제

장애물 감지 시 프로그램 전체가 종료되었다.

### 해결

현재 이동 블록만 종료하고 다음 블록을 실행하도록 Interpreter를 수정하였다.

---

## 최종 결과

### 구현 완료

- 블록 코딩 UI
- ROS2 연동
- rosbridge 통신
- TurtleBot3 제어
- Runtime Interpreter
- Repeat
- If
- Nested Block
- Runtime Skip
- Highlight
- Emergency Stop
- LiDAR 기반 장애물 감지
- Ai 블록 코딩 Assistant

---

# 프로젝트 회고

## 잘된 점

- Web과 ROS2를 안정적으로 연동하였다.
- Runtime Interpreter를 구현하여 중첩 구조를 지원하였다.
- TurtleBot3와 웹의 실시간 동기화를 구현하였다.
- 프로그램 작성 한것 저장하고 불러오는 기능을 구현하였다.
---

## 아쉬운 점

- 실행 경로 시각화 기능은 제외하였다.

---

## 향후 계획

- 실행 경로 시각화
- 3D 시뮬레이터 연동
- 교육용 콘텐츠 확장
