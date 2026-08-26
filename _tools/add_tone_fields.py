# -*- coding: utf-8 -*-
"""
多音字声调处理：将变音符拼音转为数字声调。

hanzi_common.json 和 hanzi_full.json 的 pinyin 字段使用变音符格式（míng），
Skill 无法程序化提取声调。本脚本为每个字添加 tone 字段：
  - tone: 整数 1-4（阴平/阳平/上声/去声），轻声为 0
  - pinyin_tone: 数字声调格式拼音（如 "ming2"）
  - is_multi_pinyin: 是否多音字（暂时无法自动检测，需人工补充）

变音符 → 声调数字映射：
  ā=1, á=2, ǎ=3, à=4 (a)
  ē=1, é=2, ě=3, è=4 (e)
  ī=1, í=2, ǐ=3, ì=4 (i)
  ō=1, ó=2, ǒ=3, ò=4 (o)
  ū=1, ú=2, ǔ=3, ù=4 (u)
  ǖ=1, ǘ=2, ǚ=3, ǜ=4 (ü)
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))

TONE_MAP = {
    'ā': ('a', 1), 'á': ('a', 2), 'ǎ': ('a', 3), 'à': ('a', 4),
    'ē': ('e', 1), 'é': ('e', 2), 'ě': ('e', 3), 'è': ('e', 4),
    'ī': ('i', 1), 'í': ('i', 2), 'ǐ': ('i', 3), 'ì': ('i', 4),
    'ō': ('o', 1), 'ó': ('o', 2), 'ǒ': ('o', 3), 'ò': ('o', 4),
    'ū': ('u', 1), 'ú': ('u', 2), 'ǔ': ('u', 3), 'ù': ('u', 4),
    'ǖ': ('ü', 1), 'ǘ': ('ü', 2), 'ǚ': ('ü', 3), 'ǜ': ('ü', 4),
}


def pinyin_to_tone(pinyin):
    """将变音符拼音转为 (无调号拼音, 声调数字)。轻声返回 0。"""
    if not pinyin:
        return pinyin, None
    result = []
    tone = None
    for ch in pinyin:
        if ch in TONE_MAP:
            base, t = TONE_MAP[ch]
            result.append(base)
            tone = t
        elif ch in '0123456789':
            # Already numeric tone
            tone = int(ch)
        elif ch == ' ':
            continue  # Skip spaces
        else:
            result.append(ch)
    clean = ''.join(result).lower().strip()
    if tone is None:
        tone = 0  # 轻声
    return clean, tone


def add_tone_fields(data):
    """为字库数据添加 tone 和 pinyin_tone 字段"""
    chars = data['chars']
    converted = 0
    already_had = 0
    for c in chars:
        pinyin = c.get('pinyin', '')
        if not pinyin:
            c['tone'] = None
            c['pinyin_tone'] = None
            continue
        # Check if already has numeric tone
        if re.search(r'[1-4]', pinyin):
            c['tone'] = int(re.search(r'[1-4]', pinyin).group())
            c['pinyin_tone'] = pinyin
            already_had += 1
            continue
        clean, tone = pinyin_to_tone(pinyin)
        c['tone'] = tone
        c['pinyin_tone'] = f'{clean}{tone}' if tone else clean
        converted += 1
    return converted, already_had


def process_file(filepath):
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    converted, already = add_tone_fields(data)
    # Update meta
    if 'meta' in data:
        data['meta']['tone_note'] = (
            f'tone 字段：0=轻声, 1=阴平, 2=阳平, 3=上声, 4=去声。'
            f'pinyin_tone 字段：数字声调格式（如 ming2）。'
            f'本次转换 {converted} 字（变音符→数字），{already} 字原已有数字声调。'
        )
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return converted, already


def main():
    files = [
        os.path.join(BASE, '..', '01-数据资料', '汉字字库', 'hanzi_common.json'),
        os.path.join(BASE, '..', '01-数据资料', '汉字字库', 'hanzi_full.json'),
    ]
    print('=== 多音字声调处理 ===')
    for fp in files:
        converted, already = process_file(fp)
        name = os.path.basename(fp)
        print(f'{name}: 转换 {converted} 字, 已有数字声调 {already} 字')
    print()
    # Verify
    common_path = files[0]
    with open(common_path, encoding='utf-8') as f:
        data = json.load(f)
    chars = data['chars']
    sample = [(c['char'], c['pinyin'], c.get('tone'), c.get('pinyin_tone')) for c in chars[:5]]
    print('示例验证:')
    for ch, py, tone, pyt in sample:
        print(f'  {ch}: {py} → tone={tone}, pinyin_tone={pyt}')
    # Count tone distribution
    tones = [c.get('tone') for c in chars if c.get('tone') is not None]
    from collections import Counter
    print(f'\n声调分布: {dict(Counter(tones).most_common())}')


if __name__ == '__main__':
    main()
