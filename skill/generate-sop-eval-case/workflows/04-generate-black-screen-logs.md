# 04 生成黑屏日志

## Purpose

根据 `item_change_ticket.json` 生成终端、命令行、堡垒机、脚本执行类日志。

## Inputs

- `item_change_ticket.json`
- `white_screen_logs.json`

## Read Now

- `schemas/black_screen_logs.schema.json`
- `references/id-time-and-evidence-rules.md`
- `references/forbidden-answer-leakage.md`
- `references/action-metadata-fields.md`
- 只有字段示例不清楚时，读取 `examples/black_screen_log_record.json`

## Do Not Read Yet

- 不读 ground truth workflow
- 不生成 SOP 对应关系

## Steps

1. 为有命令、脚本或终端查询动作的 step 生成黑屏日志。
2. 黑屏日志适合：
   - 执行 `operate_commond`
   - 执行 `command_list` 中的命令
   - grep、配置查询、批量节点查询
   - 配置修改、缓存刷新、业务明细下载/过滤
   - 回退命令和回退验证命令
3. `命令详情` 必须来自 `command_list`，或是符合 raw SOP 与运维逻辑的必要命令。
4. 每条黑屏日志都必须额外写入动作检索抓手字段：
   - `tool_unique_ids`
   - `action_unique_ids`
   - `tool_related_actions`
   - `operate_commond`
   - `command_list`
5. 抓手字段应来自对应 SOP step。黑屏 `command_list` 应包含支撑该命令的 SOP 命令或实例化命令。没有对应值时使用空数组或 `null`，不要编造。
6. 不要生成平台页面查看类黑屏日志；那应放白屏。
7. 不要在日志里写 SOP 对应答案。

## Output

- `black_screen_logs.json`

## Quality Gate

- 字段严格符合 `black_screen_logs.schema.json`。
- 无答案泄露字段。
- 命令参数与 `item_change_ticket.json` 中变量一致。
