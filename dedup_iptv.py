import re

input_file = "GuangdongIPTV_rtp_all.m3u"
output_file = "GuangdongIPTV_rtp_all_dedup.m3u"

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

channel_dict = {}

i = 0
while i < len(lines):
    if lines[i].startswith("#EXTINF"):
        extinf = lines[i].strip()
        url = lines[i+1].strip() if i+1 < len(lines) else ""
        match = re.search(r'tvg-name="([^"]+)"', extinf)
        if match:
            tvg_name = match.group(1)
            is_ultra = ("超清" in extinf or "4K" in extinf or "超清" in url or "4K" in url)
            if tvg_name not in channel_dict:
                channel_dict[tvg_name] = (extinf, url, is_ultra)
            else:
                if is_ultra and not channel_dict[tvg_name][2]:
                    channel_dict[tvg_name] = (extinf, url, is_ultra)
        i += 2
    else:
        i += 1

with open(output_file, "w", encoding="utf-8") as f:
    for extinf, url, _ in channel_dict.values():
        f.write(extinf + "\n")
        f.write(url + "\n") 