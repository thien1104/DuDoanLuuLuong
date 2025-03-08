import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_autorefresh import st_autorefresh
import datetime
import base64

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="Nghiên cứu khoa học", layout="wide")

# Hàm để chuyển ảnh sang dạng Base64
def get_base64(file_path):
    with open(file_path, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()
    return encoded_string

# Đọc ảnh nền từ thư mục máy
background_image_path = "Aluoi4.jpg"  # Đảm bảo đường dẫn đúng với ảnh trong thư mục dự án
background_base64 = get_base64(background_image_path)
# CSS tùy chỉnh để thêm hình nền
page_bg_img = f"""
<style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{background_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
</style>
"""
# Thêm CSS vào ứng dụng
st.markdown(page_bg_img, unsafe_allow_html=True)

col3, col4, col5 = st.columns([3,7,2])
with col3:
    html_code = """
    <div style="display: flex; align-items: center; padding: 10px; border-radius: 5px; width: fit-content;">
        <img src="data:image/png;base64,{image_base64}" alt="Logo" style="height: 70px; margin-right: 15px;">
        <div>
            <p style="font-size: 18px; font-weight: bold; margin: 0;color: blue;">TRƯỜNG ĐẠI HỌC BÁCH KHOA - ĐHĐN</p>
            <p style="font-size: 20px; font-weight: bold; color: blue; margin: 0;">KHOA XÂY DỰNG CÔNG TRÌNH THỦY</p>
        </div>
    </div>
    """
    # Đọc hình ảnh và chuyển sang Base64
    def get_base64(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    image_path = "Logo_KhoaXDCongTrinhThuy.png"  # Đường dẫn ảnh logo
    image_base64 = get_base64(image_path)

    # Hiển thị trên Streamlit
    st.markdown(html_code.format(image_base64=image_base64), unsafe_allow_html=True)

with col4:
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.markdown("""
<h1 style='color: blue; font-size: 70px; font-family: Arial, sans-serif; text-shadow: 3px 3px 5px rgba(0, 0, 0, 0.8);'>NGHIÊN CỨU KHOA HỌC</h1>""", unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div style="text-align: right;">
        <p style="font-size: 20px; font-weight: bold; color: blue; margin-bottom: 1px;">Giáo viên hướng dẫn:</p>
        <p style="line-height: 1.2;font-size: 18px;">PGS.TS. Nguyễn Chí Công<br>TS. Đoàn Viết Long<br>ThS. Phạm Lý Triều</p>
        <p style="font-size: 20px; font-weight: bold; color: blue; margin-bottom: 1px;">Sinh viên thực hiện:</p>
        <p style="line-height: 1.2;font-size: 18px;">Lê Tấn Duy - 22DTTM<br>Lê Thanh Thiên - 22DTTM</p>
    </div>
    """, unsafe_allow_html=True)

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
    st.write("")
    st.write("")
    st.markdown("<h1 style='text-align: center; color: red; font-size: 50px; text-shadow: 3px 3px 5px rgba(0, 0, 0, 0.3);'>  SẢN PHẨM DỰ ĐOÁN LƯU LƯỢNG VỀ HỒ THỦY ĐIỆN A LƯỚI<br>DỰA TRÊN MÔ HÌNH HỌC MÁY</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 7])
    with col1:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.markdown("<h3 style='font-size: 25px;'>📅 Chọn số ngày bạn muốn hiển thị:</h3>", unsafe_allow_html=True)
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
        st.markdown("<h2 style='text-align: center; color: purple; font-size:40px;'>📊 Biểu đồ tổng hợp: Lượng mưa & Lưu lượng dự đoán về hồ A Lưới</h2>", unsafe_allow_html=True)
        fig, ax1 = plt.subplots(figsize=(10, 5),facecolor=None)
        fig.patch.set_alpha(0.7) # Đặt màu nền cho biểu đồ

        # Lọc dữ liệu theo ngày được chọn
        filtered_df = df[df["Day"].isin(selected_days)]

        # Trục Y bên trái (Lưu lượng Q2)
        ax1.set_xlabel("Ngày")  
        ax1.set_ylabel("Lưu lượng dự đoán (m³/s)", color="red")  
        ax1.plot(filtered_df["Day"], filtered_df["Q2"], marker="o", linestyle="-", color="red", label="Lưu lượng dự đoán") 
        ax1.tick_params(axis="y", labelcolor="red")  
        ax1.set_ylim(0, 50)
        ax1.grid(True, linestyle="--", color="red", alpha=0.3)  # Lưới cho trục X và trục Y bên trái (Q2)
        ax1.set_facecolor("none")  # Trục chính không có nền

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
        ax2.grid(True, linestyle="--", color="blue", alpha=0.3)  # Lưới cho trục Y bên phải (X)

        # Hiển thị giá trị lượng mưa trên cột
        for i, txt in enumerate(filtered_df["X"]):
            ax2.annotate(f"{txt:.1f}", (filtered_df["Day"].iloc[i], filtered_df["X"].iloc[i]), 
                         textcoords="offset points", xytext=(0,5), ha='center', fontsize=14, color="blue")

        fig.tight_layout()  
        st.pyplot(fig)

else:
    st.error("⚠ Không có dữ liệu hoặc thiếu cột quan trọng trong Google Sheets!")  # Hiển thị lỗi nếu dữ liệu không hợp lệ)