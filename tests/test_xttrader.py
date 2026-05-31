# -*- coding: utf-8 -*-
"""
交易账户查询测试（只读，不涉及下单）

用法: pytest tests/test_xttrader.py -v -s
前置: Windows 服务端已启动 + MiniQMT 已登录，.env 中 ACCOUNT_ID 已填写
"""
import os
import time
from dotenv import load_dotenv

load_dotenv()

from qmt.xtquant.xttrader import XtQuantTrader
from qmt.xtquant.xttype import StockAccount

PATH = os.getenv("QMT_PATH", "")
SESSION_ID = int(os.getenv("TEST_SESSION_ID", "123456"))
ACCOUNT_ID = os.getenv("ACCOUNT_ID", "")
ACCOUNT_TYPE = os.getenv("TEST_ACCOUNT_TYPE", "STOCK")


def _trader():
    account = StockAccount(ACCOUNT_ID, ACCOUNT_TYPE)
    xt = XtQuantTrader(PATH, SESSION_ID)
    xt.start()
    xt.connect()
    xt.subscribe(account)
    time.sleep(1)
    return xt, account


def test_query_stock_asset():
    """查询账户资产"""
    xt, account = _trader()
    asset = xt.query_stock_asset(account)
    assert asset is not None
    assert "cash" in asset
    assert "total_asset" in asset


def test_query_stock_positions():
    """查询持仓（可能为空）"""
    xt, account = _trader()
    positions = xt.query_stock_positions(account)
    # 允许空持仓
    if positions is not None and len(positions) > 0:
        assert "stock_code" in positions[0]


def test_query_stock_orders():
    """查询当日委托（可能为空）"""
    xt, account = _trader()
    orders = xt.query_stock_orders(account)
    if orders is not None and len(orders) > 0:
        assert "stock_code" in orders[0]


def test_query_stock_trades():
    """查询当日成交（可能为空）"""
    xt, account = _trader()
    trades = xt.query_stock_trades(account)
    if trades is not None and len(trades) > 0:
        assert "stock_code" in trades[0]
