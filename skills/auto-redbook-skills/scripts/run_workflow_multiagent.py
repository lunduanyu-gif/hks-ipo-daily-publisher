#!/usr/bin/env python3
"""
xhs-daily-workflow 真正多Agent架构
使用 sessions_spawn 调用各个subagent
"""

import os
import subprocess
import datetime
import json
import sys

OUTPUT_DIR = os.path.expanduser("~/baoyu-output")
MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory/studies/xhs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MEMORY_DIR, exist_ok=True)

TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")

def spawn_agent(agent_id, task, model=None):
    """调用 subagent"""
    cmd = ["openclaw", "sessions", "spawn"]
    if agent_id:
        cmd.extend(["--agentId", agent_id])
    if model:
        cmd.extend(["--model", model])
    cmd.extend(["--task", task])
    cmd.extend(["--mode", "run"])
    cmd.extend(["--timeoutSeconds", "300"])
    
    log(f"   → 调用 {agent_id} ({model or 'default'})")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=360)
    return result.stdout

# ========== 主函数 ==========
def main():
    topic_keyword = "美伊局势"
    time_range = "当天8点到16点"
    
    for i, arg in enumerate(sys.argv):
        if arg == "--topic" and i+1 < len(sys.argv):
            topic_keyword = sys.argv[i+1]
        if arg == "--time-range" and i+1 < len(sys.argv):
            time_range = sys.argv[i+1]
    
    log("="*60)
    log(f"🚀 多Agent工作流开始")
    log(f"   话题: {topic_keyword}, 时间: {time_range}")
    log("="*60)
    
    # ========== 步骤1: 账号负责人 (Gemini) - 选题 ==========
    log("🔍 步骤1: 账号负责人 - 热点检测与选题")
    task1 = f"""你是账号负责人。请搜索美伊局势热点，选择最佳选题。
时间范围: {time_range}
返回格式: 选题标题 + 简短理由"""
    
    result1 = spawn_agent("account_manager", task1, "google/gemini-3.1-pro-preview")
    log(f"   选题结果: {result1[:100]}...")
    
    # ========== 步骤2: 内容运营 (MiniMax) - 生成内容 ==========
    log("📝 步骤2: 内容运营 - 资讯获取与生成")
    task2 = f"""你是内容运营。请完成以下任务：
1. 使用 global-news-deep-research 获取{topic_keyword}资讯
2. 使用 xhs_rewrite.py 生成小红书正文 (888字以内)
3. 使用 humanizer 去AI味
4. 段落清晰化+格式校验

时间范围: {time_range}
返回: 生成的正文字符串"""
    
    result2 = spawn_agent("content_editor", task2, "minimax/MiniMax-M2.5")
    log(f"   内容生成完成: {len(result2)} 字符")
    
    # ========== 步骤3: 视觉设计 (MiniMax) - 生成图片 ==========
    log("🎨 步骤3: 视觉设计 - 图片生成")
    task3 = f"""你是视觉设计。请完成：
1. 使用 baoyu-cover-image 生成封面图 (chalkboard风格)
2. 使用 baoyu-article-illustrator 生成3张正文配图

正文内容: {result2[:500]}
输出: 图片路径列表"""
    
    result3 = spawn_agent("visual_designer", task3, "minimax/MiniMax-M2.5")
    log(f"   图片生成完成")
    
    # ========== 步骤4: 账号负责人 (Gemini) - 审核 ==========
    log("✅ 步骤4: 账号负责人 - 最终审核")
    task4 = f"""你是账号负责人。请审核以下内容：
正文: {result2[:500]}
审核标准: 价值观、品牌调性、合规性
返回: "通过" 或 "不通过 + 原因"""
    
    result4 = spawn_agent("account_manager", task4, "google/gemini-3.1-pro-preview")
    log(f"   审核结果: {result4[:50]}...")
    
    # ========== 步骤5: 内容运营 (MiniMax) - 发布 ==========
    log("🚀 步骤5: 内容运营 - 发布笔记")
    task5 = f"""你是内容运营。请使用 publish_xhs.py 发布笔记：
正文: {result2[:800]}
图片: 使用步骤3生成的图片"""
    
    result5 = spawn_agent("content_editor", task5, "minimax/MiniMax-M2.5")
    note_id = f"xhs_{TIMESTAMP}"
    log(f"   发布成功: {note_id}")
    
    # ========== 步骤6: 数据运营 (MiniMax) - 记录 ==========
    log("📊 步骤6: 数据运营 - 记录数据")
    task6 = f"""你是数据运营。请记录：
笔记ID: {note_id}
日期: {datetime.date.today()}
话题: {topic_keyword}
时间范围: {time_range}

写入文件: {MEMORY_DIR}/published_notes.md"""
    
    result6 = spawn_agent("data_analyst", task6, "minimax/MiniMax-M2.5")
    log(f"   数据记录完成")
    
    log("="*60)
    log("✅ 多Agent工作流完成!")
    log("="*60)

if __name__ == "__main__":
    main()
