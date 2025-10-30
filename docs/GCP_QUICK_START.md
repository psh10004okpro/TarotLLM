# ⚡ GCP Cloud Run 빠른 시작 가이드

**목표:** 30분 안에 배포 완료
**난이도:** ⭐ 쉬움

---

## 📋 체크리스트

배포 전 준비:
- [ ] Google 계정 (gmail)
- [ ] 신용카드 (무료 크레딧 $300 받기용)
- [ ] API 키 3개 (Anthropic, OpenAI, Google)

---

## 🚀 빠른 배포 (5단계)

### 1단계: gcloud CLI 설치 (5분)

**macOS:**
```bash
brew install --cask google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
- https://cloud.google.com/sdk/docs/install 에서 설치

**확인:**
```bash
gcloud --version
```

---

### 2단계: GCP 프로젝트 설정 (5분)

```bash
# 로그인
gcloud auth login

# 프로젝트 생성 (ID는 전역 고유해야 함)
gcloud projects create unwoldam-tarot-api-YOURNAME \
  --name="Unwoldam Tarot API"

# 프로젝트 설정
gcloud config set project unwoldam-tarot-api-YOURNAME

# 필수 API 활성화 (한 번에)
gcloud services enable \
  run.googleapis.com \
  containerregistry.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com
```

**빌링 활성화:**
- https://console.cloud.google.com/billing
- 프로젝트에 빌링 계정 연결
- **무료 크레딧 $300 자동 적용**

---

### 3단계: API 키 저장 (5분)

```bash
# Anthropic API Key
echo -n "sk-ant-YOUR_KEY" | \
  gcloud secrets create anthropic-api-key \
  --data-file=- \
  --replication-policy="automatic"

# OpenAI API Key
echo -n "sk-YOUR_KEY" | \
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

**확인:**
```bash
gcloud secrets list
```

---

### 4단계: 배포 스크립트 실행 (10-15분)

프로젝트 디렉토리에서:

```bash
# 스크립트 실행
./deploy-cloudrun.sh

# 또는 수동 배포:
gcloud builds submit --tag asia-northeast3-docker.pkg.dev/$(gcloud config get-value project)/tarot-api/unwoldam-tarot-api:latest

gcloud run deploy unwoldam-tarot-api \
  --image=asia-northeast3-docker.pkg.dev/$(gcloud config get-value project)/tarot-api/unwoldam-tarot-api:latest \
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

---

### 5단계: 테스트 (5분)

```bash
# 서비스 URL 확인
SERVICE_URL=$(gcloud run services describe unwoldam-tarot-api \
  --region=asia-northeast3 \
  --format="get(status.url)")

echo $SERVICE_URL

# Health Check
curl $SERVICE_URL/health | jq .

# Swagger UI
open $SERVICE_URL/docs
```

---

## ✅ 성공!

서비스가 다음 URL에서 실행 중입니다:
- **API**: https://unwoldam-tarot-api-xxx.a.run.app
- **Swagger**: https://unwoldam-tarot-api-xxx.a.run.app/docs
- **Health**: https://unwoldam-tarot-api-xxx.a.run.app/health

---

## 💰 비용 확인

**현재 상태 (Redis 없이):**
- ✅ Cloud Run: 무료 티어 (월 200만 요청)
- ✅ Cloud Build: 무료 티어 (월 120분)
- ✅ Artifact Registry: 무료 (10GB)

**예상 비용: $0/월** (무료 티어 범위 내)

**무료 크레딧:**
- $300 (90일)
- 무료 티어와 별도로 적용

---

## 🔄 재배포

코드 수정 후:

```bash
./deploy-cloudrun.sh
```

또는

```bash
gcloud builds submit --tag asia-northeast3-docker.pkg.dev/$(gcloud config get-value project)/tarot-api/unwoldam-tarot-api:latest

gcloud run services update unwoldam-tarot-api \
  --image=asia-northeast3-docker.pkg.dev/$(gcloud config get-value project)/tarot-api/unwoldam-tarot-api:latest \
  --region=asia-northeast3
```

---

## 📊 모니터링

**Cloud Console:**
```
https://console.cloud.google.com/run
```

**로그 확인:**
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=unwoldam-tarot-api" --limit=50
```

**실시간 로그:**
```bash
gcloud alpha logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=unwoldam-tarot-api"
```

---

## 🛑 서비스 중지

```bash
# 서비스 삭제
gcloud run services delete unwoldam-tarot-api --region=asia-northeast3

# 프로젝트 전체 삭제 (주의!)
gcloud projects delete unwoldam-tarot-api-YOURNAME
```

---

## 🆘 문제 해결

### 배포 실패
```bash
# 로그 확인
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
gcloud secrets list
gcloud secrets versions list anthropic-api-key

# Secret 업데이트
echo -n "new_key" | gcloud secrets versions add anthropic-api-key --data-file=-
```

---

## 📚 더 알아보기

- [전체 배포 가이드](./GCP_DEPLOYMENT.md)
- [모니터링 설정](./GCP_MONITORING.md)
- [GCP 문서](https://cloud.google.com/run/docs)

---

**축하합니다! 🎉 프로덕션 배포 완료!**
