"""
股票数据API服务
提供JSON格式的股票数据给AI智能体调用
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import uvicorn
from typing import List, Optional
from datetime import datetime
import json

# 导入数据抓取模块
from data_fetcher import StockDataFetcher

app = FastAPI(
    title="股票数据API",
    description="为AI智能体提供股票数据的API服务",
    version="1.0.0"
)

# 初始化数据获取器
fetcher = StockDataFetcher()


@app.get("/")
async def root():
    """
    API 根路径，返回简单的欢迎信息和指南链接
    """
    return {
        "message": "Welcome to Stock Data API for AI Agents",
        "guide_url": "/api/ai_guide",
        "docs_url": "/docs"
    }


@app.get("/api/ai_guide")
async def get_ai_guide():
    """
    为AI智能体提供API使用指南，描述所有可用端点及其功能
    """
    return {
        "description": "本API专为AI智能体设计，提供A股市场实时数据与分析。",
        "endpoints": [
            {
                "path": "/api/stock/info",
                "method": "GET",
                "description": "获取股票基本信息（名称、行业、市值等）",
                "params": {"code": "股票代码，如 600000"}
            },
            {
                "path": "/api/stock/price",
                "method": "GET",
                "description": "获取实时行情，包含MACD、KDJ等技术指标",
                "params": {
                    "code": "股票代码",
                    "detail": "true (返回详细技术指标和资金流向数据)",
                    "include_intraday": "true (返回最近5分钟级别K线序列，用于分析尾盘急拉等微观逻辑)"
                }
            },
            {
                "path": "/api/stock/kline",
                "method": "GET",
                "description": "获取历史K线数据",
                "params": {
                    "code": "股票代码",
                    "period": "daily/weekly/monthly",
                    "adjust": "qfq (前复权) / hfq (后复权)"
                }
            },
            {
                "path": "/api/stock/news",
                "method": "GET",
                "description": "获取个股相关新闻",
                "params": {"code": "股票代码"}
            }
        ],
        "usage_tips": "对于深度分析，请在 /api/stock/price 中设置 detail=true 以获取 MACD、筹码分布和资金流向数据。"
    }


@app.get("/api/stock/info")
async def get_stock_info(code: str = Query(..., description="股票代码，例如：600000")) -> dict:
    """
    获取单个股票的基本信息
    
    Args:
        code: 股票代码
        
    Returns:
        JSON格式的股票信息
    """
    try:
        data = fetcher.get_stock_info(code)
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/stock/price")
async def get_stock_price(
    code: str = Query(..., description="股票代码"),
    detail: bool = Query(True, description="是否包含详细技术指标"),
    include_intraday: bool = Query(False, description="是否包含分时图数据(5分钟K线)")
) -> dict:
    """
    获取股票全行情（实时+技术+资金+分时）
    """
    try:
        # 1. 基础行情
        price_data = fetcher.get_stock_price(code)
        
        # 2. 如果不需要详情，直接返回
        if not detail and not include_intraday:
            return {
                "status": "success",
                "data": price_data,
                "timestamp": datetime.now().isoformat()
            }
            
        full_data = list(price_data.items())
        
        # 3. 补充技术指标与资金数据
        if detail:
            indicator_data = fetcher.get_stock_indicators(code)
            full_data.extend(indicator_data.items())
            
        # 4. 补充微观分时数据 (用于判断尾盘急拉等)
        if include_intraday:
            intraday_data = fetcher.get_stock_intraday(code)
            full_data.append(("intraday", intraday_data))
        
        # 合并数据
        return {
            "status": "success",
            "data": dict(full_data),
            "meta": {
                "timestamp": datetime.now().timestamp(),
                "source": "akshare_em",
                "version": "2.1"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/stock/historical")
async def get_stock_historical(
    code: str = Query(..., description="股票代码"),
    days: int = Query(30, description="查询天数，默认30天")
) -> dict:
    """
    获取股票历史数据
    
    Args:
        code: 股票代码
        days: 查询天数
        
    Returns:
        历史价格数据JSON
    """
    try:
        data = fetcher.get_stock_historical(code, days)
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/stock/list")
async def get_stock_list(
    market: Optional[str] = Query(None, description="市场类型：sh(沪深)、hk(港股)等"),
    limit: int = Query(20, description="返回数量")
) -> dict:
    """
    获取股票列表
    
    Args:
        market: 市场类型
        limit: 返回的股票数量
        
    Returns:
        股票列表JSON
    """
    try:
        data = fetcher.get_stock_list(market, limit)
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/stock/search")
async def search_stock(keyword: str = Query(..., description="搜索关键词：股票名称或代码")) -> dict:
    """
    搜索股票
    
    Args:
        keyword: 搜索关键词
        
    Returns:
        匹配的股票列表
    """
    try:
        results = fetcher.search_stock(keyword)
        return {
            "status": "success",
            "data": {
                "keyword": keyword,
                "count": len(results),
                "results": results
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/market/stats")
async def get_market_stats() -> dict:
    """获取市场统计信息"""
    try:
        data = fetcher.get_market_stats()
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "stock-data-api",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """根路由，显示API文档链接"""
    return {
        "message": "股票数据API服务 - 全A股实时数据",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "股票信息": "/api/stock/info?code=600000",
            "实时价格": "/api/stock/price?code=600000",
            "历史数据": "/api/stock/historical?code=600000&days=30",
            "股票列表": "/api/stock/list?limit=20",
            "搜索股票": "/api/stock/search?keyword=银行",
            "市场统计": "/api/market/stats",
            "健康检查": "/api/health"
        }
    }


if __name__ == "__main__":
    import os
    # 获取环境变量中的端口，Render 会自动注入 PORT 变量
    # 如果本地运行则默认使用 8000
    port = int(os.environ.get("PORT", 8000))
    
    # 启动服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
