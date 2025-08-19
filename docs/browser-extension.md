# 浏览器插件（MV3）

- content script：读取 location.host → 调用 /v1/sites/{host} → 注入顶栏（绿/橙/红 + 分数）。
- 一键标记：点击“危险/安全”→ 登录 → POST /v1/votes。
- 低干扰：默认仅显示颜色条；点击展开“证据卡片”。
- 缓存：同域查询 5–15 分钟 TTL，减少 API 压力。
