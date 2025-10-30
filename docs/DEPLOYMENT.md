# 🚀 프로덕션 배포 가이드

## 목차

- [배포 전 준비](#배포-전-준비)
- [Docker 배포](#docker-배포)
- [클라우드 배포](#클라우드-배포)
  - [AWS 배포](#aws-배포)
  - [GCP 배포](#gcp-배포)
  - [Azure 배포](#azure-배포)
- [CI/CD 파이프라인](#cicd-파이프라인)
- [모니터링 및 로깅](#모니터링-및-로깅)
- [성능 최적화](#성능-최적화)
- [보안 체크리스트](#보안-체크리스트)
- [트러블슈팅](#트러블슈팅)

---

## 배포 전 준비

### 1. 환경 변수 설정

```bash
# 프로덕션 환경 변수 복사
cp .env.production.example .env

# 필수 환경 변수 설정
# - LLM API Keys (ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY)
# - ALLOWED_ORIGINS (실제 도메인으로 변경)
# - SECRET_KEY (랜덤 키 생성)
# - REDIS_URL (프로덕션 Redis 주소)
```

**SECRET_KEY 생성:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. 테스트 실행

```bash
# 모든 테스트 실행
pytest tests/ -v

# 커버리지 확인
pytest --cov=app --cov-report=term tests/

# 테스트 결과: 70/70 passing ✓
```

### 3. 보안 스캔

```bash
# 의존성 취약점 스캔
safety check

# 코드 보안 스캔
bandit -r app/

# Docker 이미지 스캔
docker scan unwoldam-tarot-api:latest
```

### 4. 성능 테스트

```bash
# 부하 테스트 (Locust 사용)
locust -f tests/performance/locustfile.py

# 벤치마크 결과 확인
# - RPS (Requests Per Second)
# - 평균 응답 시간
# - 95th percentile 응답 시간
```

---

## Docker 배포

### 로컬 Docker 배포

#### 1. 개발 모드

```bash
# docker-compose.yml (개발용)
docker-compose up -d

# 로그 확인
docker-compose logs -f tarot-api

# 접속
open http://localhost:8000/docs
```

#### 2. 프로덕션 모드

```bash
# docker-compose.prod.yml (프로덕션용)
docker-compose -f docker-compose.prod.yml up -d

# Health check
curl http://localhost:8000/health

# 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps
```

### Docker 이미지 최적화

```bash
# 멀티스테이지 빌드로 이미지 크기 최적화
docker build -t unwoldam-tarot-api:latest .

# 이미지 크기 확인
docker images unwoldam-tarot-api

# Expected: ~500MB (멀티스테이지 빌드)
# Before: ~1.2GB (단일 스테이지)
```

### Docker Compose 명령어

```bash
# 시작
docker-compose -f docker-compose.prod.yml up -d

# 중지
docker-compose -f docker-compose.prod.yml down

# 재시작
docker-compose -f docker-compose.prod.yml restart

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f

# 볼륨 포함 삭제 (주의!)
docker-compose -f docker-compose.prod.yml down -v
```

---

## 클라우드 배포

### AWS 배포

#### Option 1: ECS (Elastic Container Service)

**1. ECR에 이미지 푸시**

```bash
# AWS CLI 로그인
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# 이미지 태그
docker tag unwoldam-tarot-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/unwoldam-tarot-api:latest

# 푸시
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/unwoldam-tarot-api:latest
```

**2. ECS 태스크 정의 (task-definition.json)**

```json
{
  "family": "unwoldam-tarot-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "tarot-api",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/unwoldam-tarot-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "ANTHROPIC_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:xxx:secret:tarot/anthropic_key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/unwoldam-tarot-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

**3. Redis 설정 (ElastiCache)**

```bash
# ElastiCache Redis 생성
aws elasticache create-cache-cluster \
  --cache-cluster-id unwoldam-redis \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --num-cache-nodes 1

# 엔드포인트 확인
aws elasticache describe-cache-clusters \
  --cache-cluster-id unwoldam-redis \
  --show-cache-node-info
```

**4. Application Load Balancer 설정**

```bash
# ALB 생성 및 타겟 그룹 설정
# - Health check path: /health
# - Port: 8000
# - SSL/TLS 인증서 설정
```

#### Option 2: EC2 배포

```bash
# EC2 인스턴스 접속
ssh -i key.pem ec2-user@<instance-ip>

# Docker 설치
sudo yum update -y
sudo yum install docker -y
sudo service docker start

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 프로젝트 클론 및 실행
git clone <repository-url>
cd TarotLLM
cp .env.production.example .env
# .env 파일 수정
docker-compose -f docker-compose.prod.yml up -d
```

### GCP 배포

#### Cloud Run 배포

```bash
# gcloud 로그인
gcloud auth login

# 프로젝트 설정
gcloud config set project <project-id>

# Container Registry에 이미지 푸시
docker tag unwoldam-tarot-api:latest gcr.io/<project-id>/unwoldam-tarot-api:latest
docker push gcr.io/<project-id>/unwoldam-tarot-api:latest

# Cloud Run 배포
gcloud run deploy unwoldam-tarot-api \
  --image gcr.io/<project-id>/unwoldam-tarot-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --port 8000 \
  --set-env-vars ENVIRONMENT=production \
  --set-secrets ANTHROPIC_API_KEY=anthropic_key:latest

# Redis (Memorystore)
gcloud redis instances create unwoldam-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0
```

### Azure 배포

#### Container Instances 배포

```bash
# Azure CLI 로그인
az login

# 리소스 그룹 생성
az group create --name unwoldam-rg --location eastus

# Container Registry 생성
az acr create --resource-group unwoldam-rg --name unwoldamacr --sku Basic

# 이미지 푸시
az acr login --name unwoldamacr
docker tag unwoldam-tarot-api:latest unwoldamacr.azurecr.io/unwoldam-tarot-api:latest
docker push unwoldamacr.azurecr.io/unwoldam-tarot-api:latest

# Container Instance 배포
az container create \
  --resource-group unwoldam-rg \
  --name unwoldam-tarot-api \
  --image unwoldamacr.azurecr.io/unwoldam-tarot-api:latest \
  --cpu 2 \
  --memory 2 \
  --registry-login-server unwoldamacr.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --dns-name-label unwoldam-tarot \
  --ports 8000 \
  --environment-variables ENVIRONMENT=production

# Redis (Azure Cache for Redis)
az redis create \
  --location eastus \
  --name unwoldam-redis \
  --resource-group unwoldam-rg \
  --sku Basic \
  --vm-size c0
```

---

## CI/CD 파이프라인

### GitHub Actions

프로젝트에는 3개의 GitHub Actions 워크플로우가 설정되어 있습니다:

#### 1. CI - Tests and Linting (`.github/workflows/ci.yml`)

**트리거:** Push, Pull Request (main, develop 브랜치)

**작업:**
- ✅ Code formatting (Black)
- ✅ Import sorting (isort)
- ✅ Linting (flake8)
- ✅ Unit tests (pytest)
- ✅ Coverage report
- ✅ Docker build test
- ✅ Security scan (Safety, Bandit)

#### 2. CD - Build and Deploy (`.github/workflows/cd.yml`)

**트리거:** Push to main, Tag push (v*.*.*)

**작업:**
- 🚀 Docker 이미지 빌드
- 📦 GitHub Container Registry 푸시
- 🏷️ 태그별 릴리스 생성

#### 3. PR Checks (`.github/workflows/pr-checks.yml`)

**트리거:** Pull Request

**작업:**
- ✅ PR 제목 검증
- 📊 Coverage 리포트 코멘트
- ⚡ Performance 벤치마크 (선택적)

### 워크플로우 시크릿 설정

GitHub Repository → Settings → Secrets에 다음 시크릿 추가:

```
ANTHROPIC_API_KEY
OPENAI_API_KEY
GOOGLE_API_KEY
```

---

## 모니터링 및 로깅

### 로깅 설정

#### 프로덕션 로깅 포맷 (JSON)

```python
# app/main.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "path": record.pathname,
            "line": record.lineno
        }
        return json.dumps(log_data)
```

#### CloudWatch Logs (AWS)

```python
import watchtower

logger = logging.getLogger()
logger.addHandler(watchtower.CloudWatchLogHandler(
    log_group='/aws/tarot-api',
    stream_name='production'
))
```

### 애플리케이션 모니터링

#### Prometheus + Grafana

**1. Prometheus 메트릭 추가**

```bash
pip install prometheus-fastapi-instrumentator
```

```python
# app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

**2. Grafana 대시보드**

- Request rate
- Response time (P50, P95, P99)
- Error rate
- Active sessions
- LLM API latency

#### Sentry (에러 트래킹)

```bash
pip install sentry-sdk[fastapi]
```

```python
# app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment=settings.ENVIRONMENT
)
```

---

## 성능 최적화

### 1. Gunicorn Workers 설정

```bash
# CPU 코어 기반 워커 수 계산
workers = (CPU cores * 2) + 1

# 예: 4 코어 시스템
WORKERS=9
```

### 2. Redis 최적화

```bash
# maxmemory 설정
maxmemory 512mb
maxmemory-policy allkeys-lru

# Persistence 설정
save 900 1
save 300 10
save 60 10000
```

### 3. 데이터베이스 커넥션 풀

```python
# 향후 PostgreSQL 사용 시
from sqlalchemy.pool import NullPool, QueuePool

engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10
)
```

### 4. HTTP 캐싱

```python
from fastapi import Response

@app.get("/api/v1/tarot/masters")
async def get_masters(response: Response):
    response.headers["Cache-Control"] = "public, max-age=3600"
    return masters
```

### 5. 부하 테스트 결과 (목표)

- **RPS:** 500+ requests/second
- **평균 응답 시간:** < 200ms
- **P95 응답 시간:** < 500ms
- **동시 사용자:** 1000+

---

## 보안 체크리스트

### 배포 전 확인사항

- [ ] ✅ 모든 API 키가 환경 변수로 설정됨
- [ ] ✅ DEBUG=false 설정
- [ ] ✅ ALLOWED_ORIGINS가 실제 도메인으로 설정됨
- [ ] ✅ Rate limiting 활성화 (10-20 req/min)
- [ ] ✅ HTTPS만 허용 (HTTP → HTTPS 리다이렉트)
- [ ] ✅ SECRET_KEY가 랜덤 값으로 설정됨
- [ ] ✅ 최신 의존성 설치 (chromadb 1.2.1, sentence-transformers 5.1.2)
- [ ] ✅ 보안 스캔 통과 (Safety, Bandit)
- [ ] ✅ Docker 이미지 스캔 통과
- [ ] ✅ 모든 테스트 통과 (70/70)
- [ ] ✅ Health check 엔드포인트 정상 작동
- [ ] ✅ 로그 파일 권한 설정 (644)
- [ ] ✅ Redis 비밀번호 설정 (프로덕션)
- [ ] ✅ SSL/TLS 인증서 설정

### 프로덕션 환경 보안

```bash
# Docker 컨테이너 non-root 사용자 실행
USER tarot

# 읽기 전용 파일 시스템
volumes:
  - ./data:/app/data:ro

# 리소스 제한
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

---

## 트러블슈팅

### 1. 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker logs unwoldam-tarot-api-prod

# Health check 확인
docker inspect unwoldam-tarot-api-prod | grep -A 10 Health

# 수동 테스트
docker exec -it unwoldam-tarot-api-prod /bin/bash
curl http://localhost:8000/health
```

### 2. Redis 연결 실패

```bash
# Redis 컨테이너 상태
docker ps | grep redis

# Redis 연결 테스트
docker exec -it unwoldam-redis-prod redis-cli ping
# Expected: PONG

# Redis 로그
docker logs unwoldam-redis-prod
```

### 3. 높은 메모리 사용량

```bash
# 메모리 사용량 확인
docker stats

# Worker 수 줄이기
WORKERS=2  # 기본: 4

# Redis maxmemory 제한
maxmemory 256mb
```

### 4. 느린 응답 시간

```bash
# 프로파일링 활성화
pip install py-spy

# 프로파일 캡처
py-spy top --pid <process-id>

# LLM API 타임아웃 확인
TIMEOUT=120  # Gunicorn timeout
```

### 5. LLM API 에러

```bash
# API 키 확인
echo $ANTHROPIC_API_KEY

# Rate limit 확인
# Anthropic: 10 req/min (Tier 1)
# OpenAI: 3 req/min (Free tier)

# Fallback 프로바이더 설정
DEFAULT_LLM_PROVIDER=claude
```

---

## 배포 체크리스트

### 최종 확인

- [ ] ✅ 환경 변수 모두 설정됨
- [ ] ✅ Docker 이미지 빌드 성공
- [ ] ✅ 로컬에서 프로덕션 모드 테스트
- [ ] ✅ Health check 정상
- [ ] ✅ 모든 테스트 통과
- [ ] ✅ 보안 스캔 통과
- [ ] ✅ CI/CD 파이프라인 정상 작동
- [ ] ✅ 모니터링 설정 완료
- [ ] ✅ 백업 전략 수립
- [ ] ✅ Rollback 계획 수립
- [ ] ✅ 문서 업데이트

### 배포 후 확인

- [ ] ✅ API 응답 정상
- [ ] ✅ Health check 엔드포인트 정상
- [ ] ✅ 로그 수집 정상
- [ ] ✅ 메트릭 수집 정상
- [ ] ✅ 에러 알림 설정
- [ ] ✅ SSL 인증서 유효
- [ ] ✅ DNS 설정 정상
- [ ] ✅ 성능 모니터링 활성화

---

## 참고 자료

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Gunicorn with Uvicorn](https://www.uvicorn.org/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [AWS ECS Deployment](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html)
- [GCP Cloud Run](https://cloud.google.com/run/docs)
- [Prometheus Monitoring](https://prometheus.io/docs/introduction/overview/)

---

**다음 단계:** [성능 최적화 가이드](PERFORMANCE.md) | [모니터링 대시보드 설정](MONITORING.md)
