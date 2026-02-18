"""
AI智能体集成示例
展示如何在AI应用中调用API
"""

import requests
import json
from typing import Any, Dict


# ==================== 基础API调用 ====================

def call_api(endpoint: str, params: Dict[str, Any] = None, base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """
    统一的API调用函数
    
    Args:
        endpoint: API端点，如 /api/stock/info
        params: 查询参数
        base_url: API基础URL
        
    Returns:
        API响应的JSON数据
    """
    try:
        response = requests.get(f"{base_url}{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


# ==================== AI友好的工具函数 ====================

class StockAPITools:
    """为AI智能体提供的工具集合"""
    
    @staticmethod
    def get_stock_price(code: str) -> str:
        """
        获取股票实时价格
        
        Args:
            code: 股票代码
            
        Returns:
            格式化的结果字符串
        """
        result = call_api("/api/stock/price", {"code": code})
        
        if result.get("status") == "error":
            return f"获取股票 {code} 价格失败: {result.get('message')}"
        
        data = result.get("data", {})
        return (
            f"股票 {data.get('name')} ({code}) "
            f"当前价格: ¥{data.get('current_price')}, "
            f"涨跌: {data.get('change_percent')}%"
        )
    
    @staticmethod
    def get_stock_info(code: str) -> str:
        """
        获取股票基本信息
        """
        result = call_api("/api/stock/info", {"code": code})
        
        if result.get("status") == "error":
            return f"获取股票 {code} 信息失败: {result.get('message')}"
        
        data = result.get("data", {})
        return (
            f"股票代码: {data.get('code')}\n"
            f"股票名称: {data.get('name')}\n"
            f"市场: {data.get('market')}\n"
            f"行业: {data.get('industry')}\n"
            f"市值: {data.get('market_cap')}\n"
            f"PE比率: {data.get('pe_ratio')}"
        )
    
    @staticmethod
    def get_stock_list(limit: int = 10) -> str:
        """
        获取股票列表
        """
        result = call_api("/api/stock/list", {"limit": limit})
        
        if result.get("status") == "error":
            return f"获取股票列表失败: {result.get('message')}"
        
        stocks = result.get("data", {}).get("data", [])
        
        if not stocks:
            return "未找到股票数据"
        
        lines = [f"获取了 {len(stocks)} 只股票:"]
        for stock in stocks:
            lines.append(
                f"- {stock['name']} ({stock['code']}): "
                f"¥{stock['price']} ({stock['change_percent']:+.2f}%)"
            )
        
        return "\n".join(lines)
    
    @staticmethod
    def compare_stocks(codes: list) -> str:
        """
        对比多个股票
        """
        results = []
        for code in codes:
            result = call_api("/api/stock/price", {"code": code})
            if result.get("status") == "success":
                results.append(result["data"])
        
        if not results:
            return f"无法获取 {codes} 的数据"
        
        lines = ["股票对比:"]
        for data in results:
            lines.append(
                f"- {data['name']} ({data['code']}): "
                f"¥{data['current_price']} "
                f"({data['change_percent']:+.2f}%)"
            )
        
        return "\n".join(lines)


# ==================== OpenAI Function Calling 集成示例 ====================

def get_openai_tools_definition():
    """
    获取OpenAI Function Calling的工具定义
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_stock_price",
                "description": "获取某只股票的实时价格信息，包括当前价格、涨跌幅等",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "股票代码，例如：600000（浦发银行），000858（五粮液）"
                        }
                    },
                    "required": ["code"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_stock_info",
                "description": "获取股票的基本信息，包括名称、行业、市值、PE比率等",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "股票代码"
                        }
                    },
                    "required": ["code"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_stock_list",
                "description": "获取股票列表",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "返回的股票数量，默认10",
                            "default": 10
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "compare_stocks",
                "description": "对比多个股票的价格和涨跌幅",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "codes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "股票代码列表，例如：['600000', '000858']"
                        }
                    },
                    "required": ["codes"]
                }
            }
        }
    ]


def handle_tool_call(tool_name: str, tool_input: dict) -> str:
    """
    处理AI调用的工具
    """
    if tool_name == "get_stock_price":
        return StockAPITools.get_stock_price(tool_input["code"])
    elif tool_name == "get_stock_info":
        return StockAPITools.get_stock_info(tool_input["code"])
    elif tool_name == "get_stock_list":
        return StockAPITools.get_stock_list(tool_input.get("limit", 10))
    elif tool_name == "compare_stocks":
        return StockAPITools.compare_stocks(tool_input["codes"])
    else:
        return f"未知的工具: {tool_name}"


# ==================== 使用示例 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("AI智能体集成示例")
    print("=" * 60)
    
    # 示例1: 直接调用
    print("\n【示例1】直接调用API工具:")
    print(StockAPITools.get_stock_price("600000"))
    
    print("\n" + "-" * 60)
    print("\n【示例2】获取股票信息:")
    print(StockAPITools.get_stock_info("000858"))
    
    print("\n" + "-" * 60)
    print("\n【示例3】获取股票列表:")
    print(StockAPITools.get_stock_list(5))
    
    print("\n" + "-" * 60)
    print("\n【示例4】对比多个股票:")
    print(StockAPITools.compare_stocks(["600000", "000858", "000651"]))
    
    print("\n" + "-" * 60)
    print("\n【示例5】OpenAI工具定义:")
    tools = get_openai_tools_definition()
    print(json.dumps(tools, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
