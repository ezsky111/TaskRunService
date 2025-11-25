import os
import sys
import io
import runpy
import traceback
from multiprocessing import Process, Queue
from app.utils import task_ipc


def _worker(script_path, params, env, cwd, q: Queue, context_proxy=None, log_queue=None):
    try:
        # apply env and cwd
        if env is not None:
            os.environ.clear()
            os.environ.update(env)
        if cwd:
            try:
                os.chdir(cwd)
            except Exception:
                pass

        # make sure project backend package is importable by scripts
        try:
            backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
        except Exception:
            pass

        # inject context proxy and log queue into task_ipc so script SDK can access them
        try:
            if context_proxy is not None:
                task_ipc.CONTEXT_PROXY = context_proxy
        except Exception:
            pass
        try:
            if log_queue is not None:
                task_ipc.LOG_QUEUE = log_queue
        except Exception:
            pass

        # prepare argv
        sys.argv = [script_path] + (params or [])

        # capture stdout/stderr; when a log_queue is injected we will NOT
        # return buffered output (only SDK logs will be kept).
        sio = io.StringIO()
        old_out, old_err = sys.stdout, sys.stderr

        class QueueWriter:
            def __init__(self, buffer, queue=None, level='INFO'):
                self.buffer = buffer
                self.queue = queue
                self.level = level
                self._linebuf = ''

            def write(self, s):
                try:
                    self.buffer.write(s)
                except Exception:
                    pass
                # stream lines to queue if available
                if self.queue is not None and s:
                    try:
                        self._linebuf += s
                        while '\n' in self._linebuf:
                            line, self._linebuf = self._linebuf.split('\n', 1)
                            try:
                                self.queue.put((self.level, line))
                            except Exception:
                                pass
                    except Exception:
                        pass

            def flush(self):
                try:
                    if self._linebuf and self.queue is not None:
                        try:
                            self.queue.put((self.level, self._linebuf))
                        except Exception:
                            pass
                        self._linebuf = ''
                except Exception:
                    pass

        # resolve injected queue; SDK.log will put messages into task_ipc.LOG_QUEUE
        injected_q = None
        try:
            injected_q = task_ipc.get_log_queue()
        except Exception:
            injected_q = None

        # If an injected log queue exists, we intentionally DO NOT stream
        # regular print() output into it — only messages explicitly sent
        # via task_sdk.log() (which writes into task_ipc.LOG_QUEUE) should
        # be considered persistent. Therefore, when injected_q is present
        # we pass queue=None to QueueWriter to avoid duplicating prints.
        try:
            writer_queue = None if injected_q is not None else injected_q
            sys.stdout = QueueWriter(sio, queue=writer_queue, level='INFO')
            sys.stderr = QueueWriter(sio, queue=writer_queue, level='ERROR')
            # run the script as __main__ so if it checks __name__ == '__main__' it executes
            runpy.run_path(script_path, run_name="__main__")
            # flush any remaining buffered text
            try:
                sys.stdout.flush()
            except Exception:
                pass
            try:
                sys.stderr.flush()
            except Exception:
                pass
            # If a log queue was injected, we will not return the buffered
            # stdout/stderr to the parent; consumer should rely on the
            # injected queue contents (task_sdk.log). Return empty output
            # in that case to avoid duplicate storage.
            if injected_q is not None:
                q.put({"output": "", "returncode": 0})
            else:
                output = sio.getvalue()
                q.put({"output": output, "returncode": 0})
        finally:
            sys.stdout = old_out
            sys.stderr = old_err
    except SystemExit as se:
        # capture exit code
        try:
            code = int(se.code) if se.code is not None else 0
        except Exception:
            code = 1
        output = '' if 'sio' in locals() and injected_q is not None else (sio.getvalue() if 'sio' in locals() else '')
        q.put({"output": output, "returncode": code})
    except Exception:
        tb = traceback.format_exc()
        output = '' if 'sio' in locals() and injected_q is not None else ((sio.getvalue() + "\n" + tb) if 'sio' in locals() else tb)
        q.put({"output": output, "returncode": 1})


def run_script(script_path, params=None, env=None, cwd=None, timeout=None, context_proxy=None, log_queue=None):
    """Run a Python script in a separate forked process and capture its output.

    Returns (output: str, returncode: int, timed_out: bool).
    """
    q = Queue()
    p = Process(target=_worker, args=(script_path, params, env, cwd, q, context_proxy, log_queue))
    p.start()
    p.join(timeout)
    if p.is_alive():
        # timeout: terminate process
        try:
            p.terminate()
        except Exception:
            pass
        p.join(1)
        # try to get any partial output
        partial = None
        try:
            if not q.empty():
                res = q.get_nowait()
                partial = res.get('output', '')
        except Exception:
            partial = None
        out = partial or f"ERROR: 脚本执行超时 ({timeout}s)"
        return out, -1, True

    # finished normally
    try:
        res = q.get(timeout=1)
        return res.get('output', ''), res.get('returncode', 0), False
    except Exception:
        return "", -1, False
