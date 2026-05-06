import streamlit as st
import pandas as pd
import re

# 設定寬螢幕模式
st.set_page_config(page_title="Listing 關鍵字建構器", layout="wide")

st.title("📝 Listing 關鍵字建構器")

# 切分 3:7 比例
col_left, col_right = st.columns([0.3, 0.7])

# ================= 右半邊：Listing 撰寫區 =================
with col_right:
    st.subheader("Listing 撰寫區")
    title = st.text_input("Title (標題)")
    
    st.markdown("##### Bullet Points (五點描述)")
    bp1 = st.text_area("Bullet Point 1", height=80)
    bp2 = st.text_area("Bullet Point 2", height=80)
    bp3 = st.text_area("Bullet Point 3", height=80)
    bp4 = st.text_area("Bullet Point 4", height=80)
    bp5 = st.text_area("Bullet Point 5", height=80)
    
    search_terms = st.text_input("Search Terms")

    # 將所有右側內容合併，轉小寫方便後續比對
    all_text = f"{title} {bp1} {bp2} {bp3} {bp4} {bp5} {search_terms}".lower()

# ================= 左半邊：關鍵字庫與輸入區 =================
with col_left:
    
    # 1. 宣告上半部的 Container (用來預留顯示關鍵字狀態的空間)
    st.subheader("🔑 關鍵詞狀態")
    keyword_display = st.container() 
    
    st.divider() # 加一條分隔線區隔上下半部
    
    # 2. 下半部：輸入區 (CSV 上傳 + 手動輸入)
    st.subheader("📥 導入關鍵字")
    uploaded_file = st.file_uploader("上傳 CSV 檔案 (單欄關鍵字)", type=['csv'])
    raw_keywords = st.text_area("或手動貼上關鍵字 (換行分隔)", height=150)
    
    # --- 處理資料收集 ---
    kw_set = set() # 使用 set 自動去除重複的關鍵字
    
    # 解析手動輸入
    if raw_keywords:
        for k in raw_keywords.split('\n'):
            if k.strip():
                kw_set.add(k.strip().lower())
                
    # 解析 CSV 上傳 (假設 CSV 內容就是一列一列的關鍵字)
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, header=None)
            # 將 dataframe 轉換為一維陣列並加入 set 中
            for val in df.values.flatten():
                if pd.notna(val) and str(val).strip():
                    kw_set.add(str(val).strip().lower())
        except Exception as e:
            st.error(f"讀取 CSV 發生錯誤: {e}")

    # 3. 回到上半部的 Container 進行渲染
    with keyword_display:
        if not kw_set:
            st.info("請在下方輸入或上傳關鍵字")
        else:
            # 使用 HTML 與 CSS 來客製化標籤外觀
            html_content = "<div style='display: flex; flex-wrap: wrap; gap: 6px; overflow-y: auto; max-height: 400px; padding: 5px;'>"
            
            for kw in sorted(list(kw_set)): # 排序一下讓顯示更整齊
                # 計算出現次數
                count = len(re.findall(rf'\b{re.escape(kw)}\b', all_text))
                
                if count > 0:
                    # 被使用到：綠底綠字
                    html_content += f"<span style='background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; padding: 4px 8px; border-radius: 6px; font-size: 13px; font-weight: bold;'>{kw} ({count})</span>"
                else:
                    # 未被使用：紅底紅字
                    html_content += f"<span style='background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; padding: 4px 8px; border-radius: 6px; font-size: 13px;'>{kw}</span>"
                    
            html_content += "</div>"
            
            # 渲染出帶顏色的 HTML 標籤
            st.markdown(html_content, unsafe_allow_html=True)
