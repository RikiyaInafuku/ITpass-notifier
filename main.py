import requests
import pdfplumber
import io
import os
import smtplib
from email.mime.text import MIMEText

# メール送信関数
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

# PDFダウンロード
url = "https://www3.jitec.ipa.go.jp/JitesCbt/html/examhall/pdf/沖縄県_試験開催状況一覧.pdf"
pdf_data = requests.get(url).content

# 予約日（ここを自分の日程に変える）
my_date = "2025/09/01"

# PDFチェック
found = False
with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
    for page in pdf.pages:
        table = page.extract_table()
        for row in table:
            if len(row) < 3:
                continue
            date = row[0].strip()
            seat = row[2].strip()
            if seat.isdigit() and int(seat) > 0:
                if date < my_date:
                    found = True
                    msg = f"【ITパスポート】\n{date} に空席 {seat} 席あります！"
                    send_email("ITパスポート空席通知", msg)

if not found:
    print("空席なし")
