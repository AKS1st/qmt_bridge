# -*- coding: utf-8 -*-
"""
QMT 客户端补丁（兼容旧用法）

用法：
    import qmt.patch

效果等同于在你的代码中：
    import qmt.xtquant
    import sys
    sys.modules["xtquant"] = qmt.xtquant

此后任何 `import xtquant` 都会自动转发到远程 Windows 服务端。

推荐新用法（无需补丁）：
    from qmt.xtquant import xtdata
"""

import sys
import qmt.xtquant

# 将 qmt.xtquant 注册为顶层 xtquant，使旧代码 `import xtquant` 也能工作
sys.modules["xtquant"] = qmt.xtquant
sys.modules["xtquant.xtdata"] = qmt.xtquant.xtdata
sys.modules["xtquant.xttrader"] = qmt.xtquant.xttrader

print(f"[qmt] xtquant {qmt.xtquant.__version__} 已代理至远程服务器")
