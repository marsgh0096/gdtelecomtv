import re

input_files = ["GuangdongIPTV_rtp_4k.m3u", "GuangdongIPTV_rtp_all.m3u"]
output_file = "gdiptv.m3u"

channels = {}

for input_file in input_files:
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            extinf = lines[i].strip()
            url = lines[i+1].strip() if i+1 < len(lines) else ""
            match = re.search(r'tvg-name="([^"]+)"', extinf)
            if match:
                tvg_name = match.group(1)
                is_ultra = ("超清" in extinf or "4K" in extinf or "超清" in url or "4K" in url)
                is_cavs = "CAVS" in extinf or "CAVS" in url or "CAVS" in tvg_name
                url = url.replace("rtp://", "http://192.168.2.1:4022/udp/")
                extinf = re.sub(r'group-title="IPTV-([^"]*)"', r'group-title="\1"', extinf)
                if tvg_name not in channels:
                    channels[tvg_name] = []
                channels[tvg_name].append({
                    "extinf": extinf,
                    "url": url,
                    "is_ultra": is_ultra,
                    "is_cavs": is_cavs
                })
            i += 2
        else:
            i += 1

result = []
for tvg_name, items in channels.items():
    non_cavs = [item for item in items if not item["is_cavs"]]
    if non_cavs:
        preferred = [item for item in non_cavs if item["is_ultra"]]
        chosen = preferred[0] if preferred else non_cavs[0]
    else:
        preferred = [item for item in items if item["is_ultra"]]
        chosen = preferred[0] if preferred else items[0]
    result.append((chosen["extinf"], chosen["url"]))

with open(output_file, "w", encoding="utf-8") as f:
    for extinf, url in result:
        f.write(extinf + "\n")
        f.write(url + "\n") 
