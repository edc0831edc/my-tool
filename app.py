import streamlit as st
import re
import pandas as pd

st.set_page_config(page_title="QECM 軸圈數解析工具", layout="wide")
st.title("🤖 QECM Log 軸圈數解析器 (首筆優先版)")
st.write("規則：搜尋 `2100,00,1814` 並提取 **第一次** 出現的軸號與數值")

# 上傳區
uploaded_file = st.file_uploader("請上傳 QECM Log 檔案 (.log 或 .txt)", type=["log", "txt"])

if uploaded_file:
    # 讀取 Log 內容
    content = uploaded_file.read().decode("utf-8")
    lines = content.split('\n')

    # 用來存放每個軸「最先」找到的數值
    first_values = {}

    # 正則表達式：匹配 (軸號,2100,00,1814,十六進制數值)
    pattern = r"\((\d+),2100,00,1814,([0-9a-fA-F]+)"

    for line in lines:
        match = re.search(pattern, line)
        if match:
            axis_num = match.group(1)  # 軸號
            hex_val = match.group(2)   # 十六進制值
            
            # 【關鍵修改】：如果這個軸號還沒被記錄過，才存進去 (即只保留第一筆)
            if axis_num not in first_values:
                first_values[axis_num] = hex_val

    if first_values:
        st.success("✅ 解析完成！已依照「首筆優先」原則提取數據：")
        
        final_results = []
        # 整理 J1 ~ J6 的數據
        for i in range(1, 7):
            axis_id = str(i)
            hex_str = first_values.get(axis_id, "無資料")
            
            if hex_str != "無資料":
                try:
                    dec_val = int(hex_str, 16)
                    final_results.append({
                        "軸號": f"J{axis_id}",
                        "十六進制 (Hex)": hex_str,
                        "十進制圈數 (Decimal)": f"{dec_val:,}"
                    })
                except:
                    final_results.append({"軸號": f"J{axis_id}", "十六進制 (Hex)": hex_str, "十進制圈數 (Decimal)": "轉換錯誤"})
            else:
                final_results.append({"軸號": f"J{axis_id}", "十六進制 (Hex)": "未找到關鍵字", "十進制圈數 (Decimal)": "-"})

        # 顯示結果表格
        df = pd.DataFrame(final_results)
        st.table(df)

        # 下載按鈕
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載首筆解析報表 (CSV)", data=csv, file_name="QECM_First_Record_Report.csv")
    else:
        st.error("❌ 找不到符合格式的數據，請確認 Log 內容。")

st.info("💡 目前邏輯：由上而下掃描 Log，僅保留每個軸號第一次出現的數值。")
