import streamlit as st
import pandas as pd
import requests
import time
import os
import threading
from uvicorn import run
import sys
import importlib.util
from datetime import datetime

# ================= 配置 =================
st.set_page_config(
    page_title="股票数据 API 服务中心",
    page_icon="📈",
    layout="wide",
)

# ================= 后台服务启动逻辑 =================
def run_api():
    """在后台线程启动 FastAPI"""
    import os
    import sys
    
    # 确保当前目录在sys.path中，以便能找到app.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
        
    try:
        from app import app as fastapi_app
        # 启动
        run(fastapi_app, host="127.0.0.1", port=8000)
    except ImportError as e:
        st.error(f"无法导入 app.py: {e}")
    except Exception as e:
        st.error(f"启动 API 失败: {e}")

if 'server_started' not in st.session_state:
    st.session_state.server_started = False

if not st.session_state.server_started:
    # 启动 API 线程
    t = threading.Thread(target=run_api, daemon=True)
    t.start()
    st.session_state.server_started = True
    # 等待服务启动
    time.sleep(3)

# ================= 界面逻辑 =================

st.title("📈 股票数据 API 服务中心")
st.markdown("### 为 AI 智能体提供全 A 股实时数据的接口服务")

# 侧边栏：服务状态
with st.sidebar:
    st.header("🔗 服务状态")
    try:
        # 尝试连接本地 API
        res = requests.get("http://127.0.0.1:8000/api/health", timeout=2)
        if res.status_code == 200:
            status = res.json()
            st.success("API 服务运行中 ✅")
            st.json(status)
        else:
            st.error(f"服务异常: {res.status_code}")
    except:
        st.warning("服务启动中或连接失败 ⚠️")
    
    st.divider()
    st.markdown("### 📡 外部访问指南")
    st.info("""
    Streamlit Cloud 无法直接暴露 8000 端口给外部访问。
    
    **最佳实践：**
    部署到 **Zeabur**, **Render**, **Railway** 等支持 Docker 的平台。
    """)

# 主区域：功能演示
tab1, tab2, tab3 = st.tabs(["🔍 股票查询演示", "📊 市场概览", "🤖 AI 集成指南"])

with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("测试 API")
        code_input = st.text_input("输入股票代码 (如 600519)", "600519")
        if st.button("查询实时数据", use_container_width=True):
            try:
                # 调用本地 API
                url = f"http://127.0.0.1:8000/api/stock/price?code={code_input}"
                with st.spinner(f"正在查询 {code_input}..."):
                    res = requests.get(url)
                    data = res.json()
                
                if res.status_code == 200:
                    st.session_state.last_result = data
                else:
                    st.error(f"查询失败: {data.get('detail', '未知错误')}")
            except Exception as e:
                st.error(f"连接失败: {e}")
    
    with col2:
        if 'last_result' in st.session_state:
            data = st.session_state.last_result
            stock = data.get('data', {})
            
            st.subheader(f"📊 {stock.get('name', '未知')} ({stock.get('code', '未知')})")
            
            # 漂亮的指标展示
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("当前价格", f"¥{stock.get('current_price')}", f"{stock.get('change_percent')}%")
            m2.metric("今开", f"¥{stock.get('open_price')}")
            m3.metric("最高", f"¥{stock.get('high_price')}")
            m4.metric("最低", f"¥{stock.get('low_price')}")
            
            st.divider()
            
            # 原始 JSON 展示
            with st.expander("查看原始 JSON (给 AI 看的数据)", expanded=True):
                st.json(data)

with tab2:
    st.subheader("获取市场热点股票")
    if st.button("刷新列表"):
        try:
            res = requests.get("http://127.0.0.1:8000/api/stock/list?limit=10")
            if res.status_code == 200:
                stocks = res.json()['data']['data']
                df = pd.DataFrame(stocks)
                st.dataframe(
                    df[['code', 'name', 'price', 'change_percent']],
                    column_config={
                        "code": "代码", 
                        "name": "名称",
                        "price": st.column_config.NumberColumn("最新价", format="¥%.2f"),
                        "change_percent": st.column_config.NumberColumn("涨跌幅", format="%.2f%%"),
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.error("无法获取市场数据")
        except Exception as e:
            st.error(f"请求失败: {e}")

with tab3:
    st.markdown("### 🤖 如何让 AI 使用此 API")
    st.markdown("""
    如果你已经部署到公网 (假设地址为 `https://your-api.com`)，请将以下信息提供给 AI Agent。
    """)
    
    st.subheader("1. System Prompt (系统提示词)")
    prompt_template = """你是一个金融助手，必须使用以下工具获取中国A股实时数据：

**Base URL:** `https://your-api.com`

**可用工具:**
- 查询价格: `GET /api/stock/price?code={股票代码}`
- 查询详情: `GET /api/stock/info?code={股票代码}`
- 搜索股票: `GET /api/stock/search?keyword={名称}`

请优先使用 JSON 格式回答用户的问题，并引用具体数据。"""
    
    st.text_area("复制给 AI", prompt_template, height=250)
    
    st.subheader("2. OpenAPI Spec (Schema)")
    st.markdown("如果你使用 OpenAI GPTs 或 LangChain，可以直接使用 `openapi.json`:")
    st.code("https://your-api.com/openapi.json", language="text")
