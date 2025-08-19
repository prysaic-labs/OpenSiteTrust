# OpenSiteTrust（中文）

[opensitetrust.com](https://opensitetrust.com) · 版本：v0.11 · 默认项目语言：英文（本页为中文说明）

用“规则 + 社区 + 透明解释”为网站打 0–100 分的多维风险/可信度评分，提供开放 API 与网页端 UI（浏览器扩展与论坛为后续计划）。

> 状态：v0.11 提供可用 API 与 UI，含缓存与持久化、丰富探测项、动态评分、基础多语言。

## 这是啥？

OpenSiteTrust 是一个开源、可解释、可复用的网站评分生态。我们以四个维度合成总分，并提供证据卡片：
- S 安全（HTTPS 行为与安全响应头、TLS 证书到期、DNSSEC）
- C 可信（域名启发式、可选 Google Safe Browsing v4、轻量 SEO 存在）
- T 透明（隐私/条款/关于/联系、imprint/impressum、security page、漏洞赏金、安全.txt、humans.txt）
- U 社区/用户（Wilson 置信下界；无投票时剔除；少量投票时平滑）

用途：
- 用户：一眼看到分数与绿/黄/红条，并可查看“原因”。
- 创作者/媒体：快速判断来源可信度。
- 研究者/开发者：开放 API 与可复用数据。
- 站点方：申诉与改善透明信号。

## v0.11 范围

- 评分引擎 + 解释（Redis 缓存，PostgreSQL 持久化）
- 开放 API：
  - GET /v1/sites/{host}
  - GET /v1/sites/{host}/explain
  - POST /v1/votes
- Web UI（Next.js + Tailwind + 类 shadcn 组件），基础 i18n 通过 `?lang=`（默认 en，可选 zh/ja/es）
- 反向代理与部署：Caddy + Docker Compose

## 探测与评分细节

- 安全：
  - HTTPS/HTTP 行为与关键安全响应头
    （HSTS、CSP、X-Content-Type-Options、X-Frame-Options、
    Referrer-Policy、Permissions-Policy）
  - TLS 证书剩余天数
  - DNSSEC（是否存在 DS 记录）
- 可信：
  - 域名启发式
  - 可选 Google Safe Browsing v4（设置 `GOOGLE_SAFE_BROWSING_API_KEY` 后启用；
    支持“纯 key”或“带 `?key=` 的完整 API URL”）
  - 轻量 SEO：title、meta description、canonical、robots.txt / meta robots、
    Open Graph、JSON-LD、sitemap.xml
- 透明：
  - 隐私、条款、关于、联系
  - imprint/impressum、security page、bug bounty、安全.txt、humans.txt
- 社区（U）：
  - 无用户评分：界面显示 0 且“暂无评价”，并从总分中剔除 U（S/C/T 权重等比重分）
  - 有少量评分：先用 Wilson 下界得到 U_raw，再进行两步处理：
    1) 向基线平滑：`COMMUNITY_BASELINE`（默认 0.5）
    2) 权重爬升：`COMMUNITY_RAMP_N`（默认若干票内逐步放大 U 权重）

## i18n 与输入规范

- 默认界面语言是英文；可通过 `?lang=en|zh|zh-Hant|ja|es` 切换。
- UI 与 API 均支持输入完整 URL（例：`https://opensitetrust.com/v1/health`），
  系统会自动规范化并提取 host。

## 部署

- 参考 docs/deployment.md；根目录提供 `docker-compose.yml` 与 `.env.example`。
- 环境变量（.env）示例：
  - `DATABASE_URL`、`REDIS_URL`、`JWT_SECRET`
  - `GOOGLE_SAFE_BROWSING_API_KEY=`（可留空；留空不启用 GSB；可填“原始 key”或
    “带 ?key= 的完整 API URL”）
  - `COMMUNITY_RAMP_N`、`COMMUNITY_BASELINE`（可选，用于 U 平滑与权重爬升）
- Compose 注意：`GOOGLE_SAFE_BROWSING_API_KEY` 已位于 `api.environment` 与
  `worker.environment` 下；未设置时不会导致 YAML 解析错误。

## 隐私、安全与风控

详见 docs/privacy-security.md（数据最小化、k-匿名、XSS/CSRF、签名快照、限流与
信誉加权）。

## 开源与许可

- 后端/评分引擎：AGPL-3.0
- 插件/SDK：Apache-2.0
- 用户标注数据：CC BY-SA 4.0

## 贡献

- 请阅读 CONTRIBUTING.md、CODE_OF_CONDUCT.md；安全问题参见 SECURITY.md。

## 版本与开发日志

- 默认项目语言为英文；本页为中文补充。
- 自 v0.01 起，每次有意义更新记录于 DEVLOG.md。

## 快速验证

部署后可验证：
- 健康检查：`GET /v1/health` 应显示版本 `v0.11`。
- 站点评分：访问 Web UI，输入完整 URL 或域名；无投票站点应显示 U=0 且“暂无评价”，
  总分仅由 S/C/T 构成；投票后 U 逐步生效并随票数爬升权重。
