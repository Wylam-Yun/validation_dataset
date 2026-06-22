# 动作检索字段含义

这些字段来自 raw SOP step，用来描述“这个动作依赖什么工具、动作、命令”。它们是后续检索、聚合和对齐证据的抓手，不是 ground truth 答案。

不是每个 SOP step 都有这些字段的非空值。没有值时必须保留字段，并使用空数组或 `null`，不要为了填充而编造 ID。

## 字段含义

### `tool_unique_ids`

工具或平台能力 ID。表示该 step 依赖哪个工具、平台、监控系统、自动化平台或验证工具。

例子：

- `auto_platform`
- `monitor_platform`
- `probe_platform`
- `capacity_platform`

适合出现在白屏日志和语义事件中，也可以出现在黑屏日志中用于说明命令由哪个平台承载。

没有工具时写 `[]`。

### `action_unique_ids`

具体动作 ID。表示该 step 的业务动作、自动化脚本、平台操作或命令动作。

例子：

- `svc_cfg_cli_runner`
- `svc_usage_record_fetcher`
- `svc_config_reload`
- `query_alarm_status`
- `grep_config_snapshot`

涉及具体变更执行、脚本执行、验证脚本时通常应填写。没有明确动作 ID 时写 `[]`。

### `tool_related_actions`

工具和动作之间的结构化关联。用于表达“哪个工具上有哪些动作”。

如果 raw SOP 没有给出结构化关联，可以写 `[]`，不要编复杂对象。

如果要补充，保持简单，例如：

```json
[
  {
    "tool_unique_id": "auto_platform",
    "action_unique_id": "svc_cfg_cli_runner"
  }
]
```

### `operate_commond`

SOP 中的主命令、脚本名或入口动作名。字段名沿用原数据里的拼写 `commond`，不要改成 `command`。

例子：

- `svc_cfg_cli_runner`
- `svc_usage_record_fetcher`
- `grep`
- `cluster_parallel_grep`

没有命令或脚本时写 `null`。

### `command_list`

该 step 需要执行或检索的命令、URL、告警 ID、脚本参数列表。

例子：

- `svc_cfg_cli_runner svc_cli_user Q0xJ... billing-module add extendChargeItem tenant||item||spec||name`
- `grep -A 3 "tenant:item" /opt/app/service_layer/component/config/extension_item_mapping.json`
- `A-9001201-metric-delay`
- `https://internal-monitor.example.com/service-dashboard`

没有命令、URL 或关键检索词时写 `[]`。

## 下沉到日志和语义事件

白屏日志、黑屏日志、语义事件都必须包含这五个字段：

- `tool_unique_ids`
- `action_unique_ids`
- `tool_related_actions`
- `operate_commond`
- `command_list`

取值规则：

- 优先继承对应 SOP step 的字段。
- 如果日志只对应 step 的一部分动作，可以写该日志实际相关的子集。
- 如果语义事件聚合多条日志，写这些日志相关字段的并集并去重。
- 空值要保留字段：数组字段写 `[]`，`operate_commond` 写 `null`。

## 禁止

- 不要把 `sop_phase`、`sop_step_id`、`sop_step_name` 写进日志或语义事件。
- 不要为了让字段非空而编造不存在的工具 ID 或动作 ID。
- 不要把多个无关 step 的字段混在一个日志里。
