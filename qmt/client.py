# -*- coding: utf-8 -*-
"""
QMT 客户端核心库
"""

import socket
import pickle
import struct
import os
import hmac
import hashlib
from dotenv import load_dotenv

# 加载 .env 配置
load_dotenv()

# ===== 配置（从 .env 读取）=====
QMT_SERVER_HOST = os.getenv("CLIENT_HOST", "")
QMT_SERVER_PORT = int(os.getenv("CLIENT_PORT", "0"))
TOKEN = os.getenv("TOKEN", "")


class QMTProxy:
    """通用 QMT 远程代理"""

    def __init__(self, module_name, host=None, port=None):
        self.module_name = module_name
        self.host = host or QMT_SERVER_HOST
        self.port = port or QMT_SERVER_PORT

    def __getattr__(self, name):
        def caller(*args, **kwargs):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))

                # ---- HMAC 挑战-响应认证（TOKEN 不传输）----
                # 1. 接收 nonce
                raw_len = b""
                while len(raw_len) < 4:
                    chunk = s.recv(4 - len(raw_len))
                    if not chunk:
                        raise ConnectionError("认证失败：服务端连接断开")
                    raw_len += chunk
                nonce_len = struct.unpack(">I", raw_len)[0]
                nonce = b""
                while len(nonce) < nonce_len:
                    chunk = s.recv(nonce_len - len(nonce))
                    if not chunk:
                        raise ConnectionError("认证失败：服务端连接断开")
                    nonce += chunk

                # 2. 计算 HMAC-SHA256(TOKEN, nonce) 并发送
                response = hmac.new(TOKEN.encode("utf-8"), nonce, hashlib.sha256).hexdigest()
                resp_bytes = response.encode("utf-8")
                s.sendall(struct.pack(">I", len(resp_bytes)) + resp_bytes)

                # 发送请求（包括模块名、函数名、参数）
                data = pickle.dumps((self.module_name, name, args, kwargs))
                s.sendall(struct.pack(">I", len(data)) + data)

                # 接收响应长度
                raw_len = b""
                while len(raw_len) < 4:
                    chunk = s.recv(4 - len(raw_len))
                    if not chunk:
                        raise ConnectionError("服务端连接断开")
                    raw_len += chunk
                msg_len = struct.unpack(">I", raw_len)[0]

                # 接收响应体
                resp_data = b""
                while len(resp_data) < msg_len:
                    chunk = s.recv(msg_len - len(resp_data))
                    if not chunk:
                        raise ConnectionError("服务端连接断开")
                    resp_data += chunk
                result = pickle.loads(resp_data)

                # 如果返回的是错误字典，则抛出异常
                if isinstance(result, dict) and "error" in result:
                    raise Exception(f"服务端异常:\n{result['error']}")
                return result
        return caller


# ===== 导出模块实例 =====
xtdata = QMTProxy("xtdata")
xttrader = QMTProxy("xttrader")