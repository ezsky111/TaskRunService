#!/usr/bin/env python3
"""
示例任务 A - 生成随机字符串
演示如何生成上下文变量供后续任务使用
"""

import sys
import os
import time
import uuid
import json
from datetime import datetime

def main():
    print(f"[{datetime.now().isoformat()}] ===== 任务A: 生成随机字符串 =====")
    print(f"[{datetime.now().isoformat()}] 开始执行...")
    
    # 生成随机字符串
    random_string = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    print(f"[{datetime.now().isoformat()}] 生成随机字符串: {random_string}")
    print(f"[{datetime.now().isoformat()}] 生成时间戳: {timestamp}")
    
    # 模拟一些处理
    for i in range(3):
        print(f"[{datetime.now().isoformat()}] 处理步骤 {i+1}/3")
        time.sleep(0.5)
    
    # 将上下文变量输出到标准输出
    # 格式: __CONTEXT__{"key": "value"}
    context = {
        "random_string": random_string,
        "timestamp": timestamp,
        "task_a_completed": True
    }
    print(f"__CONTEXT__{json.dumps(context)}")
    
    print(f"[{datetime.now().isoformat()}] 任务A执行完成!")
    print(f"[{datetime.now().isoformat()}] 已生成上下文变量供后续任务使用")
    return 0

if __name__ == '__main__':
    sys.exit(main())
