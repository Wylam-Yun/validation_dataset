---
name: generate-sop-eval-case
description: Use when generating high-quality SOP evaluation cases from raw_sop.json, especially when black-screen logs, white-screen logs, semantic GUI events, and separate ground truth mappings must stay schema-compatible and answer-leak free.
---

# 生成 SOP 评测 Case

## 核心原则

从 `raw_sop.json` 生成高质量评测 case。只做评测数据，不做训练数据，不生成干扰日志，除非用户明确要求。

必须只从 `raw_sop.json` 读取 SOP。不要读取 `sop.json`。

最终产物固定为：

- `item_change_ticket.json`
- `white_screen_logs.json`
- `black_screen_logs.json`
- `screen_semantic_events.json`
- `ground_truth.json`

前四个文件是题目数据，禁止泄露答案。`ground_truth.json` 是唯一允许写 SOP、日志、语义事件对应关系的答案文件。

白屏日志、黑屏日志、语义事件必须保留动作检索抓手字段：

- `tool_unique_ids`
- `action_unique_ids`
- `tool_related_actions`
- `operate_commond`
- `command_list`

这些字段来自或继承自相关 SOP step，用于帮助后续 agent 检索和聚合证据。它们不是答案字段。

不是每个 SOP step 都有这些字段的非空值。没有值时保留字段并写空数组或 `null`，不要编造工具 ID 或动作 ID。字段含义见 `references/action-metadata-fields.md`。

## 渐进加载规则

严格按顺序执行 `workflows/`。不要一次性读取所有 workflow。

执行到某一步时，只读取该 workflow 指定的 schema、reference 或 example。不要提前读取后续 workflow，尤其不要在生成题目数据前读取 `06-generate-ground-truth.md`。

执行顺序：

1. `workflows/01-read-raw-sop.md`
2. `workflows/02-generate-item-change-ticket.md`
3. `workflows/03-generate-white-screen-logs.md`
4. `workflows/04-generate-black-screen-logs.md`
5. `workflows/05-generate-screen-semantic-events.md`
6. `workflows/06-generate-ground-truth.md`
7. `workflows/07-validate-case.md`
8. 批量生成时继续执行 `workflows/08-validate-batch-quality.md`

## 禁止答案泄露

日志和语义事件中禁止出现这些答案字段：

- `对应SOP阶段`
- `对应SOP步骤ID`
- `对应SOP步骤名称`
- `candidate_expected_event_id`
- `expected_event_id`
- `sop_phase`
- `sop_step_name`

这些字段或等价信息只能出现在 `ground_truth.json`。

注意：`item_change_ticket.json` 是 SOP 实例，必须保留 step 自身的 `sop_step_id` 字段；这不是答案泄露。

## 阶段边界

- `check_before_change`：变更前准入检查，确认平台、对象、依赖、告警、权限、窗口期等状态允许开始变更。
- `change_implement`：实际执行变更，以及执行过程中的即时技术确认。
- `change_verified`：变更完成后的业务或技术效果验证。
- `change_rollback`：失败或异常后的恢复动作和恢复验证。

四个阶段都可以基于 raw SOP 和运维知识补充合理步骤。补充步骤必须服务于该阶段语义，并且应能产生白屏日志、黑屏日志或语义事件证据。

## 批量生成硬规则

如果用户要求生成多个 case：

- 先完整生成并校验 1 个 pilot case。
- pilot case 通过后，再生成下一批。
- 可以使用脚本写文件，但脚本不能只是机械套同一个模板。
- 每个 case 必须有真实变化，不能只有 ID、租户或时间变化。
- 不允许所有 case 拥有完全相同的阶段 step 组合、日志数量、语义事件数量和 ground truth 数量。

## 完成条件

单个 case 执行 `scripts/validate_case.py <case_dir>`。批量 case 执行 `scripts/validate_case.py --batch <output_dir>`。所有检查通过后才算完成。
