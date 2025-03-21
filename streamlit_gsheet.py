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
background_image_path = "A_luoi.jpg"
background_base64 = get_base64(background_image_path)

st.markdown("""
    <style>
        /* Điều chỉnh font chữ theo kích thước màn hình */
        @media screen and (max-width: 768px) {
            h1, h2, h3, h4, h5, h6 {
                font-size: 20px !important;
            }
            p, li, a {
                font-size: 16px !important;
            }
        }

        @media screen and (max-width: 480px) {
            h1, h2, h3, h4, h5, h6 {
                font-size: 16px !important;
            }
            p, li, a {
                font-size: 14px !important;
            }
        }

        /* Căn chỉnh logo */
        .stImage img {
            max-width: 100% !important;
            height: auto !important;
        }

        /* Điều chỉnh menu */
        .css-18e3th9 {
            flex-wrap: wrap;
            justify-content: center;
        }
    </style>
""", unsafe_allow_html=True)

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

# Tự động làm mới trang mỗi 500 giây (500.000 ms)
st_autorefresh(interval=500 * 1000, key="data_refresh")

st.markdown("""
    <style>
        .header-container {
            background-color: #F5F5F5 !important; /* Màu nền trắng */
            padding: 40px 50px; /* Khoảng cách lề */
            width: 100%;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.3); /* Hiệu ứng đổ bóng */
        }
        .logo-container {
            display: flex;
            align-items: center;
        }
        .logo-container img {
            height: 90px; /* Kích thước logo */
            margin-right: 15px;
        }
        .menu-container {
            display: flex;
            gap: 20px;
        }
        .menu-container button {
            background-color: transparent;
            border: none;
            font-size: 25px;
            font-weight: bold;
            color: purple; /* Màu chữ tím */
            cursor: pointer;
        }
        .menu-container button:hover {
            color: red;
        }
    </style>
""", unsafe_allow_html=True)

# Hàm mã hóa hình ảnh thành base64
def get_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

image_path = "Logo.png"  # Đường dẫn ảnh logo
image_base64 = get_base64(image_path)

# Hiển thị phần header với logo và menu
st.markdown(f"""
    <div class="header-container">
        <div class="logo-container">
            <img src="data:image/png;base64,{image_base64}" alt="Logo">
            <div>
                <p style="font-size: 26px; font-weight: bold; color: #003399; margin: 0;">
                    KHOA XÂY DỰNG CÔNG TRÌNH THỦY
                </p>
                <p style="font-size: 32px; font-weight: bold; color: blue; margin: 0;">
                    NGHIÊN CỨU KHOA HỌC
                </p>
            </div>
        </div>
        <div class="menu-container">
            <button onclick="alert('Trang chủ')">Trang chủ</button>
            <button onclick="alert('Thành viên')">Thành viên</button>
            <button onclick="alert('Giới thiệu')">Giới thiệu</button>
            <button onclick="alert('Góp ý')">Góp ý</button>
        </div>  
    </div>
""", unsafe_allow_html=True)

# Hiển thị biểu đồ mặc định trên trang chủ
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.markdown("""
    <div style="text-align: center;">
        <p style="font-weight: bold; color: red; font-size: 50px; text-shadow: 3px 3px 5px rgba(0, 0, 0, 0.3);margin-top: 0;">SẢN PHẨM DỰ BÁO LƯU LƯỢNG VỀ HỒ THỦY ĐIỆN A LƯỚI<br>DỰA TRÊN MÔ HÌNH HỌC MÁY</p>
    </div>
    """, unsafe_allow_html=True)
st.write("")
st.write("")

def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)  # Kết nối Google Sheets
    df = conn.read(worksheet="LuongMua", ttl=0) # Đọc dữ liệu từ Google Sheets
    return df

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
        fig, ax1 = plt.subplots(figsize=(9, 5), facecolor=None)
        fig.patch.set_alpha(0.6)
        
        # Lọc dữ liệu theo ngày được chọn
        filtered_df = df[df["Day"].isin(selected_days)]

        q2_min = filtered_df["Q2"].min() - 2
        q2_max = filtered_df["Q2"].max() + 5
        x2_min = filtered_df["X"].min()
        x2_max = filtered_df["X"].max() + 2

        # Trục Y bên trái (Lưu lượng Q2)
        ax1.set_xlabel("Ngày")  
        ax1.set_ylabel("Lưu lượng dự đoán (m³/s)", color="red")  
        ax1.plot(filtered_df["Day"], filtered_df["Q2"], marker="o", linestyle="-", color="red", label="Lưu lượng dự đoán") 
        ax1.tick_params(axis="y", labelcolor="red")  
        ax1.set_ylim(q2_min, q2_max)
        ax1.set_facecolor("none")  # Trục chính không có nền
        ax1.grid(True, linestyle="--", color="red", alpha=0.3)  # Lưới cho trục X và trục Y bên trái (Q2)

        # Hiển thị giá trị lưu lượng dự đoán trên biểu đồ
        for i, txt in enumerate(filtered_df["Q2"]):
            ax1.annotate(f"{txt:.2f}", (filtered_df["Day"].iloc[i], filtered_df["Q2"].iloc[i]), 
                         textcoords="offset points", xytext=(0,5), ha='center', fontsize=14, color="red")

        # Trục Y bên phải (Lượng mưa - X) - Hiển thị dưới dạng đường nhưng đảo ngược trục
        ax2 = ax1.twinx()  
        ax2.set_ylabel("Lượng mưa (mm)", color="blue")  
        ax2.bar(filtered_df["Day"], filtered_df["X"], color="blue", alpha=0.5, label="Lượng mưa")  
        ax2.tick_params(axis="y", labelcolor="blue")  
        ax2.invert_yaxis()  # Đảo ngược trục Y: 0 nằm trên, giá trị lớn xuống dưới
        ax2.set_ylim(x2_max, x2_min)
        ax2.set_facecolor("none")  # Trục chính không có nền
        ax2.grid(True, linestyle="--", color="blue", alpha=0.3)  # Lưới cho trục Y bên phải (X)

        # Hiển thị giá trị lượng mưa trên cột
        for i, txt in enumerate(filtered_df["X"]):
            ax2.annotate(f"{txt:.2f}", (filtered_df["Day"].iloc[i], filtered_df["X"].iloc[i]), 
                         textcoords="offset points", xytext=(0,5), ha='center', fontsize=14, color="blue")

        fig.tight_layout()  
        st.pyplot(fig)

    col3, col4 = st.columns([1, 4])
    with col3:
        st.markdown("<h2 style='font-size: 32px; color: purple;'> THÀNH VIÊN NHÓM</h2>", unsafe_allow_html=True)
    with col4:
        st.write("")
        st.markdown(f"""
        <div style="display: flex; flex-direction: column;">
            <p style="font-size: 26px; color: #003399; font-weight: bold; margin-bottom: 2px;">Giáo viên hướng dẫn:</p>
            <div style="font-size: 24px; line-height: 1.5;">
                   PGS.TS. Nguyễn Chí Công<br>
                   TS. Đoàn Viết Long<br>
                   ThS. Phạm Lý Triều
            </div>
            <p style="font-size: 26px; color: #003399; font-weight: bold; margin-top: 10px; margin-bottom: 2px;">Sinh viên thực hiện:</p>
            <div style="font-size: 24px; line-height: 1.5;">
                Lê Tấn Duy<br>
                Lê Thanh Thiên
            </div>
        </div>
        """, unsafe_allow_html=True)
