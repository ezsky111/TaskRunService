#!/usr/bin/env python3
"""
示例任务 B - 使用上下文变量处理数据
演示如何读取任务A生成的上下文变量
"""

import sys
import os
import json
from datetime import datetime

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
    print(f"[{datetime.now().isoformat()}] ===== 任务B: 使用上下文变量处理数据 =====")
    print(f"[{datetime.now().isoformat()}] 开始执行...")
    
    # 从环境变量读取任务A生成的随机字符串
    random_string = os.getenv('random_string', 'DEFAULT_NO_CONTEXT')
    task_a_completed = os.getenv('task_a_completed', 'false')
    timestamp_from_a = os.getenv('timestamp', 'UNKNOWN')
    
    print(f"[{datetime.now().isoformat()}] 从任务A获取的随机字符串: {random_string}")
    print(f"[{datetime.now().isoformat()}] 从任务A获取的时间戳: {timestamp_from_a}")
    print(f"[{datetime.now().isoformat()}] 任务A是否已完成: {task_a_completed}")
    
    # 检查是否成功获取了上下文
    if random_string == 'DEFAULT_NO_CONTEXT':
        print(f"[{datetime.now().isoformat()}] 警告: 未获取到任务A的上下文变量!")
    else:
        print(f"[{datetime.now().isoformat()}] 成功获取任务A的上下文变量!")
    
    items = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    
    print(f"[{datetime.now().isoformat()}] 处理数据条数: {items}")
    print(f"[{datetime.now().isoformat()}] 使用随机字符串: {random_string[:8]}... 进行数据关联")
    
    results = process_data(random_string, items)
    
    print(f"[{datetime.now().isoformat()}] 处理结果:")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # 生成新的上下文变量供下一个任务使用
    next_context = {
        "task_b_completed": True,
        "processed_items": len(results),
        "original_random_string": random_string
    }
    print(f"__CONTEXT__{json.dumps(next_context)}")
    
    print(f"[{datetime.now().isoformat()}] 数据处理任务完成!")
    print(f"[{datetime.now().isoformat()}] 已生成新的上下文变量")
    return 0

if __name__ == '__main__':
    sys.exit(main())
