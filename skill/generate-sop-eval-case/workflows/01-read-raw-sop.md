# 01 读取 Raw SOP

## Purpose

理解 `raw_sop.json` 的结构、四个阶段、每个 step 的操作/验证/回退语义。此阶段只理解输入，不生成最终文件。

## Inputs

- `raw_sop.json`

## Read Now

- `schemas/raw_sop.schema.json`
- `references/action-metadata-fields.md`

## Do Not Read Yet

- 不读 `sop.json`
- 不读 ground truth workflow
- 不读 examples，除非字段形状不清楚

## Steps

1. 校验 `raw_sop.json` 是否符合 `raw_sop.schema.json`。
2. 读取顶层字段，保留所有业务字段和空值形态。
3. 重点读取四个阶段：
   - `check_before_change`
   - `change_implement`
   - `change_verified`
   - `change_rollback`
4. 对每个 step 关注：
   - `sop_step_id`
   - `check_name`
   - `tool_unique_ids`
   - `action_unique_ids`
   - `operate_commond`
   - `command_list`
   - `operate_description`
   - `operate_verified`
   - `operate_rollback`
5. 理解动作检索字段的含义。不是每个 step 都有非空值；空数组和 `null` 是合法信息，不要补造。
6. 识别 SOP 的变更对象、变量、命令、验证工具、回退方式和风险边界。

## Output

内部理解即可，不写中间文件。

## Quality Gate

必须能说明 raw SOP 中每个阶段大致要做什么，再进入下一阶段。
