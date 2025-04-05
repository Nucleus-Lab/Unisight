import json
import pandas as pd
from typing import Dict, List, Any, Union

def normalize_json_for_pandas(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    将 MCP 服务器返回的 JSON 数据标准化为 Pandas 友好的格式。
    
    Args:
        data: MCP 服务器返回的原始 JSON 数据
        
    Returns:
        标准化后的 JSON 数据，适合转换为 Pandas DataFrame
    """
    # 如果数据为空，返回空字典
    if not data:
        return {}
    
    # 检查是否有嵌套的 items 列表
    if "items" in data and isinstance(data["items"], list):
        items = data["items"]
        
        # 如果列表为空，返回空字典
        if not items:
            return {"data": []}
        
        # 标准化每个项目
        normalized_items = []
        for item in items:
            flat_item = flatten_nested_json(item)
            normalized_items.append(flat_item)
        
        return {"data": normalized_items}
    
    # 如果没有 items 列表，尝试直接标准化
    return {"data": [flatten_nested_json(data)]}

def flatten_nested_json(nested_json: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """
    将嵌套的 JSON 对象扁平化，使其更适合 Pandas 处理。
    
    Args:
        nested_json: 嵌套的 JSON 对象
        prefix: 前缀，用于生成扁平化后的键名
        
    Returns:
        扁平化后的 JSON 对象
    """
    flattened = {}
    
    for key, value in nested_json.items():
        new_key = f"{prefix}_{key}" if prefix else key
        
        # 如果值是字典，递归扁平化
        if isinstance(value, dict):
            flattened.update(flatten_nested_json(value, new_key))
        # 如果值是列表且列表元素是字典，扁平化每个字典并创建新列表
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            # 对于简单列表，保留原始结构
            if len(value) <= 3 and all(len(item) <= 3 for item in value):
                flattened[new_key] = json.dumps(value)
            else:
                # 对于复杂列表，创建单独的列
                for i, item in enumerate(value):
                    item_key = f"{new_key}_{i}"
                    flattened.update(flatten_nested_json(item, item_key))
        else:
            # 简单值直接添加
            flattened[new_key] = value
    
    return flattened

def json_to_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    """
    将 JSON 数据转换为 Pandas DataFrame。
    
    Args:
        data: JSON 数据
        
    Returns:
        Pandas DataFrame
    """
    normalized_data = normalize_json_for_pandas(data)
    return pd.DataFrame(normalized_data.get("data", []))

# 示例用法
if __name__ == "__main__":
    # 示例 JSON 数据
    sample_data = {
        "items": [
            {
                "id": "123",
                "address": "0x123...",
                "details": {
                    "txHash": "0xabc...",
                    "blockNumber": 12345,
                    "tokenActions": [
                        {"address": "0xdef...", "amount": "100"}
                    ]
                }
            }
        ]
    }
    
    # 转换为 DataFrame
    df = json_to_dataframe(sample_data)
    print(df)