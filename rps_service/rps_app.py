import uvicorn
from fastapi import FastAPI, BackgroundTasks
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pandas as pd
import akshare as ak
import joblib
import os
from datetime import datetime
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RPS_Service")

app = FastAPI(title="RPS Calculation Service")

# Cache file path
CACHE_FILE = "rps_cache.joblib"
RPS_DATA = {}

# --- RPS Calculation Logic ---

def calculate_rps_all():
    """
    RPS Core Calculation Logic:
    1. Fetch all A-shares list.
    2. For each stock, fetch daily history (N days).
    3. Calculate gain.
    4. Rank them.
    5. Save to global RPS_DATA and disk cache.
    """
    logger.info("Starting Daily RPS Calculation...")
    
    try:
        # 1. Get stock list
        spot_df = ak.stock_zh_a_spot_em()
        if spot_df is None or spot_df.empty:
            logger.error("Failed to fetch stock list from Akshare.")
            return

        # Prepare for calculation
        stocks = spot_df['代码'].tolist()
        # Limit for demo/testing if needed, but for prod use full list
        # stocks = stocks[:100] # Uncomment for quick debug
        
        results = []
        period = 250 # Default 250 days
        
        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=400)
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        
        total = len(stocks)
        processed = 0

        # Optimization: Use ak.stock_zh_a_hist directly? 
        # No, akshare hist is per stock. We loop.
        # Note: This is slow. In production, we might need async or parallel fetch.
        # For this prototype, we do serial fetch with error handling.
        
        for code in stocks:
            try:
                # Fetch history
                df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_str, end_date=end_str, adjust="qfq")
                
                if df is None or len(df) < period:
                    continue
                    
                # Calculate gain
                latest = df.iloc[-1]['收盘']
                prev = df.iloc[-period]['收盘']
                
                if prev == 0: continue
                
                gain = (latest - prev) / prev
                results.append({"code": code, "gain": gain})
                
            except Exception as e:
                # logger.warning(f"Error fetching {code}: {e}")
                pass
            
            processed += 1
            if processed % 100 == 0:
                logger.info(f"Processed {processed}/{total} stocks...")

        if not results:
            logger.error("No RPS data calculated.")
            return

        # Create DataFrame and Rank
        df_res = pd.DataFrame(results)
        df_res['rps_rank'] = df_res['gain'].rank(pct=True) * 100
        
        # Update Global Cache
        new_cache = {}
        for _, row in df_res.iterrows():
            new_cache[row['code']] = round(row['rps_rank'], 2)
            
        global RPS_DATA
        RPS_DATA = new_cache
        
        # Persist to disk
        joblib.dump(RPS_DATA, CACHE_FILE)
        logger.info(f"RPS Calculation Completed. {len(RPS_DATA)} stocks ranked.")
        
    except Exception as e:
        logger.error(f"Critical error in calculate_rps_all: {e}")

# --- Scheduler Setup ---

scheduler = BackgroundScheduler()

# Schedule to run daily at 4:00 AM
trigger = CronTrigger(hour=4, minute=0)
scheduler.add_job(calculate_rps_all, trigger)

@app.on_event("startup")
def startup_event():
    global RPS_DATA
    # Load cache if exists
    if os.path.exists(CACHE_FILE):
        try:
            RPS_DATA = joblib.load(CACHE_FILE)
            logger.info(f"Loaded {len(RPS_DATA)} RPS records from disk cache.")
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
    else:
        logger.info("No cache found. Calculation will run on schedule or manual trigger.")
    
    scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "running", "service": "RPS Calculation", "cache_size": len(RPS_DATA)}

@app.get("/rps/stock/{code}")
def get_stock_rps(code: str, period: int = 250):
    """
    Get the cached RPS for a specific stock code.
    Currently only supports fixed 250-day period as cached.
    """
    if code in RPS_DATA:
        return {"code": code, "rps": RPS_DATA[code], "period": period}
    else:
        return {"code": code, "rps": None, "msg": "Not found in cache or not calculated yet"}

@app.post("/trigger-update")
def trigger_update(background_tasks: BackgroundTasks):
    """
    Manually trigger an update (async)
    """
    background_tasks.add_task(calculate_rps_all)
    return {"msg": "RPS update triggered in background"}

if __name__ == "__main__":
    # Run on port 8888 as defined in start_services.bat
    uvicorn.run(app, host="127.0.0.1", port=8888)
