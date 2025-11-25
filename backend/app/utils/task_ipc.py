"""进程间上下文代理占位模块。
子进程运行时，`script_runner` 会在子进程中设置 `CONTEXT_PROXY`，脚本通过 `task_sdk` 访问该代理。
"""
CONTEXT_PROXY = None

# optional log queue injected by runner
LOG_QUEUE = None


def has_proxy():
    return CONTEXT_PROXY is not None


def get_proxy():
    return CONTEXT_PROXY


def get_log_queue():
    return LOG_QUEUE

