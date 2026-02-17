"""
股票数据抓取模块
从akshare获取全A股实时数据
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
import pandas as pd

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False


class StockDataFetcher:
    """
    股票数据获取类
    从akshare获取真实的A股数据
    """
    
    def __init__(self):
        """初始化数据获取器"""
        self.stock_list = {}
        self.stock_df = None
        self.last_update = None
        
        # 初始化加载股票列表
        if AKSHARE_AVAILABLE:
            self._load_stock_list()
        else:
            self._load_fallback_stocks()
    
    def _load_stock_list(self):
        """从akshare加载全A股股票列表（使用东方财富接口，更稳定）"""
        try:
            print("正在从akshare加载全A股数据...")
            # 使用东方财富接口，通常更稳定
            self.stock_df = ak.stock_zh_a_spot_em()
            
            # 东方财富接口返回的列名：['序号', '代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '最高', '最低', '今开', '昨收', '量比', '换手率', '市盈率-动态', '市净率']
            # 构建股票列表字典
            for _, row in self.stock_df.iterrows():
                code = str(row['代码'])
                name = str(row['名称'])
                market = "sh" if code.startswith('6') else ("bj" if code.startswith(('4','8')) else "sz")
                
                # 存两份索引，方便查找
                self.stock_list[code] = {"name": name, "market": market}
                # 兼容带前缀的查找
                self.stock_list[f"{market}{code}"] = {"name": name, "market": market}
            
            self.last_update = datetime.now()
            print(f"✓ 成功加载 {len(self.stock_df)} 只A股股票")
            
        except Exception as e:
            print(f"⚠️  akshare加载失败: {e}，使用备用数据")
            # 可以在这里尝试另一个接口作为备选
            self._load_fallback_stocks()
    
    def _load_fallback_stocks(self):
        """备用：硬编码的常见股票"""
        stocks = {
            "600000": {"name": "浦发银行", "market": "sh"},
            "600519": {"name": "贵州茅台", "market": "sh"},
            "600036": {"name": "招商银行", "market": "sh"},
            "601398": {"name": "工商银行", "market": "sh"},
            "601939": {"name": "建设银行", "market": "sh"},
            "000858": {"name": "五粮液", "market": "sz"},
            "000651": {"name": "格力电器", "market": "sz"},
            "000001": {"name": "平安银行", "market": "sz"},
            "002230": {"name": "科大讯飞", "market": "sz"},
            "300750": {"name": "宁德时代", "market": "sz"},
        }
        self.stock_list = stocks
        print(f"✓ 加载了 {len(self.stock_list)} 只备用股票")
    
    def get_stock_info(self, code: str) -> Dict[str, Any]:
        """
        获取股票基本信息
        """
        if code not in self.stock_list:
            raise ValueError(f"股票代码 {code} 不存在")
            
        stock = self.stock_list[code]
        # 如果是带前缀的code，取纯代码去df查询
        pure_code = code[-6:] if len(code) > 6 else code
        
        # 尝试从akshare获取详细信息
        if AKSHARE_AVAILABLE and self.stock_df is not None:
            try:
                row = self.stock_df[self.stock_df['代码'] == pure_code].iloc[0]
                
                # 兼容不同接口的字段名
                current_price = row.get('最新价', None)
                if current_price is None: current_price = row.get('当前价')
                
                return {
                    "code": pure_code,
                    "name": stock["name"],
                    "market": stock["market"],
                    "price": float(current_price) if current_price != '-' else 0,
                    "change_percent": float(row.get('涨跌幅', 0)),
                    "volume": float(row.get('成交量', 0)),
                    "market_cap": row.get('总市值', 'N/A'),
                }
            except:
                pass
        
        # 备用数据
        return {
            "code": pure_code,
            "name": stock["name"],
            "market": stock["market"],
            "industry": "未知",
            "market_cap": "N/A",
            "pe_ratio": 0,
        }
    
    def get_stock_price(self, code: str) -> Dict[str, Any]:
        """
        获取股票实时价格
        """
        if code not in self.stock_list:
            raise ValueError(f"股票代码 {code} 不存在")
            
        stock = self.stock_list[code]
        # 如果是带前缀的code，取纯代码去df查询
        pure_code = code[-6:] if len(code) > 6 else code
        
        # 如果有akshare数据，从中获取
        if AKSHARE_AVAILABLE and self.stock_df is not None:
            try:
                row = self.stock_df[self.stock_df['代码'] == pure_code].iloc[0]
                
                # 处理可能存在的 '-' 或异常值
                def get_float(key, default=0.0):
                    val = row.get(key)
                    if val is None or val == '-' or val == '':
                        return default
                    return float(val)

                current_price = get_float('最新价')
                
                return {
                    "code": pure_code,
                    "name": stock["name"],
                    "current_price": round(current_price, 2),
                    "open_price": round(get_float('今开', current_price), 2),
                    "high_price": round(get_float('最高', current_price), 2),
                    "low_price": round(get_float('最低', current_price), 2),
                    "closed_price": round(get_float('昨收', current_price), 2),
                    "change_percent": round(get_float('涨跌幅'), 2),
                    "volume": int(get_float('成交量')),
                    "amount": get_float('成交额'),
                    "time": datetime.now().isoformat()
                }
            except Exception as e:
                print(f"获取实时数据失败 ({code}): {e}")
        
        # 备用生成数据
        base_price = random.uniform(10, 200)
        change_percent = round(random.uniform(-5, 5), 2)
        
        return {
            "code": code,
            "name": self.stock_list[code]["name"],
            "current_price": round(base_price, 2),
            "open_price": round(base_price - 1, 2),
            "high_price": round(base_price + 2, 2),
            "low_price": round(base_price - 2, 2),
            "closed_price": round(base_price - 0.5, 2),
            "change_amount": round(base_price * change_percent / 100, 2),
            "change_percent": change_percent,
            "volume": random.randint(1000000, 100000000),
            "amount": round(random.uniform(100000000, 10000000000), 2),
            "time": datetime.now().isoformat()
        }
    
    def get_stock_historical(self, code: str, days: int = 30) -> Dict[str, Any]:
        """
        获取股票历史数据
        
        Args:
            code: 股票代码
            days: 查询天数
            
        Returns:
            包含历史数据列表的字典
        """
        if code not in self.stock_list:
            raise ValueError(f"股票代码 {code} 不存在")
        
        if days > 365:
            days = 365
        
        historical_data = []
        
        # 尝试从akshare获取历史数据
        if AKSHARE_AVAILABLE:
            try:
                # 计算日期范围
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=days)
                
                # 获取历史数据
                hist_df = ak.stock_zh_a_hist(
                    symbol=code,
                    period="daily",
                    start_date=start_date.strftime("%Y%m%d"),
                    end_date=end_date.strftime("%Y%m%d"),
                    adjust="qfq"
                )
                
                if hist_df is not None and len(hist_df) > 0:
                    for _, row in hist_df.iterrows():
                        historical_data.append({
                            "date": row['日期'],
                            "open": float(row['开盘']),
                            "close": float(row['收盘']),
                            "high": float(row['最高']),
                            "low": float(row['最低']),
                            "volume": int(row['成交量']),
                            "amount": float(row['成交额'])
                        })
                    
                    return {
                        "code": code,
                        "name": self.stock_list[code]["name"],
                        "period": f"最近{days}天",
                        "count": len(historical_data),
                        "data": historical_data
                    }
            except Exception as e:
                print(f"获取历史数据失败: {e}")
        
        # 备用：生成示例数据
        base_price = 100
        for i in range(days, 0, -1):
            date = (datetime.now() - timedelta(days=i)).date()
            price_change = random.uniform(-3, 3)
            base_price += price_change
            
            historical_data.append({
                "date": str(date),
                "open": round(base_price - 0.5, 2),
                "close": round(base_price, 2),
                "high": round(base_price + 1, 2),
                "low": round(base_price - 1, 2),
                "volume": random.randint(1000000, 50000000),
                "amount": round(base_price * random.randint(1000000, 50000000), 2)
            })
        
        return {
            "code": code,
            "name": self.stock_list[code]["name"],
            "period": f"最近{days}天",
            "count": len(historical_data),
            "data": historical_data
        }
    
    def get_stock_list(self, market: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """
        获取股票列表
        
        Args:
            market: 市场类型（sh/sz等）
            limit: 返回的数量
            
        Returns:
            股票列表
        """
        stocks = []
        
        # 如果有akshare数据，从中获取
        if AKSHARE_AVAILABLE and self.stock_df is not None:
            try:
                df = self.stock_df.copy()
                
                # 按市场过滤
                if market == "sh":
                    df = df[df['代码'].str.startswith('6')]
                elif market == "sz":
                    df = df[df['代码'].str.startswith(('0', '3'))]
                
                # 按涨幅降序排序（取涨幅最大的）
                df = df.sort_values('涨跌幅', ascending=False)
                
                # 取前limit条
                for _, row in df.head(limit).iterrows():
                    stocks.append({
                        "code": row['代码'],
                        "name": row['名称'],
                        "market": "sh" if str(row['代码']).startswith('6') else "sz",
                        "price": float(row['最新价']),
                        "change_percent": float(row['涨跌幅'])
                    })
                
                return {
                    "count": len(stocks),
                    "limit": limit,
                    "market": market or "all",
                    "data": stocks
                }
            except Exception as e:
                print(f"获取股票列表失败: {e}")
        
        # 备用方案
        for code, info in list(self.stock_list.items())[:limit]:
            if market and info["market"] != market:
                continue
            
            stocks.append({
                "code": code,
                "name": info["name"],
                "market": info["market"],
                "price": round(random.uniform(10, 200), 2),
                "change_percent": round(random.uniform(-5, 5), 2)
            })
            
            if len(stocks) >= limit:
                break
        
        return {
            "count": len(stocks),
            "limit": limit,
            "market": market or "all",
            "data": stocks
        }
    
    # ============ 后续可添加的方法 ============
    
    def search_stock(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索股票（模糊匹配）
        支持股票代码和名称搜索
        """
        results = []
        keyword_lower = keyword.lower()
        
        for code, info in self.stock_list.items():
            # 代码匹配
            if keyword in code:
                results.append({"code": code, "name": info["name"]})
                continue
            
            # 名称匹配
            if keyword_lower in info["name"].lower():
                results.append({"code": code, "name": info["name"]})
        
        return results[:20]  # 最多返回20条
    
    def get_stock_comparison(self, codes: List[str]) -> Dict[str, Any]:
        """
        对比多个股票
        """
        comparison = []
        for code in codes:
            if code in self.stock_list:
                try:
                    comparison.append(self.get_stock_price(code))
                except:
                    pass
        
        return {
            "comparison_count": len(comparison),
            "data": comparison
        }
    
    def get_market_stats(self) -> Dict[str, Any]:
        """
        获取市场统计信息
        """
        if self.stock_df is None:
            return {"error": "暂无市场数据"}
        
        try:
            sh_count = len(self.stock_df[self.stock_df['代码'].str.startswith('6')])
            sz_count = len(self.stock_df[self.stock_df['代码'].str.startswith(('0', '3'))])
            
            return {
                "total_stocks": len(self.stock_df),
                "sh_stocks": sh_count,
                "sz_stocks": sz_count,
                "up_count": len(self.stock_df[self.stock_df['涨跌幅'] > 0]),
                "down_count": len(self.stock_df[self.stock_df['涨跌幅'] < 0]),
                "last_update": self.last_update.isoformat() if self.last_update else None
            }
        except:
            return {"error": "无法计算市场统计"}
