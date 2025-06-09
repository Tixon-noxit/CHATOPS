#!/bin/bash

# Скрипт подготовки сервера Ubuntu для развертывания
# Включает установку Docker, Kubernetes (kubectl), Helm и Minikube

set -e

echo "=== Обновление пакетов и установка базовых утилит ==="
sudo apt-get update && sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    net-tools \
    sudo \
    vim \
    wget \
    git \
    systemd \
    jq \
    && sudo rm -rf /var/lib/apt/lists/*

echo "=== Создание пользователя k8suser ==="
sudo groupadd docker || true  # Игнорировать ошибку если группа уже существует
sudo useradd -m k8suser -s /bin/bash 2>/dev/null || true  # Пропустить если пользователь существует
sudo usermod -aG sudo k8suser
sudo usermod -aG docker k8suser
echo 'k8suser ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/k8suser

echo "=== Установка Docker ==="
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

echo "=== Настройка Docker для пользователя ==="
sudo mkdir -p /var/run/docker.sock
sudo chown root:docker /var/run/docker.sock
sudo chmod 660 /var/run/docker.sock

echo "=== Установка kubectl ==="
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl

echo "=== Установка Helm ==="
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | sudo bash

echo "=== Установка Minikube ==="
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
rm minikube-linux-amd64

echo "=== Настройка системных параметров для Kubernetes ==="
sudo bash -c 'cat <<EOF > /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables=1
net.bridge.bridge-nf-call-ip6tables=1
EOF'
sudo sysctl --system

echo "=== Настройка завершена ==="
echo ""
echo "Для переключения на пользователя k8suser выполните:"
echo "  sudo su - k8suser"
echo ""
echo "Для запуска Minikube (после входа под k8suser):"
echo "  minikube start --driver=docker"
echo ""
echo "Проверка установки:"
echo "  docker --version"
echo "  kubectl version --client"
echo "  helm version"
echo "  minikube version"