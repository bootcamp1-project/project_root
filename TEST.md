# 🧪 TEST.md

# 블록 코딩 로봇 교육 플랫폼 테스트 결과

> ROS 2 Humble 기반 TurtleBot3 블록 코딩 교육 플랫폼 테스트 문서

---

# 1. 테스트 목적

본 테스트는 웹 애플리케이션, ROS 2, TurtleBot3 간의 통신 및 기능 구현 결과를 검증하기 위해 수행하였다.

주요 검증 항목은 다음과 같다.

- 블록 프로그램 실행
- ROS2 Topic 통신
- TurtleBot3 제어
- Runtime Interpreter
- 반복문 및 조건문
- 장애물 감지
- 긴급 정지
- 시스템 안정성

---

# 2. 테스트 환경

| 항목 | 내용 |
|------|------|
| OS | Ubuntu 22.04 LTS |
| ROS | ROS 2 Humble |
| Robot | TurtleBot3 Burger |
| Browser | Google Chrome |
| Communication | rosbridge_server |
| Language | Python, JavaScript |

---

# 3. 테스트 항목

| 번호 | 테스트 항목 | 결과 |
|------|-------------|------|
| T-01 | Web 접속 | ✅ |
| T-02 | rosbridge 연결 | ✅ |
| T-03 | 프로그램 전송 | ✅ |
| T-04 | TurtleBot3 이동 | ✅ |
| T-05 | 반복문 실행 | ✅ |
| T-06 | 조건문 실행 | ✅ |
| T-07 | 중첩 블록 실행 | ✅ |
| T-08 | Highlight | ✅ |
| T-09 | 장애물 감지 | ✅ |
| T-10 | Emergency Stop | ✅ |
| T-11 | Ai 블록코딩 보조 | ✅ |

---

# 4. 기능 테스트

## T-01 Web 접속

### 목적

웹 애플리케이션 정상 실행 확인

### 절차

1. HTTP Server 실행
2. 브라우저 접속

```
http://localhost:8000/blocks.html
```

### 기대 결과

블록 편집기가 정상 출력된다.

### 결과

✅ 성공

---

## T-02 rosbridge 연결

### 목적

WebSocket 연결 확인

### 절차

```bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

웹 접속 후 연결 확인

### 기대 결과

WebSocket Connected

### 결과

✅ 성공

---

## T-03 프로그램 실행

### 목적

블록 프로그램 전송 확인

### 테스트 프로그램

```
Forward

↓

Left

↓

Forward
```

### 기대 결과

TurtleBot3가 순서대로 동작한다.

### 결과

✅ 성공

---

## T-04 반복문 실행

### 테스트

```
Repeat (3)

↓

Forward
```

### 기대 결과

Forward가 3회 실행된다.

### 결과

✅ 성공

---

## T-05 조건문 실행

### 테스트

```
If Front

↓

Right
```

### 기대 결과

장애물이 있을 경우 Right 실행

### 결과

✅ 성공

---

## T-06 중첩 블록 실행

### 테스트

```
Repeat

↓

If

↓

Forward
```

### 기대 결과

Nested Block이 정상 수행된다.

### 결과

✅ 성공

---

## T-07 Highlight

### 목적

현재 실행 블록 표시

### 절차

프로그램 실행

↓

run_state 확인

↓

웹 Highlight 확인

### 결과

✅ 현재 실행 블록과 동일하게 표시됨

---

## T-08 Emergency Stop

### 테스트

프로그램 실행 중

↓

Emergency Stop 버튼 클릭

### 기대 결과

cmd_vel = 0

### 결과

✅ 즉시 정지

---

## T-09 LiDAR 장애물 감지

### 테스트

전방 20cm 이내 장애물 배치

### 기대 결과

현재 이동 블록 종료

### 결과

✅ Runtime Skip 정상 수행

---

## T-10 장시간 실행

### 테스트

약 30분 연속 실행

### 기대 결과

프로그램 중단 없음

### 결과

✅ 정상 동작

---

## T-11 Ai블록코딩보조

### 테스트

Ai 블록코딩 보조기능 실행

### 기대 결과

프로그램 정상 수행

### 결과

✅ 성공

---

# 5. 통신 테스트

## Topic 확인

```bash
ros2 topic list
```

확인된 Topic

```
/program
/cmd_vel
/run_state
/buzzer
/scan
/obstacle_dist/front
/obstacle_dist/rear
```

결과

✅ 정상

---

## cmd_vel 확인

```bash
ros2 topic echo /cmd_vel
```

결과

Twist 메시지가 정상 Publish됨

✅ 성공

---

## run_state 확인

```bash
ros2 topic echo /run_state
```

결과

현재 실행 블록 정보 확인

✅ 성공

---

# 6. 시나리오 테스트

## 시나리오 1

```
Forward

↓

Left

↓

Forward
```

결과

✅ 정상 이동

---

## 시나리오 2

```
Repeat (3)

↓

Forward
```

결과

✅ 3회 반복

---

## 시나리오 3

```
Repeat

↓

If Front

↓

Right
```

결과

✅ 중첩 구조 정상 수행

---

## 시나리오 4

```
Forward

↓

장애물 발견
```

결과

✅ Runtime Skip 수행

---

## 시나리오 5

```
프로그램 실행 중

↓

Emergency Stop
```

결과

✅ 즉시 정지

---

# 7. 사용자 테스트

프로젝트 팀원을 대상으로 블록 편집 및 실행 테스트를 수행하였다.

### 테스트 내용

- 블록 생성
- 블록 삭제
- 프로그램 실행
- 반복문 작성
- 조건문 작성
- 긴급 정지
- 프로그램 저장 및 불러오기

### 결과

- 블록 조작이 직관적이라는 의견이 많았다.
- 현재 실행 블록을 쉽게 확인할 수 있었다.
- 긴급 정지 기능이 즉시 동작하였다.

---

# 8. 발견된 문제 및 개선

| 문제 | 원인 | 개선 |
|------|------|------|
| Highlight 지연 | UI 갱신 지연 | run_state 기준 갱신 |
| 중첩 실행 오류 | Stack 처리 미흡 | Runtime Interpreter 개선 |
| WebSocket 재연결 실패 | 연결 종료 | 재연결 처리 추가 |
| 실행 중 수정 가능 | UI 미잠금 | Web UI Lock 적용 |

---

# 9. 테스트 결과 요약

| 항목 | 결과 |
|------|------|
| Web | ✅ |
| ROS2 | ✅ |
| rosbridge | ✅ |
| Interpreter | ✅ |
| TurtleBot3 | ✅ |
| Repeat | ✅ |
| If | ✅ |
| Nested Block | ✅ |
| Highlight | ✅ |
| Emergency Stop | ✅ |
| LiDAR | ✅ |
| Save & Load | ✅ | 
| Ai Block Coding Assistant | ✅ | 

---

# 10. 결론

모든 필수 기능(Must)은 정상적으로 동작하였다.

웹 애플리케이션과 ROS 2는 `rosbridge_server`를 통해 안정적으로 통신하였으며, Runtime Interpreter는 반복문과 조건문의 중첩 구조를 정상적으로 해석하였다.

또한 LiDAR 기반 장애물 감지와 긴급 정지 기능을 통해 실제 TurtleBot3 환경에서도 안정적으로 동작함을 확인하였다.

향후에는 실행 경로 시각화, 3D 시뮬레이터 등을 추가하여 교육용 플랫폼으로 확장할 계획이다.
