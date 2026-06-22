# 答案泄露禁令

题目数据包括 `item_change_ticket.json`、`white_screen_logs.json`、`black_screen_logs.json`、`screen_semantic_events.json`。其中 `item_change_ticket.json` 是 SOP 实例，必须保留 `sop_step_id` 等 SOP 自身字段。

禁止的是把日志或语义事件直接标注为某个 SOP step 的答案。

## 禁止字段

- `对应SOP阶段`
- `对应SOP步骤ID`
- `对应SOP步骤名称`
- `candidate_expected_event_id`
- `expected_event_id`
- `sop_phase`
- `sop_step_name`

`sop_step_id` 在 `item_change_ticket.json` 中是合法字段；但不要把 `sop_step_id` 写进黑屏日志、白屏日志或语义事件。

## 禁止写法

不要在日志或语义描述中写：

- “该日志对应 mock-02-001”
- “属于 change_implement 阶段”
- “对应 CASE02-EVT-003”
- “SOP步骤名称为……”

可以自然描述业务对象、命令、平台、动作和结果。

## 唯一例外

`ground_truth.json` 是答案文件，可以写上述字段和对应关系。
