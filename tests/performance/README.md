# 성능 테스트 가이드

## 설치

```bash
pip install locust
```

## 사용법

### 1. Web UI 모드

```bash
# Locust 웹 인터페이스 시작
locust -f tests/performance/locustfile.py

# 브라우저에서 http://localhost:8089 접속
# - Number of users: 100
# - Spawn rate: 10 users/second
# - Host: http://localhost:8000
```

### 2. Headless 모드 (자동화)

```bash
# 기본 부하 테스트 (100명, 5분)
locust -f tests/performance/locustfile.py \
    --headless \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m \
    --host http://localhost:8000

# 가벼운 테스트 (10명, 1분)
locust -f tests/performance/locustfile.py \
    --headless \
    --users 10 \
    --spawn-rate 2 \
    --run-time 1m \
    --host http://localhost:8000

# 스트레스 테스트 (500명, 10분)
locust -f tests/performance/locustfile.py \
    --headless \
    --users 500 \
    --spawn-rate 50 \
    --run-time 10m \
    --host http://localhost:8000
```

### 3. 특정 사용자 클래스 실행

```bash
# TarotAPIUser만 실행
locust -f tests/performance/locustfile.py \
    --headless \
    --users 50 \
    --spawn-rate 5 \
    TarotAPIUser

# StressTestUser (스트레스 테스트)
locust -f tests/performance/locustfile.py \
    --headless \
    --users 200 \
    --spawn-rate 20 \
    StressTestUser

# ReadOnlyUser (읽기 전용)
locust -f tests/performance/locustfile.py \
    --headless \
    --users 100 \
    --spawn-rate 10 \
    ReadOnlyUser
```

### 4. 결과 저장

```bash
# HTML 리포트 생성
locust -f tests/performance/locustfile.py \
    --headless \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m \
    --host http://localhost:8000 \
    --html reports/locust_report.html

# CSV 데이터 저장
locust -f tests/performance/locustfile.py \
    --headless \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m \
    --host http://localhost:8000 \
    --csv reports/locust_data
```

## 테스트 시나리오

### TarotAPIUser (일반 사용자)
- **10%**: Health check
- **20%**: 마스터 목록 조회
- **50%**: 타로 리딩 생성
- **20%**: 세션 생성 및 조회

### StressTestUser (스트레스 테스트)
- 짧은 대기 시간 (0.1-0.5초)
- 빠른 연속 요청
- 시스템 한계 테스트

### ReadOnlyUser (읽기 전용)
- 마스터 목록 조회
- 스프레드 목록 조회
- Health check

## 성능 목표

### 최소 요구사항
- **RPS**: 100+ requests/second
- **평균 응답 시간**: < 500ms
- **P95 응답 시간**: < 1000ms
- **에러율**: < 1%

### 권장 목표
- **RPS**: 500+ requests/second
- **평균 응답 시간**: < 200ms
- **P95 응답 시간**: < 500ms
- **에러율**: < 0.1%
- **동시 사용자**: 1000+

## 결과 분석

### 주요 메트릭

1. **Total Requests**: 총 요청 수
2. **Failures**: 실패한 요청 수
3. **RPS**: Requests Per Second
4. **Response Time (ms)**:
   - Min: 최소 응답 시간
   - Max: 최대 응답 시간
   - Average: 평균 응답 시간
   - P50: 중간값 (50th percentile)
   - P95: 95th percentile
   - P99: 99th percentile

### 성능 문제 진단

#### 높은 응답 시간
```bash
# Worker 수 증가
WORKERS=8

# Gunicorn timeout 증가
TIMEOUT=300

# Redis 커넥션 풀 확인
```

#### 높은 에러율
```bash
# Rate limiting 확인
# - 10 req/min for readings
# - 20 req/min for sessions

# LLM API 할당량 확인
# - Anthropic: 10 req/min (Tier 1)
# - OpenAI: 3 req/min (Free tier)
```

#### 메모리 부족
```bash
# Docker 메모리 제한 증가
memory: 4G

# Redis maxmemory 조정
maxmemory 1gb
```

## 예제 결과

```
Type     Name                                    # reqs      # fails  |    Avg     Min     Max    Med
--------|----------------------------------------|-------|-------------|-------|-------|-------|-------
GET      /health                                   1000     0(0.00%)  |     15       8      45     14
GET      /api/v1/tarot/masters                     2000     0(0.00%)  |     25      12      78     23
POST     /api/v1/tarot/reading                     5000    10(0.20%)  |    450     120    2500    380
POST     /api/v1/tarot/session [POST]              2000     0(0.00%)  |     35      15      95     32
--------|----------------------------------------|-------|-------------|-------|-------|-------|-------
         Aggregated                              10000    10(0.10%)  |    256       8    2500    150

Response time percentiles (approximated)
Type     Name                                              50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100%
--------|------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------
GET      /health                                             14     16     18     20     25     30     38     42     45     45     45
GET      /api/v1/tarot/masters                               23     27     32     35     45     55     68     75     78     78     78
POST     /api/v1/tarot/reading                              380    520    680    780   1200   1500   1900   2200   2500   2500   2500
POST     /api/v1/tarot/session [POST]                        32     38     45     50     65     78     88     92     95     95     95
--------|------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------
         Aggregated                                         150    280    420    550    890   1300   1700   2000   2400   2500   2500
```

## CI/CD 통합

GitHub Actions에서 실행:

```yaml
# .github/workflows/performance.yml
- name: Run performance tests
  run: |
    locust -f tests/performance/locustfile.py \
      --headless \
      --users 50 \
      --spawn-rate 5 \
      --run-time 2m \
      --host http://localhost:8000 \
      --html reports/performance.html
```
