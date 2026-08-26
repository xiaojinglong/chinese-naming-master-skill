# -*- coding: utf-8 -*-
"""
解析 James88/qiming data/sancai.txt → sancai_full.json
三才完整吉凶表：125 组（天/人/地三格五行 × 五格数字组合 × 完整解释 × 吉凶等级）
来源为民间姓名学《三才配置吉凶表》通行文本（含连珠局等备注）。
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, '..', '..', '_downloads', 'qiming-main', 'data', 'sancai.txt')
OUT = os.path.join(BASE, '..', '01-数据资料', '三才五格配置表', 'sancai_full.json')

with open(SRC, encoding='utf-8') as f:
    lines = [ln.rstrip('\n') for ln in f]

TITLE_RE = re.compile(r'^([金木水火土]{3})[　\s]*([0-9][0-9 ,　]*)$')

# 按标题行切分
groups = []
cur = None
for ln in lines:
    if ln.strip() == '':
        continue
    m = TITLE_RE.match(ln.strip())
    if m:
        if cur:
            groups.append(cur)
        cur = {'title': m.group(1), 'num_raw': m.group(2).strip(), 'body': []}
    else:
        if cur is None:
            cur = {'title': None, 'num_raw': None, 'body': []}
        cur['body'].append(ln.strip())

if cur:
    groups.append(cur)

print('切分组数:', len(groups))


def parse_nums(raw):
    """解析 111,222 / 153264 / 193 204 / 131, 242 → [天格数, 地格数]（五格配置）"""
    raw = raw.replace('　', ' ').replace(',', ' ').replace('，', ' ')
    parts = [p for p in raw.split() if p]
    nums = []
    for p in parts:
        if len(p) == 6 and p.isdigit():
            nums.append(int(p[:3]))
            nums.append(int(p[3:]))
        elif p.isdigit():
            nums.append(int(p))
    # 去重保序（部分行 111,222 这种就是两个数）
    seen = []
    for n in nums:
        if n not in seen:
            seen.append(n)
    return seen


GRADE_PAT = re.compile(r'【([^】]+)】')
results = []
missing_grade = 0
combo_set = set()

for g in groups:
    if not g['title']:
        continue
    title = g['title']
    combo_set.add(title)
    body = g['body']
    grade = None
    gm = GRADE_PAT.search(' '.join(body))
    if gm:
        grade = gm.group(1)
        # 移除等级行，保留纯解释
        body = [b for b in body if '【' not in b]
    else:
        missing_grade += 1
    explanation = '\n'.join(body).strip()
    nums = parse_nums(g['num_raw'])
    results.append({
        'tian': title[0],
        'ren': title[1],
        'di': title[2],
        'combination': title,
        'wuge_nums': nums,          # 对应天格数/地格数（三才对应的五格数字组合）
        'grade': grade,
        'explanation': explanation,
    })

# 补缺失组合：源文件 sancai.txt 本身缺 金金火，用推导版 sancai_125.json 补全
SANCAL_OLD = os.path.join(BASE, '..', '01-数据资料', '三才五格配置表', 'sancai_125.json')
missing_combos = set()
for r in results:
    missing_combos.add(r['combination'])
all_combos = {''.join(p) for p in __import__('itertools').product('金木水火土', repeat=3)}
gap = sorted(all_combos - missing_combos)
if gap and os.path.exists(SANCAL_OLD):
    old = json.load(open(SANCAL_OLD, encoding='utf-8'))
    old_map = {(r['tian'], r['ren'], r['di']): r for r in old['sancai']}
    for combo in gap:
        k = (combo[0], combo[1], combo[2])
        o = old_map.get(k)
        results.append({
            'tian': combo[0],
            'ren': combo[1],
            'di': combo[2],
            'combination': combo,
            'wuge_nums': [],
            'grade': o['grade'] if o else None,
            'explanation': '（源三才表 James88/data/sancai.txt 缺此组合，本条由五行生克推导版 sancai_125.json 补充）',
        })
    print('补充缺失组合:', gap)

results.sort(key=lambda r: ['金木水火土'.index(r['tian']), '金木水火土'.index(r['ren']), '金木水火土'.index(r['di'])])
print('最终组数:', len(results))

# 吉凶等级分布（补全后）
grades = {}
for r in results:
    grades[r['grade']] = grades.get(r['grade'], 0) + 1

# 与现有 sancai_125.json（五行生克推导版）交叉校验
cross = []
if os.path.exists(SANCAL_OLD):
    old = json.load(open(SANCAL_OLD, encoding='utf-8'))
    old_map = {(r['tian'], r['ren'], r['di']): r for r in old['sancai']}
    for r in results:
        k = (r['tian'], r['ren'], r['di'])
        o = old_map.get(k)
        cross.append({'combination': r['combination'], 'old_grade': o['grade'] if o else None, 'new_grade': r['grade']})

out = {
    'meta': {
        'name': '三才配置吉凶完整表（附解释）',
        'version': '1.0.0',
        'source': 'James88/qiming data/sancai.txt（民间姓名学通行文本）',
        'note': 'grade 为原文【】标注的吉凶等级；explanation 为完整断语；wuge_nums 为该三才组合对应的天格/地格数字（如 木木木→111,222 表示天格1/地格1 与 天格2/地格2 皆为此三才）。与 sancai_125.json（五行生克推导版）并存：本表为权威解释版。',
        'grade_distribution': grades,
    },
    'count': len(results),
    'sancai': results,
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print('解析组数:', len(results), '| 组合数(应125):', len(combo_set))
print('缺等级组:', missing_grade)
print('等级分布:', grades)
# 交叉校验抽样
print('交叉校验(新旧对照前8):')
for c in cross[:8]:
    print(' ', c['combination'], '| 推导版:', c['old_grade'], '| 原文版:', c['new_grade'])
