# -*- coding: utf-8 -*-
"""
QMT 中转服务端（Windows运行）
同时处理 xtdata 和 xttrade 的代理请求
"""

import socket
import pickle
import struct
import traceback
import json
import logging
import os
import sys
import secrets
import hmac
import hashlib
from dotenv import load_dotenv

# 加载 .env 配置
load_dotenv()

# 服务端必须使用系统真实的 xtquant，但 pickle 反序列化又需要 qmt 路径
# 策略：临时从 sys.path 移除 qmt 目录 → 导入系统 xtquant → 恢复 qmt 路径
_qmt_dir = os.path.dirname(os.path.abspath(__file__))
_qmt_removed = False
if _qmt_dir in sys.path:
    sys.path.remove(_qmt_dir)
    _qmt_removed = True

from xtquant import xtdata
from xtquant import xttrader
from xtquant.xttype import StockAccount
from xtquant import xtconstant

# 恢复 qmt 路径，确保 pickle 能反序列化 qmt.xtquant.xttype.StockAccount
if _qmt_removed:
    sys.path.append(_qmt_dir)

# ===== 日志配置 =====
def setup_logging(to_file: bool = False, log_dir: str = None):
    """配置日志：控制台输出 或 文件输出（30天滚动分割）

    Args:
        to_file: 是否写入日志文件
        log_dir:  日志目录，默认项目根目录下的 logs/
    """
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 清除已有 handlers（避免重复添加）
    root_logger.handlers.clear()

    if to_file:
        from logging.handlers import TimedRotatingFileHandler
        if log_dir is None:
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "qmt-server.log")

        handler = TimedRotatingFileHandler(
            log_path,
            when="D",
            interval=30,
            backupCount=12,
            encoding="utf-8",
        )
        # 立即刷新：每条日志写完后立刻落盘，方便 qmt-server log -f 实时追踪
        _orig_flush = handler.stream.flush
        def _flush_and_sync():
            _orig_flush()
            os.fsync(handler.stream.fileno())
        handler.stream.flush = _flush_and_sync
        handler.setFormatter(fmt)
        handler.setLevel(logging.INFO)
        root_logger.addHandler(handler)
    else:
        # 控制台输出
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(fmt)
        handler.setLevel(logging.INFO)
        root_logger.addHandler(handler)

    return logging.getLogger(__name__)


# 默认使用控制台输出（直接 python server.py 时）
_is_daemon = os.environ.get("QMT_DAEMON", "0") == "1"
logger = setup_logging(to_file=_is_daemon)

# ===== 配置（从 .env 读取）=====
HOST = os.getenv("SERVER_HOST", "0.0.0.0")
PORT = int(os.getenv("SERVER_PORT", "8888"))
QMT_PATH = os.getenv("QMT_PATH", "")
ACCOUNT_ID = os.getenv("ACCOUNT_ID", "")
TOKEN = os.getenv("TOKEN", "")

# TOKEN 必填：未设置则生成建议值并拒绝启动
if not TOKEN:
    import string as _string
    _suggested = ''.join(secrets.choice(_string.ascii_letters + _string.digits) for _ in range(32))
    print(f"[错误] 未设置 TOKEN，请在 .env 中设置后重新启动:\n  TOKEN={_suggested}")
    sys.exit(1)

# ===== xttrade 全局实例 =====
xt_trader = None
account = None


def init_xtrade():
    """初始化 xttrade 交易模块"""
    global xt_trader, account
    import random

    # 创建交易实例
    session_id = random.randint(100000, 999999)
    xt_trader = xttrader.XtQuantTrader(QMT_PATH, session_id)
    xt_trader.start()

    # 连接 MiniQMT
    connect_result = xt_trader.connect()
    if connect_result == 0:
        logger.info("交易模块连接成功")
    else:
        logger.error("交易模块连接失败")
        return False

    # 创建并订阅账户
    account = StockAccount(ACCOUNT_ID)
    subscribe_result = xt_trader.subscribe(account)
    if subscribe_result == 0:
        logger.info("账户订阅成功, account_id=%s", ACCOUNT_ID)
        return True
    else:
        logger.error("账户订阅失败")
        return False


def _summarize_result(result):
    """生成结果摘要，避免打印原始数据"""
    try:
        import pandas as pd
        if isinstance(result, pd.DataFrame):
            return f"DataFrame({result.shape[0]}行 x {result.shape[1]}列)"
    except ImportError:
        pass
    if isinstance(result, dict):
        return f"dict({len(result)}个键)"
    elif isinstance(result, (list, tuple)):
        return f"{type(result).__name__}({len(result)}项)"
    elif isinstance(result, str):
        if len(result) > 100:
            return f"str(长度{len(result)})"
        return f"str: {result!r}"
    elif isinstance(result, bytes):
        return f"bytes(长度{len(result)})"
    elif result is None:
        return "None"
    else:
        return f"{type(result).__name__}: {result!r}"


def handle_xtdata_call(func_name, args, kwargs):
    """处理 xtdata 模块的调用"""
    logger.info("xtdata.%s 调用, args=%s", func_name, str(args)[:200])
    func = getattr(xtdata, func_name)
    result = func(*args, **kwargs)
    logger.info("xtdata.%s 返回 -> %s", func_name, _summarize_result(result))
    return result


def _make_picklable(obj):
    """将 C 扩展对象/列表转为可 pickle 的 dict/list"""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool, bytes, dict)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_make_picklable(v) for v in obj]
    if hasattr(obj, "__dict__"):
        return {k: _make_picklable(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
    # C 扩展对象（如 XtAsset）：用 dir() 提取非可调用的公开属性
    try:
        attrs = [a for a in dir(obj) if not a.startswith("_")]
        data = {}
        for a in attrs:
            try:
                v = getattr(obj, a)
                if not callable(v):
                    data[a] = _make_picklable(v)
            except Exception:
                pass
        if data:
            return data
    except Exception:
        pass
    return str(obj)


def handle_xttrade_call(func_name, args, kwargs):
    """处理 xttrader 模块的调用"""
    # 需要补全 account 参数的函数列表
    need_account = ["order_stock", "order_stock_async", "cancel_order_stock",
                    "query_stock_asset", "query_stock_orders", "query_stock_trades",
                    "query_positions"]
    # 不需要补全的列表（类方法或不使用 account）
    no_account = ["run", "stop", "on_stock_order", "get_order_id"]

    # 补全 account 参数
    if func_name in need_account and account is not None:
        modified_args = list(args)
        if len(modified_args) == 0 or (isinstance(modified_args[0], str) and modified_args[0] == ACCOUNT_ID):
            modified_args.insert(0, account)
        args = tuple(modified_args)

    logger.info("xttrader.%s 调用, args=%s", func_name, str(args)[:200])

    # 调用真实函数
    if hasattr(xt_trader, func_name):
        func = getattr(xt_trader, func_name)
        result = func(*args, **kwargs)
        logger.info("xttrader.%s 返回 -> %s", func_name, _summarize_result(result))
        return result
    else:
        raise AttributeError(f"xttrader模块没有函数: {func_name}")


def handle_call(module, func_name, args, kwargs):
    """路由分发到不同模块"""
    if module == "xtdata":
        return handle_xtdata_call(func_name, args, kwargs)
    elif module == "xttrader":
        return handle_xttrade_call(func_name, args, kwargs)
    else:
        raise ValueError(f"不支持的模块: {module}")


def _recv_exact(conn, n):
    data = b""
    while len(data) < n:
        chunk = conn.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def main():
    # 初始化 xttrade（失败不影响服务启动，xtdata 仍可用）
    try:
        init_xtrade()
    except Exception as e:
        logger.warning("xttrade 初始化失败: %s，交易功能不可用，行情功能正常", e)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)
        logger.info("服务端启动, 监听 %s:%s", HOST, PORT)
        logger.info("支持模块: xtdata, xttrader")

        while True:
            conn, addr = s.accept()
            logger.info("新连接来自 %s", addr)
            with conn:
                # ---- TOKEN 认证（HMAC 挑战-响应，TOKEN 不传输） ----
                nonce = secrets.token_bytes(32)
                conn.sendall(struct.pack(">I", 32) + nonce)

                raw_len = _recv_exact(conn, 4)
                if not raw_len:
                    continue
                msg_len = struct.unpack(">I", raw_len)[0]
                if msg_len != 64:  # SHA256 hex digest = 64 bytes
                    logger.warning("认证失败（响应长度异常）: %s", addr)
                    resp = pickle.dumps({"error": "TOKEN 认证失败"})
                    conn.sendall(struct.pack(">I", len(resp)) + resp)
                    break
                response_data = _recv_exact(conn, msg_len)
                if not response_data:
                    continue
                expected = hmac.new(TOKEN.encode("utf-8"), nonce, hashlib.sha256).hexdigest()
                if not hmac.compare_digest(response_data.decode("utf-8"), expected):
                    logger.warning("认证失败: %s", addr)
                    resp = pickle.dumps({"error": "TOKEN 认证失败"})
                    conn.sendall(struct.pack(">I", len(resp)) + resp)
                    break
                # ---- 认证通过，处理请求 ----
                while True:
                    try:
                        # 接收消息长度（4字节大端）
                        raw_len = _recv_exact(conn, 4)
                        if not raw_len:
                            break
                        msg_len = struct.unpack(">I", raw_len)[0]
                        # 接收完整消息体
                        data = _recv_exact(conn, msg_len)
                        if not data:
                            break
                        # 消息格式: (module, func_name, args, kwargs)
                        module, func_name, args, kwargs = pickle.loads(data)
                        logger.info("收到请求: %s.%s", module, func_name)
                        # 调用处理函数
                        result = handle_call(module, func_name, args, kwargs)
                        result = _make_picklable(result)
                        resp = pickle.dumps(result)
                        conn.sendall(struct.pack(">I", len(resp)) + resp)
                    except Exception as e:
                        # 将异常信息返回给客户端
                        err_msg = traceback.format_exc()
                        logger.error("调用异常: %s", err_msg.splitlines()[-1] if err_msg.strip() else str(e))
                        resp = pickle.dumps({"error": err_msg})
                        conn.sendall(struct.pack(">I", len(resp)) + resp)


if __name__ == "__main__":
    main()