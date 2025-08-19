# API 规范（节选）

鉴权：
- Serverless：uni-id（邮箱/手机/第三方）
- 容器化：JWT（短期）+ Refresh Token；密码使用 Argon2

## 示例
GET /v1/sites/{host}
```
{
  "host": "example.com",
  "score": 82.4,
  "level": "green",
  "breakdown": {"S":0.92,"C":0.72,"T":0.68,"U":0.77},
  "updated_at": "2025-08-17T08:30:00Z"
}
```

GET /v1/sites/{host}/explain
```
{
  "host": "example.com",
  "model_version": "v0.1",
  "signals": [
    {"key":"https","value":true,"effect":"+0.05S"},
    {"key":"csp","value":false,"effect":"-0.05S"},
    {"key":"brand_mismatch","value":false},
    {"key":"has_citation","value":true,"effect":"+0.15C"},
    {"key":"about_contact","value":true,"effect":"+0.15T"},
    {"key":"community_wilson","value":0.77,"effect":"+0.20U"}
  ]
}
```

POST /v1/votes（鉴权）
```
{ "host":"foo.shop", "label":"danger", "reason":"仿冒支付页" }
```
响应：
```
{ "ok": true, "new_score": 41.6 }
```

论坛：
- GET /v1/forum/{host}/posts
- POST /v1/forum/{host}/posts（鉴权）
- POST /v1/reactions → 对帖子/评论点赞点踩

错误码：401、429、422、403
