# 🚀 Google Cloud Run 배포 가이드

## 개요

이 가이드는 Unwoldam Tarot API를 Google Cloud Run에 배포하는 전체 과정을 설명합니다.

**예상 시간:** 30-40분
**예상 비용:** 무료 티어 범위 내 ($300 크레딧 활용)
**난이도:** ⭐ 쉬움

---

## 📋 사전 준비

### 1. Google Cloud 계정
- Google 계정 필요
- 신용카드 등록 필요 (무료 크레딧 $300 제공)
- https://cloud.google.com 접속

### 2. 필수 도구 설치

#### gcloud CLI 설치

**macOS:**
```bash
# Homebrew 사용
brew install --cask google-cloud-sdk

# 또는 설치 스크립트
curl https://sdk.cloud.google.com | bash
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
- https://cloud.google.com/sdk/docs/install 에서 설치 프로그램 다운로드

#### 설치 확인
```bash
gcloud --version
# Google Cloud SDK 450.0.0 이상
```

---

## 🔧 1단계: GCP 프로젝트 설정

### 1.1 gcloud 초기화

```bash
# gcloud 로그인
gcloud auth login

# 프로젝트 생성 (ID는 전역 고유해야 함)
gcloud projects create unwoldam-tarot-api \
  --name="Unwoldam Tarot API"

# 프로젝트 설정
gcloud config set project unwoldam-tarot-api

# 현재 프로젝트 확인
gcloud config get-value project
```

### 1.2 필수 API 활성화

```bash
# Cloud Run API
gcloud services enable run.googleapis.com

# Container Registry API
gcloud services enable containerregistry.googleapis.com

# Artifact Registry API (권장)
gcloud services enable artifactregistry.googleapis.com

# Cloud Build API (자동 빌드용)
gcloud services enable cloudbuild.googleapis.com

# Secret Manager API (API 키 저장용)
gcloud services enable secretmanager.googleapis.com

# Redis (Memorystore) API
gcloud services enable redis.googleapis.com

# VPC Access API (Redis 연결용)
gcloud services enable vpcaccess.googleapis.com

# 전부 한번에 활성화
gcloud services enable \
  run.googleapis.com \
  containerregistry.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  redis.googleapis.com \
  vpcaccess.googleapis.com
```

### 1.3 빌링 계정 연결

```bash
# 빌링 계정 확인
gcloud billing accounts list

# 프로젝트에 빌링 연결
gcloud billing projects link unwoldam-tarot-api \
  --billing-account=XXXXXX-XXXXXX-XXXXXX
```

---

## 🔐 2단계: Secret Manager에 API 키 저장

### 2.1 API 키를 Secret으로 생성

```bash
# Anthropic API Key
echo -n "your_anthropic_api_key" | \
  gcloud secrets create anthropic-api-key \
  --data-file=- \
  --replication-policy="automatic"

# OpenAI API Key
echo -n "your_openai_api_key" | \
  gcloud secrets create openai-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Google API Key (Gemini)
echo -n "your_google_api_key" | \
  gcloud secrets create google-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Secret Key (세션 암호화용)
python3 -c "import secrets; print(secrets.token_urlsafe(32), end='')" | \
  gcloud secrets create secret-key \
  --data-file=- \
  --replication-policy="automatic"
```

### 2.2 Secret 확인

```bash
# 생성된 Secret 목록 확인
gcloud secrets list

# Secret 버전 확인
gcloud secrets versions list anthropic-api-key
```

---

## 🗄️ 3단계: Redis (Memorystore) 설정

### Option A: Memorystore Redis (권장 - 프로덕션)

**비용:** 약 $25-50/월 (1GB Basic)

```bash
# VPC Connector 생성 (Cloud Run과 Redis 연결용)
gcloud compute networks vpc-access connectors create tarot-connector \
  --region=asia-northeast3 \
  --subnet-range=10.8.0.0/28

# Redis 인스턴스 생성 (서울 리전)
gcloud redis instances create unwoldam-redis \
  --size=1 \
  --region=asia-northeast3 \
  --redis-version=redis_7_0 \
  --tier=basic

# Redis 정보 확인
gcloud redis instances describe unwoldam-redis --region=asia-northeast3

# Redis IP 주소 확인 (나중에 사용)
gcloud redis instances describe unwoldam-redis \
  --region=asia-northeast3 \
  --format="get(host)"
```

### Option B: 메모리 기반 (개발/테스트)

**비용:** 무료

Redis 없이 배포하려면 이 단계를 건너뛰세요. API가 자동으로 메모리 기반 세션 저장소를 사용합니다.

---

## 🐳 4단계: Docker 이미지 빌드 및 푸시

### 4.1 Artifact Registry 저장소 생성

```bash
# Artifact Registry 저장소 생성
gcloud artifacts repositories create tarot-api \
  --repository-format=docker \
  --location=asia-northeast3 \
  --description="Unwoldam Tarot API Docker images"

# Docker 인증 설정
gcloud auth configure-docker asia-northeast3-docker.pkg.dev
```

### 4.2 이미지 빌드 및 푸시

```bash
# 프로젝트 디렉토리로 이동
cd /path/to/TarotLLM

# 프로젝트 ID 확인
PROJECT_ID=$(gcloud config get-value project)
echo $PROJECT_ID

# Docker 이미지 빌드
docker build -t asia-northeast3-docker.pkg.dev/$PROJECT_ID/tarot-api/unwoldam-tarot-api:latest .

# 이미지 푸시
docker push asia-northeast3-docker.pkg.dev/$PROJECT_ID/tarot-api/unwoldam-tarot-api:latest
```

**또는 Cloud Build 사용 (자동 빌드):**

```bash
# Cloud Build로 빌드 및 푸시 (더 빠름)
gcloud builds submit \
  --tag asia-northeast3-docker.pkg.dev/$PROJECT_ID/tarot-api/unwoldam-tarot-api:latest
```

---

## ☁️ 5단계: Cloud Run 배포

### 5.1 환경 변수 준비

프로젝트 루트에 `cloudrun-env.yaml` 파일 생성:

```yaml
# cloudrun-env.yaml
API_V1_STR: "/api/v1"
PROJECT_NAME: "Unwoldam Tarot API"
VERSION: "1.2.0"
ALLOWED_ORIGINS: "https://yourdomain.com,https://www.yourdomain.com"
ENVIRONMENT: "production"
DEBUG: "false"
LOG_LEVEL: "INFO"
HOST: "0.0.0.0"
PORT: "8080"
CLAUDE_MODEL: "claude-sonnet-4-5-20250929"
OPENAI_MODEL: "gpt-4-turbo"
GEMINI_MODEL: "gemini-pro"
DEFAULT_LLM_PROVIDER: "claude"
```

### 5.2 Cloud Run 배포 (Redis 없이)

```bash
PROJECT_ID=$(gcloud config get-value project)

gcloud run deploy unwoldam-tarot-api \
  --image=asia-northeast3-docker.pkg.dev/$PROJECT_ID/tarot-api/unwoldam-tarot-api:latest \
  --platform=managed \
  --region=asia-northeast3 \
  --allow-unauthenticated \
  --port=8000 \
  --memory=2Gi \
  --cpu=2 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=300 \
  --env-vars-file=cloudrun-env.yaml \
  --set-secrets=ANTHROPIC_API_KEY=anthropic-api-key:latest \
  --set-secrets=OPENAI_API_KEY=openai-api-key:latest \
  --set-secrets=GOOGLE_API_KEY=google-api-key:latest \
  --set-secrets=SECRET_KEY=secret-key:latest
```

### 5.3 Cloud Run 배포 (Redis 포함)

```bash
# Redis IP 가져오기
REDIS_HOST=$(gcloud redis instances describe unwoldam-redis \
  --region=asia-northeast3 \
  --format="get(host)")

# Redis URL 환경 변수 추가하여 배포
gcloud run deploy unwoldam-tarot-api \
  --image=asia-northeast3-docker.pkg.dev/$PROJECT_ID/tarot-api/unwoldam-tarot-api:latest \
  --platform=managed \
  --region=asia-northeast3 \
  --allow-unauthenticated \
  --port=8000 \
  --memory=2Gi \
  --cpu=2 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=300 \
  --env-vars-file=cloudrun-env.yaml \
  --set-env-vars=REDIS_URL=redis://$REDIS_HOST:6379/0 \
  --set-secrets=ANTHROPIC_API_KEY=anthropic-api-key:latest \
  --set-secrets=OPENAI_API_KEY=openai-api-key:latest \
  --set-secrets=GOOGLE_API_KEY=google-api-key:latest \
  --set-secrets=SECRET_KEY=secret-key:latest \
  --vpc-connector=tarot-connector
```

### 5.4 배포 확인

```bash
# 서비스 URL 확인
gcloud run services describe unwoldam-tarot-api \
  --region=asia-northeast3 \
  --format="get(status.url)"

# 출력 예시: https://unwoldam-tarot-api-abc123-an.a.run.app
```

---

## ✅ 6단계: 배포 테스트

### 6.1 Health Check

```bash
# URL 저장
SERVICE_URL=$(gcloud run services describe unwoldam-tarot-api \
  --region=asia-northeast3 \
  --format="get(status.url)")

# Health check
curl $SERVICE_URL/health | jq .

# 예상 출력:
# {
#   "status": "healthy",
#   "version": "1.2.0",
#   "services": {
#     "llm_providers": { "status": "available" },
#     "rag": { "status": "healthy", "cards_loaded": 78 },
#     "session": { "status": "healthy", "storage_type": "redis" }
#   }
# }
```

### 6.2 API 테스트

```bash
# 타로 마스터 목록 조회
curl $SERVICE_URL/api/v1/tarot/masters | jq .

# 타로 리딩 생성 테스트
curl -X POST $SERVICE_URL/api/v1/tarot/reading \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "question": "What does the future hold?",
    "spread_type": "three_card",
    "llm_provider": "claude",
    "tarot_master_id": "master_1",
    "draw_cards": true
  }' | jq .
```

### 6.3 Swagger UI 접속

브라우저에서 접속:
```
https://unwoldam-tarot-api-abc123-an.a.run.app/docs
```

---

## 🌐 7단계: 커스텀 도메인 설정 (선택)

### 7.1 도메인 매핑

```bash
# 도메인 매핑 생성
gcloud run domain-mappings create \
  --service=unwoldam-tarot-api \
  --domain=api.yourdomain.com \
  --region=asia-northeast3

# DNS 레코드 확인 (출력된 내용을 DNS에 추가)
gcloud run domain-mappings describe \
  --domain=api.yourdomain.com \
  --region=asia-northeast3
```

### 7.2 DNS 설정

도메인 등록 대행사에서 다음 레코드 추가:

```
Type: CNAME
Name: api
Value: ghs.googlehosted.com
```

### 7.3 SSL 인증서

Google Cloud Run이 자동으로 SSL 인증서를 발급하고 갱신합니다 (Let's Encrypt).

---

## 📊 8단계: 모니터링 설정

### 8.1 Cloud Logging

```bash
# 최근 로그 확인
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=unwoldam-tarot-api" \
  --limit=50 \
  --format=json

# 실시간 로그 스트리밍
gcloud alpha logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=unwoldam-tarot-api"
```

### 8.2 Cloud Monitoring

**Cloud Console에서:**
1. https://console.cloud.google.com/monitoring
2. Dashboards → Create Dashboard
3. 주요 메트릭 추가:
   - Request count
   - Request latency
   - Container CPU utilization
   - Container memory utilization
   - Error rate

### 8.3 알림 설정

```bash
# 이메일 알림 채널 생성
gcloud alpha monitoring channels create \
  --display-name="Admin Email" \
  --type=email \
  --channel-labels=email_address=your@email.com

# Error rate 알림 정책 생성 (Cloud Console 사용 권장)
```

---

## 💰 9단계: 비용 관리

### 9.1 예산 알림 설정

```bash
# Cloud Console에서 설정:
# Billing → Budgets & alerts → CREATE BUDGET
# 예: 월 $50 예산, 50%/90%/100% 알림
```

### 9.2 비용 최적화

```yaml
# 최소 인스턴스를 0으로 설정 (기본값)
--min-instances=0

# 사용량이 많아지면:
--min-instances=1  # Cold start 방지

# CPU 할당 정책
--cpu-throttling  # 기본값, 비용 절감
--no-cpu-throttling  # 성능 우선
```

### 9.3 예상 비용 계산

**무료 티어 (매월):**
- 200만 요청
- 360,000 vCPU-초
- 180,000 GiB-초

**예상 사용량 (월 10만 요청):**
- Cloud Run: 무료 티어 범위 내 → $0
- Memorystore Redis 1GB: $25-30
- Cloud Build (한 달 120분): 무료
- Artifact Registry (10GB): 무료

**총 예상 비용: $25-30/월** (Redis 사용 시)
**총 예상 비용: $0/월** (메모리만 사용 시)

---

## 🔄 10단계: CI/CD 연동

### 10.1 GitHub Actions Secrets 추가

GitHub Repository → Settings → Secrets:

```
GCP_PROJECT_ID: unwoldam-tarot-api
GCP_SA_KEY: <서비스 계정 JSON 키>
```

### 10.2 서비스 계정 생성

```bash
# 서비스 계정 생성
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

# 권한 부여
gcloud projects add-iam-policy-binding unwoldam-tarot-api \
  --member="serviceAccount:github-actions@unwoldam-tarot-api.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding unwoldam-tarot-api \
  --member="serviceAccount:github-actions@unwoldam-tarot-api.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding unwoldam-tarot-api \
  --member="serviceAccount:github-actions@unwoldam-tarot-api.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# JSON 키 생성
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions@unwoldam-tarot-api.iam.gserviceaccount.com

# key.json 내용을 GitHub Secrets의 GCP_SA_KEY에 복사
cat key.json
```

### 10.3 GitHub Actions 워크플로우는 이미 준비됨

`.github/workflows/cd.yml`이 main 브랜치 푸시 시 자동으로 배포합니다.

---

## 🛠️ 관리 명령어

### 서비스 관리

```bash
# 서비스 목록
gcloud run services list

# 서비스 상세 정보
gcloud run services describe unwoldam-tarot-api --region=asia-northeast3

# 트래픽 확인
gcloud run services describe unwoldam-tarot-api \
  --region=asia-northeast3 \
  --format="get(status.traffic)"

# 리비전 목록
gcloud run revisions list --service=unwoldam-tarot-api --region=asia-northeast3
```

### 업데이트 배포

```bash
# 새 이미지 빌드 및 배포
gcloud builds submit --tag asia-northeast3-docker.pkg.dev/$PROJECT_ID/tarot-api/unwoldam-tarot-api:latest

# 서비스 업데이트
gcloud run services update unwoldam-tarot-api \
  --image=asia-northeast3-docker.pkg.dev/$PROJECT_ID/tarot-api/unwoldam-tarot-api:latest \
  --region=asia-northeast3
```

### 환경 변수 업데이트

```bash
# 환경 변수 추가/변경
gcloud run services update unwoldam-tarot-api \
  --update-env-vars KEY=VALUE \
  --region=asia-northeast3

# Secret 업데이트
echo -n "new_api_key" | gcloud secrets versions add anthropic-api-key --data-file=-
```

### 스케일링 설정

```bash
# 최소/최대 인스턴스 조정
gcloud run services update unwoldam-tarot-api \
  --min-instances=1 \
  --max-instances=20 \
  --region=asia-northeast3

# 동시 요청 수 조정 (기본: 80)
gcloud run services update unwoldam-tarot-api \
  --concurrency=100 \
  --region=asia-northeast3
```

---

## 🐛 트러블슈팅

### 1. 배포 실패

```bash
# 최근 배포 로그 확인
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# Cloud Build 로그 확인
gcloud builds list --limit=5
gcloud builds log <BUILD_ID>
```

### 2. Health Check 실패

```bash
# 컨테이너 로그 확인
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=unwoldam-tarot-api" \
  --limit=100

# 로컬에서 같은 이미지 테스트
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=xxx \
  asia-northeast3-docker.pkg.dev/$PROJECT_ID/tarot-api/unwoldam-tarot-api:latest
```

### 3. Redis 연결 실패

```bash
# VPC Connector 상태 확인
gcloud compute networks vpc-access connectors describe tarot-connector --region=asia-northeast3

# Redis 인스턴스 상태 확인
gcloud redis instances describe unwoldam-redis --region=asia-northeast3

# Cloud Run에서 VPC Connector 확인
gcloud run services describe unwoldam-tarot-api \
  --region=asia-northeast3 \
  --format="get(spec.template.spec.containers[0].vpcAccess)"
```

### 4. 느린 응답 (Cold Start)

```bash
# 최소 인스턴스를 1로 설정 (항상 1개 인스턴스 유지)
gcloud run services update unwoldam-tarot-api \
  --min-instances=1 \
  --region=asia-northeast3
```

### 5. 높은 비용

```bash
# 현재 비용 확인
gcloud billing accounts list
gcloud billing projects describe unwoldam-tarot-api

# 리소스 사용량 확인
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_count"'

# 불필요한 리소스 정리
gcloud run services delete OLD_SERVICE --region=asia-northeast3
gcloud artifacts repositories delete OLD_REPO --location=asia-northeast3
```

---

## 📋 배포 체크리스트

### 배포 전
- [ ] gcloud CLI 설치 완료
- [ ] GCP 프로젝트 생성 및 빌링 활성화
- [ ] 필수 API 활성화
- [ ] Secret Manager에 API 키 저장
- [ ] Docker 이미지 빌드 테스트

### 배포 중
- [ ] Artifact Registry에 이미지 푸시
- [ ] Cloud Run 서비스 배포
- [ ] 환경 변수 및 Secret 설정
- [ ] Health check 통과

### 배포 후
- [ ] API 엔드포인트 테스트
- [ ] Swagger UI 접속 확인
- [ ] 모니터링 대시보드 설정
- [ ] 알림 설정 (이메일/Slack)
- [ ] 예산 알림 설정
- [ ] 커스텀 도메인 설정 (선택)
- [ ] SSL 인증서 확인

---

## 📞 도움말

- **GCP 문서**: https://cloud.google.com/run/docs
- **가격 계산기**: https://cloud.google.com/products/calculator
- **무료 티어**: https://cloud.google.com/free
- **커뮤니티**: https://stackoverflow.com/questions/tagged/google-cloud-run

---

**다음 단계:** [모니터링 대시보드 설정](./GCP_MONITORING.md)
