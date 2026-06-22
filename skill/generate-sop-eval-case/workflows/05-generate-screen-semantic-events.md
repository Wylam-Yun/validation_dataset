# 05 生成语义事件

## Purpose

根据 SOP 和黑白屏日志生成 GUI agent 识别出来的语义级事件。

## Inputs

- `item_change_ticket.json`
- `white_screen_logs.json`
- `black_screen_logs.json`

## Read Now

- `schemas/screen_semantic_events.schema.json`
- `references/id-time-and-evidence-rules.md`
- `references/forbidden-answer-leakage.md`
- `references/action-metadata-fields.md`
- 只有字段示例不清楚时，读取 `examples/screen_semantic_event_record.json`

## Do Not Read Yet

- 不读 ground truth workflow
- 不写 `candidate_expected_event_id`

## Steps

1. 模拟 GUI agent 从人机操作、页面、终端、日志证据中识别语义动作。
2. 语义事件粒度应高于单条日志：
   - 可以一条语义事件对应多条黑白屏日志。
   - 可以把连续页面操作抽象成一个“检查告警状态”事件。
   - 可以把命令执行与任务提交抽象成一个“提交配置修改任务”事件。
3. `evidence_refs` 可以引用：
   - 白屏日志 `日志ID`
   - 黑屏日志 `堡垒机内部单号`
   - 截图或视频帧 ID
4. 每条语义事件都必须额外写入动作检索抓手字段：
   - `tool_unique_ids`
   - `action_unique_ids`
   - `tool_related_actions`
   - `operate_commond`
   - `command_list`
5. 如果语义事件聚合多条日志，抓手字段取这些日志/SOP step 的并集，去重后写入。没有对应值时使用空数组或 `null`，不要编造。
6. `semantic_description` 写观察到的自然语言动作，不写 SOP step ID 或答案。
7. 不要复制日志字段，要做语义抽象。

## Output

- `screen_semantic_events.json`

## Quality Gate

- 字段严格符合 `screen_semantic_events.schema.json`。
- 不包含 `candidate_expected_event_id`。
- 每个 `evidence_refs` 引用的日志 ID 必须真实存在。
