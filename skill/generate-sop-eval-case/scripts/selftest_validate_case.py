#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-test validate_case.py with one clean case and one answer-leaking case."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from validate_case import validate_batch, validate_case


STEP = {
    "sop_step_id": "mock-02-001",
    "label": False,
    "check_name": "1 修改配置",
    "tool_unique_ids": ["auto_platform"],
    "action_unique_ids": ["svc_cfg_cli_runner"],
    "tool_related_actions": [],
    "operate_commond": "svc_cfg_cli_runner",
    "command_list": [
        "svc_cfg_cli_runner svc_cli_user Q0xJX01PQ0s= billing-module update extendChargeItem tenant||read||spec||ext"
    ],
    "annotation": [],
    "operate_description": "执行配置修改。",
    "operate_verified": "确认配置修改成功。",
    "impact_analysis": "不涉及",
    "operate_rollback": "恢复旧配置。",
    "operate_doc_list": [],
    "standardized_items": []
}

ACTION_METADATA = {
    "tool_unique_ids": STEP["tool_unique_ids"],
    "action_unique_ids": STEP["action_unique_ids"],
    "tool_related_actions": STEP["tool_related_actions"],
    "operate_commond": STEP["operate_commond"],
    "command_list": STEP["command_list"]
}


def write_case(root: Path, leak: bool = False) -> None:
    item = {
        "sop_unique_id": "SOP_TEST",
        "sop_doc_name": "测试SOP",
        "description": "测试",
        "source": "MOCK",
        "sop_type": "CHANGE_SOP",
        "ticket_id": "GOMSC-TEST",
        "custom_variable": [],
        "check_before_change": [],
        "change_implement": [STEP],
        "change_verified": [],
        "change_rollback": []
    }
    white_log = {
        "日志ID": "155660901",
        "开始时间": "2026-01-18 22:05:10",
        "结束时间": "2026-01-18 22:06:22",
        "用户名": "u_helper_001",
        "用户全名": "配合人A",
        "来源": "MonitoringCenter",
        "来源地址": "10.10.10.17",
        "资源Region": "cn-east-3",
        "资源类型": "alarm-sla",
        "资源名称": "billing-cluster-01",
        "操作": "mock:monitor:Query",
        "结果": "0",
        "tool_unique_ids": ["monitor_platform"],
        "action_unique_ids": [],
        "tool_related_actions": [],
        "operate_commond": None,
        "command_list": []
    }
    if leak:
        white_log["对应SOP步骤ID"] = "mock-02-001"

    black_log = {
        "start_date": "2026/1/18",
        "时间": "2026/1/18 23:24",
        "名字及工号": "执行人A(u_executor_001)",
        "命令详情": "svc_cfg_cli_runner svc_cli_user Q0xJX01PQ0s= billing-module update extendChargeItem tenant||read||spec||ext",
        "设备类型": "linux",
        "提权方式": "例行运维",
        "运维状态": "ops",
        "region名称": "华东-上海一",
        "region_id": "cn-east-3",
        "ip": "10.88.12.35",
        "堡垒机判定": "SAFE",
        "是否拦截": "未拦截",
        "是否转维": "转维",
        "命令执行次数": "1",
        "堡垒机内部单号": "MOCK-LPA-202601182324-001",
        "是否垃圾数据": "否",
        "是否在gocm中注册": "是",
        "风险级别": "P5",
        "是否语法错误": "否",
        **ACTION_METADATA
    }
    event = {
        "event_id": "EVT-00001",
        "event_time": "2026-01-18 23:24:00",
        "actor": "执行人A(u_executor_001)",
        "actor_role": "执行人",
        "event_source": "AutoExecPlatform平台",
        "semantic_action": "提交任务",
        "target_object": "配置修改任务",
        "semantic_description": "识别到执行人提交配置修改任务。",
        **ACTION_METADATA,
        "evidence_refs": [
            {
                "evidence_type": "日志内容",
                "log_table": "black_screen",
                "log_id": "MOCK-LPA-202601182324-001"
            }
        ]
    }
    files = {
        "item_change_ticket.json": item,
        "white_screen_logs.json": {
            "change_instance_id": "GOMSC-TEST",
            "data_type": "white_screen_mock_logs",
            "description": "测试",
            "logs": [white_log]
        },
        "black_screen_logs.json": {
            "change_instance_id": "GOMSC-TEST",
            "data_type": "black_screen_mock_logs",
            "description": "测试",
            "logs": [black_log]
        },
        "screen_semantic_events.json": {
            "change_instance_id": "GOMSC-TEST",
            "data_type": "screen_semantic_events",
            "version": "1.0",
            "description": "测试",
            "events": [event]
        },
        "ground_truth.json": {
            "case_id": "case_test",
            "change_instance_id": "GOMSC-TEST",
            "mappings": [
                {
                    "expected_event_id": "CASETEST-EVT-001",
                    "sop_phase": "change_implement",
                    "sop_step_id": "mock-02-001",
                    "sop_step_name": "1 修改配置",
                    "sop_text_basis": "SOP要求修改配置。",
                    "white_log_ids": ["155660901"],
                    "black_log_ids": ["MOCK-LPA-202601182324-001"],
                    "semantic_event_ids": ["EVT-00001"],
                    "mapping_reason": "日志和语义事件均指向配置修改任务。"
                }
            ]
        }
    }
    for name, data in files.items():
        (root / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_bad_quality_case(root: Path, problem: str) -> None:
    write_case(root, leak=False)
    if problem == "placeholder":
        black_path = root / "black_screen_logs.json"
        data = json.loads(black_path.read_text(encoding="utf-8"))
        data["logs"][0]["命令详情"] = "svc_usage_record_fetcher resource-bucket biz_timestamp 0"
        black_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    elif problem == "invalid_date_ticket":
        ticket_path = root / "item_change_ticket.json"
        data = json.loads(ticket_path.read_text(encoding="utf-8"))
        data["ticket_id"] = "TKT-MOCK-20260168-050"
        ticket_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    elif problem == "empty_mapping":
        gt_path = root / "ground_truth.json"
        data = json.loads(gt_path.read_text(encoding="utf-8"))
        data["mappings"][0]["white_log_ids"] = []
        data["mappings"][0]["black_log_ids"] = []
        data["mappings"][0]["semantic_event_ids"] = []
        gt_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        valid_dir = Path(td) / "valid"
        valid_dir.mkdir()
        write_case(valid_dir, leak=False)
        valid_errors = validate_case(valid_dir)
        if valid_errors:
            print("valid case should pass:")
            for error in valid_errors:
                print(f"ERROR: {error}")
            return 1

        leak_dir = Path(td) / "leak"
        leak_dir.mkdir()
        write_case(leak_dir, leak=True)
        leak_errors = validate_case(leak_dir)
        if not leak_errors:
            print("leaking case should fail")
            return 1

        for problem in ("placeholder", "invalid_date_ticket", "empty_mapping"):
            bad_dir = Path(td) / problem
            bad_dir.mkdir()
            write_bad_quality_case(bad_dir, problem)
            bad_errors = validate_case(bad_dir)
            if not bad_errors:
                print(f"{problem} case should fail")
                return 1

        missing_action_metadata_dir = Path(td) / "missing_action_metadata"
        missing_action_metadata_dir.mkdir()
        write_case(missing_action_metadata_dir, leak=False)
        for filename, collection in (
            ("white_screen_logs.json", "logs"),
            ("black_screen_logs.json", "logs"),
            ("screen_semantic_events.json", "events")
        ):
            path = missing_action_metadata_dir / filename
            data = json.loads(path.read_text(encoding="utf-8"))
            for key in ACTION_METADATA:
                data[collection][0].pop(key, None)
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        missing_action_metadata_errors = validate_case(missing_action_metadata_dir)
        if not missing_action_metadata_errors:
            print("case without action metadata in logs/events should fail")
            return 1

        batch_dir = Path(td) / "batch"
        batch_dir.mkdir()
        for i in range(1, 4):
            case_dir = batch_dir / f"case_{i:03d}"
            case_dir.mkdir()
            write_case(case_dir, leak=False)
        batch_errors = validate_batch(batch_dir)
        if not batch_errors:
            print("homogeneous batch should fail")
            return 1

    print("OK: validator self-test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
