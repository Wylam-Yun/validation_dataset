# ID、时间和证据规则

## ID 规则

- `change_instance_id`：同一个 case 的所有文件必须一致。
- 白屏 `日志ID`：使用数字字符串，保持递增，例如 `155660901`。
- 黑屏 `堡垒机内部单号`：使用可读唯一值，例如 `MOCK-LPA-202601182324-001`。
- 语义事件 `event_id`：使用 `EVT-00001` 递增。
- ground truth `expected_event_id`：使用 case 前缀，例如 `CASE02-EVT-001`。

如果 ID 中包含 `YYYYMMDD` 形式日期，日期必须真实存在。禁止生成 `20260168`、`20260050`、`20261301` 这类假日期。

## 占位符禁令

生成后的 case 不允许保留未实例化占位符：

- `<CLI访问凭据Base64编码>` 或任何 `<...>`
- `resource-bucket`
- `biz_timestamp`
- 除 `custom_variable` 字段外的 `${TenantId}`、`${ItemCode}` 或任何 `${...}`

这些内容如果来自 raw SOP 示例，生成 case 时必须替换成具体值。

## 时间规则

时间线必须符合运维顺序：

1. 变更前检查
2. 实际执行变更
3. 执行后即时确认
4. 变更后验证
5. 如需要，执行回退和回退验证

格式要求：

- 白屏时间：`YYYY-MM-DD HH:mm:ss`
- 语义事件时间：`YYYY-MM-DD HH:mm:ss`
- 黑屏 `start_date`：`YYYY/M/D`
- 黑屏 `时间`：`YYYY/M/D HH:mm`

## 证据引用规则

语义事件的 `evidence_refs` 可以引用白屏或黑屏日志：

```json
{
  "evidence_type": "日志内容",
  "log_table": "white_screen",
  "log_id": "155660901",
  "time_range": "2026-01-18 22:05:10 ~ 2026-01-18 22:06:22"
}
```

```json
{
  "evidence_type": "日志内容",
  "log_table": "black_screen",
  "log_id": "MOCK-LPA-202601182324-001",
  "time_range": "2026-01-18 23:24:00 ~ 2026-01-18 23:24:59"
}
```

也可以引用截图或视频帧：

```json
{
  "evidence_type": "截图",
  "evidence_id": "screen_155660901_001"
}
```

不要在 `evidence_refs` 中写 SOP 阶段、SOP step ID 或 ground truth 信息。
