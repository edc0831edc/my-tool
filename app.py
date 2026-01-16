import streamlit as st
import pandas as pd
import re

# 網頁基本設定
st.set_page_config(page_title="QECM Log 軸圈數精準解析器", layout="wide")
st.title("🤖 QECM Log 軸圈數自動解析工具 (首筆優先版)")
st.write("目前設定：搜尋 `2100,00,1814` 並提取各軸 (J1~J6) 的第一筆 HEX 數值。")

# 檔案上傳介面
uploaded_file = st.file_uploader("請上傳 QECM Log 檔案 (.log)", type=["log", "txt"])

if uploaded_file:
    # 讀取 Log 檔案
    content = uploaded_file.read().decode("utf-8")
    lines = content.split('\n')

    # 建立一個空間來存放 J1~J6 的第一筆數據
    # 格式會是 { "1": "00987376", "2": "006B53DD", ... }
    extracted_data = {}
    
    # 定義要搜尋的關鍵字組合
    target_key = "2100,00,1814"

    for line in lines:
        # 1. 先確認這一行有沒有關鍵字
        if target_key in line and "QsiCoEApi_WriteSlaveSdoObject16" in line:
            try:
                # 2. 使用正規表示式精準抓取括號內的 (軸號, ..., HEX)
                # 規則：抓取 ( 後的第一個數字，以及最後一個逗號後的十六進制
                match = re.search(r"\((\d+),.*,([0-9a-fA-F]{8})", line)
                
                if match:
                    axis_id = match.group(1)   # 軸號 (1, 2, 3...)
                    hex_value = match.group(2) # 十六進制值 (00987376...)
                    
                    # 3. 如果這個軸號還沒被紀錄過，且在 1~6 之間，就存入第一筆
                    if axis_id not in extracted_data and axis_id in ["1", "2", "3", "4", "5", "6"]:
                        extracted_data[axis_id] = hex_value
            except:
                continue

    # 當檔案掃描完畢，檢查是否有抓到資料
    if extracted_data:
        st.success("✅ 解析成功！結果如下表：")
        
        final_list = []
        # 依照 J1 到 J6 的順序整理
        for i in range(1, 7):
            axis_str = str(i)
            hex_str = extracted_data.get(axis_str, "N/A")
            
            if hex_str != "N/A":
                # 十六進制轉十進制
                dec_val = int(hex_str, 16)
                final_list.append({
                    "軸號": f"J{axis_str}",
                    "十六進制 (HEX)": hex_str,
                    "十進制圈數 (DEC)": f"{dec_val:,}" # 加上千分位
                })
            else:
                final_list.append({
                    "軸號": f"J{axis_str}",
                    "十六進制 (HEX)": "未找到數據",
                    "十進制圈數 (DEC)": "-"
                })

        # 顯示美化表格
        df = pd.DataFrame(final_list)
        st.table(df)

        # 提供下載 CSV 功能
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下載解析結果 (CSV)",
            data=csv,
            file_name="QECM_Axis_Report.csv",
            mime="text/csv",
        )
    else:
        st.error("❌ 無法在 Log 中解析到符合 `2100,00,1814` 格式的數據。")

st.divider()
st.info("💡 邏輯備註：本工具會由上而下掃描 Log，僅保留每個軸號第一次出現的寫入記錄。")
