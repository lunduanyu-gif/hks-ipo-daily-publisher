# 港股打新工作流 Cron 配置参考

## 创建 Cron Job

```javascript
cron.add({
  name: 'hks-ipo-daily-publisher',
  schedule: {
    kind: 'cron',
    expr: '0 11 * * *',   // 每天 11:00
    tz: 'Asia/Shanghai'
  },
  payload: {
    kind: 'agentTurn',
    message: '执行港股打新每日发布工作流。参考 SKILL.md。目标：抓取一只正在申购的港股新股，通过 NotebookLM 研究，发布到小红书和微信公众号。详见 hks-ipo-daily-publisher skill。',
    model: 'minimax/MiniMax-M2.7'
  },
  sessionTarget: 'isolated',
  delivery: {
    mode: 'announce',
    channel: 'telegram',
    to: 'telegram:-1003751978564'
  },
  enabled: true
})
```

## 执行日志

每次执行后记录到：`memory/YYYY-MM-DD-hks-ipo-execution.md`
