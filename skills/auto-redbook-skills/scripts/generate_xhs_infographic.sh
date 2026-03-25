#!/bin/bash
# 小红书信息图生成脚本
# 确保使用专业风格、竖屏、详细模式

set -e

# 默认参数
THEME="professional"
MODE="auto-split"
WIDTH=1080
HEIGHT=1440
DPR=2

# 解析参数
INPUT_FILE=""
OUTPUT_DIR="."

usage() {
    echo "用法: $0 <输入Markdown文件> [选项]"
    echo ""
    echo "选项:"
    echo "  -o, --output-dir <目录>    输出目录 (默认: 当前目录)"
    echo "  -t, --theme <主题>         主题 (默认: professional)"
    echo "  -m, --mode <模式>         分页模式 (默认: auto-split)"
    echo "  -h, --help                显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 content.md -o ./output"
    echo "  $0 content.md -t professional -m auto-split"
    exit 1
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -t|--theme)
            THEME="$2"
            shift 2
            ;;
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        -*)
            echo "未知选项: $1"
            usage
            ;;
        *)
            INPUT_FILE="$1"
            shift
            ;;
    esac
done

# 检查输入文件
if [ -z "$INPUT_FILE" ]; then
    echo "错误: 请指定输入文件"
    usage
fi

if [ ! -f "$INPUT_FILE" ]; then
    echo "错误: 输入文件不存在: $INPUT_FILE"
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 显示配置
echo "📋 生成配置:"
echo "  输入: $INPUT_FILE"
echo "  输出: $OUTPUT_DIR"
echo "  主题: $THEME"
echo "  模式: $MODE"
echo "  尺寸: ${WIDTH}x${HEIGHT} @ ${DPR}x"
echo ""

# 执行渲染
echo "🎨 正在渲染图片..."
python3 scripts/render_xhs.py "$INPUT_FILE" \
    -o "$OUTPUT_DIR" \
    -t "$THEME" \
    -m "$MODE" \
    -w "$WIDTH" \
    -h "$HEIGHT" \
    --dpr "$DPR"

echo ""
echo "✅ 渲染完成!"
echo "📁 输出文件: $OUTPUT_DIR/cover.png"
ls -la "$OUTPUT_DIR"/card_*.png 2>/dev/null || true
