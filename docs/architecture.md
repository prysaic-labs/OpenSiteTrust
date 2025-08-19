# 技术架构

两条路线（可混合）：

## A. Serverless 极速落地
- 前端：UniApp H5
- 后端：uniCloud 云函数（Node）
- 数据库：云数据库（Mongo-like）
- 缓存/限流：云缓存或内置
- 优点：0 运维，上线快；缺点：后期灵活性弱

## B. 可控容器化（推荐）
- 前端：Next.js / UniApp H5
- API：FastAPI（Python）或 NestJS（Node）
- Worker：Celery/RQ（Python）或 BullMQ（Node）
- 数据库：PostgreSQL
- 缓存：Redis（缓存 + 限流 + 队列）
- 代理：Caddy/Nginx；CDN/WAF：Cloudflare

开发最小机：2 vCPU / 4GB / 40GB；MVP 上线：4 vCPU / 8GB / 80GB。
