# -*- coding: utf-8 -*-
"""
qmt.xtquant — 客户端 xtquant 包入口

用户通过 `from qmt.xtquant import xtdata` 即可获得远程代理，
无需额外调用 patch。其他子模块（xttype、xtconstant 等）正常可用。

服务端使用系统真实的 xtquant，不受此包影响。
"""

__version__ = "xtquant_241014_b"

import sys
import types
from qmt.client import xtdata as _xtdata_proxy, xttrader as _xttrader_proxy

# ====================================================================
# 1. xtdata → 远程代理
# ====================================================================
xtdata = _xtdata_proxy

# ====================================================================
# 2. xttrader → 远程代理包装
# ====================================================================
class XtQuantTrader:
    """xttrader 代理类，实例方法透明转发到远程 Windows 服务端"""

    def __init__(self, path, session_id):
        self.path = path
        self.session_id = session_id
        self._proxy = _xttrader_proxy

    def start(self):
        pass

    def connect(self):
        # 远程端已完成连接，本地返回成功
        import random
        return 0

    def run(self):
        pass

    def stop(self):
        pass

    def subscribe(self, account):
        return 0

    def __getattr__(self, name):
        return getattr(self._proxy, name)

    def order_stock(self, account, stock_code, order_type, order_volume,
                    price_type, price, strategy_name="", order_remark=""):
        return self._proxy.order_stock(
            account, stock_code, order_type,
            order_volume, price_type, price,
            strategy_name, order_remark,
        )


# 创建 xttrader 子模块，覆盖本地 xttrader.py
xttrader = types.ModuleType("qmt.xtquant.xttrader")
xttrader.XtQuantTrader = XtQuantTrader
sys.modules["qmt.xtquant.xttrader"] = xttrader

# ====================================================================
# 3. 修复 StockAccount 的 pickle 支持（跨网络序列化）
# ====================================================================
from qmt.xtquant.xttype import StockAccount   # noqa: E402
from qmt.xtquant import xtconstant as _XTCONST_  # noqa: E402

_ACCOUNT_TYPE_REVERSE = {v: k for k, v in _XTCONST_.ACCOUNT_TYPE_DICT.items()}

def _stock_account_reduce(self):
    type_str = _ACCOUNT_TYPE_REVERSE.get(self.account_type, "STOCK")
    return (StockAccount, (self.account_id, type_str))

StockAccount.__reduce__ = _stock_account_reduce
