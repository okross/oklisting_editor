import streamlit as st
import pandas as pd
import re
import io

# 頁面設定
st.set_page_config(page_title="Listing 關鍵字建構器 Pro", layout="wide")

# 透過左右留白，解決「太寬、滿版」的問題
spacer_left, main_col, spacer_right = st.columns([1, 8, 1])

with main_col:
    st.title("📝 Listing 關鍵字建構器")
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
            # 計算包含空格的總字元數
            char_count = len(text)
            word_count = len(text.split())
            st.caption(f"🔹 總字元數 (含空格): {char_count} | 單字數: {word_count}")
            
            # 1. 偵測 Emoji (紅色嚴厲警告)
            emoji_pattern = re.compile(r'[\U00010000-\U0010ffff\u2600-\u27BF]')
            if emoji_pattern.search(text):
                st.error("🚨 警告：偵測到 Emoji！平台規範嚴格禁止，建議立刻移除。")
            
            # 2. 偵測非建議標點符號 (黃色提醒)
            # 更新建議使用的符號清單：加入冒號 :
            suggested_symbols = '. , - % " ( ) :'
            # 找出所有不合法的符號並去重 (允許清單中加入 :)
            invalid_chars = set(re.findall(r'[^a-zA-Z0-9\s.,\-%"():]', text))
            
            if invalid_chars:
                # 將找出的不合法符號轉為字串顯示
                detected_symbols = " ".join(list(invalid_chars))
                st.warning(f'⚠️ 偵測到不建議的符號: [ {detected_symbols} ]。建議僅使用: {suggested_symbols}')
                    
        return text

    # ================= 右半邊：Listing 撰寫區 =================
    with col_right:
        st.subheader("Listing 撰寫區")
        
        title = render_input("Title (標題)", placeholder="輸入產品標題...")
        
        st.markdown("##### Bullet Points (五點描述)")
        bp1 = render_input("Bullet Point 1", is_area=True, height=80)
        bp2 = render_input("Bullet Point 2", is_area=True, height=80)
        bp3 = render_input("Bullet Point 3", is_area=True, height=80)
        bp4 = render_input("Bullet Point 4", is_area=True, height=80)
        bp5 = render_input("Bullet Point 5", is_area=True, height=80)
        
        search_terms = render_input("Search Terms")

        # 合併內容進行關鍵字比對
        all_text = f"{title} {bp1} {bp2} {bp3} {bp4} {bp5} {search_terms}".lower()
        
        st.markdown("---")
        st.subheader("📤 導出 Listing")
        
        if st.button("打包為 Excel 檔案"):
            df_export = pd.DataFrame({
                "欄位": ["Title", "Bullet Point 1", "Bullet Point 2", "Bullet Point 3", "Bullet Point 4", "Bullet Point 5", "Search Terms"],
                "內容": [title, bp1, bp2, bp3, bp4, bp5, search_terms]
            })
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Listing Draft')
            
            st.download_button(
                label="📥 點此下載 Excel",
                data=buffer.getvalue(),
                file_name="Listing_Draft.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # ================= 左半邊：關鍵字庫 =================
    with col_left:
        st.subheader("🔑 關鍵詞狀態")
        keyword_display = st.container() 
        
        st.divider() 
        
        st.subheader("📥 導入關鍵字")
        uploaded_file = st.file_uploader("上傳 CSV/Excel", type=['csv', 'xlsx', 'xls'])
        raw_keywords = st.text_area("或手動貼上關鍵字 (換行分隔)", height=150)
        
        kw_set = set() 
        
        if raw_keywords:
            for k in raw_keywords.split('\n'):
                if k.strip(): kw_set.add(k.strip().lower())
                    
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_kw = pd.read_csv(uploaded_file, header=None)
                else:
                    df_kw = pd.read_excel(uploaded_file, header=None)
                
                for val in df_kw.values.flatten():
                    if pd.notna(val) and str(val).strip():
                        kw_set.add(str(val).strip().lower())
            except Exception as e:
                st.error(f"讀取檔案失敗: {e}")

        with keyword_display:
            if not kw_set:
                st.info("請導入關鍵字")
            else:
                html_content = "<div style='display: flex; flex-wrap: wrap; gap: 6px; overflow-y: auto; max-height: 400px; padding: 5px;'>"
                for kw in sorted(list(kw_set)): 
                    count = len(re.findall(rf'\b{re.escape(kw)}\b', all_text))
                    bg = "#d4edda" if count > 0 else "#f8d7da"
                    color = "#155724" if count > 0 else "#721c24"
                    html_content += f"<span style='background-color: {bg}; color: {color}; border: 1px solid opacity 0.1; padding: 4px 8px; border-radius: 6px; font-size: 13px;'>{kw} ({count})</span>"
                html_content += "</div>"
                st.markdown(html_content, unsafe_allow_html=True)
