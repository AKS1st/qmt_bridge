# -*- coding: utf-8 -*-
"""
行情数据读取测试

用法: pytest tests/test_xtdata.py -v -s
前置: Windows 服务端已启动，.env 中 CLIENT_HOST / CLIENT_PORT 已配置
"""
import os
from dotenv import load_dotenv

load_dotenv()

from qmt.xtquant import xtdata

CODE = os.getenv("TEST_STOCK_CODE", "000001.SZ")
PERIOD = os.getenv("TEST_PERIOD", "1d")
START = os.getenv("TEST_START_TIME", "20250501")
END = os.getenv("TEST_END_TIME", "20250531")


def test_download_history_data():
    """下载历史K线"""
    xtdata.download_history_data(CODE, PERIOD, START, END)


def test_get_market_data():
    """读取K线（需先下载）"""
    data = xtdata.get_market_data(
        field_list=["open", "high", "low", "close", "volume"],
        stock_list=[CODE],
        period=PERIOD,
        start_time=START,
        end_time=END,
    )
    assert data is not None
    assert "close" in data
    assert not data["close"].empty
    assert CODE in data["close"].index
    assert data["close"].shape[1] > 0


def test_get_local_data():
    """读取本地缓存K线"""
    data = xtdata.get_local_data(
        field_list=["close"],
        stock_list=[CODE],
        period=PERIOD,
        start_time=START,
        end_time=END,
    )
    assert data is not None
    assert CODE in data


def test_get_divid_factors():
    """读取除权因子"""
    factors = xtdata.get_divid_factors(CODE, PERIOD)
    assert factors is not None


def test_get_full_kline():
    """读取当日全量K线（部分 QMT 版本可能不支持）"""
    try:
        kline = xtdata.get_full_kline([CODE], PERIOD)
    except Exception as e:
        if "function not realize" in str(e).lower() or "不支持" in str(e):
            import pytest
            pytest.skip("QMT 版本暂不支持此功能")
        raise
    assert isinstance(kline, dict)
