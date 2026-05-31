# QMT Bridge

> 跨平台 QMT（迅投量化交易终端）远程调用桥梁。

将 Windows 上的 `xtquant` SDK 封装为 TCP 服务，使 Linux / macOS 等其他平台也能调用行情和交易接口，无需本地安装 QMT 客户端。

## 架构

```
┌───────────────────────────┐         TCP          ┌──────────────────────────┐
│  客户端 (任意平台)          │ ◄──────────────────► │  服务端 (仅 Windows)       │
│                           │                      │                          │
│  from qmt.xtquant import  │  TOKEN 认证 +         │  qmt/server.py            │
│    xtdata, XtQuantTrader   │  pickle 序列化调用    │  xtdata / xttrader (SDK)  │
│  (远程代理)                │ ◄──────────────────  │                           │
└───────────────────────────┘                      └──────────────────────────┘
```

| 组件 | 平台 | 依赖 |
|------|------|------|
| 服务端 | **Windows** | Python 3.8+, xtquant SDK (QMT/MiniQMT) |
| 客户端 | Linux/macOS/Windows | Python 3.8+, python-dotenv |

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/AKS1st/qmt_bridge.git
cd qmt_bridge
```

### 2. 安装

```bash
pip install -e ".[test]"
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填写你的配置：

```ini
# 服务端（必填）
QMT_PATH=<your_qmt_userdata_mini_path>
ACCOUNT_ID=<your_account_id>

# 认证 TOKEN（必填，服务端和客户端需一致）
TOKEN=<your_token>

# 客户端（必填）
CLIENT_HOST=<your_windows_ip>
```

> 首次启动时如未设置 `TOKEN`，服务端会自动生成一个随机 TOKEN 并提示你填入 `.env`。

### 4. 启动服务端（Windows）

确保 MiniQMT 已登录并运行后：

```bash
# CLI 方式（推荐）
qmt-server start              # 检查连接 → 后台静默运行
qmt-server log -f             # 实时查看日志
qmt-server stop               # 停止服务

# 或直接运行
python qmt/server.py          # 前台模式，日志输出到控制台
```

### 5. 运行测试

```bash
pytest tests/ -v
```

## 在策略中使用

```python
# 推荐：直接导入代理
from qmt.xtquant import xtdata
from qmt.xtquant.xttrader import XtQuantTrader
from qmt.xtquant.xttype import StockAccount

data = xtdata.get_market_data(...)
```

```python
# 兼容旧用法：一行 patch
import qmt.patch
from xtquant import xtdata
```

## qmt-server CLI

| 命令 | 说明 |
|------|------|
| `start` | 检查连接 → 后台静默运行 |
| `stop` | 停止后台服务 |
| `log` | 分页查看日志 |
| `log -f` | 实时追踪（tail -f） |

日志位于 `logs/qmt-server.log`，每 30 天滚动分割，保留最近 12 个归档。

## 项目结构

```
qmt_bridge/
├── qmt/
│   ├── server.py        # 服务端（仅 Windows）
│   ├── client.py        # TCP 客户端库
│   ├── patch.py         # 旧 import qmt.patch 兼容
│   ├── cli.py           # qmt-server 命令行
│   └── xtquant/         # 客户端 SDK 源码（仅 .py）
│       └── __init__.py  # 挂载远程代理
├── tests/
│   ├── test_xtdata.py   # 行情读取测试
│   ├── test_xttrader.py # 账户查询测试（只读）
│   └── test_patch.py    # 旧用法兼容测试
├── .env.example         # 配置模板
├── pyproject.toml
└── README.md
```

## 安全提示

- `.env` 包含敏感信息（账号、TOKEN、IP），**切勿提交到 Git**
- 通信通过 `TOKEN` 认证，不匹配的连接会被拒绝
- 使用 pickle 序列化，建议仅在**可信内网**使用
- 可在防火墙中限制服务端端口访问来源
