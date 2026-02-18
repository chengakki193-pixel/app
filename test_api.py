"""
API测试脚本
用于测试各个端点
"""

import requests
import json
from typing import Dict, Any


class APITester:
    """API测试工具"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def test_health(self) -> Dict[str, Any]:
        """测试健康检查"""
        print("\n✓ 测试健康检查...")
        response = requests.get(f"{self.base_url}/api/health")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return data
    
    def test_stock_info(self, code: str = "600000") -> Dict[str, Any]:
        """测试获取股票信息"""
        print(f"\n✓ 测试获取股票信息 ({code})...")
        response = requests.get(f"{self.base_url}/api/stock/info", params={"code": code})
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return data
    
    def test_stock_price(self, code: str = "600000") -> Dict[str, Any]:
        """测试获取股票价格"""
        print(f"\n✓ 测试获取股票价格 ({code})...")
        response = requests.get(f"{self.base_url}/api/stock/price", params={"code": code})
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return data
    
    def test_stock_historical(self, code: str = "600000", days: int = 10) -> Dict[str, Any]:
        """测试获取历史数据"""
        print(f"\n✓ 测试获取历史数据 ({code}, {days}天)...")
        response = requests.get(
            f"{self.base_url}/api/stock/historical",
            params={"code": code, "days": days}
        )
        print(f"状态码: {response.status_code}")
        data = response.json()
        # 只打印前3条数据
        if "data" in data and "data" in data["data"]:
            data_copy = data.copy()
            data_copy["data"]["data"] = data_copy["data"]["data"][:3]
            print(f"响应 (仅前3条): {json.dumps(data_copy, ensure_ascii=False, indent=2)}")
        else:
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return data
    
    def test_stock_list(self, market: str = None, limit: int = 3) -> Dict[str, Any]:
        """测试获取股票列表"""
        print(f"\n✓ 测试获取股票列表...")
        params = {"limit": limit}
        if market:
            params["market"] = market
        response = requests.get(f"{self.base_url}/api/stock/list", params=params)
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return data
    
    def test_error_handling(self) -> Dict[str, Any]:
        """测试错误处理"""
        print(f"\n✓ 测试错误处理 (无效股票代码)...")
        response = requests.get(f"{self.base_url}/api/stock/info", params={"code": "999999"})
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return data
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("股票数据API测试")
        print("=" * 60)
        
        try:
            # 基本测试
            self.test_health()
            self.test_stock_info("600000")
            self.test_stock_info("000858")
            self.test_stock_price("600000")
            self.test_stock_historical("600000", 10)
            self.test_stock_list(None, 3)
            self.test_stock_list("sh", 2)
            
            # 错误处理测试
            self.test_error_handling()
            
            print("\n" + "=" * 60)
            print("✓ 所有测试完成！")
            print("=" * 60)
            
        except requests.exceptions.ConnectionError:
            print("\n❌ 错误: 无法连接到服务器")
            print("请确保服务器已启动: python app.py")
        except Exception as e:
            print(f"\n❌ 测试出错: {str(e)}")


if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
