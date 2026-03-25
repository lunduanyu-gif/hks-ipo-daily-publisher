# auto-redbook-skills

> 小红书每日自动发布工作流 - Agent架构版

自动化生成并发布小红书笔记，支持多 Agent 协作。

## 功能特性

- 📰 **资讯获取** - 自动搜索最新新闻
- ✍️ **内容生成** - 三段式结构（开头+干货+互动）
- 🎨 **去AI味** - humanizer 处理
- 📝 **小红书化** - 段落明显化，适量 emoji
- 🖼️ **配图生成** - 封面图 + 正文配图
- 📤 **MCP 发布** - 话题标签正确展示

## 工作流

```
1. 资讯获取 → 2. 生成初稿 → 3. humanizer去AI味 → 4. 小红书化 → 5. 生成配图 → 6. MCP发布 → 7. Telegram通知
```

## 规则

| 项目 | 限制 |
|------|------|
| 标题 | ≤20字 |
| 正文 | 600-800汉字 |
| Emoji | 5-8个 |
| 标签 | 5-10个 |
| 正文配图 | ≥5张 |
| 封面风格 | chalkboard |

## ⚠️ 发布铁律

- **内容不完整绝不发！** 封面图+正文配图（≥5张）必须齐全
- 每步必检查：每完成一步都要检查是否成功
- 出现问题即停：中间任意一步出现问题，直接停止发布

## 快速开始

### 1. 配置 MCP

```bash
# 启动小红书 MCP 服务
cd /tmp
./xiaohongshu-mcp-darwin-arm64 &

# MCP 地址: http://localhost:18060/mcp
```

### 2. 配置 Cookie

```bash
# 编辑 scripts/.env，填入小红书 Cookie
```

### 3. 运行工作流

```bash
cd ~/.openclaw/workspace/skills/auto-redbook-skills

# 早间任务（8点）
python3 scripts/run_workflow.py --topic "美伊局势" --time-range "前一天16点到当天8点"

# 午间任务（16点）
python3 scripts/run_workflow.py --topic "美伊局势" --time-range "当天8点到16点"
```

### 4. MCP 发布

```bash
python3 scripts/publish_mcp.py "标题" "正文" "图片路径" 标签1 标签2...
```

## 项目结构

```
auto-redbook-skills/
├── SKILL.md              # Skill 定义
├── README.md             # 说明文档
├── config/               # 配置文件
│   └── com.openclaw.xhs-daily-workflow.plist
└── scripts/             # 脚本
    ├── .env              # 环境变量（Cookie）
    ├── publish_mcp.py    # MCP 发布脚本
    ├── publish_xhs.py    # 旧版发布脚本
    └── run_workflow.py   # 工作流入口
```

## 开发指南

### 修改流程

1. **新建分支**
   ```bash
   git checkout -b feat-xxx-description
   ```

2. **修改代码**

3. **提交**
   ```bash
   git add .
   git commit -m "feat: 添加xxx功能"
   ```

4. **推送 PR**
   ```bash
   git push origin feat-xxx-description
   ```

### 分支命名

- `feat-xx` - 新功能
- `fix-xx` - 修复
- `refactor-xx` - 重构

### Commit 规范

```
feat: 新功能
fix: 修复问题
refactor: 重构
docs: 文档更新
chore: 其他修改
```

## 依赖

- Python 3.10+
- requests
- xhs (小红书 API)
- baoyu-cover-image (封面图)
- baoyu-article-illustrator (正文配图)

## License

MIT
