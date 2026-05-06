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
    
    col_left, col_right = st.columns([0.3, 0.7])

    # ================= 錯誤定位顯示函式 =================
    def check_errors_and_display(text):
        if not text:
            return
        
        # 準備標記字串
        # 🔴 紅色: Emoji
        # 🟡 黃色: 不合法符號
        emoji_pattern = re.compile(r'[\U00010000-\U0010ffff\u2600-\u27BF]')
        allowed_chars = r'a-zA-Z0-9\s.,\-%"()'
        
        error_marks = []
        has_critical = False
        has_warning = False
        
        for char in text:
            if emoji_pattern.search(char):
                error_marks.append('<span style="color:white; background-color:red; font-weight:bold; padding:0 2px;">X</span>')
                has_critical = True
            elif not re.match(f'[{allowed_chars}]', char):
                error_marks.append('<span style="color:black; background-color:yellow; font-weight:bold; padding:0 2px;">X</span>')
                has_warning = True
            else:
                # 為了對齊，沒問題的地方放透明的字或全形空格（這裡用 HTML 佔位）
                error_marks.append('<span style="color:#f0f2f6;">_</span>') 
        
        # 顯示字數統計（含空格）
        char_count = len(text)
        st.caption(f"📏 總字元數 (含空格): {char_count}")

        # 如果有錯誤，顯示檢視區
        if has_critical or has_warning:
            st.markdown("---")
            st.markdown("⚠️ **錯誤位置檢視 (對應上方位置):**")
            # 這裡使用 code 字體確保等寬對齊
            st.markdown(f'<div style="font-family: monospace; word-break: break-all; line-height: 1.5;">'
                        f'{"".join(error_marks)}'
                        f'</div>', unsafe_allow_html=True)
            
            if has_critical:
                st.error("❌ 紅色 X：偵測到 Emoji，請務必移除。")
            if has_warning:
                st.warning("⚠️ 黃色 X：非建議符號，請確認是否符合規範。")
            st.markdown("---")

    # ================= 自定義輸入框渲染 =================
    def render_input(label, is_area=False, height=100, placeholder=""):
        if is_area:
            text = st.text_area(label, height=height, placeholder=placeholder)
        else:
            text = st.text_input(label, placeholder=placeholder)
        
        check_errors_and_display(text)
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

        all_text = f"{title} {bp1} {bp2} {bp3} {bp4} {bp5} {search_terms}".lower()
        
        st.markdown("---")
        if st.button("打包為 Excel 檔案"):
            df_export = pd.DataFrame({
                "欄位": ["Title", "Bullet Point 1", "Bullet Point 2", "Bullet Point 3", "Bullet Point 4", "Bullet Point 5", "Search Terms"],
                "內容": [title, bp1, bp2, bp3, bp4, bp5, search_terms]
            })
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False)
            st.download_button(label="📥 下載 Excel", data=buffer.getvalue(), file_name="Listing.xlsx")

    # ================= 左半邊：關鍵字庫 =================
    with col_left:
        st.subheader("🔑 關鍵詞狀態")
        keyword_display = st.container() 
        st.divider() 
        st.subheader("📥 導入關鍵字")
        uploaded_file = st.file_uploader("上傳 CSV/Excel", type=['csv', 'xlsx', 'xls'])
        raw_keywords = st.text_area("手動貼上關鍵字", height=150)
        
        kw_set = set() 
        if raw_keywords:
            for k in raw_keywords.split('\n'):
                if k.strip(): kw_set.add(k.strip().lower())
        if uploaded_file:
            try:
                df_kw = pd.read_csv(uploaded_file, header=None) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file, header=None)
                for val in df_kw.values.flatten():
                    if pd.notna(val) and str(val).strip(): kw_set.add(str(val).strip().lower())
            except: st.error("讀取失敗")

        with keyword_display:
            if not kw_set:
                st.info("請導入關鍵字")
            else:
                html_content = "<div style='display: flex; flex-wrap: wrap; gap: 6px; overflow-y: auto; max-height: 400px;'>"
                for kw in sorted(list(kw_set)): 
                    count = len(re.findall(rf'\b{re.escape(kw)}\b', all_text))
                    bg = "#d4edda" if count > 0 else "#f8d7da"
                    color = "#155724" if count > 0 else "#721c24"
                    html_content += f"<span style='background-color:{bg}; color:{color}; padding:4px 8px; border-radius:6px; font-size:13px;'>{kw} ({count})</span>"
                html_content += "</div>"
                st.markdown(html_content, unsafe_allow_html=True)
