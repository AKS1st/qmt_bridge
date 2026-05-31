# -*- coding: utf-8 -*-
"""
QMT Bridge CLI — qmt-server 命令行工具

用法:
    qmt-server start     启动服务（检查连接后转入后台）
    qmt-server stop      停止后台服务
    qmt-server log       查看日志（less 风格翻页）
"""

import os
import sys
import time
import signal
import argparse
import subprocess
from pathlib import Path

# ===== 路径常量 =====
_QMT_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _QMT_DIR.parent
_LOG_DIR = _PROJECT_DIR / "logs"
_PID_FILE = _LOG_DIR / "qmt-server.pid"
_LOG_FILE = _LOG_DIR / "qmt-server.log"


def _ensure_log_dir():
    _LOG_DIR.mkdir(parents=True, exist_ok=True)


# ====================================================================
#  pid 管理
# ====================================================================

def _read_pid():
    """读取 PID 文件，返回进程ID或None"""
    if not _PID_FILE.exists():
        return None
    try:
        with open(_PID_FILE) as f:
            return int(f.read().strip())
    except (ValueError, IOError):
        return None


def _write_pid(pid):
    """写入 PID 文件"""
    _ensure_log_dir()
    with open(_PID_FILE, "w") as f:
        f.write(str(pid))


def _remove_pid():
    """删除 PID 文件"""
    try:
        _PID_FILE.unlink(missing_ok=True)
    except Exception:
        pass


def _is_process_running(pid):
    """检测指定 PID 的进程是否存活（跨平台）"""
    if pid is None:
        return False
    try:
        if sys.platform == "win32":
            # Windows: 用 tasklist 检查
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True, text=True,
            )
            return str(pid) in result.stdout
        else:
            os.kill(pid, 0)
            return True
    except (OSError, ProcessLookupError):
        return False


# ====================================================================
#  start — 连接检查 + 后台启动
# ====================================================================

def _check_connection():
    """
    导入 server 模块并检查 xttrade/xtdata 连接是否可用。
    返回 True 表示连接成功，False 表示失败。
    失败原因直接打印到 stderr。
    """
    print("正在检查 QMT 连接...", file=sys.stderr)
    try:
        from qmt import server
        from qmt.server import init_xtrade, logger
    except ImportError as e:
        print(f"无法导入 server 模块: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"初始化 server 模块失败: {e}", file=sys.stderr)
        return False

    # 检查 xtdata 可用性
    try:
        from qmt.server import xtdata
        # 尝试获取沪深A股列表，验证行情连接
        stock_list = xtdata.get_stock_list_in_sector("沪深A股")
        if stock_list and len(stock_list) > 0:
            print(f"  xtdata 行情连接成功 (沪深A股 {len(stock_list)} 只)", file=sys.stderr)
        else:
            print("  xtdata 行情连接失败: 获取股票列表为空", file=sys.stderr)
            return False
    except Exception as e:
        print(f"  xtdata 行情连接失败: {e}", file=sys.stderr)
        return False

    # 检查 xttrade 可用性
    try:
        ok = init_xtrade()
        if ok:
            print(f"  xttrade 交易连接成功", file=sys.stderr)
        else:
            print(f"  xttrade 交易连接失败", file=sys.stderr)
            return False
    except Exception as e:
        print(f"  xttrade 交易连接失败: {e}", file=sys.stderr)
        return False

    return True


def cmd_start(args):
    """启动服务：检查连接 → 成功后转入后台静默运行"""

    # 1. 检查是否已在运行
    pid = _read_pid()
    if pid and _is_process_running(pid):
        print(f"服务已在运行中 (PID: {pid})")
        return

    # 清理残留 PID 文件
    if pid:
        _remove_pid()

    # 2. 连接检查（前台执行，失败直接报错退出）
    if not _check_connection():
        print("\n[错误] QMT 连接失败，服务启动中止。请检查 QMT_PATH 和 ACCOUNT_ID 配置。", file=sys.stderr)
        sys.exit(1)

    # 3. 启动后台进程
    _ensure_log_dir()
    print("\n连接检查通过，启动后台服务...", file=sys.stderr)

    python_exe = sys.executable

    if sys.platform == "win32":
        # Windows: DETACHED_PROCESS 实现后台静默
        proc = subprocess.Popen(
            [python_exe, "-m", "qmt.cli", "_daemon"],
            stdout=open(_LOG_FILE, "a"),
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        # Linux/macOS: start_new_session 实现 daemon
        proc = subprocess.Popen(
            [python_exe, "-m", "qmt.cli", "_daemon"],
            stdout=open(_LOG_FILE, "a"),
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )

    # 4. 等待子进程写入 PID 文件
    for _ in range(30):  # 最多等3秒
        time.sleep(0.1)
        new_pid = _read_pid()
        if new_pid and _is_process_running(new_pid):
            print(f"服务已启动 (PID: {new_pid})")
            print(f"日志文件: {_LOG_FILE}")
            return

    print("[警告] 服务进程可能启动失败，请查看日志文件", file=sys.stderr)
    sys.exit(1)


def cmd_daemon(_args=None):
    """后台守护进程入口（内部使用，不由用户直接调用）"""
    # 必须在导入 server 之前设置，触发文件日志输出
    os.environ["QMT_DAEMON"] = "1"
    _write_pid(os.getpid())

    try:
        from qmt.server import main
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        _remove_pid()


# ====================================================================
#  stop — 停止后台服务
# ====================================================================

def cmd_stop(args):
    """停止后台服务"""
    pid = _read_pid()

    if pid is None:
        print("未找到运行中的服务 (PID 文件不存在)")
        return

    if not _is_process_running(pid):
        print(f"PID {pid} 对应的进程已不存在，清理 PID 文件")
        _remove_pid()
        return

    print(f"正在停止服务 (PID: {pid})...")

    if sys.platform == "win32":
        try:
            subprocess.run(["taskkill", "/PID", str(pid), "/F"],
                           capture_output=True, check=True)
            print("服务已停止")
        except subprocess.CalledProcessError:
            print(f"无法停止进程 {pid}", file=sys.stderr)
    else:
        try:
            os.kill(pid, signal.SIGTERM)
            # 等待进程退出
            for _ in range(50):  # 最多等5秒
                time.sleep(0.1)
                if not _is_process_running(pid):
                    break
            if _is_process_running(pid):
                os.kill(pid, signal.SIGKILL)
                time.sleep(0.5)
            print("服务已停止")
        except ProcessLookupError:
            print("进程已不存在")
        except Exception as e:
            print(f"停止失败: {e}", file=sys.stderr)

    _remove_pid()


# ====================================================================
#  log — less 风格日志查看器
# ====================================================================

def _get_single_key():
    """跨平台获取单个按键"""
    if sys.platform == "win32":
        import msvcrt
        while True:
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                # 处理特殊按键
                if ch == b'\xe0':
                    ch2 = msvcrt.getch()
                    if ch2 == b'H':  # 上箭头
                        return 'KEY_UP'
                    elif ch2 == b'P':  # 下箭头
                        return 'KEY_DOWN'
                    elif ch2 == b'I':  # Page Up
                        return 'KEY_PAGE_UP'
                    elif ch2 == b'Q':  # Page Down
                        return 'KEY_PAGE_DOWN'
                    elif ch2 == b'G':  # Home
                        return 'KEY_HOME'
                    elif ch2 == b'O':  # End
                        return 'KEY_END'
                try:
                    return ch.decode('utf-8', errors='replace')
                except Exception:
                    return '?'
            time.sleep(0.05)  # 降低 CPU 占用
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = os.read(fd, 3)
            if ch == b'\x1b[A':
                return 'KEY_UP'
            elif ch == b'\x1b[B':
                return 'KEY_DOWN'
            elif ch == b'\x1b[5':
                return 'KEY_PAGE_UP'
            elif ch == b'\x1b[6':
                return 'KEY_PAGE_DOWN'
            elif ch == b'\x1b[H':
                return 'KEY_HOME'
            elif ch == b'\x1b[F':
                return 'KEY_END'
            else:
                return ch.decode('utf-8', errors='replace')
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def cmd_log(args):
    """less 风格查看日志文件

    操作键:
      j / ↓       下移一行
      k / ↑       上移一行
      Space / PgDn 下翻一页
      b / PgUp    上翻一页
      g / Home    跳到开头
      G / End     跳到末尾
      f            开启实时追踪（tail -f）
      q / Ctrl+C  退出
      h           显示帮助
    """
    log_file = args.file if args.file else str(_LOG_FILE)

    if not os.path.exists(log_file):
        print(f"日志文件不存在: {log_file}")
        sys.exit(1)

    if args.follow:
        _cmd_log_follow(log_file)
    else:
        _cmd_log_pager(log_file)


def _cmd_log_follow(log_file):
    """实时追踪模式：tail -f 风格"""
    print(f"实时追踪: {log_file}  (Ctrl+C 退出)")
    print("-" * 60)

    try:
        with open(log_file, encoding="utf-8", errors="replace") as f:
            # 先跳到文件末尾
            f.seek(0, os.SEEK_END)

            while True:
                line = f.readline()
                if line:
                    print(line, end='')
                else:
                    time.sleep(0.3)
    except KeyboardInterrupt:
        print("\n已退出追踪")


def _cmd_log_pager(log_file):
    """分页查看模式"""
    # 读取全部日志行
    with open(log_file, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    if not lines:
        print("(日志为空)")
        return

    total_lines = len(lines)
    term_height = os.get_terminal_size().lines
    page_size = max(term_height - 2, 1)  # 留两行给状态栏
    current_pos = max(total_lines - page_size, 0)  # 默认显示最后页（类似 tail）
    all_on_screen = total_lines <= page_size

    def _show_page():
        """显示当前页"""
        os.system('cls' if sys.platform == 'win32' else 'clear')
        end = min(current_pos + page_size, total_lines)
        for i in range(current_pos, end):
            print(lines[i], end='')
        # 状态栏
        if all_on_screen:
            status = f"(共 {total_lines} 行 — 全部显示 | f 实时追踪 | q 退出 | h 帮助)"
        else:
            pct = int(min(current_pos + page_size, total_lines) / total_lines * 100)
            status = (f"行 {current_pos + 1}-{end} / {total_lines} ({pct}%) "
                      f"| j/k 滚动 | Space 翻页 | f 追踪 | q 退出 | h 帮助")
        print(f"\n\x1b[7m {status} \x1b[0m")

    _show_page()

    try:
        while True:
            key = _get_single_key()

            if key in ('q', 'Q', '\x03'):  # q 或 Ctrl+C
                break
            elif key in ('f', 'F'):
                # 切换到实时追踪模式
                break  # 退出 pager，由调用方决定——这里直接退出即可，用户会看到提示
            elif key in ('j', 'KEY_DOWN'):
                if current_pos + page_size < total_lines:
                    current_pos += 1
            elif key in ('k', 'KEY_UP'):
                if current_pos > 0:
                    current_pos -= 1
            elif key in (' ', 'KEY_PAGE_DOWN'):
                if not all_on_screen:
                    current_pos = min(current_pos + page_size, max(total_lines - page_size, 0))
            elif key in ('b', 'B', 'KEY_PAGE_UP'):
                if not all_on_screen:
                    current_pos = max(current_pos - page_size, 0)
            elif key in ('g', 'KEY_HOME'):
                current_pos = 0
            elif key in ('G', 'KEY_END'):
                current_pos = max(total_lines - page_size, 0)
            elif key in ('h', 'H'):
                _show_help()
                if sys.platform == "win32":
                    import msvcrt
                    msvcrt.getch()
                else:
                    input("按任意键返回...")
                _show_page()
                continue

            _show_page()
    except KeyboardInterrupt:
        pass

    # 退出后恢复终端
    print()  # 换行


def _show_help():
    """显示帮助信息"""
    os.system('cls' if sys.platform == 'win32' else 'clear')
    help_text = """
╔══════════════════════════════════════════════╗
║        QMT Server 日志查看器 — 操作帮助         ║
╠══════════════════════════════════════════════╣
║  j / ↓          下移一行                      ║
║  k / ↑          上移一行                      ║
║  Space / PgDn   向下翻一页                    ║
║  b / PgUp       向上翻一页                    ║
║  g / Home       跳到文件开头                  ║
║  G / End        跳到文件末尾                  ║
║  f              实时追踪（tail -f）           ║
║  h              显示此帮助                    ║
║  q / Ctrl+C     退出查看器                    ║
╚══════════════════════════════════════════════╝
"""
    print(help_text)


# ====================================================================
#  命令行入口
# ====================================================================

def main():
    parser = argparse.ArgumentParser(
        prog="qmt-server",
        description="QMT Bridge 服务管理工具",
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # start
    parser_start = subparsers.add_parser("start", help="启动服务（检查连接后转入后台）")
    parser_start.set_defaults(func=cmd_start)

    # stop
    parser_stop = subparsers.add_parser("stop", help="停止后台服务")
    parser_stop.set_defaults(func=cmd_stop)

    # log
    parser_log = subparsers.add_parser("log", help="查看日志（less 风格翻页，-f 实时追踪）")
    parser_log.add_argument("file", nargs="?", default=None,
                            help="日志文件路径（默认: logs/qmt-server.log）")
    parser_log.add_argument("-f", "--follow", action="store_true",
                            help="实时追踪模式（tail -f 风格，自动刷新新日志）")
    parser_log.set_defaults(func=cmd_log)

    # _daemon (内部命令)
    parser_daemon = subparsers.add_parser("_daemon", add_help=False,
                                          help=argparse.SUPPRESS)
    parser_daemon.set_defaults(func=cmd_daemon)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
