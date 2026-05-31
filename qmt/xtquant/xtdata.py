# -*- coding: utf-8 -*-
"""
xtdata 行情数据接口（桩）

本文件提供函数签名和参数说明，用于 IDE 代码提示。
所有调用通过 QMT Bridge TCP 代理转发到 Windows 服务端执行。
以下文档来自 xtquant SDK 原始 docstring，确保与真实 SDK 一致。
"""


def subscribe_quote(stock_code, period='1d', start_time='', end_time='', count=0, callback=None):
    """订阅股票行情数据
    :param stock_code: 股票代码 e.g. "000001.SZ"
    :param period: 周期 分笔"tick" 分钟线"1m"/"5m" 日线"1d"等周期
    :param start_time: 开始时间，格式YYYYMMDD/YYYYMMDDhhmmss/YYYYMMDDhhmmss.milli，e.g."20200427" "20200427093000" "20200427093000.000"
        若取某日全量历史数据，时间需要具体到秒，e.g."20200427093000"
    :param end_time: 结束时间 同"开始时间"
    :param count: 数量 -1全部/n: 从结束时间向前数n个
    :param callback:
        订阅回调函数onSubscribe(datas)
        :param datas: {stock : [data1, data2, ...]} 数据字典
    :return: int 订阅序号
    """
    ...


def subscribe_whole_quote(code_list, callback=None):
    """订阅全推数据
    :param code_list: 市场代码列表 ["SH", "SZ"]
    :param callback:
        订阅回调函数onSubscribe(datas)
        :param datas: {stock1 : data1, stock2 : data2, ...} 数据字典
    :return: int 订阅序号
    """
    ...


def unsubscribe_quote(seq):
    """:param seq: 订阅接口subscribe_quote返回的订阅号"""
    ...


def run():
    """阻塞线程接收行情回调"""
    ...


def get_market_data(field_list=None, stock_list=None, period='1d',
                    start_time='', end_time='', count=-1,
                    dividend_type='none', fill_data=True):
    """获取历史行情数据
    :param field_list: 行情数据字段列表，[]为全部字段
        K线可选字段：
            "time"                #时间戳
            "open"                #开盘价
            "high"                #最高价
            "low"                 #最低价
            "close"               #收盘价
            "volume"              #成交量
            "amount"              #成交额
            "settle"              #今结算
            "openInterest"        #持仓量
        分笔可选字段：
            "time"                #时间戳
            "lastPrice"           #最新价
            "open"                #开盘价
            "high"                #最高价
            "low"                 #最低价
            "lastClose"           #前收盘价
            "amount"              #成交总额
            "volume"              #成交总量
            "pvolume"             #原始成交总量
            "stockStatus"         #证券状态
            "openInt"             #持仓量
            "lastSettlementPrice" #前结算
            "askPrice1"~"askPrice5" #卖一价~卖五价
            "bidPrice1"~"bidPrice5" #买一价~买五价
            "askVol1"~"askVol5"     #卖一量~卖五量
            "bidVol1"~"bidVol5"     #买一量~买五量
    :param stock_list: 股票代码 "000001.SZ"
    :param period: 周期 分笔"tick" 分钟线"1m"/"5m"/"15m" 日线"1d"
        Level2行情快照"l2quote" 快照补充"l2quoteaux" 逐笔委托"l2order" 逐笔成交"l2transaction"
        大单统计"l2transactioncount" 委买委卖队列"l2orderqueue"
        Level1逐笔成交统计"transactioncount1m"/"transactioncount1d"
        期货仓单"warehousereceipt" 期货席位"futureholderrank" 互动问答"interactiveqa"
    :param start_time: 起始时间 "20200101" "20200101093000"
    :param end_time: 结束时间 "20201231" "20201231150000"
    :param count: 数量 -1全部/n: 从结束时间向前数n个
    :param dividend_type: 除权类型"none" "front" "back" "front_ratio" "back_ratio"
    :param fill_data: 对齐时间戳时是否填充数据，仅对K线有效，分笔周期不对齐时间戳
        为True时，以缺失数据的前一条数据填充
            open、high、low、close 为前一条数据的close
            amount、volume为0
            settle、openInterest 和前一条数据相同
        为False时，缺失数据所有字段填NaN
    :return: 数据集，分笔数据和K线数据格式不同
        period为'tick'时：{stock1 : value1, stock2 : value2, ...}
            value为 np.ndarray 数据列表，按time增序排列
        period为其他K线周期时：{field1 : value1, field2 : value2, ...}
            value为 pd.DataFrame，index为stock_list，columns为time_list
    """
    ...


def get_local_data(field_list=None, stock_list=None, period='1d',
                   start_time='', end_time='', count=-1,
                   dividend_type='none', fill_data=True, data_dir=None):
    """从本地缓存读取行情数据，参数同 get_market_data，额外支持 data_dir 指定数据目录"""
    ...


def get_full_tick(code_list):
    """获取盘口tick数据
    :param code_list: (list)stock.market组成的股票代码列表
    :return: dict {'stock.market': {dict}}
    """
    ...


def get_divid_factors(stock_code, start_time='', end_time=''):
    """获取除权除息日及对应的权息
    :param stock_code: (str)股票代码
    :return: pd.DataFrame 数据集
    """
    ...


def get_l2_quote(field_list=None, stock_code='', start_time='', end_time='', count=-1):
    """level2实时行情"""
    ...


def get_l2_order(field_list=None, stock_code='', start_time='', end_time='', count=-1):
    """level2逐笔委托"""
    ...


def get_l2_transaction(field_list=None, stock_code='', start_time='', end_time='', count=-1):
    """level2逐笔成交"""
    ...


def download_history_data(stock_code, period, start_time='', end_time='', incrementally=None):
    """:param stock_code: str 品种代码，例如：'000001.SZ'
    :param period: str 数据周期
    :param start_time: str 开始时间
        格式为 YYYYMMDD 或 YYYYMMDDhhmmss 或 ''
        例如：'20230101' '20231231235959'
        空字符串代表全部，自动扩展到完整范围
    :param end_time: str 结束时间 格式同开始时间
    :param incrementally: 是否增量下载
        bool: 是否增量下载
        None: 使用start_time控制，start_time为空则增量下载
    """
    ...


def get_financial_data(stock_list, table_list=None, start_time='', end_time='',
                       report_type='report_time'):
    """获取财务数据
    :param stock_list: (list)合约代码列表
    :param table_list: (list)报表名称列表
    :param start_time: (str)起始时间
    :param end_time: (str)结束时间
    :param report_type: (str) 时段筛选方式 'announce_time' / 'report_time'
    :return: field: list[str], date: list[int], stock: list[str], value: list[list[float]]
    """
    ...


def download_financial_data(stock_list, table_list=None, start_time='', end_time='', incrementally=None):
    """:param stock_list: 股票代码列表
    :param table_list: 财务数据表名列表，[]为全部表
        可选范围：['Balance','Income','CashFlow','Capital','Top10FlowHolder','Top10Holder','HolderNum','PershareIndex']
    :param start_time: 开始时间，格式YYYYMMDD，e.g."20200427"
    :param end_time: 结束时间 同上，若是未来某时刻会被视作当前时间
    """
    ...


def get_instrument_detail(stock_code, iscomplete=False):
    """获取合约信息
    :param stock_code: 股票代码 e.g. "600000.SH"
    :return: dict
        ExchangeID(str):合约市场代码, InstrumentID(str):合约代码, InstrumentName(str):合约名称
        ProductID(str):合约的品种ID(期货), ProductName(str):合约的品种名称(期货)
        ExchangeCode(str):交易所代码, UniCode(str):统一规则代码
        CreateDate(str):上市日期(期货), OpenDate(str):IPO日期(股票), ExpireDate(str):退市日或者到期日
        PreClose(double):前收盘价格, SettlementPrice(double):前结算价格
        UpStopPrice(double):当日涨停价, DownStopPrice(double):当日跌停价
        FloatVolume(double):流通股本, TotalVolume(double):总股本
        LongMarginRatio(double):多头保证金率, ShortMarginRatio(double):空头保证金率
        PriceTick(double):最小变价单位, VolumeMultiple(int):合约乘数
        MainContract(int):主力合约标记, LastVolume(int):昨日持仓量
        InstrumentStatus(int):合约停牌状态, IsTrading(bool):合约是否可交易, IsRecent(bool):是否是近月合约
    """
    ...


def get_instrument_type(stock_code, variety_list=None):
    """判断证券类型
    :param stock_code: 股票代码 e.g. "600000.SH"
    :return: dict{str : bool} {类型名：是否属于该类型}
    """
    ...


def get_trading_dates(market, start_time='', end_time='', count=-1):
    """根据市场获取交易日列表
    :param market: 市场代码 e.g. 'SH','SZ','IF','DF','SF','ZF'等
    :param start_time: 起始时间 '20200101'
    :param end_time: 结束时间 '20201231'
    :param count: 数据个数，-1为全部数据
    :return: list(long) 毫秒数的时间戳列表
    """
    ...


def get_sector_list():
    """获取板块列表
    :return: (list[str])
    """
    ...


def get_stock_list_in_sector(sector_name, real_timetag=-1):
    """获取板块成份股，支持客户端左侧板块列表中任意的板块，包括自定义板块
    :param sector_name: (str)板块名称
    :param real_timetag: 时间：1512748800000 或 '20171209'，可缺省，缺省为获取最新成份，不缺省时获取对应时间的历史成份
    :return: list
    """
    ...


def download_sector_data():
    """下载行业板块数据"""
    ...


def add_sector(sector_name, stock_list):
    """增加自定义板块
    :param sector_name: 板块名称 e.g. "我的自选"
    :param stock_list: (list)stock.market组成的股票代码列表
    """
    ...


def remove_sector(sector_name):
    """删除自定义板块
    :param sector_name: 板块名称 e.g. "我的自选"
    """
    ...


def create_sector(parent_node, sector_name, overwrite=True):
    """创建板块
    :param parent_node: str 父节点，''为'我的'（默认目录）
    :param sector_name: str 要创建的板块名
    :param overwrite: bool 是否覆盖，True为跳过，False为在sector_name后增加数字编号
    """
    ...


def create_sector_folder(parent_node, folder_name, overwrite=True):
    """创建板块目录节点
    :param parent_node: str 父节点，''为'我的'（默认目录）
    :param folder_name: str 要创建的板块目录名称
    :param overwrite: bool 是否覆盖
    """
    ...


def remove_stock_from_sector(sector_name, stock_list):
    """移除板块成分股
    :param sector_name: 板块名称 e.g. "我的自选"
    :param stock_list: (list)stock.market组成的股票代码列表
    """
    ...


def reset_sector(sector_name, stock_list):
    """重置板块
    :param sector_name: 板块名称 e.g. "我的自选"
    :param stock_list: (list)stock.market组成的股票代码列表
    """
    ...


def get_index_weight(index_code):
    """获取某只股票在某指数中的绝对权重
    :param index_code: (str)指数名称
    :return: dict
    """
    ...


def download_index_weight():
    """下载指数权重数据"""
    ...


def get_holidays():
    """获取节假日列表
    :return: 8位int型日期
    """
    ...


def get_trading_calendar(market, start_time='', end_time=''):
    """获取指定市场交易日历
    :param market: str 市场
    :param start_time: str 起始时间 '20200101'
    :param end_time: str 结束时间 '20201231'
    """
    ...


def get_trading_time(stockcode):
    """返回指定股票的交易时段
    :param stockcode: 代码.市场  例如 '600000.SH'
    :return: 返回交易时段列表，第一位开始时间，第二位结束时间，第三位交易类型
        （2-开盘竞价，3-连续交易，8-收盘竞价，9-盘后定价）
    """
    ...


def download_history_contracts():
    """下载过期合约数据"""
    ...


def get_main_contract(code_market, start_time='', end_time=''):
    """获取主力合约/历史主力合约
    注意：获取历史主力合约需要先调用 xtdata.download_history_data(symbol, 'historymaincontract', '', '')
    :param code_market: 主力连续合约code，如"IF00.IF","AP00.ZF"
    :param start_time: 开始时间（可不填），格式为"%Y%m%d"，默认为""
    :param end_time: 结束时间（可不填），格式为"%Y%m%d"，默认为""
    :return: 默认取当前主力合约代码(str)；
        指定start_time不指定end_time时返回指定日期主力合约代码(str)；
        指定start_time和end_time时返回区间内主力合约组成的pd.Series
    """
    ...


def get_full_kline(field_list=None, stock_list=None, period='1m',
                   start_time='', end_time='', count=1,
                   dividend_type='none', fill_data=True):
    """k线全推获取最新交易日数据"""
    ...


def get_trading_period(stock_code):
    """获取合约最新交易时间段
    :param stock_code: 合约市场代码，例如：600000.SH
    :return: dict {market, codeRegex, product, category, tradings: [type, bartime:[dayoffset, start, end]]}
        tradings 中 type: 2盘前竞价，3连续交易，8尾盘竞价
    """
    ...


def get_all_trading_periods():
    """获取全部市场划分出来的交易时间段"""
    ...


def get_kline_trading_period(stock_code):
    """与交易时间相似，区别在于把尾盘竞价和盘中交易合并"""
    ...


def get_all_kline_trading_periods():
    """获取全部市场划分出来的K线交易时间段"""
    ...


def get_authorized_market_list():
    """获取所有已授权的市场
    :return: list
    """
    ...


def t2d(timetag, format):
    """将毫秒时间转换成日期时间
    :param timetag: (int)时间戳毫秒数
    :param format: (str)时间格式
    :return: str
    """
    ...


def timetag_to_datetime(timetag, format):
    """将毫秒时间转换成日期时间
    :param timetag: (int)时间戳毫秒数
    :param format: (str)时间格式
    :return: str
    """
    ...
