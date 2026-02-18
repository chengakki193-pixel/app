import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import math
import sys

# Windows 终端下为了防止输出乱码，有时需要设置
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def calculate_debug_rps():
    print("🚀 正在拉取实时数据进行RPS演示 (Sample Limit: 10 stocks)...")
    
    # 硬编码一些热门股票代码:
    # 600519(茅台), 300750(宁德), 002594(比亚迪), 600036(招行), 601318(平安)
    # 000858(五粮液), 600900(长电), 000333(美的), 600276(恒瑞), 300059(东财)
    target_stocks = [
        "600519", "300750", "002594", "600036", "601318", 
        "000858", "600900", "000333", "600276", "300059"
    ]
    
    period = 250  # RPS 250 (即一年)
    
    # 准备结果列表
    rps_data = []

    # 获取今天的日期
    end_date = datetime.now()
    # 获取足够长的历史数据
    start_date = end_date - timedelta(days=400)
    
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")

    print(f"📅 计算周期: {start_str} - {end_str}")
    
    for i, code in enumerate(target_stocks):
        try:
            print(f"[{i+1}/{len(target_stocks)}] Fetching {code}...", end=" ", flush=True)
            # 获取个股历史数据
            # adjust="qfq" 前复权，对RPS计算至关重要
            df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_str, end_date=end_str, adjust="qfq")
            
            if df is None or df.empty:
                print(f"⚠️ 无数据")
                continue
            
            # 检查是否有足够的数据计算 RPS
            if len(df) < period:
                print(f"⚠️ 数据不足 {period} 天 (只有 {len(df)})")
                continue

            # 获取最新和 N 天前的收盘价
            latest_close = df.iloc[-1]['收盘']
            prev_close_row = df.iloc[-period]
            prev_close = prev_close_row['收盘']
            
            # 计算涨幅
            gain = (latest_close - prev_close) / prev_close
            
            rps_data.append({
                "code": code,
                "close": latest_close,
                "gain_rate": gain
            })
            
            print(f"✅")
            
        except Exception as e:
            print(f"❌ {e}")

    # 计算 RPS (Rank)
    if not rps_data:
        print("❌ 没有成功获取任何数据")
        return

    df_rps = pd.DataFrame(rps_data)
    
    # RPS 核心逻辑:
    # rank(pct=True) 返回 0.0-1.0 的百分比排名，乘100即为 RPS 值
    df_rps['rps_250'] = df_rps['gain_rate'].rank(pct=True) * 100
    
    # 转换为百分比字符串以便展示
    df_rps['gain_pct'] = (df_rps['gain_rate'] * 100).round(2).astype(str) + '%'
    df_rps['rps_250'] = df_rps['rps_250'].round(2)
    
    # 排序
    df_rps = df_rps.sort_values(by='rps_250', ascending=False)
    
    # Markdown 输出
    print("\n====== RPS (Relative Price Strength) 演示结果 ======")
    print(f"注: 这是基于样本 {len(target_stocks)} 只热门股的相对排名演示")
    # 手动格式化因为 pandas to_markdown 需要 tabulate 库 (虽然通常都有)
    print(f"{'代码':<10} {'当前价':<10} {'涨幅(250日)':<15} {'RPS数值':<10}")
    print("-" * 50)
    for _, row in df_rps.iterrows():
        print(f"{row['code']:<10} {row['close']:<10.2f} {row['gain_pct']:<15} {row['rps_250']:<10.2f}")

    print("\n✅ 说明:")
    print("1. RPS_250 = 100.00 表示该股票是这10只里涨幅最高的。")
    print("2. 实际系统中，样本将是全市场 5000+ 只股票，计算逻辑完全相同。")

if __name__ == "__main__":
    calculate_debug_rps()
