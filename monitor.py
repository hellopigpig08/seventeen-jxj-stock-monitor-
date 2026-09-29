import os
import smtplib
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.header import Header

# 直接監控 HTML 網址（不加 .js）
PRODUCT_URL = "https://seventeenshopus.com/collections/jxj-1st-mini-album-dreamscapes/products/jxj-1st-mini-album-dreamscape-daydreamers-ver-signed-ver"

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

def check_stock():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(PRODUCT_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        html_text = response.text.lower()
        
        # 檢查網頁文字中是否包含 "sold out" 或 "sorry sold out"
        is_sold_out = "sold out" in html_text
        
        print(f"==========================================")
        print(f"📦 檢查目標: JxJ Signed Album")
        
        if not is_sold_out:
            print("🚨 庫存狀態: 【網頁已無 Sold Out 標籤 -> 有貨！】")
            send_email_notification("JxJ Signed Album")
        else:
            print("💤 庫存狀態: 【缺貨中 (Sold Out)】")
            print("ℹ️ 提示：網頁偵測到 Sold Out 關鍵字，不發送 Email。")
            
        print(f"==========================================")
            
    except Exception as e:
        print(f"❌ 檢查時發生錯誤: {e}")

def send_email_notification(product_title):
    if not all([SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL]):
        print("❌ 錯誤: 未設定完整 Email 環境變數")
        return

    subject = f"🚨 Restock 補貨提醒: {product_title}"
    body = f"SEVENTEEN 簽名版專輯網頁已補貨！\n\n網址：{PRODUCT_URL}"
    
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], msg.as_string())
        server.quit()
        print("✅ 補貨 Email 通知已成功 Send 出！")
    except Exception as e:
        print(f"❌ 發送 Email 失敗: {e}")

if __name__ == "__main__":
    check_stock()
