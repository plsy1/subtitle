import sys
import re

def time_to_ms(t):
    t = t.replace(',', '.')
    parts = re.split('[:.]', t)
    if len(parts) == 4:
        h, m, s, ms = map(int, parts)
        return ((h * 60 + m) * 60 + s) * 1000 + ms
    return 0

def ms_to_time(ms):
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def clean_srt(input_file, output_file):
    print(f"Cleaning {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(input_file, 'r', encoding='gbk', errors='ignore') as f:
            content = f.read()
            
    content = content.replace('\r\n', '\n')
    blocks = re.split(r'\n\s*\n', content.strip())
    
    subs = []
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 2:
            time_line = ""
            text_lines = []
            for line in lines:
                if '-->' in line:
                    time_line = line
                elif time_line:
                    text_lines.append(line)
            
            if time_line:
                match = re.search(r'(\d+:\d+:\d+[\.,]\d+) --> (\d+:\d+:\d+[\.,]\d+)', time_line)
                if match:
                    start = time_to_ms(match.group(1))
                    end = time_to_ms(match.group(2))
                    text = '\n'.join(text_lines).strip()
                    # Remove the arrow character
                    text = text.replace('➡', '').replace('＜', '').replace('＞', '')
                    # Skip if text only contains music symbols, brackets, or is empty after cleaning
                    if text and not re.fullmatch(r'[♬〜＜＞\s]+', text):
                        subs.append({'start': start, 'end': end, 'text': text})
    
    if not subs:
        print("No subtitles found.")
        return

    merged_subs = []
    if subs:
        current = subs[0]
        for i in range(1, len(subs)):
            nxt = subs[i]
            # If text is the same, and they are either contiguous or have a very small gap (< 500ms)
            if current['text'] == nxt['text'] and (nxt['start'] - current['end'] < 500):
                current['end'] = max(current['end'], nxt['end'])
            else:
                merged_subs.append(current)
                current = nxt
        merged_subs.append(current)
    
    print(f"Merged {len(subs)} down to {len(merged_subs)} blocks.")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, sub in enumerate(merged_subs, 1):
            f.write(f"{i}\n")
            f.write(f"{ms_to_time(sub['start'])} --> {ms_to_time(sub['end'])}\n")
            f.write(f"{sub['text']}\n\n")
    print(f"Done! Saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_srt.py <input.srt>")
    else:
        input_file = sys.argv[1]
        basename = input_file.rsplit('.', 1)[0]
        output_file = f"{basename}_cleaned.srt"
        clean_srt(input_file, output_file)
