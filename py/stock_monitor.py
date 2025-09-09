import requests
import time
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import os

# --- User Configuration (from GitHub Secrets) ---
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# --- Script Constants ---
BASE_URL = "https://wawo.wiki/"
PRODUCT_PAGE_URL = "https://wawo.wiki/index.php?rp=/store/tw-ipv6kvm"
PRODUCT_NAME = "TW-ipv6-0.3G-9"
STATE_FILE = "notified_state.txt"

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: Telegram Token or Chat ID not set in GitHub Secrets.")
        return
        
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(api_url, data=payload, timeout=15)
        if response.status_code == 200:
            print("Telegram notification sent successfully!")
        else:
            print(f"Failed to send Telegram notification: {response.status_code} {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Network exception while sending Telegram notification: {e}")

def check_stock_status():
    print(f"Checking stock for {PRODUCT_NAME}...")
    
    notified_in_stock = False
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            if f.read().strip() == 'true':
                notified_in_stock = True

    try:
        # **Key Change: Add more realistic browser headers**
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': BASE_URL,
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1'
        }
        
        response = requests.get(PRODUCT_PAGE_URL, headers=headers, timeout=15)
        response.raise_for_status() # This will raise an exception for non-200 status codes like 403
        soup = BeautifulSoup(response.text, 'html.parser')

        product_title_element = soup.find(string=re.compile(re.escape(PRODUCT_NAME), re.I))
        product_container = product_title_element.find_parent(class_='row') if product_title_element else None
        order_link_element = product_container.find('a', class_='btn-order-now') if product_container else None

        if not order_link_element:
            print("Could not find the product or its order link. Check complete.")
            return

        full_order_url = urljoin(BASE_URL, order_link_element['href'])
        
        if "cart.php" in full_order_url:
            if not notified_in_stock:
                print("Status: In Stock! Preparing to send notification...")
                message = (f"🎉 <b>Stock Alert!</b> 🎉\n\n"
                           f"<b>Package:</b> {PRODUCT_NAME}\n"
                           f"<b>Status:</b> <b>In Stock!</b>\n\n"
                           f"Purchase now!\n<a href='{full_order_url}'>Click here to order</a>")
                send_telegram_message(message)
                with open(STATE_FILE, 'w') as f:
                    f.write('true')
            else:
                print("Status: Still in stock. (Notification already sent).")
        else:
            print("Status: Out of Stock.")
            if notified_in_stock:
                print("Stock status changed from 'In Stock' to 'Out of Stock'. Resetting notification flag.")
                with open(STATE_FILE, 'w') as f:
                    f.write('false')

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error during check: {e}") # Specifically catch and print HTTP errors like 403
    except Exception as e:
        print(f"An unknown error occurred during check: {e}")

if __name__ == "__main__":
    print("Starting single GitHub Actions monitoring task...")
    check_stock_status()
    print("Monitoring task finished.")
