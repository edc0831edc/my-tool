import streamlit as st
import re
import pandas as pd

st.set_page_config(page_title="進位轉換器", layout="wide")
st.title("📑 線上 HEX 十六進制轉換工具")

# 設定區
st.sidebar.header("搜尋設定")
keyword = st.sidebar.text_input("輸入關鍵字 (例如 Address)", value="0x")

# 上傳區
uploaded_file = st.file_uploader("上傳文件 (.txt 或 .log)", type=["txt", "log"])

if uploaded_file:
    content = uploaded_file.read().decode("utf-8")
    # 尋找關鍵字後方的十六進制字元
    pattern = rf"{keyword}\s*([0-9a-fA-F]+)"
    matches = re.findall(pattern, content)

    if matches:
        results = []
        for m in matches:
            try:
                dec = int(m, 16)
                results.append({"原始資料": m, "十進制結果": dec})
            except:
                continue
        df = pd.DataFrame(results)
        st.success(f"找到 {len(results)} 筆資料")
        st.dataframe(df)
        
        # 下載按鈕
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("下載 CSV 結果", data=csv, file_name="output.csv")
    else:
        st.warning("找不到符合的數據。")
