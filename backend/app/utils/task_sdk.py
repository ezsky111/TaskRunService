"""脚本端 SDK：提供获取/更新运行时上下文的简单接口。

使用方式（脚本内）::
    from app.utils import task_sdk
    ctx = task_sdk.get_context()
    task_sdk.update_context({'key': 'value'})

该 SDK 优先使用 `task_ipc.CONTEXT_PROXY`（由 runner 注入的 `multiprocessing.Manager().dict()` 代理）。
如果代理不可用，SDK 会回退到读取环境变量，并仍然支持打印 `__CONTEXT__` 以兼容旧版实现。
"""
import os
import json
from typing import Any, Dict

from app.utils import task_ipc


def _proxy_available():
    try:
        return task_ipc.get_proxy() is not None
    except Exception:
        return False


def get_context() -> Dict[str, Any]:
    """返回当前上下文（非代理时基于环境变量）。"""
    if _proxy_available():
        proxy = task_ipc.get_proxy()
        try:
            return dict(proxy)
        except Exception:
            return {}

    # fallback: read env vars that are simple JSON or strings
    ctx = {}
    for k, v in os.environ.items():
        # skip system vars by simple heuristic (lowercase keys we set)
        if k.islower():
            ctx[k] = v
    return ctx


def get(key, default=None):
    ctx = get_context()
    return ctx.get(key, default)


def update_context(update: Dict[str, Any]):
    """更新上下文。如果有 proxy 则写入代理，否则打印 __CONTEXT__ 供上层解析。"""
    if not isinstance(update, dict):
        raise ValueError('update must be a dict')

    if _proxy_available():
        proxy = task_ipc.get_proxy()
        # shallow update
        for k, v in update.items():
            try:
                proxy[k] = v
            except Exception:
                pass
        return True

    # fallback: emit __CONTEXT__ to stdout to keep backward compatibility
    try:
        print(f"__CONTEXT__{json.dumps(update, ensure_ascii=False)}")
        return True
    except Exception:
        return False


def log(message: str, level: str = 'INFO'):
    """Emit a log message. If a LOG_QUEUE is injected, push a tuple (level, message).
    Otherwise fall back to printing to stdout.
    """
    try:
        q = task_ipc.get_log_queue()
        if q is not None:
            try:
                q.put((level, str(message)))
                return True
            except Exception:
                pass
    except Exception:
        pass

    # fallback
    try:
        print(f"[{level}] {message}")
        return True
    except Exception:
        return False


def set_key(key: str, value: Any):
    return update_context({key: value})
