import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="QECM 精準解析器", layout="wide")
st.title("🤖 QECM Log 軸圈數自動解析工具")

uploaded_file = st.file_uploader("請上傳您的 .log 檔案", type=["log", "txt"])

if uploaded_file:
    # 讀取 Log 並按行拆分
    content = uploaded_file.read().decode("utf-8")
    lines = content.splitlines()

    # 存放結果的字典：{軸號: HEX值}
    results = {}
    
    # 精準匹配規則：尋找包含關鍵字 2100,00,1814 的行
    # 並抓取 (軸號, ... 之後的最後一組 8 位 HEX
    pattern = r"\((\d+),2100,00,1814,([0-9a-fA-F]{8})\)"

    for line in lines:
        match = re.search(pattern, line)
        if match:
            axis_id = match.group(1) # 軸號 (1-6)
            hex_val = match.group(2) # HEX (00987376 等)
            
            # 只紀錄第一次出現的該軸數據 (首筆優先)
            if axis_id in ["1", "2", "3", "4", "5", "6"] and axis_id not in results:
                results[axis_id] = hex_val

    if results:
        st.success(f"解析成功！已找到各軸首筆數據。")
        
        final_table = []
        for i in range(1, 7):
            ax = str(i)
            h = results.get(ax, "N/A")
            if h != "N/A":
                d = int(h, 16)
                final_table.append({"軸號": f"J{ax}", "十六進制 (HEX)": h, "十進制圈數 (DEC)": f"{d:,}"})
            else:
                final_table.append({"軸號": f"J{ax}", "十六進制 (HEX)": "未找到", "十進制圈數 (DEC)": "-"})
        
        df = pd.DataFrame(final_table)
        st.table(df)
        st.download_button("下載 CSV 報表", df.to_csv(index=False).encode('utf-8-sig'), "QECM_Report.csv")
    else:
        st.error("在檔案中找不到關鍵字 2100,00,1814。請確認檔案內容。")
