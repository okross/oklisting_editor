import streamlit as st
import pandas as pd
import re
import io

# 頁面設定 (維持 wide，但透過 columns 來壓縮實際內容寬度)
st.set_page_config(page_title="Listing 關鍵字建構器", layout="wide")

# 透過左右留白，解決「太寬、滿版」的問題
spacer_left, main_col, spacer_right = st.columns([1, 8, 1])

with main_col:
    st.title("📝 跨境工具人專屬 Listing 建構器")
    st.markdown("---")
    
    # 比例設定為 3:7
    col_left, col_right = st.columns([0.3, 0.7])

    # ================= 自定義輸入框與驗證邏輯 =================
    def render_input(label, is_area=False, height=100, placeholder=""):
        # 建立輸入框
        if is_area:
            text = st.text_area(label, height=height, placeholder=placeholder)
        else:
            text = st.text_input(label, placeholder=placeholder)
        
        # 即時驗證與字數統計
        if text:
            char_count = len(text)
            word_count = len(text.split())
            st.caption(f"🔹 字元數: {char_count} | 單字數: {word_count}")
            
            # 偵測 Emoji (紅色嚴厲警告) - 涵蓋常見 Emoji 的 Unicode 範圍
            emoji_pattern = re.compile(r'[\U00010000-\U0010ffff\u2600-\u27BF]')
            if emoji_pattern.search(text):
                st.error("🚨 警告：偵測到 Emoji！平台規範嚴格禁止，建議立刻移除。")
            else:
                # 偵測非建議標點符號 (黃色提醒) - 僅允許英數字、空白、點、逗號、連字號
                special_char_pattern = re.compile(r'[^a-zA-Z0-9\s.,-]')
                if special_char_pattern.search(text):
                    st.warning("⚠️ 提醒：包含非建議的標點符號或特殊字元 (建議僅使用 . , - )")
                    
        return text

    # ================= 右半邊：Listing 撰寫區 =================
    with col_right:
        st.subheader("Listing 撰寫區")
        
        title = render_input("Title (標題)", is_area=False, placeholder="例如：Premium Suncatcher for Window Decor...")
        
        st.markdown("##### Bullet Points (五點描述)")
        bp1 = render_input("Bullet Point 1", is_area=True, height=80)
        bp2 = render_input("Bullet Point 2", is_area=True, height=80)
        bp3 = render_input("Bullet Point 3", is_area=True, height=80)
        bp4 = render_input("Bullet Point 4", is_area=True, height=80)
        bp5 = render_input("Bullet Point 5", is_area=True, height=80)
        
        search_terms = render_input("Search Terms", is_area=False)

        # 將所有右側內容合併，轉小寫方便後續比對
        all_text = f"{title} {bp1} {bp2} {bp3} {bp4} {bp5} {search_terms}".lower()
        
        st.markdown("---")
        st.subheader("📤 導出 Listing")
        
        # 匯出 Excel 功能
        if st.button("打包為 Excel 檔案"):
            df_export = pd.DataFrame({
                "欄位": ["Title", "Bullet Point 1", "Bullet Point 2", "Bullet Point 3", "Bullet Point 4", "Bullet Point 5", "Search Terms"],
                "內容": [title, bp1, bp2, bp3, bp4, bp5, search_terms]
            })
            
            # 使用 io.BytesIO 將 Excel 寫入記憶體，供用戶下載
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Listing Draft')
            
            st.download_button(
                label="📥 點此下載 Excel",
                data=buffer.getvalue(),
                file_name="Listing_Draft.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # ================= 左半邊：關鍵字庫與輸入區 =================
    with col_left:
        # 1. 上半部：顯示關鍵字狀態的 Container
        st.subheader("🔑 關鍵詞狀態")
        keyword_display = st.container() 
        
        st.divider() 
        
        # 2. 下半部：輸入區
        st.subheader("📥 導入關鍵字")
        uploaded_file = st.file_uploader("上傳 CSV 檔案 (單欄關鍵字)", type=['csv'])
        raw_keywords = st.text_area("或手動貼上關鍵字 (換行分隔)", height=150)
        
        kw_set = set() 
        
        if raw_keywords:
            for k in raw_keywords.split('\n'):
                if k.strip():
                    kw_set.add(k.strip().lower())
                    
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file, header=None)
                for val in df.values.flatten():
                    if pd.notna(val) and str(val).strip():
                        kw_set.add(str(val).strip().lower())
            except Exception as e:
                st.error(f"讀取 CSV 發生錯誤: {e}")

        # 3. 回到上半部進行標籤渲染
        with keyword_display:
            if not kw_set:
                st.info("請在下方輸入或上傳關鍵字")
            else:
                html_content = "<div style='display: flex; flex-wrap: wrap; gap: 6px; overflow-y: auto; max-height: 400px; padding: 5px;'>"
                
                for kw in sorted(list(kw_set)): 
                    count = len(re.findall(rf'\b{re.escape(kw)}\b', all_text))
                    
                    if count > 0:
                        html_content += f"<span style='background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; padding: 4px 8px; border-radius: 6px; font-size: 13px; font-weight: bold;'>{kw} ({count})</span>"
                    else:
                        html_content += f"<span style='background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; padding: 4px 8px; border-radius: 6px; font-size: 13px;'>{kw}</span>"
                        
                html_content += "</div>"
                st.markdown(html_content, unsafe_allow_html=True)
