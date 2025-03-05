import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_autorefresh import st_autorefresh
import datetime

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="🌐 Dự báo lưu lượng", layout="wide")

# Tự động làm mới trang mỗi 500 giây (500.000 ms)
st_autorefresh(interval=500 * 1000, key="data_refresh")

# Lấy thời gian hiện tại theo UTC+7 (Giờ Việt Nam)
last_update = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%H:%M:%S")
st.write(f"Dữ liệu cập nhật lần cuối: {last_update}")

# Đọc dữ liệu từ Google Sheets
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)  # Kết nối Google Sheets
    df = conn.read(ttl=0) # Đọc dữ liệu từ Google Sheets
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
    st.markdown("<h1 style='text-align: center; color: red; font-size: 55px;'>Sản phẩm dự đoán lưu lượng về hồ thủy điện A Lưới<br>dựa trên mô hình học máy</h1>", unsafe_allow_html=True)
    st.write("")
    st.write("") 
    st.write("")

    col1, col2 = st.columns([2, 7])
    with col1:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.markdown("<h3>📅 Chọn số ngày bạn muốn hiển thị:</h3>", unsafe_allow_html=True)
        day_options = ["Hiển thị 7 ngày tới"] + df["Day"].tolist()
        selected_days = st.multiselect("Chọn ngày:", day_options, default=["Hiển thị 7 ngày tới"])

        # Nếu chọn "7 ngày tới", hiển thị toàn bộ 7 ngày
        if "Hiển thị 7 ngày tới" in selected_days or not selected_days:
            selected_days = df["Day"].tolist()

        # Kiểm tra nếu số ngày chọn dưới 2, hiển thị cảnh báo
        if len(selected_days) < 2:
            st.warning("⚠ Vui lòng chọn ít nhất 2 ngày!")
            selected_days = []  # Không vẽ biểu đồ nếu chọn ít hơn 2 ngày

    with col2:
        st.markdown("<h2 style='text-align: center; color: purple;'>📊 Biểu đồ tổng hợp: Lượng mưa & Lưu lượng dự đoán về hồ A Lưới</h2>", unsafe_allow_html=True)
        fig, ax1 = plt.subplots(figsize=(10, 5))
        
        # Lọc dữ liệu theo ngày được chọn
        filtered_df = df[df["Day"].isin(selected_days)]

        # Trục Y bên trái (Lưu lượng Q2)
        ax1.set_xlabel("Ngày")  
        ax1.set_ylabel("Lưu lượng dự đoán (m³/s)", color="red")  
        ax1.plot(filtered_df["Day"], filtered_df["Q2"], marker="o", linestyle="-", color="red", label="Lưu lượng dự đoán") 
        ax1.tick_params(axis="y", labelcolor="red")  
        ax1.set_ylim(0, 50)

        # Hiển thị giá trị lưu lượng dự đoán trên biểu đồ
        for i, txt in enumerate(filtered_df["Q2"]):
            ax1.annotate(f"{txt:.1f}", (filtered_df["Day"].iloc[i], filtered_df["Q2"].iloc[i]), 
                         textcoords="offset points", xytext=(0,5), ha='center', fontsize=14, color="red")

        # Trục Y bên phải (Lượng mưa - X) - Hiển thị dưới dạng đường nhưng đảo ngược trục
        ax2 = ax1.twinx()  
        ax2.set_ylabel("Lượng mưa (mm)", color="blue")  
        ax2.bar(filtered_df["Day"], filtered_df["X"], color="blue", alpha=0.5, label="Lượng mưa")  
        ax2.tick_params(axis="y", labelcolor="blue")  
        ax2.invert_yaxis()  # Đảo ngược trục Y: 0 nằm trên, giá trị lớn xuống dưới
        ax2.set_ylim(30, 0)

        # Hiển thị giá trị lượng mưa trên cột
        for i, txt in enumerate(filtered_df["X"]):
            ax2.annotate(f"{txt:.1f}", (filtered_df["Day"].iloc[i], filtered_df["X"].iloc[i]), 
                         textcoords="offset points", xytext=(0,5), ha='center', fontsize=14, color="blue")

        fig.tight_layout()  
        st.pyplot(fig)
else:
    st.error("⚠ Không có dữ liệu hoặc thiếu cột quan trọng trong Google Sheets!")  # Hiển thị lỗi nếu dữ liệu không hợp lệ)
