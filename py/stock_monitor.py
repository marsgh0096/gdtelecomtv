import requests
import time
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import os

# --- 用户配置 (从GitHub Secrets中安全读取) ---
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
SOCKS_PROXY_URL = os.environ.get('SOCKS_PROXY_URL') # 新增：读取SOCKS代理URL

# --- 脚本常量 ---
BASE_URL = "https://wawo.wiki/"
PRODUCT_PAGE_URL = "https://wawo.wiki/index.php?rp=/store/tw-ipv6kvm"
PRODUCT_NAME = "TW-ipv6-0.3G-9"
STATE_FILE = "notified_state.txt"

def send_telegram_message(message):
    # 此函数不变，它将直连Telegram，不通过您的代理
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("错误: Telegram Token或Chat ID未在GitHub Secrets中设置。")
        return
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    try:
        response = requests.post(api_url, data=payload, timeout=15)
        if response.status_code == 200:
            print("Telegram提醒消息发送成功！")
        else:
            print(f"发送Telegram消息失败: {response.status_code} {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"发送Telegram消息时发生网络异常: {e}")

def check_stock_status():
    print(f"正在通过 SOCKS 代理检查 {PRODUCT_NAME} 的库存...")
    
    if not SOCKS_PROXY_URL:
        print("错误: SOCKS_PROXY_URL 未在GitHub Secrets中设置。")
        return

    # 读出上次的通知状态
    notified_in_stock = os.path.exists(STATE_FILE) and open(STATE_FILE).read().strip() == 'true'

    try:
        # --- 核心修改：配置SOCKS代理 ---
        proxies = {
            'http': SOCKS_PROXY_URL,
            'https': SOCKS_PROXY_URL
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        }
        
        # 在请求中加入 proxies 参数
        response = requests.get(PRODUCT_PAGE_URL, headers=headers, proxies=proxies, timeout=60)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        product_title_element = soup.find(string=re.compile(re.escape(PRODUCT_NAME), re.I))
        product_container = product_title_element.find_parent(class_='row') if product_title_element else None
        order_link_element = product_container.find('a', class_='btn-order-now') if product_container else None

        if not order_link_element:
            print("未找到产品或订购链接，检查结束。")
            return

        full_order_url = urljoin(BASE_URL, order_link_element['href'])
        
        if "cart.php" in full_order_url:
            if not notified_in_stock:
                print("状态：有货！准备发送通知...")
                message = (f"🎉 <b>有货提醒!</b> 🎉\n\n<b>套餐:</b> {PRODUCT_NAME}\n<b>状态:</b> <b>有货!</b>\n\n请立即前往购买！\n<a href='{full_order_url}'>点击直达</a>")
                send_telegram_message(message)
                with open(STATE_FILE, 'w') as f: f.write('true')
            else:
                print("状态：依然有货。(通知已发送过)")
        else:
            print("状态：缺货。")
            if notified_in_stock:
                print("状态变更：有货 -> 缺货。重置通知开关。")
                with open(STATE_FILE, 'w') as f: f.write('false')

    except Exception as e:
        print(f"执行检查时发生未知错误: {e}")

if __name__ == "__main__":
    print("开始执行GitHub Actions单次监控任务...")
    check_stock_status()
    print("监控任务执行完毕。")
