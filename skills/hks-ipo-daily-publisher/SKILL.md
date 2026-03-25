---
name: hks-ipo-daily-publisher
description: |
  Use when publishing HK stock IPO (港股打新) daily content to Xiaohongshu or WeChat.
  Don't use when: US stock IPO (use other tool), individual stock analysis (use hks-company-analysis), or non-IPO financial content.
  Trigger: "港股打新", "IPO", "新股申购", "hks-ipo", "发布打新内容".

  ## ACI Parameters
  | param | type | required | description |
  |-------|------|---------|-------------|
  | focus | string | no | Stock code or name to prioritize (e.g., "2526") |
  | deadline | string | no | Cutoff time for 申购 (default: 16:00 today) |
  | publish_to | array | no | Targets: ["xhs", "wechat"] (default: ["xhs"]) |

  ## Workflow Steps
  1. 抓取当日申购港股新股数据
  2. NotebookLM 深度研究 + 生成研报
  3. 事实核查（必须通过）
  4. 生成封面图 (baoyu-cover-image, chalkboard风格)
  5. 发布到小红书 / 微信公众号草稿箱

  ## Error Handling
  | error_code | meaning | suggestion |
  |-----------|---------|-----------|
  | NO_STOCKS_TODAY | 今日无新股申购 | Skip publishing, notify 俞董 |
  | COOKIE_EXPIRED | 小红书Cookie过期 | Notify 俞董 immediately |
  | NOTEBOOKLM_FAILED | 研报生成失败 | Continue with basic info only |
  | FACT_CHECK_FAIL | 事实核查未通过 | 降级发布或跳过，正文删除有误数据 |
  | PUBLISH_FAILED | 发布失败 | Retry once, then notify 俞董 |

---

# 港股打新每日发布工作流

## 流程概览

```
① 抓取新股数据（wespy-fetcher / eastmoney API）
    ↓
② NotebookLM 深度研究（nlm-notebooklm）→ 研报下载
    ↓
③ 事实核查（必须通过，方可进入 Step 4）
    ↓
④ 小红书内容生成（研报改写 + openclaw-baoyu-wrappers + xiaohongshu-skills）
    ↓
⑤ 微信公众号发布（baoyu-post-to-wechat）
    ↓
⑥ 小红书发布（xiaohongshu-skills）
    ↓
⑦ 同步到 topic#56
```

## 关键约束

- **发布数量限制**：一篇文章只能发布一次，禁止并行发布
- **发布时间**：每天 11:00 定时（cron 触发），或俞董手动指定
- **平台**：小红书 + 微信公众号（同步发布）
- **发布前必须检查**：查 memory/ 检查该股票是否已发布过
- **事实核查前置**：Step 3 核查不通过，不得进入 Step 4

## 工具路径速查

| 任务 | 工具 | 路径 |
|------|------|------|
| 抓取新股数据 | wespy-fetcher | `~/.openclaw/workspace/skills/wespy-fetcher/scripts/wespy_cli.py` |
| NotebookLM 研究 | nlm | `nlm research start` → `nlm report create` |
| 研报下载 | nlm | `nlm download report <nb-id> --output <path>` |
| 小红书内容生成 | wrappers + xiaohongshu-skills | 先生成正稿/标题，再用 `openclaw-baoyu-wrappers` 出图，最后用 `xiaohongshu-skills` 发布 |
| 微信公众号发布 | baoyu-post-to-wechat | 见下文 Step 5 详细流程 |
| 小红书发布 | xiaohongshu-skills | `python scripts/cli.py check-login && publish` |
| 图片生成 | openclaw-baoyu-wrappers | `node index.js cover/infographic` |

## 完整执行步骤

### Step 1：抓取今日申购新股

```bash
# 查看正在申购的港股
python3 ~/.openclaw/workspace/skills/wespy-fetcher/scripts/wespy_cli.py --ipo-list
# 或通过 eastmoney API 抓取
```

输出：股票代码、公司名、申购日期、上市日期、发行价区间等。
**选择标的**：选择一只尚未发布过的股票（查 memory/ 确认）。

### Step 2：NotebookLM 研究

```bash
# 创建 notebook
nlm notebook create "[代码] HK IPO 研究"

# 添加信息源 URL（从 eastmoney 获取）
nlm source add <nb-id> --url "https://www.eastmoney.com" --title "招股信息"

# 启动研究
nlm research start "公司基本面 行业地位 竞争格局 财务数据 上市风险" --notebook-id <nb-id> --mode deep

# 等待完成后导入
nlm research import <nb-id> <task-id>

# 生成研报
nlm report create <nb-id> --confirm

# 下载研报
nlm studio status <nb-id>  # 查 report artifact_id
nlm download report <nb-id> --output ~/reports/[代码]-ipo-report.md
```

### Step 3：CFO 补充

研报下载后，需 CFO 补充：
- 十五五规划关联度评分（1-10）
- 基于索罗斯反身性理论推演上市走势
- 估值区间（P/S、P/E等）
- 操作建议（仓位、止盈/止损线）

### Step 4：事实核查（强制门控，必须通过方可进入 Step 5）

**触发时机**：研报下载完成后，立即执行事实核查，不得跳过或后置。

#### 核查清单

| # | 核查项 | 核查内容 | 数据来源 |
|---|--------|----------|----------|
| F1 | 发行价区间 | 确认最新发行价区间（有无调减/调增） | 港交所披露易 hkexnews.hk / 东方财富 |
| F2 | 募资规模 | 确认区间上下限，与研报对比 | 东方财富 IPO 专题页 |
| F3 | 公司基本信息 | 注册地、主营业务、保荐人、承销商 | 招股书摘要 / 港交所 |
| F4 | 行业数据 | 若研报引用市场份额/排名，核实是否有夸大 | 行业协会、第三方研报 |
| F5 | 风险提示 | 招股书重大风险条款与研报描述是否一致 | 港交所披露易招股书 |
| F6 | 逻辑自洽 | 估值结论是否与同类公司横向可比（偏离过大需降级） | 同行 IPO 数据对比 |

#### 执行命令

```bash
# 发行价/募资规模核查
web_search --query "[公司简称] 港股IPO 发行价区间 [年份] site:hkexnews.hk OR site:eastmoney.com"

# 公司信息核查（保荐人/承销商）
web_search --query "[公司简称] 港股IPO 保荐人 承销商"

# 行业数据核查
web_search --query "[公司简称] [行业] 市场份额 排名"
```

#### 核查结论模板

在研报文件头部写入以下格式结论：

```markdown
## 事实核查结论

- [x] 发行价区间：✅ [数据]（来源：xxx，核查时间：YYYY-MM-DD）
- [x] 募资规模：✅ [数据]
- [x] 公司注册地/主营业务：✅ [数据]
- [x] 保荐人/承销商：✅ [数据]
- [ ] 行业排名：⚠️ 研报称XX%，实际为YY%（已从正文删除）
- 结论：PASS / 降级发布（删误数据） / 不可发布（跳过本次）
```

#### 降级处理规则

| 情形 | 处理方式 |
|------|----------|
| F1/F2 关键数据不一致 | 降级发布，正文删除或标注"以官方公告为准" |
| F3 公司基本信息错误 | 正文删除该条，不引用 |
| F4 行业数据夸大 | 正文删除该条，不引用 |
| F5 风险描述与招股书不符 | 以招股书为准修正研报结论 |
| F6 估值逻辑明显偏离同行 | 降低估值可信度评级，正文补充"市场可比公司参考" |
| 无法核实的数据 | 标注"待官方确认"，不作为投资依据 |

#### 严禁事项

- 禁止发布未经核查的财务数据
- 禁止使用"百分百""绝对""必定"等绝对化表述
- **所有配图禁止带小红书 logo**（生成后需人工/AI 检查图片角落）
- 核查结论未写入报告头部，不得进入 Step 5

### Step 5：小红书内容生成（当前主路径）

**主路径**：研报改写/润色 → `openclaw-baoyu-wrappers` 生成封面与信息图 → `xiaohongshu-skills` 发布图文

**核心步骤**：
1. **初稿生成**：基于研报生成核心文案，确保三段式结构
2. **Humanizer 去 AI 味**：重写文案，去除 AI 惯用语，增加真实投资人语气
3. **深度建设性意见复核**：
   - 逻辑注入：文案中必须包含 2-3 个具备实操价值的投资策略或避险逻辑
   - 避雷检查：确保内容体现客观理性的风险与机会视角，禁止情绪化
   - 互动引导：结尾需引起建设性讨论
4. **小红书化**：调整段落节奏，精准插入 Emoji，控制总字数在 500-600 字之间
5. **SEO 标签**：生成 10 个话题标签（固定 + 自选）

**输出文件**：
- 标题文件：`~/baoyu-output/xhs-title.txt`
- 正文文件：`~/baoyu-output/xhs-content.txt`
- 标签：不少于 10 个（固定：港股打新 + 自选）

**图片生成**（必须检查：无小红书 logo）：
```bash
# 封面图
cd C:\Users\77961\.openclaw\workspace\skills\openclaw-baoyu-wrappers
node index.js cover "[公司简称]港股打新" --style chalkboard -o "C:\Users\77961\baoyu-output\wechat-cover.png"

# 正文配图 x3
node index.js infographic "核心数据" --style chalkboard -o "C:\Users\77961\baoyu-output\wechat-card1.png"
node index.js infographic "投资逻辑" --style chalkboard -o "C:\Users\77961\baoyu-output\wechat-card2.png"
node index.js infographic "风险提示" --style chalkboard -o "C:\Users\77961\baoyu-output\wechat-card3.png"
```

### Step 6：微信公众号发布（baoyu-post-to-wechat）

**参考路径**：`baoyu-post-to-wechat/SKILL.md`

**执行步骤**：
1. **加载 EXTEND.md 配置**
2. **内容准备**：将小红书正文改编为公众号风格文章
   - 标题：重新设计（与小红书不同）
   - 开头：事件概述 + 重要结论
   - 正文：增加背景分析、影响评估、专业术语解释，段落更长
   - 配图：直接使用小红书封面图作为公众号封面（需标注日期时间）
   - 正文配图：必须插入到对应段落
3. **发布到草稿箱**

```bash
cd C:\Users\77961\.openclaw\workspace\skills\baoyu-post-to-wechat
bun scripts/wechat-api.ts ~/baoyu-output/wechat-article.md --theme default --cover "C:\Users\77961\baoyu-output\wechat-cover.png"
```

### Step 7：小红书发布

```bash
cd C:\Users\77961\.openclaw\workspace\skills\xiaohongshu-skills

# 检查登录
python scripts/cli.py check-login

# 发布图文
python scripts/cli.py publish \
  --title "[公司简称]港股打新" \
  --content "C:\Users\77961\baoyu-output\xhs-content.txt" \
  --images "C:\Users\77961\baoyu-output\wechat-cover.png" "C:\Users\77961\baoyu-output\wechat-card1.png" "C:\Users\77961\baoyu-output\wechat-card2.png" "C:\Users\77961\baoyu-output\wechat-card3.png" \
  --tags "港股打新" "[行业关键词]" "[公司简称]" "[其他相关话题]"（共10个）
```

### Step 8：同步到 topic#56

发布完成后，向 Telegram 群组 topic#56 发送：
- 小红书链接
- 1张封面图（标注日期时间）
- 正文全文

## 发布检查清单

```
- [ ] 确认该股票今日未发布过（查 memory/）
- [ ] 封面图生成成功
- [ ] 正文配图 x3 生成成功
- [ ] 事实核查已通过（结论已写入研报头部）
- [ ] 小红书正文生成（当前 wrappers + xiaohongshu-skills 主路径）
- [ ] 微信公众号草稿已推送（baoyu-post-to-wechat）
- [ ] 小红书已发布
- [ ] 配图检查：无小红书 logo
- [ ] 发布记录已写入 memory/
- [ ] 群里已公告
```

## Cron 配置

```
name: hks-ipo-daily-publisher
schedule: cron 0 11 * * *  # 每天 11:00
sessionTarget: isolated
payload.kind: agentTurn
payload.message: 执行港股打新每日发布工作流（参考 hks-ipo-daily-publisher SKILL.md）
delivery.mode: announce
```

## 常见问题

| 问题 | 解决 |
|------|------|
| nlm login 会话过期 | `nlm login --check` 重新认证 |
| wespy 无数据 | 改用 eastmoney 网页抓取 |
| baoyu-wrappers 生成失败 | 确认 GOOGLE_API_KEY 和 GEMINI_API_KEY 已设 |
| 小红书未登录 | `python scripts/cli.py wait-login` 扫码 |
| new_sensitive 1027 拦截 | 检查内容敏感词，调整文案表述 |
