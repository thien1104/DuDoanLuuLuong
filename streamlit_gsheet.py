import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_autorefresh import st_autorefresh
import datetime

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="🌐 Dự đoán lưu lượng", layout="wide")

# Tự động làm mới trang mỗi 500 giây (500.000 ms)
st_autorefresh(interval=500 * 1000, key="data_refresh")

# Hiển thị thời gian cập nhật dữ liệu
last_update = datetime.datetime.now().strftime("%H:%M:%S")
st.write(f"🕒 Dữ liệu cập nhật lần cuối: {last_update}")

# ✅ Hàm đọc dữ liệu từ Google Sheets
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0,  worksheet="LuongMua")
    return df

# Lấy dữ liệu từ Google Sheets
df = load_data()

if df is not None and not df.empty and "Day" in df.columns and "X" in df.columns and "Q2" in df.columns:
    # Chuyển cột "Day" sang dạng datetime
    df["Day"] = pd.to_datetime(df["Day"], errors="coerce")
    # Xóa những dòng có giá trị NaN trong cột X hoặc Q2 (đảm bảo đủ dữ liệu)
    df = df.dropna(subset=["X", "Q2"])
    # Sắp xếp theo ngày (từ cũ đến mới) và giữ lại bản ghi CUỐI CÙNG của mỗi ngày
    df = df.sort_values(by="Day").drop_duplicates(subset="Day", keep="last")
    # Định dạng lại ngày để hiển thị đẹp hơn
    df["Day"] = df["Day"].dt.strftime("%d/%m")

    st.markdown("<h1 style='text-align: center; color: purple;'>Dự đoán lưu lượng mưa trên sông A Lưới</h1>", unsafe_allow_html=True)

    # Biểu đồ lượng mưa
    st.markdown("<h2 style='text-align: center; color: red;'>📊 Biểu đồ lượng mưa theo ngày</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 5])
    with col1:
        st.markdown("<h3>📅 Chọn ngày bạn muốn dự báo:</h3>", unsafe_allow_html=True)
        selected_day = st.selectbox("Chọn ngày:", df["Day"].unique(), key="day_x", label_visibility="hidden")
        selected_data = df[df["Day"] == selected_day]

        if not selected_data.empty:
            X_value = selected_data.iloc[0]["X"]
            Q2_value = selected_data.iloc[0]["Q2"]
        else:
            X_value = "Không có dữ liệu"
            Q2_value = "Không có dữ liệu"

        st.markdown(f"<h2>➡ Lượng mưa (X): <span style='color: red;'>{X_value} mm</span></h2>", unsafe_allow_html=True)
        st.markdown(f"<h2>➡ Lưu lượng dự đoán (Q2): <span style='color: red;'>{Q2_value} m³/s</span></h2>", unsafe_allow_html=True)

    with col2:
        fig1, ax1 = plt.subplots(figsize=(9, 4))
        ax1.bar(df["Day"], df["X"], color="blue", alpha=0.7)
        ax1.set_xlabel("Ngày")
        ax1.set_ylabel("Lượng mưa (mm)")
        st.pyplot(fig1)

    # 📈 Biểu đồ lưu lượng dự đoán
    st.markdown("<h2 style='text-align: center; color: red;'>📈 Biểu đồ lưu lượng dự đoán theo ngày</h2>", unsafe_allow_html=True)

    col3, col4 = st.columns([2, 5])
    with col3:
        st.empty()
    with col4:
        fig2, ax2 = plt.subplots(figsize=(9, 4))
        ax2.plot(df["Day"], df["Q2"], marker="o", linestyle="-", color="red")
        ax2.set_xlabel("Ngày")
        ax2.set_ylabel("Lưu lượng dự đoán (m³/s)")
        st.pyplot(fig2)

else:
    st.error("⚠ Không có dữ liệu hoặc thiếu cột quan trọng trong Google Sheets!")
# Lưu dữ liệu thành file CSV
csv_filename = "data.csv"
df.to_csv(csv_filename, index=False)
