# 部署（容器化示例 / Ubuntu 24.04 基线）

根目录提供 docker-compose.yml 与 .env.example：

- 服务：api、web、worker、db(Postgres16)、redis(7)
- 环境变量：DATABASE_URL、REDIS_URL、JWT_SECRET、ALLOW_CONTENT_ANALYSIS、CACHE_TTL_SECONDS

系统基线：Ubuntu 24.04.1 LTS (GNU/Linux 6.8 x86_64)

先决条件：
- 已安装 Docker Engine 与 Docker Compose Plugin（或 docker-compose）
- 已配置磁盘与开放端口（默认 3000/8000/5432/6379，可按需调整）

快速启动（示例）：
1. 复制环境变量样例为实际 `.env`
2. 启动编排

可选命令（供参考）：
```
docker compose pull
docker compose build --no-cache
docker compose up -d
docker compose logs -f --tail=200
```

注意：当前仓库包含 API 的最小骨架（FastAPI），web/worker 将按路线图补齐。
