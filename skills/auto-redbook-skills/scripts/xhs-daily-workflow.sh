#!/bin/bash
# xhs-daily-workflow.sh - 小红书每日工作流
# 完整流程：资讯获取 → 内容生成 → 图片生成 → 发布

set -e

DATE=$(date +%Y-%m-%d)
OUTPUT_DIR=~/.openclaw/workspace/xhs-daily-skill-output/$DATE

echo "=== 小红书每日工作流 ==="
echo "日期: $DATE"

# ========== 步骤1: 检查内容完整性 ==========
echo ""
echo "📋 步骤1: 检查内容完整性..."

# 检查图片目录
if [ ! -d "$OUTPUT_DIR/images" ]; then
    echo "❌ 错误: 图片目录不存在，请先生成图片"
    exit 1
fi

# 检查封面图
if [ ! -f "$OUTPUT_DIR/images/cover.png" ]; then
    echo "❌ 错误: 封面图不存在"
    exit 1
fi

# 统计正文配图数量
ILLUST_COUNT=$(ls $OUTPUT_DIR/images/illust-*.png 2>/dev/null | wc -l | tr -d ' ')
echo "   封面图: 1 张"
echo "   正文配图: $ILLUST_COUNT 张"

if [ "$ILLUST_COUNT" -lt 3 ]; then
    echo "❌ 错误: 正文配图不足3张"
    exit 1
fi

# 检查最终版正文
FINAL_TEXT=""
for f in "$OUTPUT_DIR/text/step-06-final.md" "$OUTPUT_DIR/text/step-06-final.txt" "$OUTPUT_DIR/text/step-05-xhs-format.md"; do
    if [ -f "$f" ]; then
        FINAL_TEXT="$f"
        break
    fi
done

if [ -z "$FINAL_TEXT" ]; then
    echo "❌ 错误: 正文不存在"
    exit 1
fi

# 提取正文内容
TEXT_CONTENT=$(cat "$FINAL_TEXT")
TEXT_LEN=$(echo "$TEXT_CONTENT" | wc -c)

echo "   正文: $TEXT_LEN 字"

if [ "$TEXT_LEN" -lt 300 ]; then
    echo "❌ 错误: 正文太短 ($TEXT_LEN 字)"
    exit 1
fi

echo "✅ 内容检查通过"

# ========== 步骤2: 准备发布文件 ==========
echo ""
echo "📝 步骤2: 准备发布文件..."

mkdir -p /tmp/publish

# 标题 (从正文第一行提取，去掉# 和 emoji)
TITLE=$(echo "$TEXT_CONTENT" | head -n 1 | sed 's/^# *//' | sed 's/ 🚀$//' | sed 's/ 🔥$//')
echo "$TITLE" > /tmp/publish/title.txt

# 正文 (去掉标题行，保留完整内容)
echo "$TEXT_CONTENT" | tail -n +2 | sed '/^---$/d' > /tmp/publish/content.txt

echo "   标题: $(cat /tmp/publish/title.txt)"
echo "   正文: $(cat /tmp/publish/content.txt | wc -c) 字"

# ========== 步骤3: 检查登录状态 ==========
echo ""
echo "🔐 步骤3: 检查登录状态..."

cd ~/.openclaw/workspace/skills/xiaohongshu-skills
LOGIN_RESULT=$(python3 scripts/cli.py check-login 2>&1)
if echo "$LOGIN_RESULT" | grep -q '"logged_in": true'; then
    echo "   ✅ 已登录"
else
    echo "   ⚠️ 未登录，请扫码后运行: cd ~/.openclaw/workspace/skills/xiaohongshu-skills && python3 scripts/cli.py wait-login"
    exit 1
fi

# ========== 步骤4: 发布 ==========
echo ""
echo "🚀 步骤4: 发布笔记..."

# 收集所有图片
IMAGES_ARGS=""
IMAGES_ARGS="$IMAGES_ARGS --images $OUTPUT_DIR/images/cover.png"

for img in "$OUTPUT_DIR/images"/illust-*.png; do
    [ -f "$img" ] && IMAGES_ARGS="$IMAGES_ARGS --images $img"
done

TOTAL_IMAGES=$(echo "$IMAGES_ARGS" | tr ' ' '\n' | grep -c "images")
echo "   图片数量: $TOTAL_IMAGES 张"

# 构建命令
CMD="python3 scripts/cli.py publish \
  --title-file /tmp/publish/title.txt \
  --content-file /tmp/publish/content.txt \
  $IMAGES_ARGS \
  --tags 美伊局势 以色列 伊朗 中东 国际热点"

# 执行发布
echo "   执行发布..."
eval $CMD

echo ""
echo "✅ 工作流完成!"
echo "📝 笔记已发布成功"
