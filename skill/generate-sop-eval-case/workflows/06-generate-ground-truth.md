# 06 生成 Ground Truth

## Purpose

单独生成标准答案文件，记录 SOP、黑白屏日志、语义事件之间的一一或多对一对应关系。

## Inputs

- `item_change_ticket.json`
- `white_screen_logs.json`
- `black_screen_logs.json`
- `screen_semantic_events.json`

## Read Now

- `schemas/ground_truth.schema.json`
- 只有字段示例不清楚时，读取 `examples/ground_truth_mapping_record.json`

## Steps

1. 逐个读取 `item_change_ticket.json` 的四阶段 step。
2. 为每个有可观察证据的 SOP step 建立 mapping。
3. mapping 中写：
   - SOP 阶段
   - SOP step ID
   - SOP step 名称
   - 依据的 SOP 文本
   - 对应白屏日志 ID
   - 对应黑屏日志 ID
   - 对应语义事件 ID
   - 映射原因
4. 允许：
   - 一个 SOP step 对应多条日志
   - 多条日志支撑一个语义事件
   - 一个 SOP step 没有某类日志，但必须解释证据类型
5. `ground_truth.json` 是答案文件，不作为评测输入给被测 agent。

## Output

- `ground_truth.json`

## Quality Gate

- 符合 `ground_truth.schema.json`。
- 引用的日志 ID、事件 ID 都真实存在。
- 所有 `sop_step_id` 都存在于 `item_change_ticket.json`。
