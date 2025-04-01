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
        /* Kích thước chữ trên màn hình lớn */
        h1 { font-size: 32px !important; }
        h2 { font-size: 28px !important; }
        h3 { font-size: 24px !important; }
        p, li, a { font-size: 18px !important; }

        /* Màn hình tablet (từ 768px trở xuống) */
        @media screen and (max-width: 768px) {
            h1 { font-size: 26px !important; }
            h2 { font-size: 24px !important; }
            h3 { font-size: 20px !important; }
            p, li, a { font-size: 16px !important; }
        }

        /* Màn hình điện thoại (từ 480px trở xuống) */
        @media screen and (max-width: 480px) {
            h1 { font-size: 22px !important; }
            h2 { font-size: 20px !important; }
            h3 { font-size: 18px !important; }
            p, li, a { font-size: 14px !important; }
        }

        /* Điều chỉnh chiều rộng của select box */
        div[data-baseweb="select"] {
            width: 100% !important;
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

#Hiển thị tiêu đề ứng dụng
st.image(r"Tieu_de.png", use_container_width=True)

# Tự động làm mới trang mỗi 500 giây (500.000 ms)
st_autorefresh(interval=500 * 1000, key="data_refresh")

def load_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)  # Kết nối Google Sheets
        df = conn.read(worksheet="DuBao", ttl=0)  # Đọc dữ liệu từ Google Sheets
        return df
    except Exception as e:
        st.error("Trang web đang gặp sự cố. Vui lòng thử lại sau!")
        return None
df = load_data()

# Kiểm tra dữ liệu hợp lệ trước khi xử lý
if df is not None and not df.empty and "Day" in df.columns and "X" in df.columns and "Q2" in df.columns:
    # Chuyển cột "Day" sang kiểu datetime
    df["Day"] = pd.to_datetime(df["Day"], errors="coerce")    
    # Xóa các dòng có giá trị NaN trong cột X hoặc Q2
    df = df.dropna(subset=["X", "Q2"])
    # Sắp xếp theo ngày và giữ lại bản ghi cuối cùng của mỗi ngày
    df = df.sort_values(by="Day").drop_duplicates(subset="Day", keep="last").tail(14)
    # Định dạng lại cột ngày để hiển thị đẹp hơn
    df["Day"] = df["Day"].dt.strftime("%d/%m")

    st.markdown("<div style='font-size: 26px; color: #003399; font-weight: bold;'>📅 Chọn ngày hiển thị:</div>", unsafe_allow_html=True)
    day_options = ["Quá khứ và dự báo", "7 ngày quá khứ", "2 ngày tới", "3 ngày tới", "4 ngày tới", "5 ngày tới", "6 ngày tới", "7 ngày tới"]
    st.markdown("""
    <style>
    div[data-baseweb="select"] {
        width: 300px !important;  /* Điều chỉnh chiều rộng theo mong muốn */}
    </style>""", unsafe_allow_html=True)

    selected_option = st.selectbox("", day_options, index=0, key="day_selector", label_visibility="collapsed")


    # Lọc dữ liệu theo lựa chọn
    if selected_option == "7 ngày quá khứ":
        filtered_df = df.iloc[:7]
    #elif selected_option == "Hôm nay":
        #filtered_df = df.iloc[7:8]    
    elif selected_option == "Quá khứ và dự báo":
        filtered_df = df
    else:
        days_ahead = int(selected_option.split()[0])  # Lấy số ngày từ chuỗi
        filtered_df = df.iloc[7 : 7 + days_ahead]

    st.markdown("<div style='text-align: center; font-size: 40px; font-weight: bold; color: purple;'>📊 SẢN PHẨM DỰ BÁO LƯU LƯỢNG VỀ HỒ THỦY ĐIỆN A LƯỚI</div>", unsafe_allow_html=True)
    fig, ax1 = plt.subplots(figsize=(9, 4), facecolor=None)
    fig.patch.set_alpha(0.6)

    # Chia dữ liệu thành 2 phần: 7 ngày đầu & 7 ngày sau
    past = filtered_df.iloc[:8]  # 7 ngày đầu (cũ hơn)
    present = filtered_df.iloc[7:]  # 7 ngày sau (mới hơn)

    # Tính khoảng dựa trên toàn bộ dữ liệu để giữ cố định trục Y
    q2 = abs(df["Q2"].max() - df["Q2"].min()) * 0.15
    q2_min = df["Q2"].min() - q2
    q2_max = df["Q2"].max() * 1.5
    x2_min = df["X"].min()
    x2_max = df["X"].max() * 3

    # Trục Y bên trái (Lưu lượng Q2)
    ax1.set_xlabel("Ngày")
    ax1.set_ylabel("Lưu lượng (m³/s)", color="#cd6001")
    ax1.plot(past["Day"], past["Q2"], marker="o", linestyle="-", color="brown", label="Lưu lượng quá khứ")
    ax1.plot(present["Day"], present["Q2"], marker="o", linestyle="--", color="#fdac01", label="Lưu lượng dự báo")
    ax1.tick_params(axis="y", labelcolor="#cd6001")
    ax1.set_ylim(q2_min, q2_max)
    ax1.set_facecolor("none")  # Trục chính không có nền
    ax1.grid(True, linestyle="--", color="#cd6001", alpha=0.5)  # Lưới cho trục X và trục Y bên trái (Q2)
    # Hiển thị giá trị lưu lượng dự đoán trên biểu đồ
    for i, txt in enumerate(past["Q2"]):
        ax1.annotate(f"{txt:.1f}", (past["Day"].iloc[i], past["Q2"].iloc[i]),
             textcoords="offset points", xytext=(0, 5), ha='center', fontsize=10, color="brown")
    for i, txt in enumerate(present["Q2"]):
        ax1.annotate(f"{txt:.1f}", (present["Day"].iloc[i], present["Q2"].iloc[i]),
                     textcoords="offset points", xytext=(0, 5), ha='center', fontsize=10, color="#fdac01")

    # Trục Y bên phải (Lượng mưa - X) - Hiển thị dưới dạng đường nhưng đảo ngược trục
    ax2 = ax1.twinx()
    ax2.set_ylabel("Lượng mưa (mm)", color="blue")
    ax2.bar(past["Day"], past["X"], color="#426ec7", alpha=0.8, label="Lượng mưa quá khứ")
    ax2.bar(present["Day"], present["X"], color="#426ec7", alpha=0.6, label="Lượng mưa dự báo")
    ax2.tick_params(axis="y", labelcolor="blue")
    ax2.invert_yaxis()  # Đảo ngược trục Y: 0 nằm trên, giá trị lớn xuống dưới
    ax2.set_ylim(x2_max, x2_min)
    ax2.set_facecolor("none")  # Trục chính không có nền
    ax2.grid(True, linestyle="--", color="blue", alpha=0.3)  # Lưới cho trục Y bên phải (X)

    # Hiển thị giá trị lượng mưa trên cột
    for i, txt in enumerate(filtered_df["X"]):
        ax2.annotate(f"{txt:.1f}", (filtered_df["Day"].iloc[i], filtered_df["X"].iloc[i]),
                     textcoords="offset points", xytext=(0, 5), ha='center', fontsize=10, color="blue")


    # Thêm chú thích cho biểu đồ
    fig.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), fancybox=True, shadow=True, ncol=2)

    fig.tight_layout()
    st.pyplot(fig)

    col3, col4, col5 = st.columns([3, 5, 3])
    with col4:
        st.markdown("<div style='font-size: 32px; font-weight: bold; color: purple;'>TÓM TẮT ĐỀ TÀI</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: justify; font-size: 18px; line-height: 1.6;">
        Dự báo dòng chảy về hồ chứa sao cho chính xác và biết trước nhiều ngày để chủ động vận hành khai thác hiệu quả là công việc không hề đơn giản và luôn thách thức các nghiên cứu. 
        Trong những năm gần đây, việc ứng dụng bài toán học máy vào dự báo lưu lượng từ lượng mưa đã được rất nhiều nghiên cứu trong và ngoài nước thực hiện. 
        Tuy nhiên, tuỳ thuộc vào đặc tính dữ liệu thống kê và đặc tính vật lý của lưu vực mà mỗi mô hình học máy sẽ học và cho kết quả dự đoán với độ tin cậy khác nhau. 
        Nghiên cứu này sẽ thực hiện trên tập dữ liệu gồm lượng mưa và lưu lượng của lưu vực hồ A Lưới từ năm 2017 đến năm 2021 với 03 mô hình học máy được xem xét đó là RF, XGBoost và LSTM. 
        Kết quả huấn luyện và kiểm tra cho thấy mô hình LSTM cho chỉ số đánh giá tốt hơn 2 mô hình còn lại (NSE =0.93; MAE = 17.47; RMSE = 33.11). 
        Từ đó sử dụng mô hình LSTM để dự báo lưu lượng về hồ A Lưới từ dữ liệu mưa dự báo sẳn có trên websites weather cho lưu vực hồ A Lưới. 
        Các kết quả dự báo này được tự động cập nhật ứng dụng web Streamlit.
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("<div style='font-size: 32px; font-weight: bold; color: purple; margin-bottom: -40px;'>THÀNH VIÊN NHÓM</div>", unsafe_allow_html=True)
        selected_option = st.selectbox("",["Sinh viên thực hiện", "Giáo viên hướng dẫn"])
        if selected_option == "Giáo viên hướng dẫn":
            st.markdown(f"""
            <div style="display: flex; flex-direction: column;">
            <p style="font-size: 26px; color: #003399; font-weight: bold; margin-bottom: 2px;">Giáo viên hướng dẫn:</p>
            <div style="font-size: 24px; line-height: 1.5;">
            PGS.TS. Nguyễn Chí Công<br>
            TS. Đoàn Viết Long<br>
            ThS. Phạm Lý Triều
            </div>
            </div>
            """, unsafe_allow_html=True)
        elif selected_option == "Sinh viên thực hiện":   
            st.markdown(f"""
            <div style="display: flex; flex-direction: column;">
            <p style="font-size: 26px; color: #003399; font-weight: bold; margin-bottom: 2px;">Sinh viên thực hiện:</p>
            <div style="font-size: 24px; line-height: 1.5;">
            Lê Tấn Duy - 22DTTM<br>
            Lê Thanh Thiên - 22DTTM
            </div>
            </div>
            """, unsafe_allow_html=True)
    with col5:
        st.markdown("<div style='font-size: 32px; font-weight: bold; color: purple;'>VỊ TRÍ HỒ A LƯỚI</div>", unsafe_allow_html=True)
        st.components.v1.iframe("https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d5183.445656933609!2d107.16354377708113!3d16.196807863014435!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3140374a45533dc3%3A0x8147ee687f758a43!2zxJDhuq1wIFRoxrDhu6NuZyBOZ3Xhu5NuIFRodcyJeSDEkGnDqsyjbiBBIEzGsMahzIFp!5e1!3m2!1svi!2s!4v1743527770714!5m2!1svi!2s",
                 width=500, height=300)
