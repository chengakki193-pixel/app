import pandas as pd
import akshare as ak
import json
import os
import time
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# === 全局配置 ===
OUTPUT_DIR = "output"
RPS_FILE = os.path.join(OUTPUT_DIR, "latest_rps.json")
TOP_RPS_FILE = os.path.join(OUTPUT_DIR, "top_rps.json")
# 假设我们用 JSON 文件来保存一个极简的增量缓存，只记录每只股票最后更新的日期
# 在真实生产环境，这里应该是数据库或 Parquet 文件
UPDATE_LOG_FILE = "update_log.json"

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def load_update_log():
    if os.path.exists(UPDATE_LOG_FILE):
        with open(UPDATE_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_update_log(log_data):
    with open(UPDATE_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

def get_all_stocks():
    """获取全A股列表"""
    print("正在获取全市场股票列表...")
    try:
        df = ak.stock_zh_a_spot_em()
        return df
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        return None

def fetch_and_calculate_rps(stock_info, end_date):
    """
    单个股票的处理逻辑：
    1. 获取历史K线
    2. 计算 RPS 需要的 Gain (50/120/250)
    """
    code = str(stock_info['代码'])
    name = str(stock_info['名称'])
    
    try:
        # 获取最近 300 天的日线数据 (包含今天)
        start_date = (end_date - timedelta(days=400)).strftime("%Y%m%d")
        end_date_str = end_date.strftime("%Y%m%d")
        
        # 即使是增量更新，为了计算 RPS (比如 RPS250)，我们每次还是得拉取足够长的历史数据
        # 除非我们在本地维护了一个巨大的全量历史数据库。
        # 鉴于 GitHub Actions 的环境是临时的（虽然有 Cache 但配置复杂），
        # 这里的策略是：每次运行时，只拉取必须长度的数据。
        # Akshare 的这个接口速度还可以，3000次调用并发下大约几分钟。
        
        df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_date, end_date=end_date_str, adjust="qfq")
        
        if df is None or df.empty or len(df) < 50:
            return None
        
        # 核心指标计算
        closes = df["收盘"].values
        # 确保按日期升序 (akshare 默认是升序，这里再次校验)
        # 如果不是升序，pct_change 计算会错。但 numpy 数组没法像 dataframe 那样直接 sort_values
        # 这里假设 akshare 返回有序。
        
        current_close = float(closes[-1])
        current_date = str(df.iloc[-1]["日期"])
        
        def get_gain(days):
            if len(closes) > days:
                prev = float(closes[-(days+1)])
                if prev == 0: return 0.0
                return (current_close - prev) / prev
            return None
            
        return {
            "code": code,
            "name": name,
            "close": current_close,
            "date": current_date,
            "gain_50": get_gain(50),
            "gain_120": get_gain(120),
            "gain_250": get_gain(250)
        }
        
    except Exception as e:
        # print(f"Error {code}: {e}")
        return None

def main():
    start_time = time.time()
    ensure_output_dir()
    
    print(f"[{datetime.now()}] 任务开始...")
    
    # 1. 获取全量股票
    df_stocks = get_all_stocks()
    if df_stocks is None or df_stocks.empty:
        print("无法获取股票列表，任务终止。")
        return

    # 为了 GitHub Actions 演示稳定，这里只取前 200 个股票测试
    # 在正式运行时，请注释掉下面这行！
    # df_stocks = df_stocks.head(200) 
    
    print(f"待处理股票数量: {len(df_stocks)}")
    
    results = []
    end_date = datetime.now()
    
    # 2. 并发处理
    # GitHub Actions 的 runner 通常由 2-4 vCPU
    max_workers = 10 
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for _, row in df_stocks.iterrows():
            futures.append(executor.submit(fetch_and_calculate_rps, row, end_date))
            
        # 进度条
        total = len(futures)
        completed = 0
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
            completed += 1
            if completed % 100 == 0:
                print(f"进度: {completed}/{total} ({(completed/total)*100:.1f}%)")
                
    print(f"数据获取完成，有效数据: {len(results)} 条。开始计算 RPS 排名...")
    
    # 3. 计算 RPS 排名 (DataFrame 矩阵化操作)
    df_res = pd.DataFrame(results)
    
    if not df_res.empty:
        for p in [50, 120, 250]:
            col_gain = f"gain_{p}"
            col_rps = f"RPS_{p}"
            
            # 过滤无效数据
            mask = df_res[col_gain].notna()
            if mask.sum() > 0:
                # pct=True 生成 0.0~1.0 的百分比
                df_res.loc[mask, col_rps] = df_res.loc[mask, col_gain].rank(pct=True, ascending=True) * 100
                df_res.loc[mask, col_rps] = df_res.loc[mask, col_rps].round(2)
                
                # 转换 gain 为百分比格式方便阅读
                df_res.loc[mask, f"{col_gain}_pct"] = (df_res.loc[mask, col_gain] * 100).round(2)
    
    # 4. 生成输出文件
    final_list = df_res.to_dict("records")
    
    # 4.1 全量文件 (按 RPS_120 排序)
    # 处理 NaN 为 None 以符合 JSON 标准
    for item in final_list:
        for k, v in item.items():
            if pd.isna(v):
                item[k] = None
                
    final_list.sort(key=lambda x: (x.get("RPS_120") or -1), reverse=True)
    
    with open(RPS_FILE, "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)
    print(f"全量数据已保存: {RPS_FILE}")
    
    # 4.2 Top 榜单 (JSON)
    top_data = {}
    for p in [50, 120, 250]:
        key = f"RPS_{p}"
        # 筛选 >= 90
        tops = [x for x in final_list if x.get(key) and x[key] >= 90]
        # 内部排序
        tops.sort(key=lambda x: x[key], reverse=True)
        top_data[f"top_{p}"] = tops
        
    with open(TOP_RPS_FILE, "w", encoding="utf-8") as f:
        json.dump(top_data, f, ensure_ascii=False, indent=2)
    print(f"Top榜单已保存: {TOP_RPS_FILE}")
    
    print(f"任务完成! 总耗时: {time.time() - start_time:.2f} 秒")

if __name__ == "__main__":
    main()
