import requests
import time
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import os # 导入os库

# --- 用户配置 (从GitHub Secrets中安全读取) ---
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# --- 脚本常量 ---
BASE_URL = "https://wawo.wiki/"
PRODUCT_PAGE_URL = "https://wawo.wiki/index.php?rp=/store/tw-ipv6kvm"
PRODUCT_NAME = "TW-ipv6-0.3G-9"

# 状态文件的名称，用于在不同运行间保持状态
STATE_FILE = "notified_state.txt"

def send_telegram_message(message):
    """
    通过Telegram机器人发送一条消息。
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("错误: Telegram Token或Chat ID未在GitHub Secrets中设置。")
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
            print("Telegram提醒消息发送成功！")
        else:
            print(f"发送Telegram消息失败: {response.status_code} {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"发送Telegram消息时发生网络异常: {e}")

def check_stock_status():
    """
    GitHub Actions版的检查逻辑，通过文件来记录状态。
    """
    print(f"正在检查 {PRODUCT_NAME} 的库存...")
    
    # 读出上次的通知状态
    notified_in_stock = False
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            if f.read().strip() == 'true':
                notified_in_stock = True

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        }
        
        response = requests.get(PRODUCT_PAGE_URL, headers=headers, timeout=15)
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
                message = (f"🎉 <b>有货提醒!</b> 🎉\n\n"
                           f"<b>套餐:</b> {PRODUCT_NAME}\n"
                           f"<b>状态:</b> <b>有货!</b>\n\n"
                           f"请立即前往购买！\n<a href='{full_order_url}'>点击直达</a>")
                send_telegram_message(message)
                # 将新状态写入文件
                with open(STATE_FILE, 'w') as f:
                    f.write('true')
            else:
                print("状态：依然有货。(通知已发送过，本次不再重复提醒)")
        else:
            print("状态：缺货。")
            if notified_in_stock:
                print("库存状态由“有货”变为“缺货”，已重置通知开关。")
                # 将新状态写入文件
                with open(STATE_FILE, 'w') as f:
                    f.write('false')

    except Exception as e:
        print(f"执行检查时发生未知错误: {e}")

if __name__ == "__main__":
    print("开始执行GitHub Actions单次监控任务...")
    # 启动时不发送通知，只在有货时才发送
    check_stock_status()
    print("监控任务执行完毕。")
