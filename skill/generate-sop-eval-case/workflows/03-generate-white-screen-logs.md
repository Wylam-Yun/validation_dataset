# 03 生成白屏日志

## Purpose

根据 `item_change_ticket.json` 生成平台、页面、API、监控、自动化平台类操作日志。

## Inputs

- `item_change_ticket.json`

## Read Now

- `schemas/white_screen_logs.schema.json`
- `references/id-time-and-evidence-rules.md`
- `references/forbidden-answer-leakage.md`
- `references/action-metadata-fields.md`
- 只有字段示例不清楚时，读取 `examples/white_screen_log_record.json`

## Do Not Read Yet

- 不读 ground truth workflow
- 不生成 SOP 对应关系

## Steps

1. 为 `item_change_ticket.json` 中适合白屏承载的动作生成日志。
2. 白屏日志适合：
   - 登录或进入平台
   - 查看告警、拨测、监控、容量、指标
   - 查询变更单参数
   - 自动化平台页面/API 操作
   - 任务提交记录或查询记录
3. 如果 step 有 `tool_unique_ids`、`action_unique_ids`、`operate_commond`，要自然体现在：
   - `来源`
   - `资源类型`
   - `资源名称`
   - `操作`
4. 每条白屏日志都必须额外写入动作检索抓手字段：
   - `tool_unique_ids`
   - `action_unique_ids`
   - `tool_related_actions`
   - `operate_commond`
   - `command_list`
5. 抓手字段应来自对应 SOP step。没有对应值时使用空数组或 `null`，不要省略字段，不要编造。
6. 不要在日志里写 SOP 对应答案。
7. 时间必须与后续黑屏日志、语义事件可组成同一条变更时间线。

## Output

- `white_screen_logs.json`

## Quality Gate

- 字段严格符合 `white_screen_logs.schema.json`。
- 无答案泄露字段。
- 每条日志内容能自然关联到某个 SOP 动作，但不显式写答案。
