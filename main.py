import requests
import pdfplumber
import io
import os
import smtplib
from email.mime.text import MIMEText
import datetime

# ========== 設定 ==========
TARGET_HALLS = [
    "那覇港町試験会場",
    "OAC沖縄試験会場"
]

my_date = "2025/10/12"

# ========== メール送信関数 ==========
def send_email(subject, body):
    from_email = os.environ['EMAIL_USER']
    to_email = os.environ['EMAIL_TO']
    app_password = os.environ['EMAIL_PASS']

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(from_email, app_password)
    server.send_message(msg)
    server.quit()

# ========== 日付変換関数 ==========
def convert_date(japanese_date):
    date_part = japanese_date.split('(')[0]
    date_obj = datetime.datetime.strptime(date_part.strip(), "%Y年 %m月 %d日")
    return date_obj.strftime("%Y/%m/%d")

# ========== PDFチェック ==========
url = "https://www3.jitec.ipa.go.jp/JitesCbt/html/examhall/pdf/沖縄県_試験開催状況一覧.pdf"
pdf_data = requests.get(url).content

found = False
with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
    current_hall = None  # 直近の会場名を保存

    for page in pdf.pages:
        table = page.extract_table()
        for row in table:
            if len(row) < 6:
                continue

            cell_value = row[0]
            if cell_value is not None and cell_value.strip() != "":
                current_hall = cell_value.strip()

            if current_hall not in TARGET_HALLS:
                continue

            date = convert_date(row[3].strip())  # 日付（3列目）
            seat = row[6].strip()                # 空席数（6列目）

            if seat.isdigit() and int(seat) > 0:
                if date < my_date:
                    found = True
                    msg = f"【ITパスポート 空席通知】\n{current_hall}\n{date} に空席 {seat} 席あります！"
                    send_email("ITパスポート空席通知", msg)

if not found:
    print("空席なし")
