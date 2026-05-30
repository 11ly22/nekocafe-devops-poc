.PHONY: up down test lint scan logs ps build help

## 帮助
help:
	@echo "NekoCafe DevOps PoC - 可用命令："
	@echo "  make up      启动完整依赖栈（build + up -d）"
	@echo "  make down    停止并清理所有容器和 volume"
	@echo "  make build   仅构建镜像（不启动）"
	@echo "  make test    运行所有服务单元测试"
	@echo "  make lint    运行代码 lint（flake8 + eslint）"
	@echo "  make scan    Trivy 镜像安全扫描"
	@echo "  make logs    实时查看所有服务日志"
	@echo "  make ps      查看容器状态"

## 启动完整栈
up:
	docker compose up -d --build

## 仅构建镜像
build:
	docker compose build

## 停止并清理
down:
	docker compose down -v --remove-orphans

## 运行所有测试
test:
	@echo "==> 运行预约服务单元测试..."
	docker compose exec reservation pytest tests/ -v --tb=short
	@echo "==> 运行会员服务单元测试..."
	docker compose exec member npm test

## 代码 Lint
lint:
	@echo "==> 预约服务 Lint（flake8）..."
	docker compose exec reservation flake8 src/ tests/
	@echo "==> 会员服务 Lint（eslint）..."
	docker compose exec member npm run lint
	@echo "==> Dockerfile Lint（hadolint）..."
	hadolint services/reservation/Dockerfile
	hadolint services/member/Dockerfile

## 镜像安全扫描
scan:
	@echo "==> Trivy 扫描 reservation 镜像..."
	trivy image --severity HIGH,CRITICAL nekocafe/reservation:dev
	@echo "==> Trivy 扫描 member 镜像..."
	trivy image --severity HIGH,CRITICAL nekocafe/member:dev

## 查看日志
logs:
	docker compose logs -f reservation member

## 查看容器状态
ps:
	docker compose ps
