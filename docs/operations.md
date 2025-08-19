# 运维与监控

- 规格：
  - 开发/内测：2 vCPU / 4GB / 40GB（单机 Docker Compose）
  - MVP 上线：4 vCPU / 8GB / 80GB（API+Worker 分进程；DB/Redis 同机或托管）
  - 小型生产：API 2×(2C/4G) + Worker (4C/8G) + 托管 PG(4C/16G) + Redis(1–2G)
- SLO：API 可用性 ≥ 99.5%，P95 查询延迟 < 300ms（缓存命中）
- 监控：Prometheus + Grafana；日志：Loki；告警：错误率、P95、队列堆积、DB 连接、磁盘。
