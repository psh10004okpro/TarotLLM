#!/bin/bash
# =============================================================================
# GCP Cloud Run 배포 준비 스크립트
# 사용자 API 키를 Secret Manager에 등록
# =============================================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "======================================================================="
echo "  🔐 GCP Secret Manager - API 키 등록"
echo "======================================================================="
echo ""

# 1. gcloud 확인
log_info "gcloud CLI 확인 중..."
if ! command -v gcloud &> /dev/null; then
    log_error "gcloud CLI가 설치되어 있지 않습니다."
    echo ""
    echo "설치 방법:"
    echo "  macOS:   brew install --cask google-cloud-sdk"
    echo "  Linux:   curl https://sdk.cloud.google.com | bash"
    echo "  Windows: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

log_success "gcloud CLI 설치됨"
gcloud --version | head -1
echo ""

# 2. 프로젝트 확인
log_info "GCP 프로젝트 확인 중..."
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    log_warning "GCP 프로젝트가 설정되지 않았습니다."
    echo ""
    read -p "프로젝트 ID를 입력하세요 (예: unwoldam-tarot-api): " PROJECT_ID

    if [ -z "$PROJECT_ID" ]; then
        log_error "프로젝트 ID가 필요합니다."
        exit 1
    fi

    gcloud config set project $PROJECT_ID
fi

log_success "프로젝트 ID: $PROJECT_ID"
echo ""

# 3. Secret Manager API 활성화 확인
log_info "Secret Manager API 활성화 확인 중..."
if gcloud services list --enabled --filter="name:secretmanager.googleapis.com" --format="value(name)" | grep -q secretmanager; then
    log_success "Secret Manager API 활성화됨"
else
    log_warning "Secret Manager API를 활성화합니다..."
    gcloud services enable secretmanager.googleapis.com
    log_success "Secret Manager API 활성화 완료"
fi
echo ""

# 4. API 키 입력 및 등록
echo "======================================================================="
echo "  API 키 입력"
echo "======================================================================="
echo ""
echo "다음 API 키를 입력하세요. (입력 시 화면에 표시되지 않습니다)"
echo ""

# Anthropic API Key
echo "1️⃣  Anthropic API Key (Claude)"
echo "    예: sk-ant-api03-..."
read -sp "    입력: " ANTHROPIC_KEY
echo ""

if [ -z "$ANTHROPIC_KEY" ]; then
    log_warning "Anthropic API Key를 건너뜁니다."
else
    echo -n "$ANTHROPIC_KEY" | gcloud secrets create anthropic-api-key \
      --data-file=- \
      --replication-policy="automatic" 2>/dev/null || \
    echo -n "$ANTHROPIC_KEY" | gcloud secrets versions add anthropic-api-key --data-file=-
    log_success "Anthropic API Key 저장 완료"
fi
echo ""

# OpenAI API Key
echo "2️⃣  OpenAI API Key (GPT-4)"
echo "    예: sk-proj-..."
read -sp "    입력: " OPENAI_KEY
echo ""

if [ -z "$OPENAI_KEY" ]; then
    log_warning "OpenAI API Key를 건너뜁니다."
else
    echo -n "$OPENAI_KEY" | gcloud secrets create openai-api-key \
      --data-file=- \
      --replication-policy="automatic" 2>/dev/null || \
    echo -n "$OPENAI_KEY" | gcloud secrets versions add openai-api-key --data-file=-
    log_success "OpenAI API Key 저장 완료"
fi
echo ""

# Google API Key
echo "3️⃣  Google API Key (Gemini)"
echo "    예: AIzaSy..."
read -sp "    입력: " GOOGLE_KEY
echo ""

if [ -z "$GOOGLE_KEY" ]; then
    log_warning "Google API Key를 건너뜁니다."
else
    echo -n "$GOOGLE_KEY" | gcloud secrets create google-api-key \
      --data-file=- \
      --replication-policy="automatic" 2>/dev/null || \
    echo -n "$GOOGLE_KEY" | gcloud secrets versions add google-api-key --data-file=-
    log_success "Google API Key 저장 완료"
fi
echo ""

# Secret Key 자동 생성
echo "4️⃣  Secret Key (자동 생성)"
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32), end='')")
echo -n "$SECRET_KEY" | gcloud secrets create secret-key \
  --data-file=- \
  --replication-policy="automatic" 2>/dev/null || \
echo -n "$SECRET_KEY" | gcloud secrets versions add secret-key --data-file=-
log_success "Secret Key 생성 및 저장 완료"
echo ""

# 5. Secret 목록 확인
echo "======================================================================="
echo "  등록된 Secret 목록"
echo "======================================================================="
echo ""
gcloud secrets list
echo ""

# 6. 다음 단계 안내
echo "======================================================================="
echo "  ✅ API 키 등록 완료!"
echo "======================================================================="
echo ""
echo "다음 단계:"
echo ""
echo "1. 필수 API 활성화:"
echo "   gcloud services enable \\"
echo "     run.googleapis.com \\"
echo "     cloudbuild.googleapis.com \\"
echo "     artifactregistry.googleapis.com"
echo ""
echo "2. 배포 실행:"
echo "   ./deploy-cloudrun.sh"
echo ""
echo "======================================================================="
