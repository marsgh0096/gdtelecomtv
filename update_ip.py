import requests
from bs4 import BeautifulSoup
import re


def get_first_ip_port():
    url = "https://fofa.info/result?qbase64=IlVEUFhZIiAmJiByZWdpb249Ikh1bmFuIg=="
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 这里需要根据实际网页结构来定位IP和端口
    ip_port = soup.find('span', class_='hsxa-host').text.strip()
    return ip_port


def update_file(filename, new_ip_port):
    with open(filename, 'r') as file:
        content = file.read()

    # 使用正则表达式替换URL中的IP和端口
    updated_content = re.sub(r'(http://)(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(:\d+)?',f'http://{new_ip_port}', content)

    with open(filename, 'w') as file:
        file.write(updated_content)


if __name__ == "__main__":
    ip_port = get_first_ip_port()
    update_file('tv.m3u', ip_port)
    print(f"File updated with new IP:Port - {ip_port}")
