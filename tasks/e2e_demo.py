#!/usr/bin/env python3
"""End-to-end demo: run hello.py then data_process.py using Manager proxy.

验证：
 - hello.py 将写入上下文（使用 __CONTEXT__ 或 SDK）
 - data_process.py 使用 SDK 读取并更新上下文
"""
import time
from multiprocessing import Manager
from pathlib import Path
from app.utils.script_runner import run_script


BASE = Path(__file__).resolve().parents[1]
HELLO = str(BASE / 'tasks' / 'hello.py')
DATA = str(BASE / 'tasks' / 'data_process.py')


def main():
    m = Manager()
    proxy = m.dict()

    print('Running hello.py ...')
    out1, rc1, to1 = run_script(HELLO, env=None, cwd=str(BASE), timeout=20, context_proxy=proxy)
    print('hello return:', rc1, 'timeout:', to1)
    print(out1)
    # 如果脚本仍然使用旧的 __CONTEXT__ 输出，解析并写入代理以兼容
    try:
        for line in (out1 or '').splitlines():
            if '__CONTEXT__' in line:
                idx = line.find('__CONTEXT__')
                json_str = line[idx + len('__CONTEXT__'):].strip()
                import json
                try:
                    ctx = json.loads(json_str)
                    proxy.update(ctx)
                except Exception:
                    pass
    except Exception:
        pass
    print('proxy after hello:', dict(proxy))

    print('\nRunning data_process.py ...')
    out2, rc2, to2 = run_script(DATA, params=['3'], env=None, cwd=str(BASE), timeout=60, context_proxy=proxy)
    print('data_process return:', rc2, 'timeout:', to2)
    print(out2)
    print('proxy after data_process:', dict(proxy))

    m.shutdown()


if __name__ == '__main__':
    main()
