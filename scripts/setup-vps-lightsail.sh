#!/usr/bin/env bash
# ==============================================================================
# Setup Script cho VPS Ubuntu (AWS Lightsail / Cloud VPS) - Dự án Vạn Phát
# Chuẩn hóa môi trường: Docker, Swap 4GB, Cloudflared, Rclone (Backup R2)
# ==============================================================================

set -euo pipefail

echo "==> 1. Cập nhật hệ thống và gói cơ bản..."
sudo apt-get update -y
sudo apt-get install -y curl wget git htop ufw rsync

echo "==> 2. Thiết lập 4GB Swapfile (chống OOM cho MariaDB & Python workers)..."
if [ ! -f /swapfile ]; then
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "Swapfile 4GB đã được kích hoạt thành công."
else
    echo "Swapfile đã tồn tại, bỏ qua."
fi

echo "==> 3. Cài đặt Docker & Docker Compose..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER"
    sudo systemctl enable docker
    sudo systemctl start docker
    echo "Docker đã được cài đặt."
else
    echo "Docker đã tồn tại."
fi

echo "==> 4. Cài đặt rclone (cho kịch bản backup R2)..."
if ! command -v rclone &> /dev/null; then
    sudo -v ; curl https://rclone.org/install.sh | sudo bash
    echo "Rclone đã cài đặt thành công."
else
    echo "Rclone đã tồn tại."
fi

echo "==> 5. Cài đặt cloudflared (Cloudflare Tunnel an toàn)..."
if ! command -v cloudflared &> /dev/null; then
    curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
    echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared bookworm main' | sudo tee /etc/apt/sources.list.d/cloudflared.list
    sudo apt-get update -y
    sudo apt-get install -y cloudflared
    echo "Cloudflared đã cài đặt thành công."
else
    echo "Cloudflared đã tồn tại."
fi

echo "==> 6. Khởi tạo thư mục dự án /opt/vanphat..."
sudo mkdir -p /opt/vanphat/infra /opt/vanphat/apps /opt/vanphat/backups
sudo chown -R "$USER:$USER" /opt/vanphat

echo "=============================================================================="
echo " HOÀN TẤT THIẾT LẬP MÔI TRƯỜNG NỀN TẢNG VPS VẠN PHÁT!"
echo " Tiếp theo: Copy nội dung thư mục infra/ lên /opt/vanphat/infra và chạy docker compose."
echo "=============================================================================="
