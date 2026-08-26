# -*- coding: utf-8 -*-
"""
修复 hanzi_full.json 的康熙笔画字段：
- 问题：xinhua.csv 的"笔画"实为简体笔画口径（沐=7 而非康熙 8），且个别字有误（珺=4）。
  此前被误当作康熙笔画填充，导致五格计算错误。
- 修复：
  1. 308 常用字：用 hanzi_common.json 中人工核对的康熙笔画覆盖（可靠）。
  2. 其余字：strokes_kangxi 置空（无可靠康熙笔画来源，宁缺毋假）。
  3. xinhua_only 字的 strokes_simplified 补上 xinhua 简体笔画（整体简体口径，个别错误字影响小）。
- 同时修正 meta 说明。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
FULL = os.path.join(BASE, '..', '01-数据资料', '汉字字库', 'hanzi_full.json')
COMMON = os.path.join(BASE, '..', '01-数据资料', '汉字字库', 'hanzi_common.json')
GSC = os.path.join(BASE, '..', '05-开源项目参考', 'james88-qiming', 'data', 'gsc_pinyin.csv')

full = json.load(open(FULL, encoding='utf-8'))
common = json.load(open(COMMON, encoding='utf-8'))

# 0. gsc 简体笔画（标准数据，用于校准）
import csv
gsc_simp = {}
with open(GSC, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        w = row['word'].strip()
        if len(w) == 1 and row.get('stroke_count', '').strip().isdigit():
            gsc_simp[w] = int(row['stroke_count'])

# 1. 常用字康熙笔画映射（人工核对，可靠）
kx_map = {c['char']: c['strokes_kangxi'] for c in common['chars']}

# 2. 修复
fixed = 0
cleared = 0
for c in full['chars']:
    ch = c['char']
    # 常用字：覆盖为可靠康熙笔画
    if ch in kx_map:
        new_kx = kx_map[ch]
        if c.get('strokes_kangxi') != new_kx:
            c['strokes_kangxi'] = new_kx
            fixed += 1
        # 简体笔画：优先 gsc 标准数据，缺失才用 common 补（common 个别手工值有误，如 伟=4）
        if ch in gsc_simp:
            c['strokes_simplified'] = gsc_simp[ch]
        elif c.get('strokes_simplified') is None:
            c['strokes_simplified'] = next((x['strokes_simplified'] for x in common['chars'] if x['char'] == ch), None)
    else:
        # 非常用字：xinhua 提供的笔画是简体口径，不再是康熙笔画
        if c.get('strokes_kangxi') is not None:
            c['strokes_kangxi'] = None
            cleared += 1
        # 简体笔画：gsc 源保持原值（标准）；word_json_only 字已有 word.json 简体笔画；xinhua_only 字为 None（不补，避免错值）

full['meta']['kangxi_strokes_note'] = (
    '康熙笔画口径：308 个常用字为人工核对值（可靠）；其余字因开源三源（gsc_pinyin/xinhua/word.json）'
    '笔画均为简体口径，无法提供可靠康熙笔画，故置空——五格计算前需查 kangxi_radical_strokes.json 部首变体推算或人工核实。'
)
full['meta']['coverage']['strokes_kangxi_reliable'] = len(kx_map)

with open(FULL, 'w', encoding='utf-8') as f:
    json.dump(full, f, ensure_ascii=False, indent=1)

print('覆盖为可靠康熙笔画(常用字):', fixed, '字')
print('清空不可靠康熙笔画(其余字):', cleared, '字')
print('保留可靠康熙笔画总数:', sum(1 for c in full['chars'] if c.get('strokes_kangxi') is not None))

# 3. 用 gsc 校对 hanzi_common.json 的简体笔画，修正手工错误
common_fix = []
for c in common['chars']:
    if c['char'] in gsc_simp and c['strokes_simplified'] != gsc_simp[c['char']]:
        common_fix.append((c['char'], c['strokes_simplified'], gsc_simp[c['char']]))
        c['strokes_simplified'] = gsc_simp[c['char']]
if common_fix:
    with open(COMMON, 'w', encoding='utf-8') as f:
        json.dump(common, f, ensure_ascii=False, indent=1)
    print()
    print('hanzi_common.json 简体笔画修正', len(common_fix), '处:')
    for ch, o, nw in common_fix:
        print(f'  {ch}: {o} → {nw}')
else:
    print()
    print('hanzi_common.json 简体笔画全部与 gsc 一致，无需修正')
