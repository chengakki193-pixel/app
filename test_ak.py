import akshare as ak
try:
    df = ak.stock_zh_a_hist_min_em(symbol="600000", period="1", adjust="qfq")
    print(df.head(2))
    print(df.columns)
except Exception as e:
    print(e)
