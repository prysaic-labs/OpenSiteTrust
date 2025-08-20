# OpenSiteTrust（中文）

[opensitetrust.com](https://opensitetrust.com) · 版本：v0.26 · 默认项目语言：英文（本页为中文说明）

用“规则 + 社区 + 透明解释”为网站打 0–100 分的多维风险/可信度评分，提供开放 API 与网页端 UI（浏览器扩展与论坛为后续计划）。

> 状态：v0.25 提供可用 API 与 UI，含缓存与持久化、丰富探测项、
> 动态评分、多语言，以及 SEO 相关页面（About/Contact/Privacy）、
> robots.txt 与 sitemap，并在头部抽屉中加入“菜单”导航。

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

## MVP 范围

- 评分引擎 + 解释（Redis 缓存，PostgreSQL 持久化）
- 开放 API：
  - GET /v1/sites/{host}
  - GET /v1/sites/{host}/explain
  - POST /v1/votes
- Web UI（Next.js + Tailwind + 类 shadcn 组件），多语言通过 `?lang=`
  （默认 en，可选 zh/zh-Hant/ja/es）；新增 About/Contact/Privacy 页面，
  提供 robots.txt 与 sitemap；头部抽屉改为“菜单”并加入 SEO 导航链接。
- 反向代理与部署：Caddy + Docker Compose（加入健康检查，反向代理等待 API 就绪，减少 502）

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

## 项目规划与路线图

愿景：开放、可解释、可参与的网站可信度生态，围绕 S/C/T/U 四维信号、开放接口与社区协作。

近期（0.x）：
- 强化探测与证据卡片；提升透明/可信覆盖面
- 浏览器扩展与基础申诉/协作流程
- 公共数据导出与快照；反滥用机制
- 可选更多身份提供商与申诉流

后续（1.x）：
- 规则/插件化评分市场与数据协作
- 研究接口与高级看板；联邦化探索

## 部署

- 参考 docs/deployment.md；根目录提供 `docker-compose.yml` 与 `.env.example`。
- 环境变量（.env）示例（请勿提交 .env 到仓库）：
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

## 最低服务器规格与建议

- 最低：1 vCPU，1–2 GB 内存，10 GB 磁盘（演示/测试）
- 建议：2 vCPU，2–4 GB 内存，20+ GB 磁盘（小型生产）

## 使用与说明

1. 复制 `.env.example` 为 `.env` 并根据环境填写
   （数据库/缓存/JWT/域名，可选 GitHub OAuth 与 SMTP、GSB Key、
   NEXT_PUBLIC_VERSION）。
1. 运行 Docker Compose 构建并启动；域名解析指向服务器后，
   Caddy 自动签发证书。
1. 访问 Web；通过 `?lang=` 切换语言。

### 分步教程（Docker Compose）

前置条件：
- Ubuntu 24.04 LTS 或同类 Linux
- Docker Engine 24+ 与 Docker Compose v2
- 域名已指向服务器（A/AAAA）

1. 克隆与环境准备

- 克隆仓库并进入目录。
- 复制 `.env.example` 为 `.env` 并填写：
  - `DATABASE_URL`、`REDIS_URL`、`JWT_SECRET`、`WEB_ORIGIN`
  - 可选：`GITHUB_CLIENT_ID`、`GITHUB_CLIENT_SECRET`、
    `GITHUB_REDIRECT_URI`
  - 可选：SMTP 邮件验证码相关配置
  - 可选：`GSB_API_KEY`（Google Safe Browsing）
  - `NEXT_PUBLIC_VERSION`（与 `VERSION` 保持一致）

1. 配置 DNS 与 Caddy

- 将域名解析到服务器公网 IP。
- Caddy 会依据 `Caddyfile` 自动签发 TLS 证书。

1. 构建与启动

```bash
docker compose up -d --build
docker compose ps
```

1. 验证

- API 健康：GET `/v1/health` 应返回版本与时间。
- 公共配置：GET `/v1/config` 可查看 SMTP/GitHub 是否已配置。
- 浏览器访问你的域名；TLS 证书应有效。

1. 账号与登录

- 邮箱验证码需正确配置 SMTP。
- GitHub 登录/注册需创建 OAuth 应用（见下）。
- 管理后台权限由 `ADMIN_EMAILS` 控制。

1. 更新与重部署

```bash
git pull
docker compose up -d --build api web
docker compose logs -f --tail=200 api
```

1. 日志与维护

```bash
docker compose logs -f api
docker compose logs -f web
docker compose ps
docker compose restart api web
```

1. 备份（PostgreSQL 数据）

```bash
# 导出
docker compose exec -T db pg_dump -U postgres site > backup.sql
# 恢复（覆盖性操作）
docker compose exec -T db psql -U postgres site < backup.sql
```

### GitHub OAuth 配置

1. 在 GitHub Developers 创建 OAuth 应用。
1. Homepage URL：你的 `WEB_ORIGIN`。
1. Authorization callback URL：
   `WEB_ORIGIN/login/github-callback`。
1. 将 `GITHUB_CLIENT_ID`、`GITHUB_CLIENT_SECRET`，以及可选的
   `GITHUB_REDIRECT_URI` 写入 `.env`。

### SMTP（邮箱验证码）

- 在 `.env` 中填写 `SMTP_HOST`、`SMTP_PORT`、`SMTP_USER`、
  `SMTP_PASSWORD`、`SMTP_SENDER`。
- 通过 `POST /v1/auth/send-code` 进行测试，并观察日志。

### 常见排错

- 构建失败：
  - 检查 Docker 版本与磁盘空间。
  - 确认 `.env` 与 `docker-compose.yml` 位于同一目录。
- GitHub OAuth 400/回调异常：
  - 确认 `GITHUB_CLIENT_ID/SECRET` 与回调地址严格一致。
  - 检查 `/v1/config` 中 `github_configured: true`。
- 邮件收不到验证码：
  - 校验 SMTP 凭据；查看服务商控制台。
  - 注意限流：参见 `/v1/config.email_code_rate_limit`。
- 数据库缺列（如 `users.handle`）：
  - API 启动包含“尽力而为”的 DDL；升级后重启 `api` 即可。
- 端口冲突：
  - 确认 80/443 未被占用（停止系统自带 nginx/apache）。

### Windows PowerShell（可选）

适用于 Windows 开发者：

```powershell
docker compose up -d --build
docker compose ps
docker compose logs -f --tail 200 api
```

## 版本与开发日志

- 默认项目语言为英文；本页为中文补充。
- 自 v0.01 起，每次有意义更新记录于 DEVLOG.md。

## 快速验证

部署后可验证：
- 健康检查：`GET /v1/health` 应显示版本 `v0.12`。
- 站点评分：访问 Web UI，输入完整 URL 或域名；无投票站点应显示 U=0 且“暂无评价”，总分仅由 S/C/T 构成；投票后 U 逐步生效并随票数爬升权重。
- SEO 页面：页眉抽屉按钮显示“菜单”；其中包含 About、Contact、Privacy、
  API Docs、Health；sitemap 和 robots 可访问。
