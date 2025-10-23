#!/bin/bash
# =============================================================================
# Celery Worker Entrypoint Script
# =============================================================================
# این اسکریپت Celery Worker را با تنظیمات بهینه برای پردازش صوتی راه‌اندازی می‌کند
#
# استفاده:
#   ./entrypoint.sh
#
# متغیرهای محیطی:
#   WORKER_CONCURRENCY: تعداد worker process های همزمان (پیش‌فرض: 2)
#   WORKER_QUEUE: صف(های) مورد نظر برای پردازش (پیش‌فرض: media)
#   WORKER_LOG_LEVEL: سطح لاگ (پیش‌فرض: info)
#   WORKER_MAX_TASKS_PER_CHILD: حداکثر task قبل از restart worker (پیش‌فرض: 100)
# =============================================================================

set -e

# تنظیمات پیش‌فرض
WORKER_CONCURRENCY=${WORKER_CONCURRENCY:-2}
WORKER_QUEUE=${WORKER_QUEUE:-media}
WORKER_LOG_LEVEL=${WORKER_LOG_LEVEL:-info}
WORKER_MAX_TASKS_PER_CHILD=${WORKER_MAX_TASKS_PER_CHILD:-100}

# تنظیمات مدل (برای بهینه‌سازی warm start)
MODEL_DEVICE=${MODEL_DEVICE:-cuda}
MODEL_DEVICE_INDEX=${MODEL_DEVICE_INDEX:-0}
MODEL_COMPUTE_TYPE=${MODEL_COMPUTE_TYPE:-float16}
MODEL_NAME=${MODEL_NAME:-base}

# تنظیمات مانیتورینگ منابع
ENABLE_RESOURCE_MONITORING=${ENABLE_RESOURCE_MONITORING:-true}
VRAM_WARNING_THRESHOLD=${VRAM_WARNING_THRESHOLD:-0.85}
RAM_WARNING_THRESHOLD=${RAM_WARNING_THRESHOLD:-0.90}

# نمایش تنظیمات
echo "==============================================================================="
echo "Starting Celery Worker with following configuration:"
echo "==============================================================================="
echo "Concurrency:              $WORKER_CONCURRENCY worker processes"
echo "Queue(s):                 $WORKER_QUEUE"
echo "Log Level:                $WORKER_LOG_LEVEL"
echo "Max Tasks per Child:      $WORKER_MAX_TASKS_PER_CHILD"
echo ""
echo "Model Configuration:"
echo "  Device:                 $MODEL_DEVICE:$MODEL_DEVICE_INDEX"
echo "  Compute Type:           $MODEL_COMPUTE_TYPE"
echo "  Model Name:             $MODEL_NAME"
echo ""
echo "Resource Monitoring:"
echo "  Enabled:                $ENABLE_RESOURCE_MONITORING"
echo "  VRAM Warning Threshold: ${VRAM_WARNING_THRESHOLD} (${VRAM_WARNING_THRESHOLD}*100%)"
echo "  RAM Warning Threshold:  ${RAM_WARNING_THRESHOLD} (${RAM_WARNING_THRESHOLD}*100%)"
echo "==============================================================================="
echo ""

# اطمینان از وجود دایرکتوری‌های لازم
mkdir -p /storage/uploads /storage/results /storage/models

# بررسی دسترسی به GPU (در صورت استفاده از CUDA)
if [ "$MODEL_DEVICE" = "cuda" ]; then
    echo "Checking NVIDIA GPU availability..."
    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi --query-gpu=index,name,memory.total --format=csv
        echo ""
    else
        echo "Warning: nvidia-smi not found. GPU may not be available."
        echo "Consider setting MODEL_DEVICE=cpu if GPU is not available."
        echo ""
    fi
fi

# نمایش اطلاعات سیستم
echo "System Information:"
echo "  CPU Count: $(nproc)"
echo "  Total RAM: $(free -h | awk '/^Mem:/ {print $2}')"
echo ""

# راه‌اندازی Celery Worker
echo "Starting Celery Worker..."
echo ""

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=${PROJECT_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}

cd "$PROJECT_ROOT/backend"

exec celery -A app.celery_app worker \
    --loglevel=$WORKER_LOG_LEVEL \
    --concurrency=$WORKER_CONCURRENCY \
    --queues=$WORKER_QUEUE \
    --max-tasks-per-child=$WORKER_MAX_TASKS_PER_CHILD \
    --task-events \
    --without-gossip \
    --without-mingle \
    --without-heartbeat

# =============================================================================
# راهنمای انتخاب مقدار Concurrency
# =============================================================================
#
# مقدار --concurrency تعداد worker process های همزمان را مشخص می‌کند که
# می‌توانند به صورت موازی task ها را اجرا کنند.
#
# توصیه‌های انتخاب مقدار:
#
# 1. برای مدل‌های سنگین (Large/Medium Whisper):
#    - GPU: concurrency=1 یا 2
#    - دلیل: مدل‌های بزرگ حافظه GPU زیادی مصرف می‌کنند
#    - با concurrency بالا ریسک OOM (Out of Memory) افزایش می‌یابد
#
# 2. برای مدل‌های سبک (Tiny/Base Whisper):
#    - GPU: concurrency=2 تا 4
#    - CPU: concurrency=(تعداد CPU cores) / 2
#    - دلیل: مدل‌های کوچک حافظه کمتری نیاز دارند
#
# 3. برای سیستم‌های Multi-GPU:
#    - می‌توانید چندین worker با MODEL_DEVICE_INDEX متفاوت اجرا کنید
#    - مثال: worker1 با GPU:0، worker2 با GPU:1
#
# 4. ملاحظات عمومی:
#    - VRAM موجود: بررسی کنید که حافظه GPU کافی است
#    - RAM سیستم: هر worker حدود 2-4GB RAM نیاز دارد
#    - I/O: برای فایل‌های بزرگ، concurrency پایین‌تر بهتر است
#
# 5. فرمول تخمینی:
#    concurrency = min(
#        GPU_VRAM_GB / MODEL_SIZE_GB,
#        CPU_CORES / 2,
#        MAX_CONCURRENT_TASKS
#    )
#
# 6. نمونه تنظیمات:
#    - GPU با 8GB VRAM + Whisper Base: concurrency=2
#    - GPU با 16GB VRAM + Whisper Medium: concurrency=2
#    - GPU با 24GB VRAM + Whisper Large: concurrency=1 یا 2
#    - CPU با 16 cores + Whisper Base: concurrency=4
#
# توجه: همیشه با مقدار پایین شروع کنید و با مانیتورینگ منابع،
# به تدریج افزایش دهید تا به مقدار بهینه برسید.
#
# =============================================================================
