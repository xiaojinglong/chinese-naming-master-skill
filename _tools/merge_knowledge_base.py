# -*- coding: utf-8 -*-
"""
从 06-取名知识库/01-先秦经典/ 的 14 部经典 md 文件中提取取名素材表格，
合并到 01-数据资料/经典文学素材库/ 的 JSON 文件中。

表格格式：| 出处 | 原句 | 可取名字 | 寓意 |
- 可取名字可能含多个（用、分隔），需拆分为独立条目
- 与已有 JSON 条目按 word 去重
- 为目前缺 JSON 的经典新建文件
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.join(BASE, '..', '06-取名知识库', '01-先秦经典')
LIT = os.path.join(BASE, '..', '01-数据资料', '经典文学素材库')

# 经典文件 → JSON 文件映射 + 默认 usage
CLASSICS = {
    '01-诗经.md':   ('shijing.json',   '女名多用', '诗经'),
    '02-楚辞.md':   ('chuci.json',     '男名多用', '楚辞'),
    '03-论语.md':   ('lunyu.json',     '男女皆宜', '论语'),
    '04-周易.md':   ('zhouyi.json',    '男名多用', '周易'),
    '05-尚书.md':   ('shangshu.json',  '男名多用', '尚书'),
    '06-大学.md':   ('daxue.json',     '男女皆宜', '大学'),
    '07-中庸.md':   ('zhongyong.json', '男女皆宜', '中庸'),
    '08-道德经.md': ('daodejing.json', '男女皆宜', '道德经'),
    '09-庄子.md':   ('zhuangzi.json',  '男女皆宜', '庄子'),
    '10-列子.md':   ('liezi.json',     '男女皆宜', '列子'),
    '11-左传.md':   ('zuozhuan.json',  '男名多用', '左传'),
    '12-离骚.md':   ('lisao.json',     '男名多用', '离骚'),
    '13-管子.md':   ('guanzi.json',    '男名多用', '管子'),
    '29-孟子.md':   ('mengzi.json',    '男名多用', '孟子'),
}


def parse_table_rows(filepath):
    """从 md 文件中提取取名素材表格行，返回 (出处, 原句, 可取名字, 寓意) 列表
    支持两种表格格式：
    - 4列：出处 | 原句 | 可取名字 | 寓意
    - 3列：原句 | 可取名字 | 寓意（出处缺省，用文件名补）
    """
    with open(filepath, encoding='utf-8') as f:
        lines = f.readlines()

    entries = []
    in_table = False
    col_count = 4  # default 4 columns

    for line in lines:
        stripped = line.strip()
        # Detect table start (header row with 可取名字)
        if '|' in stripped and '可取名字' in stripped:
            cols = [c.strip() for c in stripped.split('|')[1:-1]]
            col_count = len(cols)
            in_table = True
            continue
        # Skip separator row (|---|---|)
        if in_table and re.match(r'^\|[\s-]+\|', stripped):
            continue
        # Parse data rows
        if in_table and stripped.startswith('|') and stripped.endswith('|'):
            cols = [c.strip() for c in stripped.split('|')[1:-1]]
            if col_count >= 4 and len(cols) >= 4:
                origin, quote, names_str, meaning = cols[0], cols[1], cols[2], cols[3]
            elif col_count == 3 and len(cols) >= 3:
                origin, quote, names_str = '', cols[0], cols[1]
                meaning = cols[2] if len(cols) > 2 else ''
            else:
                continue
            # Skip empty or non-naming rows
            if not names_str or names_str in ('—', '-', ''):
                continue
            # Skip section headers that got into table
            if len(names_str) > 50 or (origin and len(origin) > 30):
                continue
            entries.append((origin, quote, names_str, meaning))
        # Detect end of table
        elif in_table and not stripped.startswith('|'):
            if stripped and not stripped.startswith('#'):
                in_table = False

    return entries


def split_names(names_str):
    """拆分可取名字段（清扬、婉兮 → [清扬, 婉兮]）"""
    # Split by 、 or ，
    parts = re.split(r'[、，,]', names_str)
    # Clean each part
    result = []
    for p in parts:
        p = p.strip()
        # Remove parenthetical notes like "（作家琼瑶笔名出处）"
        p = re.sub(r'[（(].*?[）)]', '', p).strip()
        # Remove trailing punctuation
        p = p.rstrip('。.，,')
        if p and len(p) <= 8:  # Max 8 chars for a name word
            result.append(p)
    return result


def process_classic(md_filename, json_filename, default_usage, source_name):
    """处理一部经典：解析表格 → 合并到 JSON"""
    md_path = os.path.join(KB, md_filename)
    json_path = os.path.join(LIT, json_filename)

    if not os.path.exists(md_path):
        return 0, 0, 0

    # Parse markdown
    entries = parse_table_rows(md_path)

    # Load existing JSON (or create new)
    if os.path.exists(json_path):
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {
            'source': source_name,
            'desc': f'{source_name}取名素材（含知识库精读笔记提取）',
            'items': [],
            'count': 0
        }

    # Build existing words set
    existing_words = {item['word'] for item in data['items']}
    old_count = len(data['items'])

    # Merge entries
    added = 0
    for origin, quote, names_str, meaning in entries:
        names = split_names(names_str)
        for name in names:
            if name and name not in existing_words:
                # Build full origin with source
                full_origin = f'《{source_name}·{origin}》' if origin else f'《{source_name}》'
                data['items'].append({
                    'word': name,
                    'origin': full_origin,
                    'quote': quote,
                    'meaning': meaning,
                    'usage': default_usage,
                    'pinyin': None  # Markdown tables don't have pinyin
                })
                existing_words.add(name)
                added += 1

    data['count'] = len(data['items'])

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    return old_count, len(data['items']), added


def main():
    print('=' * 60)
    print('知识库取名素材提取与合并')
    print('=' * 60)
    print()

    total_old = 0
    total_new = 0
    total_added = 0

    for md_file, (json_file, usage, source) in CLASSICS.items():
        old, new, added = process_classic(md_file, json_file, usage, source)
        total_old += old
        total_new += new
        total_added += added
        status = '(新建)' if old == 0 else '(扩充)'
        print(f'  {source:6s} {md_file:16s} → {json_file:20s} {old:4d}→{new:4d} (+{added:3d}) {status}')

    print()
    print(f'文学素材总计: {total_old} → {total_new} (+{total_added})')
    print()

    # Also update the schema to include new files
    print('新增 JSON 文件:')
    for md_file, (json_file, usage, source) in CLASSICS.items():
        json_path = os.path.join(LIT, json_file)
        if os.path.exists(json_path):
            with open(json_path, encoding='utf-8') as f:
                d = json.load(f)
            print(f'  {json_file}: {len(d["items"])} 条')


if __name__ == '__main__':
    main()
