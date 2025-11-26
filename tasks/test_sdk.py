#!/usr/bin/env python3
"""Test script that uses task_sdk to write to shared context."""
from datetime import datetime
from app.utils import task_sdk

def main():
    task_sdk.log('test_sdk starting')
    task_sdk.update_context({'from_test': True, 'ts': datetime.now().isoformat()})
    task_sdk.log('test_sdk done')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
