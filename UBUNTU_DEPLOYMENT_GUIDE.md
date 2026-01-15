# ESG-Radar Ubuntu 서버 배포 가이드

**대상**: Ubuntu 20.04 / 22.04 LTS  
**작성일**: 2026-01-15  
**난이도**: 중급

---

## 📋 목차

1. [서버 사양 요구사항](#1-서버-사양-요구사항)
2. [초기 서버 설정](#2-초기-서버-설정)
3. [프로젝트 배포](#3-프로젝트-배포)
4. [Nginx 설정](#4-nginx-설정)
5. [Systemd 서비스 등록](#5-systemd-서비스-등록)
6. [SSL 인증서 (HTTPS)](#6-ssl-인증서-https)
7. [모니터링 및 로그](#7-모니터링-및-로그)
8. [백업 및 유지보수](#8-백업-및-유지보수)
9. [문제 해결](#9-문제-해결)

---

## 1. 서버 사양 요구사항

### 최소 사양
- **CPU**: 2 vCPU
- **RAM**: 4GB
- **디스크**: 20GB SSD
- **OS**: Ubuntu 20.04 / 22.04 LTS
- **네트워크**: 공인 IP

### 권장 사양
- **CPU**: 4 vCPU
- **RAM**: 8GB
- **디스크**: 50GB SSD
- **OS**: Ubuntu 22.04 LTS
- **네트워크**: 공인 IP + 도메인

---

## 2. 초기 서버 설정

### 2.1 서버 접속

```bash
# SSH로 서버 접속
ssh root@your_server_ip

# 또는 사용자 계정으로
ssh username@your_server_ip
```

### 2.2 시스템 업데이트

```bash
# 패키지 목록 업데이트
sudo apt update

# 설치된 패키지 업그레이드
sudo apt upgrade -y

# 불필요한 패키지 제거
sudo apt autoremove -y
```

### 2.3 필수 패키지 설치

```bash
# 기본 개발 도구
sudo apt install -y build-essential git curl wget vim

# Python 3.11 설치
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# pip 설치
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.11

# Python 3.11을 기본으로 설정
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
sudo update-alternatives --config python3
```

### 2.4 방화벽 설정

```bash
# UFW 방화벽 설치 및 활성화
sudo apt install -y ufw

# SSH 포트 허용 (매우 중요! 먼저 설정)
sudo ufw allow 22/tcp

# HTTP/HTTPS 포트 허용
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 방화벽 활성화
sudo ufw enable

# 상태 확인
sudo ufw status
```

---

## 3. 프로젝트 배포

### 3.1 배포용 사용자 생성

```bash
# esg 사용자 생성
sudo adduser esg

# sudo 권한 부여
sudo usermod -aG sudo esg

# esg 사용자로 전환
su - esg
```

### 3.2 프로젝트 클론

```bash
# 홈 디렉토리로 이동
cd ~

# GitHub에서 클론
git clone https://github.com/yourusername/ESG_Detect.git

# 프로젝트 디렉토리로 이동
cd ESG_Detect

# 또는 zip 파일로 전송한 경우
# scp -r ESG_Detect esg@your_server_ip:/home/esg/
```

### 3.3 가상환경 설정

```bash
# 가상환경 생성
python3.11 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip

# 의존성 설치
pip install -r requirements.txt

# 설치 확인
pip list
```

### 3.4 환경변수 설정

```bash
# .env 파일 생성
nano .env
```

`.env` 파일 내용:
```env
# OpenAI API 키
OPENAI_API_KEY=your_openai_api_key_here

# Flask 설정
FLASK_ENV=production
SECRET_KEY=your_secret_key_here_change_this

# 서버 설정
PORT=5000
WORKERS=4

# 로그 레벨
LOG_LEVEL=INFO
```

```bash
# 파일 권한 설정 (중요!)
chmod 600 .env

# 소유자만 읽기/쓰기 가능
ls -la .env
# 결과: -rw------- 1 esg esg
```

### 3.5 uploads 디렉토리 생성

```bash
# 업로드 디렉토리 생성
mkdir -p uploads

# 권한 설정
chmod 755 uploads
```

### 3.6 테스트 실행

```bash
# 가상환경 활성화 (이미 활성화되어 있으면 생략)
source venv/bin/activate

# Flask 앱 실행 (테스트)
python app.py

# 다른 터미널에서 테스트
curl http://localhost:5000

# 정상 작동 확인 후 Ctrl+C로 중단
```

---

## 4. Nginx 설정

### 4.1 Nginx 설치

```bash
# Nginx 설치
sudo apt install -y nginx

# Nginx 시작
sudo systemctl start nginx
sudo systemctl enable nginx

# 상태 확인
sudo systemctl status nginx
```

### 4.2 Nginx 설정 파일 생성

```bash
# 설정 파일 생성
sudo nano /etc/nginx/sites-available/esg-radar
```

`/etc/nginx/sites-available/esg-radar` 내용:

```nginx
# HTTP 서버 (나중에 HTTPS로 리다이렉트)
server {
    listen 80;
    server_name esgradar-ai.com www.esgradar-ai.com;

    # 최대 업로드 크기 (100MB)
    client_max_body_size 100M;

    # 로그 파일
    access_log /var/log/nginx/esg-radar-access.log;
    error_log /var/log/nginx/esg-radar-error.log;

    # Gunicorn으로 프록시
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 타임아웃 설정 (PDF 처리 시간 고려)
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # 정적 파일 (나중에 추가 가능)
    location /static {
        alias /home/esg/ESG_Detect/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 보안 헤더
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

### 4.3 Nginx 설정 활성화

```bash
# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/esg-radar /etc/nginx/sites-enabled/

# 기본 설정 비활성화 (선택)
sudo rm /etc/nginx/sites-enabled/default

# 설정 파일 문법 검사
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
```

---

## 5. Systemd 서비스 등록

### 5.1 Systemd 서비스 파일 생성

```bash
# 서비스 파일 생성
sudo nano /etc/systemd/system/esg-radar.service
```

`/etc/systemd/system/esg-radar.service` 내용:

```ini
[Unit]
Description=ESG-Radar Gunicorn Application
After=network.target

[Service]
Type=notify
User=esg
Group=esg
RuntimeDirectory=gunicorn
WorkingDirectory=/home/esg/ESG_Detect
Environment="PATH=/home/esg/ESG_Detect/venv/bin"
EnvironmentFile=/home/esg/ESG_Detect/.env
ExecStart=/home/esg/ESG_Detect/venv/bin/gunicorn \
    -c /home/esg/ESG_Detect/gunicorn_config.py \
    app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5.2 서비스 활성화 및 시작

```bash
# systemd 데몬 리로드
sudo systemctl daemon-reload

# 서비스 시작
sudo systemctl start esg-radar

# 부팅 시 자동 시작 설정
sudo systemctl enable esg-radar

# 상태 확인
sudo systemctl status esg-radar

# 로그 확인
sudo journalctl -u esg-radar -f
```

### 5.3 서비스 관리 명령어

```bash
# 서비스 시작
sudo systemctl start esg-radar

# 서비스 중지
sudo systemctl stop esg-radar

# 서비스 재시작
sudo systemctl restart esg-radar

# 서비스 상태 확인
sudo systemctl status esg-radar

# 실시간 로그 보기
sudo journalctl -u esg-radar -f

# 최근 100줄 로그
sudo journalctl -u esg-radar -n 100

# 오늘 로그만
sudo journalctl -u esg-radar --since today
```

---

## 6. SSL 인증서 (HTTPS)

### 6.1 Certbot 설치

```bash
# Certbot 설치
sudo apt install -y certbot python3-certbot-nginx
```

### 6.2 SSL 인증서 발급

```bash
# Let's Encrypt 인증서 자동 발급 및 Nginx 설정
sudo certbot --nginx -d esgradar-ai.com -d www.esgradar-ai.com

# 이메일 입력 및 약관 동의
# Certificate is saved at: /etc/letsencrypt/live/your_domain.com/fullchain.pem
# Key is saved at:         /etc/letsencrypt/live/your_domain.com/privkey.pem
```

### 6.3 자동 갱신 설정

```bash
# 자동 갱신 테스트
sudo certbot renew --dry-run

# 자동 갱신은 systemd timer로 이미 설정됨
sudo systemctl status certbot.timer

# 수동 갱신 (필요시)
sudo certbot renew
```

### 6.4 HTTPS 설정 확인

Certbot이 자동으로 Nginx 설정을 수정합니다:

```bash
# Nginx 설정 확인
sudo nano /etc/nginx/sites-available/esg-radar
```

추가된 내용 예시:
```nginx
server {
    listen 443 ssl http2;
    server_name esgradar-ai.com www.esgradar-ai.com;

    ssl_certificate /etc/letsencrypt/live/esgradar-ai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/esgradar-ai.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # 나머지 설정...
}

# HTTP -> HTTPS 리다이렉트
server {
    listen 80;
    server_name esgradar-ai.com www.esgradar-ai.com;
    return 301 https://$server_name$request_uri;
}

# www를 메인 도메인으로 리다이렉트
server {
    listen 443 ssl http2;
    server_name www.esgradar-ai.com;
    
    ssl_certificate /etc/letsencrypt/live/esgradar-ai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/esgradar-ai.com/privkey.pem;
    
    return 301 https://esgradar-ai.com$request_uri;
}
```

---

## 7. 모니터링 및 로그

### 7.1 로그 위치

```bash
# Nginx 로그
/var/log/nginx/esg-radar-access.log  # 접속 로그
/var/log/nginx/esg-radar-error.log   # 에러 로그

# Gunicorn/Flask 로그
sudo journalctl -u esg-radar         # Systemd 로그

# 실시간 로그 모니터링
sudo tail -f /var/log/nginx/esg-radar-access.log
sudo journalctl -u esg-radar -f
```

### 7.2 로그 회전 설정

```bash
# logrotate 설정 생성
sudo nano /etc/logrotate.d/esg-radar
```

`/etc/logrotate.d/esg-radar` 내용:
```
/var/log/nginx/esg-radar-*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

### 7.3 시스템 모니터링

```bash
# 실시간 시스템 리소스 확인
htop  # 없으면 sudo apt install htop

# 디스크 사용량
df -h

# 메모리 사용량
free -h

# CPU 사용량
top

# 프로세스 확인
ps aux | grep gunicorn

# 포트 확인
sudo netstat -tulpn | grep :5000
sudo netstat -tulpn | grep :80
```

### 7.4 애플리케이션 헬스체크

```bash
# 헬스체크 스크립트 생성
nano ~/health_check.sh
```

`health_check.sh` 내용:
```bash
#!/bin/bash

# ESG-Radar 헬스체크 스크립트

echo "====== ESG-Radar Health Check ======"
echo "시간: $(date)"
echo ""

# 1. Systemd 서비스 상태
echo "1. 서비스 상태:"
systemctl is-active esg-radar
echo ""

# 2. 프로세스 확인
echo "2. Gunicorn 프로세스:"
ps aux | grep gunicorn | grep -v grep | wc -l
echo ""

# 3. 포트 확인
echo "3. 포트 5000 리스닝:"
sudo netstat -tulpn | grep :5000
echo ""

# 4. HTTP 응답 확인
echo "4. HTTP 응답 (로컬):"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:5000
echo ""

# 5. 디스크 사용량
echo "5. 디스크 사용량:"
df -h /home/esg/ESG_Detect
echo ""

# 6. 메모리 사용량
echo "6. 메모리 사용량:"
free -h
echo ""

# 7. 최근 에러 로그
echo "7. 최근 에러 (최근 10줄):"
sudo tail -n 10 /var/log/nginx/esg-radar-error.log
echo ""

echo "======================================"
```

```bash
# 실행 권한 부여
chmod +x ~/health_check.sh

# 실행
./health_check.sh
```

---

## 8. 백업 및 유지보수

### 8.1 자동 백업 스크립트

```bash
# 백업 디렉토리 생성
mkdir -p ~/backups

# 백업 스크립트 생성
nano ~/backup.sh
```

`backup.sh` 내용:
```bash
#!/bin/bash

# ESG-Radar 백업 스크립트

BACKUP_DIR=~/backups
PROJECT_DIR=~/ESG_Detect
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="esg_radar_backup_${DATE}.tar.gz"

echo "백업 시작: ${DATE}"

# 프로젝트 백업 (uploads 포함)
tar -czf ${BACKUP_DIR}/${BACKUP_FILE} \
    -C $(dirname ${PROJECT_DIR}) \
    $(basename ${PROJECT_DIR})

# 백업 파일 크기
du -h ${BACKUP_DIR}/${BACKUP_FILE}

# 7일 이상 된 백업 삭제
find ${BACKUP_DIR} -name "esg_radar_backup_*.tar.gz" -mtime +7 -delete

echo "백업 완료: ${BACKUP_FILE}"
echo "보관 중인 백업 파일:"
ls -lh ${BACKUP_DIR}
```

```bash
# 실행 권한
chmod +x ~/backup.sh

# 테스트 실행
./backup.sh
```

### 8.2 Cron 자동 백업 설정

```bash
# crontab 편집
crontab -e

# 매일 새벽 3시에 백업 실행
0 3 * * * /home/esg/backup.sh >> /home/esg/backup.log 2>&1
```

### 8.3 코드 업데이트 절차

```bash
# 1. 프로젝트 디렉토리로 이동
cd ~/ESG_Detect

# 2. 백업 먼저!
~/backup.sh

# 3. Git pull (또는 파일 전송)
git pull origin main

# 또는 scp로 파일 전송
# scp -r new_files/* esg@your_server_ip:/home/esg/ESG_Detect/

# 4. 의존성 업데이트 (requirements.txt 변경 시)
source venv/bin/activate
pip install -r requirements.txt

# 5. 서비스 재시작
sudo systemctl restart esg-radar

# 6. 상태 확인
sudo systemctl status esg-radar

# 7. 로그 확인 (에러 없는지)
sudo journalctl -u esg-radar -n 50
```

---

## 9. 문제 해결

### 9.1 서비스가 시작되지 않음

```bash
# 상세 로그 확인
sudo journalctl -u esg-radar -n 100 --no-pager

# 일반적인 원인:
# 1. .env 파일 누락
ls -la /home/esg/ESG_Detect/.env

# 2. 가상환경 경로 오류
which gunicorn  # /home/esg/ESG_Detect/venv/bin/gunicorn

# 3. 포트 충돌
sudo netstat -tulpn | grep :5000
sudo lsof -i :5000

# 4. 권한 문제
ls -la /home/esg/ESG_Detect/
```

### 9.2 502 Bad Gateway (Nginx)

```bash
# Gunicorn이 실행 중인지 확인
sudo systemctl status esg-radar

# 포트 5000이 열려있는지
sudo netstat -tulpn | grep :5000

# Gunicorn 로그 확인
sudo journalctl -u esg-radar -f

# Nginx 에러 로그
sudo tail -f /var/log/nginx/esg-radar-error.log
```

### 9.3 파일 업로드 실패

```bash
# uploads 디렉토리 권한 확인
ls -ld /home/esg/ESG_Detect/uploads
# drwxr-xr-x 2 esg esg

# 권한 수정 (필요시)
chmod 755 /home/esg/ESG_Detect/uploads

# Nginx client_max_body_size 확인
sudo grep -r "client_max_body_size" /etc/nginx/

# 디스크 공간 확인
df -h
```

### 9.4 메모리 부족

```bash
# 현재 메모리 사용량
free -h

# Gunicorn worker 수 줄이기
nano /home/esg/ESG_Detect/gunicorn_config.py
# workers = 2  # 4 -> 2로 줄임

# 서비스 재시작
sudo systemctl restart esg-radar

# 스왑 메모리 추가 (임시 해결)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 9.5 OpenAI API 오류

```bash
# .env 파일 확인
cat /home/esg/ESG_Detect/.env | grep OPENAI_API_KEY

# API 키 테스트
python3 << EOF
import os
from dotenv import load_dotenv
load_dotenv()
print(f"API Key: {os.getenv('OPENAI_API_KEY')[:10]}...")
EOF

# 네트워크 연결 확인
curl https://api.openai.com/v1/models -H "Authorization: Bearer YOUR_API_KEY"
```

---

## 10. 빠른 배포 스크립트 (올인원)

서버에 처음 배포할 때 사용할 수 있는 자동화 스크립트입니다.

```bash
# deploy.sh 생성
nano ~/deploy.sh
```

`deploy.sh` 내용:

```bash
#!/bin/bash

set -e  # 에러 발생 시 중단

echo "======================================"
echo "ESG-Radar 서버 배포 스크립트"
echo "======================================"
echo ""

# 색상 코드
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 변수 설정
PROJECT_NAME="ESG_Detect"
DOMAIN="esgradar-ai.com"
OPENAI_KEY="your_openai_api_key"  # 수정 필요

# 1. 시스템 업데이트
echo -e "${GREEN}[1/10] 시스템 업데이트...${NC}"
sudo apt update && sudo apt upgrade -y

# 2. Python 3.11 설치
echo -e "${GREEN}[2/10] Python 3.11 설치...${NC}"
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.11

# 3. 필수 패키지 설치
echo -e "${GREEN}[3/10] 필수 패키지 설치...${NC}"
sudo apt install -y build-essential git nginx

# 4. 방화벽 설정
echo -e "${GREEN}[4/10] 방화벽 설정...${NC}"
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
echo "y" | sudo ufw enable

# 5. 프로젝트 클론 (이미 있으면 스킵)
echo -e "${GREEN}[5/10] 프로젝트 설정...${NC}"
if [ ! -d "$HOME/$PROJECT_NAME" ]; then
    git clone https://github.com/yourusername/$PROJECT_NAME.git
fi
cd $HOME/$PROJECT_NAME

# 6. 가상환경 및 의존성
echo -e "${GREEN}[6/10] Python 의존성 설치...${NC}"
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 7. 환경변수 설정
echo -e "${GREEN}[7/10] 환경변수 설정...${NC}"
cat > .env << EOF
OPENAI_API_KEY=${OPENAI_KEY}
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
PORT=5000
WORKERS=4
LOG_LEVEL=INFO
EOF
chmod 600 .env

mkdir -p uploads
chmod 755 uploads

# 8. Systemd 서비스
echo -e "${GREEN}[8/10] Systemd 서비스 등록...${NC}"
sudo tee /etc/systemd/system/esg-radar.service > /dev/null << EOF
[Unit]
Description=ESG-Radar Gunicorn Application
After=network.target

[Service]
Type=notify
User=$USER
Group=$USER
RuntimeDirectory=gunicorn
WorkingDirectory=$HOME/$PROJECT_NAME
Environment="PATH=$HOME/$PROJECT_NAME/venv/bin"
EnvironmentFile=$HOME/$PROJECT_NAME/.env
ExecStart=$HOME/$PROJECT_NAME/venv/bin/gunicorn -c $HOME/$PROJECT_NAME/gunicorn_config.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable esg-radar
sudo systemctl start esg-radar

# 9. Nginx 설정
echo -e "${GREEN}[9/10] Nginx 설정...${NC}"
sudo tee /etc/nginx/sites-available/esg-radar > /dev/null << EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};
    client_max_body_size 100M;

    access_log /var/log/nginx/esg-radar-access.log;
    error_log /var/log/nginx/esg-radar-error.log;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/esg-radar /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 10. 상태 확인
echo -e "${GREEN}[10/10] 배포 완료! 상태 확인...${NC}"
echo ""
echo "======================================"
echo "Systemd 서비스 상태:"
sudo systemctl status esg-radar --no-pager
echo ""
echo "Nginx 상태:"
sudo systemctl status nginx --no-pager
echo ""
echo "포트 확인:"
sudo netstat -tulpn | grep :5000
echo ""
echo "======================================"
echo -e "${GREEN}배포 완료!${NC}"
echo "접속 주소: http://${DOMAIN}"
echo ""
echo "다음 단계:"
echo "1. 도메인 DNS 설정: A 레코드를 서버 IP로 지정"
echo "2. SSL 인증서 발급: sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
echo ""
echo "로그 확인: sudo journalctl -u esg-radar -f"
echo "======================================"
```

```bash
# 실행 권한 부여
chmod +x ~/deploy.sh

# 스크립트 실행 전에 변수 수정!
nano ~/deploy.sh
# DOMAIN과 OPENAI_KEY 수정

# 실행
./deploy.sh
```

---

## 11. 체크리스트

배포 후 확인사항:

### ✅ 서비스 상태
- [ ] `sudo systemctl status esg-radar` → active (running)
- [ ] `sudo systemctl status nginx` → active (running)
- [ ] `sudo netstat -tulpn | grep :5000` → gunicorn 리스닝
- [ ] `sudo netstat -tulpn | grep :80` → nginx 리스닝

### ✅ 접속 테스트
- [ ] `curl http://localhost:5000` → HTML 응답
- [ ] `curl http://your_domain.com` → HTML 응답
- [ ] 브라우저에서 `http://your_domain.com` 접속

### ✅ 기능 테스트
- [ ] PDF 업로드 → 정상 처리
- [ ] 기본 검토 → 결과 출력
- [ ] Pre-Assurance 분석 → 대시보드 표시

### ✅ 보안
- [ ] `.env` 파일 권한 600
- [ ] 방화벽 활성화 (ufw)
- [ ] SSL 인증서 설치 (HTTPS)

### ✅ 백업
- [ ] 백업 스크립트 작동
- [ ] Cron 자동 백업 설정

---

## 12. 유용한 명령어 모음

```bash
# 서비스 관리
sudo systemctl start esg-radar
sudo systemctl stop esg-radar
sudo systemctl restart esg-radar
sudo systemctl status esg-radar
sudo journalctl -u esg-radar -f

# Nginx 관리
sudo systemctl restart nginx
sudo nginx -t
sudo tail -f /var/log/nginx/esg-radar-access.log

# 프로세스 확인
ps aux | grep gunicorn
ps aux | grep nginx

# 포트 확인
sudo netstat -tulpn | grep :5000
sudo netstat -tulpn | grep :80

# 리소스 모니터링
htop
free -h
df -h

# 백업
~/backup.sh

# 헬스체크
~/health_check.sh
```

---

## 📞 문제 발생 시

1. **로그 확인**
   ```bash
   sudo journalctl -u esg-radar -n 100
   sudo tail -f /var/log/nginx/esg-radar-error.log
   ```

2. **서비스 재시작**
   ```bash
   sudo systemctl restart esg-radar
   sudo systemctl restart nginx
   ```

3. **헬스체크 실행**
   ```bash
   ~/health_check.sh
   ```

4. **백업에서 복구**
   ```bash
   cd ~
   tar -xzf backups/esg_radar_backup_YYYYMMDD_HHMMSS.tar.gz
   sudo systemctl restart esg-radar
   ```

---

**배포 성공하면 접속 주소**: `https://esgradar-ai.com` 🚀

