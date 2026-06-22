# Examples

这些 examples 只用于理解字段形状，不是完整 case。

不要复制其中的 ID、时间、租户、Region、IP、step 内容或变量值。生成真实 case 时必须根据用户提供的 `raw_sop.json` 和目标场景重新生成。

默认不要读取 examples。只有 workflow 明确要求“字段示例不清楚时”才读取对应 example。

白屏、黑屏、语义事件示例中的 `tool_unique_ids`、`action_unique_ids`、`tool_related_actions`、`operate_commond`、`command_list` 只是字段形状示例。真实 case 应继承对应 SOP step 的值；如果没有值，写空数组或 `null`。
