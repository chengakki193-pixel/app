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
async def get_stock_price(code: str = Query(..., description="股票代码")) -> dict:
    """
    获取股票实时价格
    
    Args:
        code: 股票代码
        
    Returns:
        包含价格信息的JSON
    """
    try:
        data = fetcher.get_stock_price(code)
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
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
    # 启动服务器
    # 生产环境可用: gunicorn -w 4 -b 0.0.0.0:8000 app:app
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
