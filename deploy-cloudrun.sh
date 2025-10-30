#!/bin/bash
# =============================================================================
# Google Cloud Run 배포 스크립트
# Unwoldam Tarot API
# =============================================================================

set -e  # 에러 발생 시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로깅 함수
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

# 배너 출력
echo "======================================================================="
echo "  🎴 Unwoldam Tarot API - Google Cloud Run 배포 스크립트"
echo "======================================================================="
echo ""

# 1. 프로젝트 ID 확인
log_info "GCP 프로젝트 확인 중..."
PROJECT_ID=$(gcloud config get-value project)

if [ -z "$PROJECT_ID" ]; then
    log_error "GCP 프로젝트가 설정되지 않았습니다."
    log_info "다음 명령어로 프로젝트를 설정하세요:"
    echo "  gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

log_success "프로젝트 ID: $PROJECT_ID"
echo ""

# 2. 리전 설정
REGION="asia-northeast3"  # 서울
log_info "배포 리전: $REGION (서울)"
echo ""

# 3. 서비스 이름
SERVICE_NAME="unwoldam-tarot-api"
log_info "서비스 이름: $SERVICE_NAME"
echo ""

# 4. 이미지 태그
IMAGE_TAG="asia-northeast3-docker.pkg.dev/$PROJECT_ID/tarot-api/$SERVICE_NAME:latest"
log_info "이미지 태그: $IMAGE_TAG"
echo ""

# 5. Redis 사용 여부 확인
read -p "Redis (Memorystore)를 사용하시겠습니까? (y/N): " use_redis
use_redis=${use_redis:-N}
echo ""

# 6. Cloud Build로 이미지 빌드
log_info "Docker 이미지 빌드 중... (약 3-5분 소요)"
gcloud builds submit --tag $IMAGE_TAG

if [ $? -ne 0 ]; then
    log_error "Docker 이미지 빌드 실패"
    exit 1
fi

log_success "Docker 이미지 빌드 완료"
echo ""

# 7. Cloud Run 배포 명령어 구성
log_info "Cloud Run 배포 중..."

DEPLOY_CMD="gcloud run deploy $SERVICE_NAME \
  --image=$IMAGE_TAG \
  --platform=managed \
  --region=$REGION \
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
  --set-secrets=SECRET_KEY=secret-key:latest"

# Redis 사용 시 추가 설정
if [[ $use_redis =~ ^[Yy]$ ]]; then
    log_info "Redis 설정 추가 중..."

    # Redis IP 가져오기
    REDIS_HOST=$(gcloud redis instances describe unwoldam-redis \
      --region=$REGION \
      --format="get(host)" 2>/dev/null || echo "")

    if [ -z "$REDIS_HOST" ]; then
        log_warning "Redis 인스턴스를 찾을 수 없습니다."
        log_info "다음 명령어로 Redis를 생성하세요:"
        echo "  gcloud redis instances create unwoldam-redis --size=1 --region=$REGION --redis-version=redis_7_0 --tier=basic"

        read -p "Redis 없이 계속 배포하시겠습니까? (y/N): " continue_without_redis
        continue_without_redis=${continue_without_redis:-N}

        if [[ ! $continue_without_redis =~ ^[Yy]$ ]]; then
            log_info "배포를 중단합니다."
            exit 1
        fi
    else
        log_success "Redis 호스트: $REDIS_HOST"
        DEPLOY_CMD="$DEPLOY_CMD \
          --set-env-vars=REDIS_URL=redis://$REDIS_HOST:6379/0 \
          --vpc-connector=tarot-connector"
    fi
fi

# 8. 배포 실행
eval $DEPLOY_CMD

if [ $? -ne 0 ]; then
    log_error "Cloud Run 배포 실패"
    exit 1
fi

log_success "Cloud Run 배포 완료"
echo ""

# 9. 서비스 URL 가져오기
log_info "서비스 URL 확인 중..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --format="get(status.url)")

log_success "서비스 URL: $SERVICE_URL"
echo ""

# 10. Health Check
log_info "Health Check 테스트 중..."
sleep 5  # 서비스가 완전히 시작될 때까지 대기

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $SERVICE_URL/health)

if [ "$HTTP_STATUS" = "200" ]; then
    log_success "Health Check 통과 (200 OK)"

    # Health Check 결과 출력
    log_info "Health Check 결과:"
    curl -s $SERVICE_URL/health | jq . || curl -s $SERVICE_URL/health
else
    log_error "Health Check 실패 (HTTP $HTTP_STATUS)"
    log_warning "로그를 확인하세요:"
    echo "  gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit=50"
fi

echo ""

# 11. 배포 완료 정보
echo "======================================================================="
echo "  ✅ 배포 완료!"
echo "======================================================================="
echo ""
echo "📍 서비스 URL:"
echo "   $SERVICE_URL"
echo ""
echo "📖 Swagger UI:"
echo "   $SERVICE_URL/docs"
echo ""
echo "🔍 Health Check:"
echo "   $SERVICE_URL/health"
echo ""
echo "📊 Cloud Console:"
echo "   https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/metrics?project=$PROJECT_ID"
echo ""
echo "📝 로그 확인:"
echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit=50"
echo ""
echo "🔄 재배포:"
echo "   ./deploy-cloudrun.sh"
echo ""
echo "======================================================================="
