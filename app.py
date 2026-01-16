import streamlit as st
import re
import pandas as pd

st.set_page_config(page_title="QECM 軸圈數解析工具", layout="wide")
st.title("🤖 QECM Log 軸圈數自動解析器")
st.write("規則：搜尋 `2100,00,1814` 並提取對應軸號與十六進制數值")

# 上傳區
uploaded_file = st.file_uploader("請上傳 QECM Log 檔案 (.log 或 .txt)", type=["log", "txt"])

if uploaded_file:
    # 讀取 Log 內容
    content = uploaded_file.read().decode("utf-8")
    lines = content.split('\n')

    # 用來存放每個軸最後找到的數值
    # 格式：{ "1": "00987376", "2": "006B53DD", ... }
    latest_values = {}

    # 正規表示式說明：
    # \((\d+) : 抓取左括號後的數字 (軸號)
    # ,2100,00,1814, : 匹配你的關鍵字格式
    # ([0-9a-fA-F]+) : 抓取後方的十六進制字串
    pattern = r"\((\d+),2100,00,1814,([0-9a-fA-F]+)"

    for line in lines:
        match = re.search(pattern, line)
        if match:
            axis_num = match.group(1)  # 軸號 (1, 2, 3...)
            hex_val = match.group(2)   # 十六進制值
            latest_values[axis_num] = hex_val

    if latest_values:
        st.success("✅ 解析成功！已提取最新軸圈數數據：")
        
        final_results = []
        # 整理 J1 ~ J6 的數據
        for i in range(1, 7):
            axis_id = str(i)
            hex_str = latest_values.get(axis_id, "無資料")
            
            if hex_str != "無資料":
                try:
                    dec_val = int(hex_str, 16)
                    final_results.append({
                        "軸號": f"J{axis_id}",
                        "十六進制 (Hex)": hex_str,
                        "十進制圈數 (Decimal)": f"{dec_val:,}" # 加上千分位符號方便閱讀
                    })
                except:
                    final_results.append({"軸號": f"J{axis_id}", "十六進制 (Hex)": hex_str, "十進制圈數 (Decimal)": "轉換錯誤"})
            else:
                final_results.append({"軸號": f"J{axis_id}", "十六進制 (Hex)": "未找到關鍵字", "十進制圈數 (Decimal)": "-"})

        # 轉換為表格顯示
        df = pd.DataFrame(final_results)
        
        # 使用美觀的表格呈現
        st.table(df)

        # 額外提供下載功能
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載解析報表 (CSV)", data=csv, file_name="QECM_Axis_Report.csv")
    else:
        st.error("❌ 在 Log 中找不到關鍵字 `2100,00,1814`。請確認檔案內容格式。")

st.info("💡 提示：程式會自動抓取 Log 中「最後一次」出現的寫入數值作為目前的圈數。")
