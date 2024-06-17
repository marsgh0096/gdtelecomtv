import re

def process_file(input_path, output_path):
    seen_tvg_names = set()
    with open(input_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(output_path, 'w', encoding='utf-8') as file:
        for line in lines:
            if line.startswith('#EXTINF:'):
                tvg_name_match = re.search(r'tvg-name="([^"]+)"', line)
                if tvg_name_match:
                    tvg_name = tvg_name_match.group(1)
                    if tvg_name not in seen_tvg_names:
                        seen_tvg_names.add(tvg_name)
                        file.write(line)
                    else:
                        # Skip next line (the stream URL of the duplicate entry)
                        下一处(file.readline(), None)
                        continue
            elif line.startswith('rtp://'):
                new_line = re.sub(r'rtp://(\d+\.\d+\.\d+\.\d+):(\d+)'，r'http://192.168.2.1:4022/udp/\1:\2', line)
                file.write(new_line)
            else:
                file.write(line)

if __name__ == "__main__":
    process_file('GuangdongIPTV_rtp_all.m3u'， 'GuangdongIPTV_rtp_all_modified.m3u')
