# 🚀 지금 바로 배포하기 (3단계)

**예상 시간: 20-30분**

---

## 사전 준비

✅ Google Cloud 계정 (있음)
✅ API 키 3개:
   - Anthropic API Key (Claude) - https://console.anthropic.com/
   - OpenAI API Key (GPT-4) - https://platform.openai.com/api-keys
   - Google API Key (Gemini) - https://makersuite.google.com/app/apikey

---

## 📍 1단계: gcloud CLI 설치 (5분)

### macOS
```bash
brew install --cask google-cloud-sdk
```

### Linux
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Windows
https://cloud.google.com/sdk/docs/install 에서 설치

### 확인
```bash
gcloud --version
# Google Cloud SDK 450.0.0 이상이면 OK
```

---

## 🔐 2단계: GCP 설정 및 API 키 등록 (10분)

### A. GCP 로그인 및 프로젝트 생성

```bash
# 1. 로그인
gcloud auth login

# 2. 프로젝트 생성 (ID는 전역 고유해야 함, 예: unwoldam-tarot-api-yourname)
gcloud projects create unwoldam-tarot-api-yourname \
  --name="Unwoldam Tarot API"

# 3. 프로젝트 설정
gcloud config set project unwoldam-tarot-api-yourname

# 4. 빌링 활성화 (브라우저에서)
# https://console.cloud.google.com/billing
# - 신용카드 등록
# - 무료 크레딧 $300 자동 적용
# - 프로젝트에 빌링 계정 연결

# 5. 필수 API 활성화
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com
```

### B. API 키 등록 (자동 스크립트)

```bash
# TarotLLM 디렉토리에서 실행
./setup-secrets.sh
```

**또는 수동 등록:**

```bash
# Anthropic API Key
echo -n "sk-ant-YOUR_KEY" | \
  gcloud secrets create anthropic-api-key \
  --data-file=- \
  --replication-policy="automatic"

# OpenAI API Key
echo -n "sk-proj-YOUR_KEY" | \
  gcloud secrets create openai-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Google API Key
echo -n "AIzaSyYOUR_KEY" | \
  gcloud secrets create google-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Secret Key (자동 생성)
python3 -c "import secrets; print(secrets.token_urlsafe(32), end='')" | \
  gcloud secrets create secret-key \
  --data-file=- \
  --replication-policy="automatic"
```

### C. Secret 확인

```bash
gcloud secrets list

# 출력 예시:
# NAME                CREATE_TIME          REPLICATION_POLICY
# anthropic-api-key   2025-01-30T12:00:00  automatic
# google-api-key      2025-01-30T12:00:00  automatic
# openai-api-key      2025-01-30T12:00:00  automatic
# secret-key          2025-01-30T12:00:00  automatic
```

---

## ☁️ 3단계: Cloud Run 배포 (10-15분)

### 자동 배포 (권장)

```bash
# TarotLLM 디렉토리에서 실행
./deploy-cloudrun.sh
```

스크립트가 자동으로:
1. ✅ Docker 이미지 빌드 (Cloud Build)
2. ✅ Artifact Registry에 푸시
3. ✅ Cloud Run에 배포
4. ✅ Health Check 테스트
5. ✅ 서비스 URL 출력

**예상 출력:**

```
======================================================================
  ✅ 배포 완료!
======================================================================

📍 서비스 URL:
   https://unwoldam-tarot-api-abc123xyz-an.a.run.app

📖 Swagger UI:
   https://unwoldam-tarot-api-abc123xyz-an.a.run.app/docs

🔍 Health Check:
   https://unwoldam-tarot-api-abc123xyz-an.a.run.app/health

======================================================================
```

---

## ✅ 배포 확인

### 1. Health Check

```bash
# 자동으로 출력된 URL 사용
curl https://unwoldam-tarot-api-xxx.a.run.app/health

# 예상 출력:
{
  "status": "healthy",
  "version": "1.2.0",
  "services": {
    "llm_providers": { "status": "available" },
    "rag": { "status": "healthy", "cards_loaded": 78 },
    "session": { "status": "healthy" }
  }
}
```

### 2. Swagger UI

브라우저에서 접속:
```
https://unwoldam-tarot-api-xxx.a.run.app/docs
```

### 3. API 테스트

```bash
# 타로 마스터 목록 조회
curl https://unwoldam-tarot-api-xxx.a.run.app/api/v1/tarot/masters

# 타로 리딩 테스트
curl -X POST https://unwoldam-tarot-api-xxx.a.run.app/api/v1/tarot/reading \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "question": "What does the future hold?",
    "spread_type": "three_card",
    "llm_provider": "claude",
    "tarot_master_id": "master_1",
    "draw_cards": true
  }'
```

---

## 🎉 배포 완료!

축하합니다! 프로덕션 타로 API가 운영 중입니다!

### 📊 모니터링

**Cloud Console:**
```
https://console.cloud.google.com/run/detail/asia-northeast3/unwoldam-tarot-api/metrics
```

**로그 확인:**
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=unwoldam-tarot-api" --limit=50
```

**실시간 로그:**
```bash
gcloud alpha logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=unwoldam-tarot-api"
```

### 💰 비용 확인

**예상 비용 (Redis 없이):**
- Cloud Run: $0/월 (무료 티어 범위 내)
- Cloud Build: $0/월 (무료 티어)
- Artifact Registry: $0/월 (무료)

**총: $0/월** ✨

---

## 🔄 재배포 (코드 수정 후)

```bash
./deploy-cloudrun.sh
```

또는

```bash
# 이미지만 재빌드
gcloud builds submit --tag asia-northeast3-docker.pkg.dev/$(gcloud config get-value project)/tarot-api/unwoldam-tarot-api:latest

# 서비스 업데이트
gcloud run services update unwoldam-tarot-api \
  --image=asia-northeast3-docker.pkg.dev/$(gcloud config get-value project)/tarot-api/unwoldam-tarot-api:latest \
  --region=asia-northeast3
```

---

## 🛑 서비스 중지

```bash
# 서비스 삭제 (비용 절약)
gcloud run services delete unwoldam-tarot-api --region=asia-northeast3

# 프로젝트 전체 삭제 (주의!)
gcloud projects delete unwoldam-tarot-api-yourname
```

---

## 🆘 문제 해결

### 배포 실패

```bash
# 빌드 로그 확인
gcloud builds list --limit=5
gcloud builds log <BUILD_ID>
```

### Health Check 실패

```bash
# 컨테이너 로그
gcloud logging read "resource.type=cloud_run_revision" --limit=100
```

### API 키 문제

```bash
# Secret 확인
gcloud secrets versions access latest --secret=anthropic-api-key

# Secret 업데이트
echo -n "new_key" | gcloud secrets versions add anthropic-api-key --data-file=-
```

---

## 📞 추가 도움말

- [GCP 빠른 시작](docs/GCP_QUICK_START.md)
- [GCP 전체 가이드](docs/GCP_DEPLOYMENT.md)
- [GCP 문서](https://cloud.google.com/run/docs)

---

**이제 시작하세요! 🚀**

```bash
# 1. gcloud CLI 설치 확인
gcloud --version

# 2. API 키 등록
./setup-secrets.sh

# 3. 배포!
./deploy-cloudrun.sh
```
