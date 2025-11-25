#!/usr/bin/env python3
"""
示例任务 B - 使用上下文变量处理数据
演示如何读取任务A生成的上下文变量
"""

import sys
import os
import json
from datetime import datetime
import time
from app.utils import task_sdk

def process_data(random_string, items=5):
    """处理数据，使用来自任务A的随机字符串"""
    results = []
    for i in range(items):
        results.append({
            'id': i,
            'value': i * 2,
            'timestamp': datetime.now().isoformat(),
            'random_string': random_string,  # 使用从任务A获得的随机字符串
            'combined': f"{random_string}-{i}"
        })
    return results

def main():
    task_sdk.log(f"[{datetime.now().isoformat()}] ===== 任务B: 使用上下文变量处理数据 =====", level='INFO')
    task_sdk.log(f"[{datetime.now().isoformat()}] 开始执行...", level='INFO')
    time.sleep(30)
    # 从共享上下文读取任务A生成的随机字符串（优先使用 SDK）
    random_string = task_sdk.get('random_string', 'DEFAULT_NO_CONTEXT')
    task_a_completed = task_sdk.get('task_a_completed', False)
    timestamp_from_a = task_sdk.get('timestamp', 'UNKNOWN')
    
    task_sdk.log(f"[{datetime.now().isoformat()}] 从任务A获取的随机字符串: {random_string}", level='INFO')
    task_sdk.log(f"[{datetime.now().isoformat()}] 从任务A获取的时间戳: {timestamp_from_a}", level='INFO')
    task_sdk.log(f"[{datetime.now().isoformat()}] 任务A是否已完成: {task_a_completed}", level='INFO')
    
    # 检查是否成功获取了上下文
    if random_string == 'DEFAULT_NO_CONTEXT':
        task_sdk.log(f"[{datetime.now().isoformat()}] 警告: 未获取到任务A的上下文变量!", level='WARNING')
    else:
        task_sdk.log(f"[{datetime.now().isoformat()}] 成功获取任务A的上下文变量!", level='INFO')
    
    items = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    
    task_sdk.log(f"[{datetime.now().isoformat()}] 处理数据条数: {items}", level='INFO')
    task_sdk.log(f"[{datetime.now().isoformat()}] 使用随机字符串: {random_string[:8]}... 进行数据关联", level='INFO')
    
    results = process_data(random_string, items)
    
    task_sdk.log(f"[{datetime.now().isoformat()}] 处理结果:", level='INFO')
    task_sdk.log(json.dumps(results, indent=2, ensure_ascii=False), level='INFO')
    
    # 生成新的上下文变量供下一个任务使用（通过 SDK 更新共享代理）
    next_context = {
        "task_b_completed": True,
        "processed_items": len(results),
        "original_random_string": random_string
    }
    try:
        task_sdk.update_context(next_context)
    except Exception:
        # 兼容回退：仍然打印 __CONTEXT__ 以便旧实现解析
        print(f"__CONTEXT__{json.dumps(next_context)}")
    
    task_sdk.log(f"[{datetime.now().isoformat()}] 数据处理任务完成!", level='INFO')
    task_sdk.log(f"[{datetime.now().isoformat()}] 已生成新的上下文变量", level='INFO')
    return 0

if __name__ == '__main__':
    sys.exit(main())
