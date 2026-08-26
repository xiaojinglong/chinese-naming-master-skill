# -*- coding: utf-8 -*-
"""
构建全量汉字字库 hanzi_full.json
数据源（James88/qiming 仓库 data/ 目录）：
  1. gsc_pinyin.csv      → 主数据：简体笔画、五行、部首、繁体、拼音（8105字）
  2. xinhua.csv          → 康熙笔画（10239字，含 gsc 没有的字）
  3. word.json           → 释义 explanation + 康熙原文 more（16142字）
字段对齐 hanzi_schema.json
"""
import csv
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, '..', '..', '_downloads', 'qiming-main', 'data')
OUT = os.path.join(BASE, '..', '01-数据资料', '汉字字库', 'hanzi_full.json')

# ---------- 1. 读取 gsc_pinyin.csv 主数据 ----------
gsc = {}          # char -> dict
gsc_rows = 0
with open(os.path.join(SRC, 'gsc_pinyin.csv'), encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        gsc_rows += 1
        w = row['word'].strip()
        if not w or len(w) != 1:      # 仅保留单字
            continue
        gsc[w] = {
            'char': w,
            'traditional': row.get('traditional', '').strip() or None,
            'pinyin': row.get('pinyin', '').strip() or None,
            'strokes_simplified': int(row['stroke_count']) if row.get('stroke_count', '').strip().isdigit() else None,
            'wuxing': row.get('wuxing', '').strip() or None,
            'radical': row.get('radical', '').strip() or None,
        }

# ---------- 2. 读取 xinhua.csv 康熙笔画 ----------
xinhua = {}       # char -> (strokes_kangxi, radical, pinyin)
xinhua_rows = 0
with open(os.path.join(SRC, 'xinhua.csv'), encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split(',')
        if len(parts) < 4:
            continue
        w, rad, st, py = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
        if not w or len(w) != 1:
            continue
        xinhua_rows += 1
        if w not in xinhua:      # 保留第一条（xinhua.csv 可能重复）
            xinhua[w] = {
                'strokes_kangxi': int(st) if st.isdigit() else None,
                'radical_xinhua': rad,
                'pinyin_xinhua': None if py == 'error' else py,
            }

# ---------- 3. 读取 word.json 释义 ----------
word_json = {}
with open(os.path.join(SRC, 'word.json'), encoding='utf-8') as f:
    wj = json.load(f)
    for item in wj:
        w = item.get('word', '').strip()
        if not w or len(w) != 1:
            continue
        word_json[w] = item

# ---------- 3.5 读取 wuxing_dict_jianti.json 补五行 ----------
wuxing_map = {}   # char -> wuxing
with open(os.path.join(SRC, 'wuxing_dict_jianti.json'), encoding='utf-8') as f:
    wxj = json.load(f)
    for wx, strokes in wxj.items():
        for lst in strokes.values():
            for w in lst:
                if w not in wuxing_map:   # 仅首次
                    wuxing_map[w] = wx
# 繁体五行表：按繁体字反查（用于给繁体字补五行，价值有限，简单并入）
try:
    with open(os.path.join(SRC, 'wuxing_dict_fanti.json'), encoding='utf-8') as f:
        wxf = json.load(f)
        for wx, strokes in wxf.items():
            for lst in strokes.values():
                for w in lst:
                    if w not in wuxing_map:
                        wuxing_map[w] = wx
except Exception:
    pass

# ---------- 4. 合并 ----------
def clean_meaning(text):
    """释义清理：去换行压缩、截断"""
    if not text:
        return None
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:120] if text else None

def clean_kangxi(text):
    """康熙原文清理：截断"""
    if not text:
        return None
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:200] if text else None

chars = []
seen = set()

# 4a. gsc 主体
for w, d in gsc.items():
    seen.add(w)
    xh = xinhua.get(w, {})
    wj = word_json.get(w, {})
    rec = {
        'char': w,
        'traditional': d['traditional'],
        'pinyin': d['pinyin'],
        'strokes_simplified': d['strokes_simplified'],
        'strokes_kangxi': xh.get('strokes_kangxi'),
        'wuxing': d['wuxing'] or wuxing_map.get(w),
        'radical': d['radical'],
        'meaning': clean_meaning(wj.get('explanation')) if wj else None,
        'kangxi_meaning': clean_kangxi(wj.get('more')) if wj else None,
        'lucky': None,
        'rare_flag': False,
        'difficult_flag': False,
        'homophone_risk': None,
        'gender_hint': 'neutral',
        'variant_notes': None,
        'source': 'gsc_pinyin',
    }
    chars.append(rec)

# 4b. xinhua 独有字（gsc 未覆盖）
extra = 0
for w, xh in xinhua.items():
    if w in seen:
        continue
    wj = word_json.get(w, {})
    rec = {
        'char': w,
        'traditional': wj.get('oldword') if wj and wj.get('oldword') and wj.get('oldword') != w else None,
        'pinyin': xh.get('pinyin_xinhua') or (wj.get('pinyin') if wj else None),
        'strokes_simplified': None,
        'strokes_kangxi': xh.get('strokes_kangxi'),
        'wuxing': wuxing_map.get(w),
        'radical': xh.get('radical_xinhua'),
        'meaning': clean_meaning(wj.get('explanation')) if wj else None,
        'kangxi_meaning': clean_kangxi(wj.get('more')) if wj else None,
        'lucky': None,
        'rare_flag': False,
        'difficult_flag': False,
        'homophone_risk': None,
        'gender_hint': 'neutral',
        'variant_notes': None,
        'source': 'xinhua_only',
    }
    chars.append(rec)
    extra += 1

# 4c. word.json 独有字（两个 csv 都没有）
word_only = 0
for w in word_json:
    if w in seen:
        continue
    wj = word_json[w]
    rec = {
        'char': w,
        'traditional': wj.get('oldword') if wj.get('oldword') and wj.get('oldword') != w else None,
        'pinyin': wj.get('pinyin'),
        'strokes_simplified': int(wj['strokes']) if str(wj.get('strokes', '')).isdigit() else None,
        'strokes_kangxi': None,
        'wuxing': wuxing_map.get(w),
        'radical': wj.get('radicals'),
        'meaning': clean_meaning(wj.get('explanation')),
        'kangxi_meaning': clean_kangxi(wj.get('more')),
        'lucky': None,
        'rare_flag': False,
        'difficult_flag': False,
        'homophone_risk': None,
        'gender_hint': 'neutral',
        'variant_notes': None,
        'source': 'word_json_only',
    }
    chars.append(rec)
    word_only += 1

# 排序：按码位
chars.sort(key=lambda c: ord(c['char']))

# ---------- 5. 后处理标记 ----------
for c in chars:
    ks = c['strokes_kangxi'] or c['strokes_simplified'] or 0
    # 难写字：笔画 >= 20
    if ks >= 20:
        c['difficult_flag'] = True
    # 生僻标记：word_json_only 且无五行无康熙笔画（未进入主流字库），或笔画缺失
    if c['source'] == 'word_json_only':
        c['rare_flag'] = True

out = {
    'meta': {
        'name': '全量汉字字库（合并版）',
        'version': '1.0.0',
        'built_from': 'James88/qiming data/ (gsc_pinyin.csv + xinhua.csv + word.json)',
        'note': '康熙笔画取自 xinhua.csv；释义与康熙原文取自 word.json；五行/简体笔画/部首/繁体取自 gsc_pinyin.csv',
        'sources': {
            'gsc_pinyin.csv': gsc_rows,
            'xinhua.csv': xinhua_rows,
            'word.json': len(word_json),
            'wuxing_dict_jianti.json': len(wuxing_map),
        },
        'coverage': {
            'gsc_primary': len(gsc),
            'xinhua_extra': extra,
            'word_json_extra': word_only,
        },
    },
    'count': len(chars),
    'chars': chars,
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print('gsc_pinyin.csv 行数:', gsc_rows, '| 主字:', len(gsc))
print('xinhua.csv 行数:', xinhua_rows, '| 康熙笔画字:', len(xinhua))
print('word.json 条数:', len(word_json))
print('合并后总字数:', len(chars), '| gsc主体:', len(gsc), '| xinhua补充:', extra, '| word.json补充:', word_only)
print('输出:', OUT)
