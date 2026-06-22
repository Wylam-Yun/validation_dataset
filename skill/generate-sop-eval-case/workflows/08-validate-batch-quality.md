# 08 批量质量校验

## Purpose

当用户要求生成多个 case 时，检查批量数据是否只是模板化复制。该阶段只在批量生成时执行。

## Inputs

批量输出目录，例如：

- `case_001`
- `case_002`
- `case_003`

每个 case 目录内必须包含五个标准文件。

## Read Now

- `scripts/validate_case.py`
- `references/id-time-and-evidence-rules.md`
- `references/forbidden-answer-leakage.md`

## Steps

1. 先逐个 case 运行单 case 校验。
2. 再运行批量校验：

```bash
python scripts/validate_case.py --batch <output_dir>
```

3. 如果批量校验失败，修复对应 case 后重跑。

## Batch Quality Gates

批量数据必须满足：

- 每个 case 都通过单 case schema 和质量检查。
- 所有 case 的关键 ID 不重复。
- 不允许所有 case 拥有完全相同的阶段 step 组合和证据数量。
- 不允许批量生成假日期 ID。
- 不允许保留未实例化占位符。
- 不允许 ground truth mapping 没有任何证据。

## Common Failure Patterns

- 只替换 `TenantId`、`ItemCode` 和编号，其他结构完全一样。
- `change_implement` 永远只有一个大 step。
- 每个 case 都是同样的 3 条黑屏、6 条白屏、7 个语义事件。
- ground truth 为了覆盖 SOP step 写空 mapping。
- 命令里还保留 `resource-bucket`、`biz_timestamp`、`<CLI访问凭据Base64编码>`。

## Output

批量校验通过的 case 目录。
