---
name: daily-content-publisher
description: |
  Use when generating and publishing daily content to BOTH Xiaohongshu (小红书) daily content.
  Don't use when: image generation only (use openclaw-baoyu-wrappers), or one-off posts without automated workflow.
  Trigger: "小红书", "每日发布", "XHS", "auto-redbook", "同步发布", "auto-publish".

  This skill publishes to TWO platforms in one workflow: Xiaohongshu AND WeChat Official Account.
  Xiaohongshu title must be <=20 characters (UC震撼部风格).
  WeChat title follows the formula: "人物 x 平台：数字 + 悬念词".
  WeChat body must be >=800 characters, with one matching infographic per paragraph.
  信息来源 must be cited at the bottom of WeChat article.
  Never skip any step. If any step fails, notify 俞董 immediately in the group.

  ## ACI Parameters
  | param | type | required | description |
  |-------|------|---------|-------------|
  | topic | string | yes | Content topic/focus (e.g., "美伊局势", "港股打新") |
  | time_window | string | no | News window: "16:00-08:00" (default) |
  | publish_to | array | no | Targets: ["xhs", "wechat"] (default: ["xhs"]) |

  ## Content Specs (ACI Constraints)
  | spec | value | error_code if violated |
  |------|-------|----------------------|
  | 小红书标题字数 | <=20字 | TITLE_TOO_LONG |
  | 小红书正文字数 | 500-600字 | BODY_TOO_SHORT / BODY_TOO_LONG |
  | 配图数量 | >=5张 | NOT_ENOUGH_IMAGES |
  | 标签数量 | 10个 | NOT_ENOUGH_TAGS |
  | 小红书标题风格 | UC震撼部，疑问句更佳 | TITLE_WRONG_STYLE |
  | 公众号正文字数 | >=800字 | WECHAT_BODY_TOO_SHORT |
  | 公众号配图 | 每段一张，精准匹配 | WECHAT_IMAGE_MISSING |
  | 公众号标题 | 人物x平台：数字+悬念词 | WECHAT_TITLE_WRONG |
  | 信息来源 | 末尾注明媒体来源 | SOURCE_MISSING |

  ## Error Handling
  | error_code | meaning | suggestion |
  |-----------|---------|-----------|
  | NO_HOT_NEWS | 时间窗口内无热点 | Expand window to 24h |
  | COOKIE_EXPIRED | 小红书Cookie过期 | Notify 俞董 immediately |
  | CANVAS_FAILED | 图片生成失败 | Retry once, notify 俞董 |
  | PUBLISH_FAILED | 发布失败 | Retry once, notify 俞董 |
  | TITLE_TOO_LONG | 标题超过20字 | Truncate or rewrite |

  ## 发布铁律
  - 内容不完整（封面图 + 配图 + 正文）绝不发！
  - 一篇文章只能发布一次，禁止并行发布！
---

## 🎯 核心理念
通过 Agent 架构实现“选题-撰写-视觉-发布-数据”全链路自动化，特别强化了“干货审核”流程。

## 🤖 内容生成流程 (正文生产 SOP)
*   **Step 01 (资讯抓取)**：`global-news-deep-research` 获取实时资讯。
*   **Step 02 (初稿生成)**：基于调研报告生成核心文案，确保三段式结构。
*   **Step 03 (Humanizer 去 AI 味)**：重写文案，去除 AI 惯用的车轱辘话，增加真实投资人的语感。
*   **Step 04 (深度加持)**：强制审核“核心观点”与“建设性意见”。
*   **Step 04.5 (深度建设性意见复核 - 锁定步骤)**：
    - **逻辑注入**：文案中必须包含 2-3 个具备实操价值的投资策略或避险逻辑。
    - **避雷检查**：确保内容体现客观理性的风险与机会视角，禁止情绪化。
    - **互动引导**：结尾需引起建设性讨论，而非简单提问。
*   **Step 05 (小红书化)**：调整段落节奏，精准插入 Emoji，控制总字数在 500-600 字之间。

## 📌 小红书标题规范（俞董2026-03-23确认，强制执行）
- **字数**：≤20字
- **风格**：UC震惊部风格，情绪爆点，疑问句更佳
- **示例**：「霍尔木兹被封！油价要暴涨？A股这一板块要爆！」
- **严禁**：超过20字、过于平淡、纯资讯风格

## 🔧 Windows 环境兼容性指引
- **封面生成**：使用 `node C:\Users\77961\.openclaw\workspace\skills\openclaw-baoyu-wrappers\index.js cover \"标题\" --style chalkboard`
- **信息图生成**：使用 `node C:\Users\77961\.openclaw\workspace\skills\openclaw-baoyu-wrappers\index.js infographic \"内容\" --style chalkboard`
- **注意事项**：Windows 下请务必使用 CMD 或 PowerShell 绝对路径，且路径及参数中若包含特殊字符，需使用 \ 转义。

---

## 🚀 运行方式
- **手动启动**：`python3 ~/.openclaw/workspace/skills/auto-redbook-skills/scripts/run_workflow.py`
- **自动运行 (Cron)**：已配置 8:00 和 16:00 定时执行，并自动传入对应的时间范围参数。
