---
name: openclaw-baoyu-wrappers
description: |
  Use when generating Baoyu cover images, infographics, or Xiaohongshu image sets from OpenClaw on Windows.
  Don't use when: you only need raw image prompting (use nano-banana-pro), text-only formatting, or direct social publishing.
  Trigger: "生成封面图", "信息图", "小红书配图", "baoyu wrapper", "cover image".

  ## ACI Parameters
  | param | type | required | description |
  |-------|------|----------|-------------|
  | command | enum | yes | One of `cover`, `infographic`, `xhs` |
  | content | string | yes | Core title or content summary used to build the prompt |
  | style | string | no | Visual style preset such as `chalkboard`, `retro`, `bold` |
  | output | string | no | Explicit output path; defaults to `workspace/baoyu-output/` |

  ## Error Handling
  | error_code | meaning | suggestion |
  |-----------|---------|-----------|
  | API_KEY_MISSING | Gemini key unavailable in env or `.env` | Load `.openclaw/.env` or set `GEMINI_API_KEY` / `GOOGLE_API_KEY` |
  | IMAGE_GEN_FAILED | Underlying Nano Banana image call failed | Retry once, then inspect stderr and prompt |
  | INVALID_COMMAND | Unsupported wrapper command | Use `cover`, `infographic`, or `xhs` |
  | OUTPUT_WRITE_FAILED | Output file could not be written | Check target path and permissions |
---

# OpenClaw Baoyu Wrappers

Thin OpenClaw-friendly wrappers around the Baoyu image generation flow.

## Commands

| Command | Purpose |
|--------|---------|
| `cover` | Generate a single cover image |
| `infographic` | Generate an infographic card |
| `xhs` | Generate a Xiaohongshu image set |

## Usage

```bash
node index.js cover "标题内容" --style chalkboard
node index.js infographic "要点摘要" --style retro
node index.js xhs "正文摘要" --style notion --count 6
```

## Notes

- Default output directory: `C:\Users\77961\.openclaw\workspace\baoyu-output`
- Wrapper delegates to `workspace/skills/nano-banana-pro/scripts/generate_image.py`
- Runtime now supports loading Gemini credentials from `.openclaw/.env`
