# -*- coding: utf-8 -*-
"""
基于 120W 姓名性别语料统计汉字性别倾向：
1. 生成 性别倾向统计.json（全量 2210 字）
2. 校准 hanzi_common.json（308 字）与 hanzi_full.json 的 gender_hint
规则：男占比 >=0.8 → male；<=0.2 → female；其余 neutral（频次 <30 视为样本不足，不覆盖）
"""
import json
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, '..', '..', '_downloads', 'qiming-main', 'data', 'Chinese_Names_Corpus_Gender（120W）.txt')
OUT_STAT = os.path.join(BASE, '..', '01-数据资料', '性别语料库', '性别倾向统计.json')
COMMON = os.path.join(BASE, '..', '01-数据资料', '汉字字库', 'hanzi_common.json')
FULL = os.path.join(BASE, '..', '01-数据资料', '汉字字库', 'hanzi_full.json')

# ---------- 1. 统计 ----------
male = defaultdict(int)
female = defaultdict(int)
total = 0
unknown = 0
with open(SRC, encoding='utf-8-sig') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.rsplit(',', 1)
        if len(parts) != 2:
            continue
        name, g = parts[0].strip(), parts[1].strip()
        if g == '未知':
            unknown += 1
            continue
        total += 1
        for ch in name:
            if g == '男':
                male[ch] += 1
            else:
                female[ch] += 1

stats = []
all_chars = set(male) | set(female)
for ch in all_chars:
    m, fv = male[ch], female[ch]
    n = m + fv
    ratio = round(m / n, 4) if n else None
    if n >= 30:
        if ratio >= 0.8:
            hint = 'male'
        elif ratio <= 0.2:
            hint = 'female'
        else:
            hint = 'neutral'
    else:
        hint = 'neutral'
    stats.append({
        'char': ch,
        'male_count': m,
        'female_count': fv,
        'total': n,
        'male_ratio': ratio,
        'gender_hint': hint,
        'confident': n >= 30,
    })
stats.sort(key=lambda x: -x['total'])

stat_map = {s['char']: s for s in stats}

out_stat = {
    'meta': {
        'name': '汉字性别倾向统计（基于姓名语料）',
        'version': '1.0.0',
        'source': 'James88/qiming data/Chinese_Names_Corpus_Gender（120W）.txt',
        'corpus_size': total,
        'corpus_unknown': unknown,
        'chars_covered': len(stats),
        'rule': 'male_ratio>=0.8→male；<=0.2→female；否则 neutral；频次<30 视为样本不足 confident=false',
        'note': '性别统计基于整字在姓名中的出现频次，作为取名性别倾向参考（非绝对标准）。',
    },
    'count': len(stats),
    'chars': stats,
}
os.makedirs(os.path.dirname(OUT_STAT), exist_ok=True)
with open(OUT_STAT, 'w', encoding='utf-8') as f:
    json.dump(out_stat, f, ensure_ascii=False, indent=1)
print('性别统计文件:', OUT_STAT, '| 字数:', len(stats))

# ---------- 2. 校准 hanzi_common.json ----------
common = json.load(open(COMMON, encoding='utf-8'))
changed = []
kept = []
for c in common['chars']:
    s = stat_map.get(c['char'])
    if s and s['confident']:
        old = c.get('gender_hint')
        if old != s['gender_hint']:
            changed.append((c['char'], old, s['gender_hint'], s['male_ratio']))
        c['gender_hint'] = s['gender_hint']
        c['gender_hint_source'] = 'corpus'
    else:
        c.setdefault('gender_hint_source', 'manual')
        kept.append(c['char'])
common['meta']['gender_hint_note'] = 'gender_hint 已用 120W 姓名语料校准（confident 时覆盖为语料标注），未覆盖字保留手工标注。详见 01-数据资料/性别语料库/性别倾向统计.json'
with open(COMMON, 'w', encoding='utf-8') as f:
    json.dump(common, f, ensure_ascii=False, indent=1)
print('常用字库校准: 覆盖变更', len(changed), '条 | 保留手工', len(kept), '字')
print('变更明细(前30):')
for ch, o, nw, r in changed[:30]:
    print(f'  {ch}: {o} → {nw} (男占比{r:.2f})')

# ---------- 3. 校准 hanzi_full.json ----------
full = json.load(open(FULL, encoding='utf-8'))
updated = 0
for c in full['chars']:
    s = stat_map.get(c['char'])
    if s and s['confident']:
        c['gender_hint'] = s['gender_hint']
        updated += 1
with open(FULL, 'w', encoding='utf-8') as f:
    json.dump(full, f, ensure_ascii=False, indent=1)
print('全量字库校准: 更新', updated, '字（共', len(full['chars']), '字）')
