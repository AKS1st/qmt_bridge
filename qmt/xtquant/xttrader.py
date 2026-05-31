# -*- coding: utf-8 -*-
"""
xttrader 交易接口（桩）

本文件提供类和方法签名以及参数说明，用于 IDE 代码提示。
所有调用通过 QMT Bridge TCP 代理转发到 Windows 服务端执行。
以下文档来自 xtquant SDK 原始 docstring，确保与真实 SDK 一致。
"""


class XtQuantTraderCallback:
    """交易回调基类 — 继承此类并重写回调方法以接收事件推送"""

    def on_connected(self):
        """连接成功推送"""
        ...

    def on_disconnected(self):
        """连接断开推送"""
        ...

    def on_account_status(self, status):
        """:param status: XtAccountStatus对象"""
        ...

    def on_stock_asset(self, asset):
        """:param asset: XtAsset对象"""
        ...

    def on_stock_order(self, order):
        """:param order: XtOrder对象"""
        ...

    def on_stock_trade(self, trade):
        """:param trade: XtTrade对象"""
        ...

    def on_stock_position(self, position):
        """:param position: XtPosition对象"""
        ...

    def on_order_error(self, order_error):
        """:param order_error: XtOrderError 对象"""
        ...

    def on_cancel_error(self, cancel_error):
        """:param cancel_error: XtCancelError 对象"""
        ...

    def on_order_stock_async_response(self, response):
        """:param response: XtOrderResponse 对象"""
        ...

    def on_cancel_order_stock_async_response(self, response):
        """:param response: XtCancelOrderResponse 对象"""
        ...

    def on_smt_appointment_async_response(self, response):
        """:param response: XtSmtAppointmentResponse 对象"""
        ...


class XtQuantTrader:
    """交易接口 — 通过 TCP 代理到远程 Windows 服务端执行实际交易操作"""

    # ---- 生命周期 ----

    def start(self):
        """启动交易模块"""
        ...

    def stop(self):
        """停止交易模块"""
        ...

    def connect(self):
        """连接交易服务，返回连接结果"""
        ...

    def subscribe(self, account):
        """订阅账号
        :param account: 证券账号
        """
        ...

    def unsubscribe(self, account):
        """取消订阅账号
        :param account: 证券账号
        """
        ...

    def run(self):
        """阻塞运行等待回调"""
        ...

    # ---- 查询 ----

    def query_stock_asset(self, account):
        """:param account: 证券账号
        :return: 返回当前证券账号的资产数据
        """
        ...

    def query_stock_asset_async(self, account, callback):
        """:param account: 证券账号
        :return: 返回当前证券账号的资产数据
        """
        ...

    def query_stock_orders(self, account, cancelable_only=False):
        """:param account: 证券账号
        :param cancelable_only: 仅查询可撤委托
        :return: 返回当日所有委托的委托对象组成的list
        """
        ...

    def query_stock_orders_async(self, account, callback, cancelable_only=False):
        """:param account: 证券账号
        :param cancelable_only: 仅查询可撤委托
        :return: 返回当日所有委托的委托对象组成的list
        """
        ...

    def query_stock_trades(self, account):
        """:param account: 证券账号
        :return: 返回当日所有成交的成交对象组成的list
        """
        ...

    def query_stock_trades_async(self, account, callback):
        """:param account: 证券账号
        :return: 返回当日所有成交的成交对象组成的list
        """
        ...

    def query_stock_positions(self, account):
        """:param account: 证券账号
        :return: 返回当日所有持仓的持仓对象组成的list
        """
        ...

    def query_stock_positions_async(self, account, callback):
        """:param account: 证券账号
        :return: 返回当日所有持仓的持仓对象组成的list
        """
        ...

    def query_stock_position(self, account, stock_code):
        """:param account: 证券账号
        :param stock_code: 证券代码, 例如"600000.SH"
        :return: 返回证券代码对应的持仓对象
        """
        ...

    def query_stock_order(self, account, order_id):
        """:param account: 证券账号
        :param order_id: 订单编号，同步报单接口返回的编号
        :return: 返回订单编号对应的委托对象
        """
        ...

    # ---- 交易 ----

    def order_stock(self, account, stock_code, order_type, order_volume,
                    price_type, price, strategy_name='', order_remark=''):
        """:param account: 证券账号
        :param stock_code: 证券代码, 例如"600000.SH"
        :param order_type: 委托类型, 23:买, 24:卖
        :param order_volume: 委托数量, 股票以'股'为单位, 债券以'张'为单位
        :param price_type: 报价类型, 详见帮助手册
        :param price: 报价价格, 如果price_type为指定价, 那price为指定的价格, 否则填0
        :param strategy_name: 策略名称
        :param order_remark: 委托备注
        :return: 返回下单请求序号, 成功委托后的下单请求序号为大于0的正整数, 如果为-1表示委托失败
        """
        ...

    def order_stock_async(self, account, stock_code, order_type, order_volume,
                          price_type, price, strategy_name='', order_remark=''):
        """:param account: 证券账号
        :param stock_code: 证券代码, 例如"600000.SH"
        :param order_type: 委托类型, 23:买, 24:卖
        :param order_volume: 委托数量, 股票以'股'为单位, 债券以'张'为单位
        :param price_type: 报价类型, 详见帮助手册
        :param price: 报价价格, 如果price_type为指定价, 那price为指定的价格, 否则填0
        :param strategy_name: 策略名称
        :param order_remark: 委托备注
        :return: 返回下单请求序号, 成功委托后的下单请求序号为大于0的正整数, 如果为-1表示委托失败
        """
        ...

    def cancel_order_stock(self, account, order_id):
        """:param account: 证券账号
        :param order_id: 委托编号, 报单时返回的编号
        :return: 返回撤单成功或者失败, 0:成功,  -1:撤单失败
        """
        ...

    def cancel_order_stock_async(self, account, order_id):
        """:param account: 证券账号
        :param order_id: 委托编号, 报单时返回的编号
        :return: 返回撤单请求序号, 成功委托后的撤单请求序号为大于0的正整数, 如果为-1表示撤单失败
        """
        ...

    def cancel_order_stock_sysid(self, account, market, sysid):
        """:param account: 证券账号
        :param market: 交易市场 0:上海 1:深圳
        :param sysid: 柜台合同编号
        :return: 返回撤单成功或者失败, 0:成功,  -1:撤单失败
        """
        ...

    def cancel_order_stock_sysid_async(self, account, market, sysid):
        """:param account: 证券账号
        :param market: 交易市场 0:上海 1:深圳
        :param sysid: 柜台编号
        :return: 返回撤单请求序号, 成功委托后的撤单请求序号为大于0的正整数, 如果为-1表示撤单失败
        """
        ...
