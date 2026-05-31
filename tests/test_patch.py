# -*- coding: utf-8 -*-
"""
兼容旧用法测试：import qmt.patch 后正常 import xtquant

用法: pytest tests/test_patch.py -v
前置: Windows 服务端已启动
"""
import os
from dotenv import load_dotenv

load_dotenv()

import qmt.patch                 # noqa: E402
from xtquant import xtdata       # noqa: E402

CODE = os.getenv("TEST_STOCK_CODE", "000001.SZ")
PERIOD = os.getenv("TEST_PERIOD", "1d")
START = os.getenv("TEST_START_TIME", "20250501")
END = os.getenv("TEST_END_TIME", "20250531")


def test_patch_import():
    """通过 import qmt.patch 方式代理 xtquant"""
    assert xtdata is not None


def test_patch_remote_call():
    """通过 patch 方式的远程行情调用"""
    xtdata.download_history_data(CODE, PERIOD, START, END)
    data = xtdata.get_market_data(
        field_list=["close"],
        stock_list=[CODE],
        period=PERIOD,
        start_time=START,
        end_time=END,
    )
    assert data is not None
    assert "close" in data
    assert not data["close"].empty
