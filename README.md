<<<<<<< HEAD
# Stock Data API for AI Agents

专为 AI 智能体（如 Gemini, GPTs）设计的 A 股即时数据服务。提供实时行情、技术指标（MACD/KDJ）、资金流向和筹码分布数据。

## 🌟 核心功能

- **纯净 API**: 专为 LLM Function Calling 优化。
- **深度数据**: 包含 MACD、均线系统、筹码分布、主力资金流向。
- **自说明**: 提供 AI 自我指南端点，让 AI 自动学会如何使用。

## 🚀 快速开始

**Base URL**: `https://stock-data-api-sgdm.onrender.com`

### 1. 智能体集成指南

请直接将以下 Prompt 复制给您的 AI 智能体：

```text
你是一个专业的金融数据分析助手。你的核心数据源是 `https://stock-data-api-sgdm.onrender.com`。
请首先访问 GET /api/ai_guide 了解所有可用工具。
在分析股票时，务必使用 GET /api/stock/price?code=xxxxx&detail=true 获取深度技术指标。
```

### 2. 主要端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/ai_guide` | **AI 专用指南**，返回 API 的完整使用说明 |
| GET | `/api/stock/price` | 获取实时行情 + 深度指标 (参数: `detail=true`) |
| GET | `/api/stock/info` | 获取股票基本面信息 |
| GET | `/api/stock/kline` | 获取历史 K 线数据 |

## 🛠️ 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

服务将运行在 `http://localhost:8000`。

## 📦 部署 (Render)

本项目已配置 Dockerfile，可直接部署到 Render。

1. Fork 本仓库
2. 在 Render 创建新的 Web Service
3. 连接 GitHub 仓库
4. Runtime 选择 **Docker**
5. 部署即可

## License

MIT

### 获取实时价格
```
GET /api/stock/price?code=600000
```

**返回示例：**
```json
{
  "status": "success",
  "data": {
    "code": "600000",
    "name": "浦发银行",
    "current_price": 12.50,
    "open_price": 12.30,
    "high_price": 12.80,
    "low_price": 12.10,
    "change_percent": 1.62,
    "volume": 45000000,
    "time": "2026-02-17T15:00:00"
  },
  "timestamp": "2026-02-17T10:30:00"
}
```

### 获取历史数据
```
GET /api/stock/historical?code=600000&days=30
```

**请求参数：**
- `code` (必需): 股票代码
- `days` (可选): 查询天数，默认30天，最多365天

**返回示例：**
```json
{
  "status": "success",
  "data": {
    "code": "600000",
    "name": "浦发银行",
    "period": "最近30天",
    "count": 30,
    "data": [
      {
        "date": "2026-01-20",
        "open": 11.50,
        "close": 11.60,
        "high": 11.80,
        "low": 11.40,
        "volume": 35000000
      },
      ...
    ]
  }
}
```

### 获取股票列表
```
GET /api/stock/list?market=sh&limit=20
```

**请求参数：**
- `market` (可选): 市场类型，如 sh(沪深)、sz(深圳)
- `limit` (可选): 返回数量，默认20

**返回示例：**
```json
{
  "status": "success",
  "data": {
    "count": 2,
    "limit": 20,
    "market": "sh",
    "data": [
      {
        "code": "600000",
        "name": "浦发银行",
        "market": "sh",
        "price": 12.50,
        "change_percent": 1.62
      },
      ...
    ]
  }
}
```

### 健康检查
```
GET /api/health
```

## 与AI智能体集成

### 1. OpenAI Function Calling

```python
from openai import OpenAI

client = OpenAI()

# 定义函数供AI调用
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "获取股票的实时价格",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "股票代码，如600000"
                    }
                },
                "required": ["code"]
            }
        }
    }
]

# 实现函数调用
def get_stock_price(code: str):
    import requests
    response = requests.get(f"http://localhost:8000/api/stock/price?code={code}")
    return response.json()
```

### 2. LangChain Tools

```python
from langchain.tools import tool
import requests

@tool
def get_stock_data(code: str) -> dict:
    """获取股票数据"""
    response = requests.get(f"http://localhost:8000/api/stock/info?code={code}")
    return response.json()

@tool
def get_stock_price_data(code: str) -> dict:
    """获取股票实时价格"""
    response = requests.get(f"http://localhost:8000/api/stock/price?code={code}")
    return response.json()
```

## 数据源配置

目前使用示例数据。当你确定具体的数据源后，修改 `data_fetcher.py` 中的方法即可：

**常用数据源库：**
- **akshare**: 免费的中文财经数据库
- **tushare**: 提供A股数据接口
- **pandas-datareader**: 获取国际股票数据

**修改示例（使用akshare）：**
```python
import akshare as ak

def get_stock_price(self, code: str):
    # 调用akshare API
    data = ak.stock_zh_a_spot()
    # 处理数据...
    return formatted_data
```

## 部署到生产环境

### 使用Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### 使用Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app:main", "--host", "0.0.0.0", "--port", "8000"]
```

## 开发建议

1. **添加数据库缓存** - 一些数据可以缓存到Redis或本地数据库
2. **添加速率限制** - 使用 `slowapi` 库限制请求频率
3. **添加认证** - 可以添加API Key或JWT认证
4. **错误处理** - 完善异常处理和日志记录
5. **性能优化** - 对大量数据请求进行分页处理

## 常见问题

**Q: 如何添加更多股票？**  
A: 修改 `data_fetcher.py` 中的 `self.stock_list` 字典

**Q: 如何使用真实数据源？**  
A: 修改 `get_stock_price` 等方法，调用真实API替代示例数据

**Q: API返回错误怎么办？**  
A: 查看 `/docs` 中的API文档，确保请求参数正确

## 支持的股票代码(示例)

- 600000 - 浦发银行
- 000858 - 五粮液
- 000651 - 格力电器
- 600519 - 贵州茅台

## License

MIT
=======
# Stock Data API for AI Agents

专为 AI 智能体（如 Gemini, GPTs）设计的 A 股即时数据服务。提供实时行情、技术指标（MACD/KDJ）、资金流向和筹码分布数据。

## 🌟 核心功能

- **纯净 API**: 专为 LLM Function Calling 优化。
- **深度数据**: 包含 MACD、均线系统、筹码分布、主力资金流向。
- **自说明**: 提供 AI 自我指南端点，让 AI 自动学会如何使用。

## 🚀 快速开始

**Base URL**: `https://stock-data-api-sgdm.onrender.com`

### 1. 智能体集成指南

请直接将以下 Prompt 复制给您的 AI 智能体：

```text
你是一个专业的金融数据分析助手。你的核心数据源是 `https://stock-data-api-sgdm.onrender.com`。
请首先访问 GET /api/ai_guide 了解所有可用工具。
在分析股票时，务必使用 GET /api/stock/price?code=xxxxx&detail=true 获取深度技术指标。
```

### 2. 主要端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/ai_guide` | **AI 专用指南**，返回 API 的完整使用说明 |
| GET | `/api/stock/price` | 获取实时行情 + 深度指标 (参数: `detail=true`) |
| GET | `/api/stock/info` | 获取股票基本面信息 |
| GET | `/api/stock/kline` | 获取历史 K 线数据 |

## 🛠️ 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

服务将运行在 `http://localhost:8000`。

## 📦 部署 (Render)

本项目已配置 Dockerfile，可直接部署到 Render。

1. Fork 本仓库
2. 在 Render 创建新的 Web Service
3. 连接 GitHub 仓库
4. Runtime 选择 **Docker**
5. 部署即可

## License

MIT

### 获取实时价格
```
GET /api/stock/price?code=600000
```

**返回示例：**
```json
{
  "status": "success",
  "data": {
    "code": "600000",
    "name": "浦发银行",
    "current_price": 12.50,
    "open_price": 12.30,
    "high_price": 12.80,
    "low_price": 12.10,
    "change_percent": 1.62,
    "volume": 45000000,
    "time": "2026-02-17T15:00:00"
  },
  "timestamp": "2026-02-17T10:30:00"
}
```

### 获取历史数据
```
GET /api/stock/historical?code=600000&days=30
```

**请求参数：**
- `code` (必需): 股票代码
- `days` (可选): 查询天数，默认30天，最多365天

**返回示例：**
```json
{
  "status": "success",
  "data": {
    "code": "600000",
    "name": "浦发银行",
    "period": "最近30天",
    "count": 30,
    "data": [
      {
        "date": "2026-01-20",
        "open": 11.50,
        "close": 11.60,
        "high": 11.80,
        "low": 11.40,
        "volume": 35000000
      },
      ...
    ]
  }
}
```

### 获取股票列表
```
GET /api/stock/list?market=sh&limit=20
```

**请求参数：**
- `market` (可选): 市场类型，如 sh(沪深)、sz(深圳)
- `limit` (可选): 返回数量，默认20

**返回示例：**
```json
{
  "status": "success",
  "data": {
    "count": 2,
    "limit": 20,
    "market": "sh",
    "data": [
      {
        "code": "600000",
        "name": "浦发银行",
        "market": "sh",
        "price": 12.50,
        "change_percent": 1.62
      },
      ...
    ]
  }
}
```

### 健康检查
```
GET /api/health
```

## 与AI智能体集成

### 1. OpenAI Function Calling

```python
from openai import OpenAI

client = OpenAI()

# 定义函数供AI调用
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "获取股票的实时价格",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "股票代码，如600000"
                    }
                },
                "required": ["code"]
            }
        }
    }
]

# 实现函数调用
def get_stock_price(code: str):
    import requests
    response = requests.get(f"http://localhost:8000/api/stock/price?code={code}")
    return response.json()
```

### 2. LangChain Tools

```python
from langchain.tools import tool
import requests

@tool
def get_stock_data(code: str) -> dict:
    """获取股票数据"""
    response = requests.get(f"http://localhost:8000/api/stock/info?code={code}")
    return response.json()

@tool
def get_stock_price_data(code: str) -> dict:
    """获取股票实时价格"""
    response = requests.get(f"http://localhost:8000/api/stock/price?code={code}")
    return response.json()
```

## 数据源配置

目前使用示例数据。当你确定具体的数据源后，修改 `data_fetcher.py` 中的方法即可：

**常用数据源库：**
- **akshare**: 免费的中文财经数据库
- **tushare**: 提供A股数据接口
- **pandas-datareader**: 获取国际股票数据

**修改示例（使用akshare）：**
```python
import akshare as ak

def get_stock_price(self, code: str):
    # 调用akshare API
    data = ak.stock_zh_a_spot()
    # 处理数据...
    return formatted_data
```

## 部署到生产环境

### 使用Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### 使用Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app:main", "--host", "0.0.0.0", "--port", "8000"]
```

## 开发建议

1. **添加数据库缓存** - 一些数据可以缓存到Redis或本地数据库
2. **添加速率限制** - 使用 `slowapi` 库限制请求频率
3. **添加认证** - 可以添加API Key或JWT认证
4. **错误处理** - 完善异常处理和日志记录
5. **性能优化** - 对大量数据请求进行分页处理

## 常见问题

**Q: 如何添加更多股票？**  
A: 修改 `data_fetcher.py` 中的 `self.stock_list` 字典

**Q: 如何使用真实数据源？**  
A: 修改 `get_stock_price` 等方法，调用真实API替代示例数据

**Q: API返回错误怎么办？**  
A: 查看 `/docs` 中的API文档，确保请求参数正确

## 支持的股票代码(示例)

- 600000 - 浦发银行
- 000858 - 五粮液
- 000651 - 格力电器
- 600519 - 贵州茅台

## License

MIT
>>>>>>> 57106fa4c35ea2549e3f0a7c9fcb749db681d5e8
