#!/usr/bin/env python3
"""
小红书风格报告转写脚本 v4
接入 Gemini API 生成真正的小红书风格内容
"""

import os
import sys
import json
import re
import requests
from pathlib import Path


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


def call_gemini(prompt: str) -> str:
    """调用 Gemini API"""
    if not GEMINI_API_KEY:
        print("⚠️ 未配置 GEMINI_API_KEY")
        return None
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7
        }
    }
    
    try:
        resp = requests.post(url, headers=headers, params=params, json=data, timeout=120)
        if resp.status_code == 200:
            result = resp.json()
            return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        else:
            print(f"❌ API 错误: {resp.status_code} - {resp.text[:100]}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None


def read_report(input_path: str) -> str:
    """读取报告文件"""
    with open(input_path, 'r', encoding='utf-8') as f:
        return f.read()


def count_chinese_chars(text: str) -> int:
    """统计中文字符数量"""
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    return len(chinese_chars)


def clean_and_validate_content(content: str, max_length: int = 888) -> tuple:
    """
    段落清晰化 + 格式校验 + 去重复标签
    返回: (处理后的内容, 是否需要重试)
    """
    lines = content.split('\n')
    cleaned_lines = []
    
    # 1. 去除标题行（如 # 小红书正文）
    for line in lines:
        line = line.strip()
        # 跳过纯标题行
        if line.startswith('# ') and len(line) < 20:
            continue
        # 跳过空行但保留段落分隔
        if line:
            cleaned_lines.append(line)
    
    # 重新组合，确保段落间有空行
    paragraphs = []
    for line in cleaned_lines:
        if line.strip():
            paragraphs.append(line.strip())
    
    # 用双换行分隔段落
    content = '\n\n'.join(paragraphs)
    
    # 2. 提取并去重标签
    tags = re.findall(r'#[\u4e00-\u9fff]+', content)
    unique_tags = list(dict.fromkeys(tags))  # 保持顺序去重
    content = re.sub(r'#[\u4e00-\u9fff]+', '', content)  # 移除所有标签
    content = content.strip() + '\n\n' + ' '.join(unique_tags)  # 重新添加去重后的标签
    
    # 3. 统计字数
    chinese_count = count_chinese_chars(content)
    
    # 4. 校验
    issues = []
    if chinese_count > max_length:
        issues.append(f"字数超限: {chinese_count}/{max_length}")
    if len(unique_tags) < 3:
        issues.append(f"标签不足: {len(unique_tags)}")
    
    return content, len(issues) > 0, chinese_count


def extract_title_and_content(report: str) -> tuple:
    """从报告中提取标题和内容"""
    lines = report.strip().split('\n')
    
    title = ""
    content_lines = []
    
    for line in lines:
        if line.startswith('# ') and not title:
            title = line.replace('# ', '').strip()
        elif line.strip():
            content_lines.append(line)
    
    if not title and lines:
        title = lines[0].replace('#', '').strip()
    
    content = '\n'.join(content_lines[:30])
    return title, content


def generate_xhs_content(report_path: str, max_length: int = 888) -> str:
    """使用 Gemini 生成小红书风格内容"""
    
    report = read_report(report_path)
    title, content = extract_title_and_content(report)
    
    if not title:
        title = "今日财经解读"
    
    prompt = f"""你是一位拥有哈佛商学院经济和金融学双博士学位的顶级财经分析师，曾在全球顶级投行担任首席策略师。

请将以下新闻报告转换为小红书风格内容，要求专业、深度、有见解：

新闻主题：{title}

新闻内容：
{content[:2000]}

要求：
1. 开头用一句话概括新闻最核心的反转或亮点（一针见血）
2. 中间列出3个深度要点（用1️⃣ 2️⃣ 3️⃣ 格式），每个要点之间用空行分隔便于阅读，每个要点：
   - 用通俗易懂的大白话解释（让普通人都能看懂）
   - 融入专业分析（数据和逻辑支撑）
   - 结论一针见血
3. 给出2-3个建设性投资建议（具体方向+逻辑），每条建议之间用空行分隔
4. 结尾用问句引导评论
5. 添加 #话题 标签（至少3个标签，短小精悍），⚠️禁止重复！每个标签只能出现一次
6. 文字内容+所有标签总字数控制在888个汉字以内（不含标点符号和空格）
7. 禁止使用 md 格式符号
8. 禁止车轱辘话，禁止正确的废话，禁止泛泛而谈
9. 内容要让读者真的能学会东西，自然融入费曼学习法的教学风格
10. 段落之间必须用空行分隔，确保阅读体验清晰

    print("   调用 Gemini API...")
    result = call_gemini(prompt)
    
    if result:
        # 截取中文字数
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', result)
        if len(chinese_chars) > max_length:
            # 简单截断（实际应该让API重新生成）
            print(f"   警告：中文字数 {len(chinese_chars)} 超过限制 {max_length}")
        
        return f"# {title}\n\n{result}"
    return None


def generate_xhs_content_fallback(title: str, report: str) -> str:
    """规则生成（无 API 时的备选）"""
    sentences = re.split(r'[。！？\n]', report)
    key_sentences = [s.strip() for s in sentences if len(s.strip()) > 10][:5]
    
    content = f"""# {title}

📌 核心要点

1️⃣ {key_sentences[0] if len(key_sentences) > 0 else "市场出现新变化"}

2️⃣ {key_sentences[1] if len(key_sentences) > 1 else "需要关注的重要因素"}

3️⃣ {key_sentences[2] if len(key_sentences) > 2 else "可能的影响"}

💡 投资建议

• 控制仓位，分批建仓
• 关注确定性机会
• 避免追涨杀跌

💬 你怎么看？欢迎评论区聊聊！

#投资理财 #财经热点 #美伊局势"""

    return content


def main():
    import argparse
    parser = argparse.ArgumentParser(description="小红书风格内容生成")
    parser.add_argument("--input", "-i", required=True, help="输入报告文件")
    parser.add_argument("--output", "-o", required=True, help="输出文件")
    parser.add_argument("--max-length", type=int, default=888, help="最大字数")
    args = parser.parse_args()
    
    print(f"📝 生成小红书风格内容...")
    print(f"   输入: {args.input}")
    print(f"   输出: {args.output}")
    
    # 1. 生成初稿
    content = generate_xhs_content(args.input, args.max_length)
    
    if not content:
        print("⚠️ 使用规则生成（API 不可用）")
        report = read_report(args.input)
        title, _ = extract_title_and_content(report)
        content = generate_xhs_content_fallback(title, report)
    
    # 2. 去AI味 (humanizer) - 这里先跳过，假设外部处理
    # TODO: 集成 humanizer
    
    # 3. 段落清晰化 + 格式校验 + 去重复标签
    print("   校验内容...")
    cleaned_content, needs_retry, chinese_count = clean_and_validate_content(content, args.max_length)
    
    if needs_retry:
        print(f"   ⚠️ 内容需要调整: {chinese_count}字")
    
    # 保存
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"✅ 内容已生成并校验完成 ({chinese_count} 字)")
    print(f"   文件: {args.output}")


if __name__ == "__main__":
    main()
