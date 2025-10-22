# مستندات مانیتورینگ و لاگ‌گذاری

این سند سیستم مانیتورینگ، لاگ‌گذاری و هشدارها در سیستم Writers را توضیح می‌دهد.

## 🎯 نمای کلی

سیستم Writers از یک Stack کامل برای مانیتورینگ و لاگ‌گذاری استفاده می‌کند:

- **Prometheus**: جمع‌آوری و ذخیره متریک‌ها
- **Grafana**: نمایش بصری داده‌ها
- **Loki**: جمع‌آوری و query لاگ‌ها
- **Promtail**: ارسال لاگ‌ها به Loki
- **Alertmanager**: مدیریت هشدارها
- **Exporters**: جمع‌آوری متریک‌های مختلف

## 🔧 نصب و راه‌اندازی

### راه‌اندازی با Docker Compose

```bash
cd infrastructure

# راه‌اندازی monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# یا استفاده از اسکریپت
sudo bash scripts/setup-monitoring.sh
```

### دسترسی به Dashboardها

پس از راه‌اندازی:

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **Alertmanager**: http://localhost:9093

## 📊 Prometheus

### متریک‌های جمع‌آوری شده

#### متریک‌های Application (FastAPI)

```python
# در backend/app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

متریک‌های موجود:

```
# HTTP Requests
http_requests_total{method="GET", path="/api/tasks", status="200"}

# Request Duration
http_request_duration_seconds_bucket{le="0.1", method="GET", path="/api/tasks"}

# In-Progress Requests
http_requests_inprogress{method="GET", path="/api/tasks"}
```

#### متریک‌های سیستم (Node Exporter)

```
# CPU
node_cpu_seconds_total
node_load1
node_load5
node_load15

# Memory
node_memory_MemTotal_bytes
node_memory_MemAvailable_bytes
node_memory_MemFree_bytes

# Disk
node_filesystem_avail_bytes
node_filesystem_size_bytes
node_disk_io_time_seconds_total

# Network
node_network_receive_bytes_total
node_network_transmit_bytes_total
```

#### متریک‌های PostgreSQL

```
# Connections
pg_stat_database_numbackends

# Transactions
pg_stat_database_xact_commit
pg_stat_database_xact_rollback

# Locks
pg_locks_count

# Database Size
pg_database_size_bytes
```

#### متریک‌های Redis

```
# Memory
redis_memory_used_bytes
redis_memory_max_bytes

# Commands
redis_commands_processed_total
redis_commands_duration_seconds_total

# Keys
redis_db_keys
redis_db_keys_expiring

# Connections
redis_connected_clients
```

### Query‌های مفید Prometheus

```promql
# نرخ درخواست‌های HTTP
rate(http_requests_total[5m])

# متوسط زمان پاسخ
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

# نرخ خطا
rate(http_requests_total{status=~"5.."}[5m])

# استفاده از CPU
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# استفاده از RAM
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100

# فضای دیسک باقی‌مانده
(node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100
```

### پیکربندی Prometheus

فایل `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'writers-cluster'
    environment: 'production'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

# Load rules
rule_files:
  - '/etc/prometheus/alerts/*.yml'

# Scrape configurations
scrape_configs:
  # Backend metrics
  - job_name: 'writers-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  # Node Exporter (system metrics)
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # PostgreSQL Exporter
  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Redis Exporter
  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']

  # Nginx Exporter
  - job_name: 'nginx-exporter'
    static_configs:
      - targets: ['nginx-exporter:9113']
```

## 📈 Grafana

### ورود اولیه

1. دسترسی به http://localhost:3001
2. ورود با admin/admin
3. تغییر رمز عبور

### Datasources

Datasource‌های زیر به صورت خودکار تنظیم می‌شوند:

#### Prometheus
```yaml
name: Prometheus
type: prometheus
url: http://prometheus:9090
access: proxy
isDefault: true
```

#### Loki
```yaml
name: Loki
type: loki
url: http://loki:3100
access: proxy
```

### Dashboards آماده

#### 1. System Overview Dashboard

متریک‌های نمایش داده شده:
- CPU Usage
- Memory Usage
- Disk Space
- Network Traffic
- System Load

```json
{
  "dashboard": {
    "title": "System Overview",
    "panels": [
      {
        "title": "CPU Usage",
        "targets": [
          {
            "expr": "100 - (avg(irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
          }
        ]
      }
    ]
  }
}
```

#### 2. Application Performance Dashboard

متریک‌های نمایش داده شده:
- Request Rate
- Response Time (p50, p95, p99)
- Error Rate
- Active Requests

#### 3. Database Performance Dashboard

متریک‌های نمایش داده شده:
- Active Connections
- Transaction Rate
- Query Duration
- Database Size
- Cache Hit Ratio

#### 4. Redis Performance Dashboard

متریک‌های نمایش داده شده:
- Memory Usage
- Commands/sec
- Hit Rate
- Connected Clients
- Key Count

### ایجاد Dashboard سفارشی

```bash
# Export dashboard
curl -H "Authorization: Bearer <api_key>" \
  http://localhost:3001/api/dashboards/uid/<dashboard_uid> > dashboard.json

# Import dashboard
curl -X POST \
  -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" \
  -d @dashboard.json \
  http://localhost:3001/api/dashboards/db
```

## 📝 Loki (Log Aggregation)

### پیکربندی Loki

فایل `loki-config.yml`:

```yaml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2024-01-01
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/index
    cache_location: /loki/cache
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: true
  retention_period: 168h
```

### Promtail (Log Collector)

فایل `promtail-config.yml`:

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  # Backend logs
  - job_name: writers-backend
    static_configs:
      - targets:
          - localhost
        labels:
          job: writers-backend
          __path__: /var/log/writers/backend/*.log

  # Frontend logs
  - job_name: writers-frontend
    static_configs:
      - targets:
          - localhost
        labels:
          job: writers-frontend
          __path__: /var/log/writers/frontend/*.log

  # Worker logs
  - job_name: writers-worker
    static_configs:
      - targets:
          - localhost
        labels:
          job: writers-worker
          __path__: /var/log/writers/worker/*.log

  # Nginx logs
  - job_name: nginx
    static_configs:
      - targets:
          - localhost
        labels:
          job: nginx
          __path__: /var/log/nginx/*log
```

### Query‌های مفید Loki

```logql
# تمام لاگ‌های Backend
{job="writers-backend"}

# لاگ‌های خطا
{job="writers-backend"} |= "ERROR"

# لاگ‌های با pattern خاص
{job="writers-backend"} |~ "user.*login"

# تعداد خطاها در 5 دقیقه اخیر
sum(count_over_time({job="writers-backend"} |= "ERROR" [5m]))

# نرخ خطا
rate({job="writers-backend"} |= "ERROR" [5m])

# لاگ‌های JSON parsed
{job="writers-backend"} | json | level="error"
```

## 🚨 Alertmanager

### پیکربندی Alertmanager

فایل `alertmanager.yml`:

```yaml
global:
  resolve_timeout: 5m
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@yourdomain.com'
  smtp_auth_username: 'alerts@yourdomain.com'
  smtp_auth_password: 'your_password'

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'email-notifications'
  
  routes:
    # Critical alerts -> immediate notification
    - match:
        severity: critical
      receiver: 'critical-notifications'
      continue: true
    
    # Warning alerts -> grouped notification
    - match:
        severity: warning
      receiver: 'warning-notifications'
      group_wait: 30s

receivers:
  - name: 'email-notifications'
    email_configs:
      - to: 'team@yourdomain.com'
        headers:
          Subject: '[Writers] Alert: {{ .GroupLabels.alertname }}'

  - name: 'critical-notifications'
    email_configs:
      - to: 'oncall@yourdomain.com'
        headers:
          Subject: '[CRITICAL] {{ .GroupLabels.alertname }}'
    # Slack webhook (optional)
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
        title: 'Critical Alert'

  - name: 'warning-notifications'
    email_configs:
      - to: 'team@yourdomain.com'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'cluster', 'service']
```

### قوانین هشدار (Alert Rules)

فایل `alerts/application.yml`:

```yaml
groups:
  - name: application_alerts
    interval: 30s
    rules:
      # High Error Rate
      - alert: HighErrorRate
        expr: |
          (sum(rate(http_requests_total{status=~"5.."}[5m])) by (job)
          /
          sum(rate(http_requests_total[5m])) by (job)) * 100 > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "{{ $labels.job }} has error rate of {{ $value }}%"

      # High Response Time
      - alert: HighResponseTime
        expr: |
          histogram_quantile(0.95, 
            rate(http_request_duration_seconds_bucket[5m])
          ) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time"
          description: "95th percentile response time is {{ $value }}s"

      # Service Down
      - alert: ServiceDown
        expr: up{job=~"writers-.*"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"
          description: "{{ $labels.job }} has been down for more than 1 minute"
```

فایل `alerts/infrastructure.yml`:

```yaml
groups:
  - name: infrastructure_alerts
    interval: 30s
    rules:
      # High CPU Usage
      - alert: HighCPUUsage
        expr: |
          100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value }}% on {{ $labels.instance }}"

      # High Memory Usage
      - alert: HighMemoryUsage
        expr: |
          (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) 
          / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}% on {{ $labels.instance }}"

      # Critical Memory Usage
      - alert: CriticalMemoryUsage
        expr: |
          (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) 
          / node_memory_MemTotal_bytes * 100 > 95
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Critical memory usage"
          description: "Memory usage is {{ $value }}% on {{ $labels.instance }}"

      # Low Disk Space
      - alert: LowDiskSpace
        expr: |
          (node_filesystem_avail_bytes{mountpoint="/"} 
          / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 20
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space"
          description: "Only {{ $value }}% disk space available on {{ $labels.instance }}"

      # Critical Disk Space
      - alert: CriticalDiskSpace
        expr: |
          (node_filesystem_avail_bytes{mountpoint="/"} 
          / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 10
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Critical disk space"
          description: "Only {{ $value }}% disk space available on {{ $labels.instance }}"
```

## 📊 Logging Best Practices

### ساختار Log در Backend

```python
import logging
import json
from datetime import datetime

# تنظیمات logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/writers/backend/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Structured logging
def log_event(event_type: str, data: dict):
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'data': data
    }
    logger.info(json.dumps(log_data))

# استفاده
log_event('user_login', {
    'user_id': 123,
    'ip': '192.168.1.1',
    'success': True
})
```

### Log Levels

- **DEBUG**: اطلاعات تفصیلی برای debugging
- **INFO**: رویدادهای عادی (login, logout, etc.)
- **WARNING**: موارد غیرعادی که نیاز به توجه دارند
- **ERROR**: خطاهای قابل handle
- **CRITICAL**: خطاهای جدی که نیاز به اقدام فوری دارند

## 🔍 Dashboard‌های پیشرفته

### SLI/SLO Dashboard

```yaml
# Service Level Indicators
panels:
  - title: "Availability (SLI)"
    expr: |
      (sum(rate(http_requests_total{status!~"5.."}[30d])) 
      / sum(rate(http_requests_total[30d]))) * 100
    target: 99.9  # SLO

  - title: "Latency (SLI)"
    expr: |
      histogram_quantile(0.95, 
        rate(http_request_duration_seconds_bucket[30d])
      )
    target: 0.5  # 500ms SLO
```

### Business Metrics Dashboard

```yaml
panels:
  - title: "Daily Active Users"
    expr: count(count_over_time({job="writers-backend"} |= "user_login" [24h]))

  - title: "Tasks Created"
    expr: sum(increase(http_requests_total{path="/api/tasks", method="POST"}[24h]))

  - title: "Files Processed"
    expr: sum(increase(celery_task_success_total{task="process_file"}[24h]))
```

## 🔗 Integration با CI/CD

```yaml
# در .github/workflows/deploy.yml
- name: Check Service Health
  run: |
    curl -f http://localhost:8000/health || exit 1
    
- name: Check Prometheus Targets
  run: |
    curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health!="up")'
    
- name: Alert on Deploy
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Deployment completed'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## 📝 نکات مهم

1. **Retention Policy را تنظیم کنید**
   - Prometheus: 15-30 روز
   - Loki: 7-14 روز
   - Long-term storage با Thanos یا Cortex

2. **Alert Fatigue را مدیریت کنید**
   - فقط alert‌های مهم را فعال کنید
   - از Grouping و Inhibition استفاده کنید

3. **Dashboard‌ها را سازمان‌دهی کنید**
   - یک Dashboard کلی برای Overview
   - Dashboard‌های جداگانه برای هر سرویس

4. **Log Sampling برای Production**
   - همه لاگ‌ها را log نکنید
   - از sampling برای high-volume logs استفاده کنید

---

برای اطلاعات بیشتر، به مستندات رسمی [Prometheus](https://prometheus.io/docs/), [Grafana](https://grafana.com/docs/), و [Loki](https://grafana.com/docs/loki/) مراجعه کنید.
