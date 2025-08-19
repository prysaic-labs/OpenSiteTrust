# 评分模型（0–100，四维合成）

总分：
Score = sigmoid( 3*(0.4*S + 0.25*C + 0.15*T + 0.2*U) - 1.5 ) * 100

阈值：
- >= 80 绿色（低风险）
- 60–79 橙色（需谨慎）
- < 60 红色（高风险）

## 维度定义
- S 安全性 (0.4)：URL/域名、HTTPS/HSTS/CSP/XFO/XCTO、敏感表单、品牌冒用。
- C 可信度 (0.25)：外部引用/来源、标题煽动性、紧迫诱导用语。
- T 透明度 (0.15)：About/Contact、作者/组织/备案/公司信息、广告/赞助标注。
- U 社区意见 (0.2)：用户投票 → Wilson 下置信界 + 用户信誉加权。

## 可解释输出（示例）
- "域名含 punycode"、"无 CSP"、"提及 Apple 但域非 apple.com"、"缺少引用"、"标题煽动性强"、"社区危险票 37%（n=124）"。

## 伪代码
```
def compose_score(S, C, T, U):
    # S/C/T/U in [0,1]
    z = 0.4*S + 0.25*C + 0.15*T + 0.2*U
    return round( (1/(1+math.exp(-(3*z - 1.5)))) * 100, 1 )

# S：根据规则打“危险权重”再转为安全比分
danger = clip(
  2*has_punycode + 1.5*mixed_scripts + 1*suspicious_tld + 2*at_or_ip +
  1*shortener + 2.5*brand_mismatch + 1*(not https) + 0.5*(not hsts) +
  0.5*(not csp) + 0.5*(not xfo) + 1*has_password_form , max=10
)
S = 1 - danger/10
```

## 社区加权（提示）
- Wilson 下置信界；用户信誉：历史准确度、账号年龄、异常模式降权。
