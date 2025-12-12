# Gunicorn 설정
import multiprocessing
import os

# 워커 프로세스 수 (2GB RAM 인스턴스)
workers = 2  # 2GB면 2개 워커 운영 가능

# 워커 타임아웃 (초) - PDF 처리 시간 고려
timeout = 300  # 5분

# 워커 클래스
worker_class = 'sync'

# 메모리 누수 방지: 워커가 처리할 최대 요청 수 (이후 재시작)
max_requests = 20  # 메모리 여유 있으니 증가
max_requests_jitter = 5

# 로그 레벨
loglevel = 'info'

# 바인드 주소
bind = f"0.0.0.0:{os.environ.get('PORT', 10000)}"

# Graceful timeout
graceful_timeout = 120

# Keep alive
keepalive = 5

# Worker tmp directory (메모리 대신 디스크 사용)
worker_tmp_dir = '/dev/shm'

# 메모리 제한 (각 워커당 ~900MB)
worker_connections = 1000

