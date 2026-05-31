# -*- coding: utf-8 -*-
"""
类型常量定义（桩）

本文件包含 QMT Bridge 客户端所需的协议常量值，
用于 StockAccount 等数据类型的序列化兼容以及交易参数引用。
常量值与 QMT 协议保持一致，确保 Windows 服务端互通。
"""

# ══════════════════════════════════════════════════════════════════
# 账号类型
# ══════════════════════════════════════════════════════════════════
FUTURE_ACCOUNT = 1              # 期货
SECURITY_ACCOUNT = 2            # 股票
CREDIT_ACCOUNT = 3              # 信用（两融）
FUTURE_OPTION_ACCOUNT = 5       # 期货期权
STOCK_OPTION_ACCOUNT = 6        # 股票期权（ETF 期权）
HUGANGTONG_ACCOUNT = 7          # 沪港通
INCOME_SWAP_ACCOUNT = 8         # 收益互换
NEW3BOARD_ACCOUNT = 10          # 全国股转（新三板）
SHENGANGTONG_ACCOUNT = 11       # 深港通
AT_OFFSITEBANKING = 13          # 场外理财
AT_OUTTER_FUTURE = 1001         # 外盘期货
AT_IB = 1002                    # IB（盈透）
AT_NS_TRUSTBANK = 15001         # 场外托管
AT_INTERBANK = 15002            # 银行间
AT_BANK = 15003                 # 银行
AT_OTC = 15005                  # 场外

# 账号类型枚举 → 字符串标识映射
ACCOUNT_TYPE_DICT = {
    FUTURE_ACCOUNT: "FUTURE",
    SECURITY_ACCOUNT: "STOCK",
    CREDIT_ACCOUNT: "CREDIT",
    FUTURE_OPTION_ACCOUNT: "FUTURE_OPTION",
    STOCK_OPTION_ACCOUNT: "STOCK_OPTION",
    HUGANGTONG_ACCOUNT: "HUGANGTONG",
    SHENGANGTONG_ACCOUNT: "SHENGANGTONG",
    NEW3BOARD_ACCOUNT: "NEW3BOARD",
    INCOME_SWAP_ACCOUNT: "INCOME_SWAP",
    AT_OFFSITEBANKING: "OFFSITEBANKING",
    AT_OUTTER_FUTURE: "OUTTER_FUTURE",
    AT_IB: "IB",
    AT_NS_TRUSTBANK: "NS_TRUSTBANK",
    AT_INTERBANK: "INTERBANK",
    AT_BANK: "BANK",
    AT_OTC: "OTC",
}

# ══════════════════════════════════════════════════════════════════
# 市场类型（整数枚举）
# ══════════════════════════════════════════════════════════════════
SH_MARKET = 0                        # 上海证券交易所
SZ_MARKET = 1                        # 深圳证券交易所
MARKET_ENUM_BEIJING = 70             # 北京证券交易所
MARKET_ENUM_SHANGHAI_FUTURE = 3      # 上海期货交易所
MARKET_ENUM_DALIANG_FUTURE = 4       # 大连商品交易所
MARKET_ENUM_ZHENGZHOU_FUTURE = 5     # 郑州商品交易所
MARKET_ENUM_INDEX_FUTURE = 2         # 中国金融期货交易所
MARKET_ENUM_INTL_ENERGY_FUTURE = 6   # 上海国际能源交易中心
MARKET_ENUM_GUANGZHOU_FUTURE = 75    # 广州期货交易所
MARKET_ENUM_SHANGHAI_STOCK_OPTION = 7   # 上海股票期权
MARKET_ENUM_SHENZHEN_STOCK_OPTION = 67   # 深圳股票期权

# ══════════════════════════════════════════════════════════════════
# 市场代码（字符串标识）
# ══════════════════════════════════════════════════════════════════
MARKET_SHANGHAI = "SH"               # 上交所
MARKET_SHENZHEN = "SZ"               # 深交所
MARKET_BEIJING = "BJ"                # 北交所
MARKET_SHANGHAI_FUTURE = "SF"        # 上期所
MARKET_DALIANG_FUTURE = "DF"         # 大商所
MARKET_ZHENGZHOU_FUTURE = "ZF"       # 郑商所
MARKET_INDEX_FUTURE = "IF"           # 中金所
MARKET_INTL_ENERGY_FUTURE = "INE"    # 能源中心
MARKET_GUANGZHOU_FUTURE = "GF"       # 广期所
MARKET_SHANGHAI_STOCK_OPTION = "SHO" # 上海期权
MARKET_SHENZHEN_STOCK_OPTION = "SZO" # 深圳期权

# 市场字符串 → 整数枚举映射
MARKET_STR_TO_ENUM_MAPPING = {
    MARKET_SHANGHAI: SH_MARKET,
    MARKET_SHENZHEN: SZ_MARKET,
    MARKET_BEIJING: MARKET_ENUM_BEIJING,
    MARKET_SHANGHAI_FUTURE: MARKET_ENUM_SHANGHAI_FUTURE,
    MARKET_DALIANG_FUTURE: MARKET_ENUM_DALIANG_FUTURE,
    MARKET_ZHENGZHOU_FUTURE: MARKET_ENUM_ZHENGZHOU_FUTURE,
    MARKET_INDEX_FUTURE: MARKET_ENUM_INDEX_FUTURE,
    MARKET_INTL_ENERGY_FUTURE: MARKET_ENUM_INTL_ENERGY_FUTURE,
    MARKET_GUANGZHOU_FUTURE: MARKET_ENUM_GUANGZHOU_FUTURE,
    MARKET_SHANGHAI_STOCK_OPTION: MARKET_ENUM_SHANGHAI_STOCK_OPTION,
    MARKET_SHENZHEN_STOCK_OPTION: MARKET_ENUM_SHENZHEN_STOCK_OPTION,
}

# ══════════════════════════════════════════════════════════════════
# 委托类型（股票）
# ══════════════════════════════════════════════════════════════════
STOCK_BUY = 23      # 买入
STOCK_SELL = 24     # 卖出

# ══════════════════════════════════════════════════════════════════
# 账号连接状态
# ══════════════════════════════════════════════════════════════════
ACCOUNT_STATUS_INVALID = -1    # 无效
ACCOUNT_STATUS_OK = 0          # 正常
ACCOUNT_STATUS_WAITING_LOGIN = 1   # 等待登录
ACCOUNT_STATUSING = 2              # 登录中
ACCOUNT_STATUS_FAIL = 3            # 登录失败
ACCOUNT_STATUS_INITING = 4         # 初始化
ACCOUNT_STATUS_CORRECTING = 5      # 数据校正
ACCOUNT_STATUS_CLOSED = 6          # 已收盘
ACCOUNT_STATUS_ASSIS_FAIL = 7      # 副链路断开
ACCOUNT_STATUS_DISABLEBYSYS = 8    # 系统停用
ACCOUNT_STATUS_DISABLEBYUSER = 9   # 用户停用
