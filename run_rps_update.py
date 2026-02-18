import time
from data_fetcher import StockDataFetcher

def main():
    print("Initialize Fetcher...")
    fetcher = StockDataFetcher()
    print("Start updating RPS... (This will take a long time)")
    fetcher.update_rps_rankings()
    print("Done!")

if __name__ == "__main__":
    main()
