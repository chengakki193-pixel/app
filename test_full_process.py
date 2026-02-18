import requests
import time
import json
from datetime import datetime

# API_URL = "http://127.0.0.1:8000"  # 本地调试用
API_URL = "https://stock-data-api-sgdm.onrender.com" # 远程生产环境

TEST_CODE = "600000" # 浦发银行
TEST_PARAMS = {
    "code": TEST_CODE,
    "detail": "true",
    "include_intraday": "true"
}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def test_full_process():
    log(f"开始全流程测试 - 目标: {API_URL}")
    log(f"测试股票: {TEST_CODE}, 参数: {TEST_PARAMS}")
    
    start_time = time.time()
    
    try:
        # 1. 发起请求
        log("1. 发起 HTTP GET 请求...")
        req_start = time.time()
        response = requests.get(f"{API_URL}/api/stock/price", params=TEST_PARAMS, timeout=30)
        req_end = time.time()
        log(f"   请求耗时: {req_end - req_start:.4f} 秒")
        
        if response.status_code != 200:
            log(f"❌ 请求失败: Status Code {response.status_code}")
            log(f"   响应内容: {response.text}")
            return

        data = response.json()
        total_time = time.time() - start_time
        
        # 2. 解析数据
        log(f"2. 接收数据成功，总大小: {len(response.content)} bytes")
        log(f"   总耗时: {total_time:.4f} 秒")
        
        # 3. 验证数据完整性
        log("3. 开始校验数据完整性...")
        status = data.get("status")
        result_data = data.get("data", {})
        
        # 检查项清单
        checks = [
            ("API状态", status == "success", f"Status: {status}"),
            ("基础报价 (Basic Quote)", "quote" in result_data and result_data["quote"].get("current") is not None, "当前价存在"),
            ("技术指标 (Indicators)", "indicators" in result_data, "MA/MACD/RPS等"),
            ("   - RPS数据 (GitHub源)", 
             result_data.get("indicators", {}).get("rps_source") == "github_chengakki193" and 
             result_data.get("indicators", {}).get("rps_50") is not None, 
             f"RPS_50: {result_data.get('indicators', {}).get('rps_50')}"),
            ("   - MACD数据", len(result_data.get("indicators", {}).get("macd_30d", [])) > 0, "MACD列表非空"),
            ("   - 均线数据", result_data.get("indicators", {}).get("ma", {}).get("ma5") is not None, "MA5存在"),
            ("筹码分布 (Chips)", "chips" in result_data, "分布数据存在"),
            ("资金流向 (Capital)", "capital" in result_data, "字段存在(允许为None)"),
            ("   - 实时资金流", result_data.get("capital", {}).get("flow") is None, "预期为None (免费接口限制)"), 
            ("分时数据 (Intraday)", "intraday" in result_data and len(result_data["intraday"]) > 0, f"点数: {len(result_data.get('intraday', []))}")
        ]
        
        print("-" * 50)
        print(f"{'检查项':<25} | {'状态':<6} | {'备注'}")
        print("-" * 50)
        
        for name, passed, note in checks:
            icon = "✅" if passed else "❌"
            # 特殊处理资金流的预期缺失
            if "资金流" in name and passed: 
                icon = "⚠️" # 确实没拿到，但是是预期的
            
            print(f"{name:<25} | {icon:<6} | {note}")
            
        print("-" * 50)
        
        log("测试完成")

    except Exception as e:
        log(f"❌ 测试过程中发生异常: {str(e)}")

if __name__ == "__main__":
    test_full_process()
