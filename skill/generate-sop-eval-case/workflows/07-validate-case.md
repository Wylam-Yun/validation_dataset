# 07 校验 Case

## Purpose

对完整 case 做机器校验和人工质量检查。

## Inputs

case 目录，至少包含：

- `item_change_ticket.json`
- `white_screen_logs.json`
- `black_screen_logs.json`
- `screen_semantic_events.json`
- `ground_truth.json`

## Read Now

- 所有 `schemas/*.schema.json`
- `references/forbidden-answer-leakage.md`
- `references/id-time-and-evidence-rules.md`
- `scripts/validate_case.py`

## Steps

1. 运行：

```bash
python scripts/validate_case.py <case_dir>
```

2. 修复所有失败项。
3. 再次运行，直到通过。
4. 做人工检查：
   - SOP 内容是否被认真理解。
   - 黑屏日志是否只承载命令/终端/堡垒机动作。
   - 白屏日志是否只承载平台/API/页面/监控动作。
   - 语义事件是否是抽象识别结果，不是答案。
   - ground truth 是否完整且解释清楚。
   - 是否还存在 `resource-bucket`、`biz_timestamp`、尖括号或 `${...}` 变量占位符。
   - ground truth 每条 mapping 是否至少有一种证据。
   - `change_implement` 是否把多个实质命令挤进单个大 step。
   - 每条白屏、黑屏、语义事件是否都有动作检索抓手字段。

## Output

- 校验通过的完整 case 目录。

## Quality Gate

校验脚本必须退出码为 0。
