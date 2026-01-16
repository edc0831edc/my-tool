import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="QECM 軸圈數精準解析", layout="wide")
st.title("🤖 QECM Log 軸圈數精準解析器")

uploaded_file = st.file_uploader("請上傳 QECM Log 檔案", type=["log", "txt"])

if uploaded_file:
    # 讀取 Log 檔案
    content = uploaded_file.read().decode("utf-8")
    lines = content.split('\n')

    # 存放每個軸最先找到的數據 { "1": "HEX", ... }
    first_records = {}
    target_key = "2100,00,1814"

    for line in lines:
        # 尋找包含關鍵字的行
        if target_key in line and "QsiCoEApi_WriteSlaveSdoObject16" in line:
            # 正規表示式：抓取括號後的第一個數字(軸號)，以及最後一個逗號後的 8 位 HEX
            match = re.search(r"\((\d+),.*,([0-9a-fA-F]{8})\)", line)
            if match:
                axis_id = match.group(1)
                hex_val = match.group(2)
                # 首筆優先：如果該軸還沒紀錄過，才存入
                if axis_id in ["1", "2", "3", "4", "5", "6"] and axis_id not in first_records:
                    first_records[axis_id] = hex_val

    if first_records:
        st.success("✅ 已成功提取各軸首筆數據")
        
        display_list = []
        for i in range(1, 7):
            ax = str(i)
            h = first_records.get(ax, "N/A")
            if h != "N/A":
                d = int(h, 16)
                display_list.append({"軸號": f"J{ax}", "十六進制 (HEX)": h, "十進制圈數 (DEC)": f"{d:,}"})
            else:
                display_list.append({"軸號": f"J{ax}", "十六進制 (HEX)": "未找到", "十進制圈數 (DEC)": "-"})
        
        df = pd.DataFrame(display_list)
        st.table(df)
        st.download_button("📥 下載報表", df.to_csv(index=False).encode('utf-8-sig'), "Report.csv")
    else:
        st.error("❌ 找不到符合 2100,00,1814 格式的數據，請確認上傳的 Log 是否正確。")
