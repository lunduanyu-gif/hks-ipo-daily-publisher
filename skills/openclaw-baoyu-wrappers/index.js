#!/usr/bin/env node

const { execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const BAOYU_IMAGE_GEN = 'C:/Users/77961/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py';
const OUTPUT_DIR = 'C:/Users/77961/.openclaw/workspace/baoyu-output';

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

function generateImage(prompt, outputPath) {
  const args = [
    BAOYU_IMAGE_GEN,
    '--prompt', prompt,
    '--filename', outputPath,
    '--resolution', '2K'
  ];
  console.log('Generating: ' + outputPath);
  try {
    execFileSync('python', args, { stdio: 'inherit', cwd: 'C:/Users/77961/.openclaw/workspace' });
    console.log('Generated: ' + outputPath);
  } catch (error) {
    console.error('Error: ' + error.message);
    throw error;
  }
}

const args = process.argv.slice(2);
const cmd = args[0];
if (!['cover', 'infographic', 'xhs'].includes(cmd)) {
  console.log('Usage: node index.js <cover|infographic|xhs> <content> [--style name] [--count n]');
  process.exit(1);
}

const content = args[1] || '';
let style = 'chalkboard';
let count = 6;

for (let i = 2; i < args.length; i++) {
  if (args[i] === '--style' && args[i+1]) style = args[++i];
  else if (args[i] === '--count' && args[i+1]) count = parseInt(args[++i]);
}

const timestamp = Date.now();
const NW = '图片不得包含任何水印、Logo或第三方平台标识。';

const coverPrompts = {
  chalkboard: 'chalkboard粉笔风格, 黑色黑板背景, 手写字体',
  retro: 'retro复古配色, 橙棕色调, 扁平矢量风格',
  warm: '暖色调, 温馨配色, 手绘风格',
  elegant: '优雅配色, 精致风格, 简约大方',
  minimal: '极简风格, 黑白灰配色, 几何图形',
  bold: '高对比配色, 醒目风格, 鲜艳色彩',
  tech: 'technical蓝图风格, 工程制图, 等距视角'
};

const xhsPrompts = {
  cute: 'cute可爱风格, 粉色系, 卡通元素',
  retro: 'retro复古风格, 暖色系, 扁平矢量',
  chalkboard: 'chalkboard粉笔风格, 黑板背景',
  notion: 'notion风格, 简约设计, 知识卡片',
  bold: 'bold醒目风格, 高对比, 强视觉冲击',
  tech: 'technical蓝图风格, 工程制图, 等距视角'
};

const infogPrompts = {
  chalkboard: 'chalkboard粉笔风格, 黑色黑板背景, 手写字体',
  craft: 'craft手工艺风格, 纸质纹理, 手工制作',
  corporate: 'corporate Memphis风格, 扁平矢量, 鲜艳填充',
  tech: 'technical蓝图风格, 工程制图, 等距视角',
  retro: '复古风格, 怀旧配色, 经典设计'
};

if (cmd === 'cover') {
  const sp = coverPrompts[style] || coverPrompts.chalkboard;
  const prompt = '小红书封面图: 标题为 ' + content + '。' + sp + ', 竖版9:16, 简洁专业。图片仅允许出现与标题相关的文字。' + NW;
  generateImage(prompt, OUTPUT_DIR + '/cover-' + timestamp + '.png');
} else if (cmd === 'infographic') {
  const sp = infogPrompts[style] || infogPrompts.chalkboard;
  const prompt = '小红书信息卡片: 主题为 ' + content + '。' + sp + ', 竖版9:16, 信息要点布局, 简洁专业。图片仅允许出现与主题相关的数据和文字。' + NW;
  generateImage(prompt, OUTPUT_DIR + '/infographic-' + timestamp + '.png');
} else if (cmd === 'xhs') {
  const sp = xhsPrompts[style] || xhsPrompts.chalkboard;
  for (let i = 1; i <= count; i++) {
    const isCover = i === 1;
    let prompt;
    if (isCover) {
      prompt = '小红书封面图: 标题为 ' + content + '。' + sp + ', 竖版9:16, 简洁专业。图片仅允许出现与标题相关的文字。' + NW;
    } else {
      prompt = '小红书内容卡片: 主题为 ' + content + '。' + sp + ', 竖版9:16, 信息丰富, 段落清晰。图片仅允许出现与主题相关的内容元素。' + NW;
    }
    generateImage(prompt, OUTPUT_DIR + '/xhs-' + i + '-' + timestamp + '.png');
  }
}
console.log('完成');
