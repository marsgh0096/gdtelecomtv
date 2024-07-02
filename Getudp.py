# @Time : 2024/7/2 17:35 02 17
# @Author : Mars.G
# @FileName: 获取第一个 IP.py
# @Software: PyCharm

import requests
import re

# 目标网址
url = 'https://fofa.info/result?qbase64=IlVEUFhZIiAmJiByZWdpb249Ikh1bmFuIg%3D%3D'

# 发起 GET 请求
response = requests.get(url)

# 获取网页 html 内容
html_content = response.text

# 通过正则在 HTML 中寻找 IP 地址，匹配IP地址可能带有的端口
ip_address = re.findall( r'[0-9]+(?:\.[0-9]+){3}(?:\:[0-9]{1,5})?', html_content)

ip = ip_address[0]
