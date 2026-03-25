#!/usr/bin/env python3
"""
小红书 MCP 发布脚本
使用 xiaohongshu-mcp 发布笔记，话题标签正确展示
"""

import requests
import json
import os
import sys

MCP_URL = "http://localhost:18060/mcp"

def init_session():
    """初始化 MCP 会话"""
    session = requests.Session()
    init_resp = session.post(MCP_URL, json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "xhs-publisher", "version": "1.0"}
        }
    })
    session_id = init_resp.headers.get('mcp-session-id')
    if not session_id:
        raise Exception("无法获取 MCP session")
    session.headers.update({"mcp-session-id": session_id})
    return session

def check_login(session):
    """检查登录状态"""
    resp = session.post(MCP_URL, json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": "check_login_status", "arguments": {}}
    })
    result = resp.json()
    content = result.get("result", {}).get("content", [])
    if content and "已登录" in content[0].get("text", ""):
        return True
    return False

def publish(session, title, content, images, tags):
    """发布笔记"""
    arguments = {
        "title": title,
        "content": content,
        "images": images,
        "tags": tags
    }
    
    resp = session.post(MCP_URL, json={
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "publish_content",
            "arguments": arguments
        }
    })
    
    result = resp.json()
    content_result = result.get("result", {}).get("content", [])
    if content_result:
        return content_result[0].get("text", "")
    return str(result)

def main():
    if len(sys.argv) < 4:
        print("用法: python publish_mcp.py <标题> <正文> <图片路径> <标签1> <标签2> ...")
        sys.exit(1)
    
    title = sys.argv[1]
    content = sys.argv[2]
    images = [sys.argv[3]] if sys.argv[3] else []
    tags = sys.argv[4:] if len(sys.argv) > 4 else []
    
    print(f"标题: {title}")
    print(f"正文: {content[:50]}...")
    print(f"图片: {images}")
    print(f"标签: {tags}")
    print()
    
    try:
        session = init_session()
        print("✓ MCP 会话已初始化")
        
        if not check_login(session):
            print("❌ 未登录，请先扫码登录")
            sys.exit(1)
        print("✓ 已登录")
        
        result = publish(session, title, content, images, tags)
        print(f"\n✓ 发布结果: {result}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
