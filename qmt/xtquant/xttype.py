# -*- coding: utf-8 -*-
"""
数据类型定义（桩）

本文件包含 QMT Bridge 客户端所需的类型桩，用于：
1. StockAccount 的创建与 pickle 序列化/反序列化
2. 交易回调中各数据结构的类型识别

这些类定义与 QMT 协议结构保持一致，确保网络传输互通。
所有数据类均位于 qmt.xtquant.xttype 模块路径下。
"""
from . import xtconstant as _XTCONST_


class StockAccount:
    """证券账号类型，用于报单、撤单、查询等交易操作

    用法::

        account = StockAccount("你的资金账号", "STOCK")

    :ivar account_id: 资金账号字符串
    :ivar account_type: 账号类型整数值（参见 xtconstant.ACCOUNT_TYPE_DICT）
    """

    def __new__(cls, account_id, account_type="STOCK"):
        if not isinstance(account_id, str):
            raise TypeError("account_id 必须为字符串类型")
        return super().__new__(cls)

    def __init__(self, account_id, account_type="STOCK"):
        account_type = account_type.upper()
        reversed_dict = {v: k for k, v in _XTCONST_.ACCOUNT_TYPE_DICT.items()}
        int_type = reversed_dict.get(account_type)
        if int_type is None:
            raise ValueError(f"不支持的账号类型: {account_type}")
        self.account_type = int_type
        self.account_id = account_id


# ══════════════════════════════════════════════════════════════════
# 以下类型桩用于服务器返回数据的反序列化兼容。
# 服务端通过 _make_picklable 已将 C 扩展对象转为 dict，
# 保留类定义确保 pickle 反序列化不因缺少类型而失败。
# ══════════════════════════════════════════════════════════════════


class XtAsset:
    """账户资金信息

    :ivar account_type: 账号类型（固定为 SECURITY_ACCOUNT）
    :ivar account_id: 资金账号
    :ivar cash: 可用资金
    :ivar frozen_cash: 冻结资金
    :ivar market_value: 持仓总市值
    :ivar total_asset: 总资产
    """
    def __init__(self, account_id="", cash=0.0, frozen_cash=0.0,
                 market_value=0.0, total_asset=0.0):
        self.account_type = _XTCONST_.SECURITY_ACCOUNT
        self.account_id = account_id
        self.cash = cash
        self.frozen_cash = frozen_cash
        self.market_value = market_value
        self.total_asset = total_asset


class XtOrder:
    """委托详情

    :ivar account_id: 资金账号
    :ivar stock_code: 证券代码，如 "600000.SH"
    :ivar order_id: 委托编号（系统分配的整数 ID）
    :ivar order_sysid: 柜台委托编号
    :ivar order_time: 报单时间
    :ivar order_type: 委托类型（STOCK_BUY=23 买 / STOCK_SELL=24 卖）
    :ivar order_volume: 委托数量（股/张）
    :ivar price_type: 报价类型（FIX_PRICE=11 限价 / LATEST_PRICE=5 最新价 等）
    :ivar price: 委托价格
    :ivar traded_volume: 已成交数量
    :ivar traded_price: 成交均价
    :ivar order_status: 委托状态（48=未报 49=待报 50=已报 55=部成 56=已成 54=已撤 57=废单）
    :ivar status_msg: 状态描述文字（如废单原因）
    :ivar strategy_name: 策略名称
    :ivar order_remark: 委托备注
    """
    def __init__(self, account_id="", stock_code="", order_id=0, order_sysid="",
                 order_time=0, order_type=0, order_volume=0, price_type=0,
                 price=0.0, traded_volume=0, traded_price=0.0, order_status=0,
                 status_msg="", strategy_name="", order_remark="", direction=0,
                 offset_flag=0, stock_code1=""):
        self.account_type = _XTCONST_.SECURITY_ACCOUNT
        self.account_id = account_id
        self.stock_code = stock_code
        self.order_id = order_id
        self.order_sysid = order_sysid
        self.order_time = order_time
        self.order_type = order_type
        self.order_volume = order_volume
        self.price_type = price_type
        self.price = price
        self.traded_volume = traded_volume
        self.traded_price = traded_price
        self.order_status = order_status
        self.status_msg = status_msg
        self.strategy_name = strategy_name
        self.order_remark = order_remark
        self.direction = direction
        self.offset_flag = offset_flag
        self.stock_code1 = stock_code1


class XtTrade:
    """成交详情

    :ivar account_id: 资金账号
    :ivar stock_code: 证券代码
    :ivar traded_id: 成交编号
    :ivar traded_time: 成交时间
    :ivar traded_price: 成交价格
    :ivar traded_volume: 成交数量
    :ivar traded_amount: 成交金额
    :ivar order_id: 对应委托编号
    :ivar order_sysid: 柜台委托编号
    :ivar commission: 手续费
    """
    def __init__(self, account_id="", stock_code="", order_type=0, traded_id=0,
                 traded_time=0, traded_price=0.0, traded_volume=0,
                 traded_amount=0.0, order_id=0, order_sysid="",
                 strategy_name="", order_remark="", direction=0, offset_flag=0,
                 stock_code1="", commission=0.0):
        self.account_type = _XTCONST_.SECURITY_ACCOUNT
        self.account_id = account_id
        self.order_type = order_type
        self.stock_code = stock_code
        self.traded_id = traded_id
        self.traded_time = traded_time
        self.traded_price = traded_price
        self.traded_volume = traded_volume
        self.traded_amount = traded_amount
        self.order_id = order_id
        self.order_sysid = order_sysid
        self.strategy_name = strategy_name
        self.order_remark = order_remark
        self.direction = direction
        self.offset_flag = offset_flag
        self.stock_code1 = stock_code1
        self.commission = commission


class XtPosition:
    """持仓详情

    :ivar account_id: 资金账号
    :ivar stock_code: 证券代码
    :ivar volume: 持仓数量
    :ivar can_use_volume: 可用数量（可卖）
    :ivar open_price: 开仓价
    :ivar market_value: 持仓市值
    :ivar frozen_volume: 冻结数量
    :ivar on_road_volume: 在途股份
    :ivar yesterday_volume: 昨日持仓量
    :ivar avg_price: 持仓成本价
    """
    def __init__(self, account_id="", stock_code="", volume=0,
                 can_use_volume=0, open_price=0.0, market_value=0.0,
                 frozen_volume=0, on_road_volume=0, yesterday_volume=0,
                 avg_price=0.0, direction=0, stock_code1=""):
        self.account_type = _XTCONST_.SECURITY_ACCOUNT
        self.account_id = account_id
        self.stock_code = stock_code
        self.volume = volume
        self.can_use_volume = can_use_volume
        self.open_price = open_price
        self.market_value = market_value
        self.frozen_volume = frozen_volume
        self.on_road_volume = on_road_volume
        self.yesterday_volume = yesterday_volume
        self.avg_price = avg_price
        self.direction = direction
        self.stock_code1 = stock_code1


class XtOrderError:
    """委托失败信息

    :ivar account_id: 资金账号
    :ivar order_id: 委托编号
    :ivar error_id: 错误码
    :ivar error_msg: 错误描述
    :ivar strategy_name: 策略名称
    :ivar order_remark: 委托备注
    """
    def __init__(self, account_id="", order_id=0, error_id=None,
                 error_msg=None, strategy_name=None, order_remark=None):
        self.account_type = _XTCONST_.SECURITY_ACCOUNT
        self.account_id = account_id
        self.order_id = order_id
        self.error_id = error_id
        self.error_msg = error_msg
        self.strategy_name = strategy_name
        self.order_remark = order_remark


class XtCancelError:
    """撤单失败信息

    :ivar account_id: 资金账号
    :ivar order_id: 委托编号
    :ivar market: 交易市场（SH_MARKET=0 上海 / SZ_MARKET=1 深圳）
    :ivar order_sysid: 柜台委托编号
    :ivar error_id: 错误码
    :ivar error_msg: 错误描述
    """
    def __init__(self, account_id="", order_id=0, market=0, order_sysid="",
                 error_id=None, error_msg=None):
        self.account_type = _XTCONST_.SECURITY_ACCOUNT
        self.account_id = account_id
        self.order_id = order_id
        self.market = market
        self.order_sysid = order_sysid
        self.error_id = error_id
        self.error_msg = error_msg


class XtAccountStatus:
    """账号连接状态

    :ivar account_id: 资金账号
    :ivar account_type: 账号类型
    :ivar status: 状态码（-1=无效 0=正常 1=等待登录 2=登录中 3=失败
                  4=初始化 5=数据校正 6=已收盘 7=副链断开 8=系统停用 9=用户停用）
    """
    def __init__(self, account_id="", account_type=0, status=0):
        self.account_id = account_id
        self.account_type = account_type
        self.status = status
