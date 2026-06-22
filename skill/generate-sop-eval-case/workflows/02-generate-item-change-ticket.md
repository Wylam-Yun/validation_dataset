# 02 生成 Item Change Ticket

## Purpose

基于 `raw_sop.json` 生成实例化后的 `item_change_ticket.json`。这是评测输入中的 SOP 实例。

## Inputs

- `raw_sop.json`
- 用户给定或自行设定的 case 参数，例如租户、对象、Region、集群、IP、人员、时间窗口

## Read Now

- `schemas/item_change_ticket.schema.json`
- `references/ops-generation-rules.md`
- 只有字段示例不清楚时，读取 `examples/raw_sop_minimal.json` 和 `examples/item_change_ticket_step_record.json`

## Do Not Read Yet

- 不生成日志
- 不生成语义事件
- 不生成 ground truth

## Steps

1. 复制 raw SOP 顶层结构，保持字段名、数组、对象、null、布尔值格式。
2. 实例化顶层字段，例如：
   - `ticket_id`
   - `source`
   - `description`
   - `cloud_service`
   - `change_scene`
   - `custom_variable`
3. 对四个阶段都允许基于 raw SOP 和运维知识补全合理 step：
   - `check_before_change`：补平台运行状况、告警、拨测、容量、权限、窗口期、并行变更、上游依赖等准入检查。
   - `change_implement`：补执行脚本、修改配置、刷新缓存、执行结果即时确认等。
   - `change_verified`：补变更后告警复查、监控观察、业务明细验证、新配置生效、旧配置不再命中等。
   - `change_rollback`：补恢复旧配置、刷新缓存、回退后多节点确认、回退后业务和告警复查等。
4. 补充 step 时必须满足：
   - 能从 raw SOP 的操作、验证、回退文本找到依据，或属于该运维场景必需动作。
   - 能产生可观察证据。
   - 不跨阶段放错动作。
5. 字段规则：
   - 具体变更执行动作，合理填写 `action_unique_ids`。
   - 涉及工具、平台、监控或验证能力，合理填写 `tool_unique_ids`。
   - 涉及命令或脚本时，必须填写 `operate_commond` 和 `command_list`。
   - `operate_description`、`operate_verified`、`operate_rollback` 不写负责人。
   - `impact_analysis` 默认写 `不涉及`，除非 raw SOP 明确要求。
6. 不要保留未实例化占位符：
   - `custom_variable` 字段可以保留 raw SOP 的变量名，例如 `${TenantId}`。
   - 不要在 `operate_description`、`operate_verified`、`operate_rollback`、`command_list` 或日志相关内容中保留 `${TenantId}`、`${ItemCode}` 这类变量。
   - 不要把 `custom_variable` 写成 `${TenantId}=tenant...` 这种赋值形式；具体值应体现在 SOP 文本、命令和日志中。
   - 不要保留 `resource-bucket`、`biz_timestamp` 这类示例参数。
   - 不要保留 `<CLI访问凭据Base64编码>` 这类尖括号占位符。
7. `ticket_id`、日志 ID、堡垒机内部单号等如果包含日期，日期必须真实合法。
8. `change_implement` 中如果一个 step 包含多个实质不同命令，应拆成多个 step。例如创建命令和 grep 验证命令通常不应挤在一个 step 里。

## Batch Gate

批量生成时，先生成 1 个 pilot case 并完成 workflow 03-07 校验。pilot case 通过后，才能批量扩展。

允许用脚本批量写 JSON，但脚本必须基于 per-case 参数和阶段组合生成，不允许所有 case 使用完全相同的 step 结构和证据数量。

## Output

- `item_change_ticket.json`

## Quality Gate

- 符合 `item_change_ticket.schema.json`。
- 四阶段语义边界清楚。
- 不包含答案字段。
