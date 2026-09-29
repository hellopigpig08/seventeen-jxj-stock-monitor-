import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.header import Header

# 目標商品網址與 API JSON 網址
PRODUCT_URL = "https://seventeenshopus.com/collections/jxj-1st-mini-album-dreamscapes/products/jxj-1st-mini-album-dreamscape-daydreamers-ver-signed-ver"
JSON_URL = PRODUCT_URL + ".js"

# 從 GitHub Secrets / 環境變數讀取
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

def check_stock():
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
    }
    
    try:
        response = requests.get(JSON_URL, headers=headers, timeout=10)
        response.raise_for_status()
            
        data = response.json()
        title = data.get("title", "JxJ Signed Album")
        variants = data.get("variants", [])
        
        # 找出所有有貨的特定款式 (Variants)
        available_variants = [v.get("title") for v in variants if v.get("available", False)]
        
        print(f"商品名稱: {title}")
        
        if available_variants:
            available_str = ", ".join(available_variants)
            print(f"現時庫存狀態: 有貨 (Available) - 款式: {available_str}")
            send_email_notification(title, available_str)
        else:
            print("現時庫存狀態: 缺貨 (Sold Out)")
            
    except Exception as e:
        print(f"檢查時發生錯誤: {e}")

def send_email_notification(product_title, available_info):
    if not all([SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL]):
        print("❌ 錯誤: 未設定完整 Email 環境變數 (SENDER_EMAIL / SENDER_PASSWORD / RECEIVER_EMAIL)")
        return

    subject = f"🚨 Restock 補貨提醒: {product_title}"
    body = f"你關注嘅商品已經補貨啦！\n\n商品名稱：{product_title}\n有貨款式：{available_info}\n發售/購買連結：{PRODUCT_URL}"
    
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
