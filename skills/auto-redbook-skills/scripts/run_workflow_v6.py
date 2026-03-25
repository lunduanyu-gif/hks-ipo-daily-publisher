#!/usr/bin/env python3
"""
xhs-daily-workflow v6 - 使用subagents工具调用
"""

import os, sys, datetime, json
from openclaw.subagents import spawn

OUTPUT_DIR = os.path.expanduser("~/baoyu-output")
MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory/studies/xhs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MEMORY_DIR, exist_ok=True)
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")

def main():
    topic_keyword = "美伊局势"
    time_range = "当天8点到16点"
    
    for i, arg in enumerate(sys.argv):
        if arg == "--topic" and i+1 < len(sys.argv):
            topic_keyword = sys.argv[i+1]
        if arg == "--time-range" and i+1 < len(sys.argv):
            time_range = sys.argv[i+1]
    
    log("="*60)
    log(f"🚀 多Agent工作流 v6")
    log("="*60)
    
    # 步骤1: 账号负责人
    log("🔍 步骤1: 账号负责人")
    try:
        result1 = spawn(agent_id="account_manager", task="搜索美伊局势热点，返回选题", timeout=120)
        log(f"   结果: {result1[:100] if result1 else '无'}")
    except Exception as e:
        log(f"   错误: {e}")
    
    # 步骤2: 内容运营
    log("📝 步骤2: 内容运营")
    try:
        result2 = spawn(agent_id="content_editor", task="生成小红书正文：美伊局势", timeout=120)
        log(f"   结果: {len(result2) if result2 else 0} 字符")
    except Exception as e:
        log(f"   错误: {e}")
    
    # 步骤3: 视觉设计
    log("🎨 步骤3: 视觉设计")
    try:
        result3 = spawn(agent_id="visual_designer", task="生成小红书封面图和配图", timeout=120)
        log(f"   完成")
    except Exception as e:
        log(f"   错误: {e}")
    
    # 步骤4: 审核
    log("✅ 步骤4: 审核")
    try:
        result4 = spawn(agent_id="account_manager", task="审核内容是否通过", timeout=60)
        log(f"   结果: {result4[:50] if result4 else '无'}")
    except Exception as e:
        log(f"   错误: {e}")
    
    # 步骤5: 发布
    log("🚀 步骤5: 发布")
    try:
        result5 = spawn(agent_id="content_editor", task="发布笔记", timeout=120)
        log(f"   完成")
    except Exception as e:
        log(f"   错误: {e}")
    
    # 步骤6: 数据记录
    log("📊 步骤6: 数据记录")
    try:
        result6 = spawn(agent_id="data_analyst", task=f"记录笔记 xhs_{TIMESTAMP}", timeout=60)
        log(f"   完成")
    except Exception as e:
        log(f"   错误: {e}")
    
    log("="*60)
    log("✅ 完成!")

if __name__ == "__main__":
    main()
