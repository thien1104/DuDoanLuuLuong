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
st.write(f"Dữ liệu cập nhật lần cuối: {last_update}")

# ✅ Hàm đọc dữ liệu từ Google Sheets
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)  # Kết nối Google Sheets
    df = conn.read(ttl=0)  # Đọc dữ liệu, không lưu cache (ttl=0)
    return df

# Lấy dữ liệu từ Google Sheets
df = load_data()

# Kiểm tra dữ liệu hợp lệ trước khi xử lý
if df is not None and not df.empty and "Day" in df.columns and "X" in df.columns and "Q2" in df.columns:
    # Chuyển cột "Day" sang kiểu datetime
    df["Day"] = pd.to_datetime(df["Day"], errors="coerce")
    
    # Xóa các dòng có giá trị NaN trong cột X hoặc Q2
    df = df.dropna(subset=["X", "Q2"])
    
    # Sắp xếp theo ngày và giữ lại bản ghi cuối cùng của mỗi ngày
    df = df.sort_values(by="Day").drop_duplicates(subset="Day", keep="last").tail(7)
    
    # Định dạng lại cột ngày để hiển thị đẹp hơn
    df["Day"] = df["Day"].dt.strftime("%d/%m")

    # Tiêu đề chính của ứng dụng
    st.markdown("<h1 style='text-align: center; color: purple;'>Sản phẩm dự đoán lưu lượng về hồ thủy điện A Lưới dựa trên mô hình học máy</h1>", unsafe_allow_html=True)

    # Biểu đồ tổng hợp lượng mưa & lưu lượng dự đoán
    st.markdown("<h2 style='text-align: center; color: red;'>📊 Biểu đồ tổng hợp: Lượng mưa & Lưu lượng dự đoán</h2>", unsafe_allow_html=True)
    
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
        fig, ax1 = plt.subplots(figsize=(10, 5))
        
        # Trục Y bên trái (Lưu lượng Q2)
        ax1.set_xlabel("Ngày")  
        ax1.set_ylabel("Lưu lượng dự đoán (m³/s)", color="red")  
        ax1.plot(df["Day"], df["Q2"], marker="o", linestyle="-", color="red", label="Lưu lượng dự đoán")  
        ax1.tick_params(axis="y", labelcolor="red")  

        # Hiển thị giá trị lưu lượng dự đoán trên biểu đồ
        for i, txt in enumerate(df["Q2"]):
            ax1.annotate(f"{txt:.1f}", (df["Day"].iloc[i], df["Q2"].iloc[i]), 
                         textcoords="offset points", xytext=(0,5), ha='center', fontsize=10, color="red")

        # Trục Y bên phải (Lượng mưa - X)
        ax2 = ax1.twinx()  
        ax2.set_ylabel("Lượng mưa (mm)", color="blue")  
        bars = ax2.bar(df["Day"], df["X"], color="blue", alpha=0.5, label="Lượng mưa")  
        ax2.tick_params(axis="y", labelcolor="blue")  
        ax2.invert_yaxis()  # Đảo ngược trục Y để 0 nằm trên, giá trị lớn hơn xuống dưới

        # Hiển thị giá trị lượng mưa trên biểu đồ
        for bar in bars:
            height = bar.get_height()
            ax2.annotate(f"{height:.1f}", xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0,5), textcoords="offset points", ha='center', fontsize=10, color="blue")

        fig.tight_layout()  
        st.pyplot(fig)  



else:
    st.error("⚠ Không có dữ liệu hoặc thiếu cột quan trọng trong Google Sheets!")  # Hiển thị lỗi nếu dữ liệu không hợp lệ
