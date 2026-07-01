from __future__ import annotations


def minimal_parsed() -> dict:
    return {
        "file_name": "minimal.cpt",
        "fr_version": "11.0",
        "sheet_count": 1,
        "file_size_kb": 12.3,
        "report_type": "query",
        "datasets": [
            {
                "name": "ds_sales",
                "type": "EmbeddedTableData",
                "columns": ["region", "amount"],
            }
        ],
        "widgets": [
            {
                "name": "region",
                "widget_type": "ComboBox",
                "bound_dataset": "ds_sales",
                "key_column": "region",
                "display_column": "region",
            }
        ],
        "cell_bindings": [
            {"pos": "A1", "dataset": "ds_sales", "column": "region", "data_mode": "list_group"},
            {"pos": "B1", "dataset": "ds_sales", "column": "amount", "data_mode": "aggregate"},
        ],
        "formula_cells": [
            {"pos": "C1", "formula": "=SUM(B1)"},
            {"pos": "D1", "formula": "=SUM(Z99)"},
        ],
        "label_data_pairs": [],
        "dataset_shared_keys": [],
        "highlight_rules_summary": [],
        "writeback_config": None,
        "db_connections": [],
        "errors": [],
    }


def minimal_analysis() -> dict:
    return {
        "purpose": "按区域查看销售金额。",
        "layout_description": "区域与金额列表。",
        "dataset_relationships": "单数据集报表。",
        "field_semantics": "region 为区域，amount 为销售额。",
        "interaction_chains": [{"widget_name": "region", "param_role": "筛选区域"}],
        "formula_explanations": [{"pos": "C1", "formula": "=SUM(B1)", "meaning": "汇总金额"}],
        "indicator_dict": [{"indicator_name": "销售额", "source_field": "amount", "type": "度量", "description": "销售额"}],
        "notes_or_risks": ["内置数据集样例需要真实数据复核。"],
        "development_steps": ["创建数据集", "配置控件", "设计单元格"],
    }
