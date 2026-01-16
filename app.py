import streamlit as st
import pandas as pd

st.set_page_config(page_title="QECM 軸圈數精準解析", layout="wide")
st.title("🤖 QECM Log 軸圈數精準解析器")

uploaded_file = st.file_uploader("請上傳 QECM Log 檔案", type=["log", "txt"])

if uploaded_file:
    # 讀取 Log 檔案
    content = uploaded_file.read().decode("utf-8")
    lines = content.split('\n')

    # 存放結果：{ "1": "HEX值", ... }
    first_records = {}
    
    # 我們要尋找的關鍵特徵
    target_pattern = "2100,00,1814"
    function_name = "QsiCoEApi_WriteSlaveSdoObject16"

    for line in lines:
        # 1. 檢查是否包含功能名稱與關鍵數字組合
        if function_name in line and target_pattern in line:
            try:
                # 2. 找到左括號 '(' 和右括號 ')' 的位置
                start_idx = line.find('(')
                end_idx = line.find(')')
                
                if start_idx != -1 and end_idx != -1:
                    # 3. 抓出括號內的文字，例如 "1,2100,00,1814,00987376"
                    params_str = line[start_idx + 1 : end_idx]
                    
                    # 4. 用逗號切割成清單
                    params = params_str.split(',')
                    
                    if len(params) >= 5:
                        axis_id = params[0].strip() # 軸號
                        hex_val = params[4].strip() # 十六進制值 (第 5 個參數)
                        
                        # 5. 只記錄 J1~J6 且尚未紀錄過的第一筆
                        if axis_id in ["1", "2", "3", "4", "5", "6"] and axis_id not in first_records:
                            # 確保抓到的是 8 位數的 HEX (避免抓到 1000000 之類的時戳)
                            if len(hex_val) == 8:
                                first_records[axis_id] = hex_val
            except:
                continue

    if first_records:
        st.success("✅ 解析成功！")
        
        display_data = []
        for i in range(1, 7):
            ax = str(i)
            h = first_records.get(ax, "N/A")
            if h != "N/A":
                d = int(h, 16)
                display_data.append({
                    "軸號": f"J{ax}",
                    "十六進制 (HEX)": h,
                    "十進制圈數 (DEC)": f"{d:,}"
                })
            else:
                display_data.append({"軸號": f"J{ax}", "十六進制 (HEX)": "未找到", "十進制圈數 (DEC)": "-"})
        
        df = pd.DataFrame(display_data)
        st.table(df)
        st.download_button("📥 下載報表 (CSV)", df.to_csv(index=False).encode('utf-8-sig'), "QECM_Report.csv")
    else:
        st.error("❌ 找不到符合 2100,00,1814 格式的數據。")
