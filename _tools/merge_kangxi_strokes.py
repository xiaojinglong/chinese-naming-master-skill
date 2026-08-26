# -*- coding: utf-8 -*-
"""
全量接入康熙笔画数据（breezyreeds/kangxi-strokecount，63,696 字）。

核心逻辑：
  strokes.json 的键是"字符本身"，简体字存简体笔画、繁体字存康熙笔画。
  姓名学需要康熙（繁体）笔画，因此必须查"繁体形式"才能拿到正确值。

接入策略（按可靠性排序）：
  1. 有 traditional 字段 → 查 traditional 形式（可靠）
  2. 无 traditional 但能从 gsc_pinyin 简繁映射推得 → 查映射的繁体形式（可靠）
  3. 上述都不行 → 直接查 char 本身（该字即自身繁体形式，或简繁同形；标记 kangxi_source）
  4. 308 常用字交叉验证：对比人工核对值与新数据，报告差异

输出：
  - 更新 hanzi_full.json 的 strokes_kangxi 字段
  - 新增 kangxi_source 字段（'traditional_lookup' / 'simp_trad_map' / 'direct' / 'manual_verified' / None）
  - 打印覆盖率、验证结果
"""
import json
import os
import csv

BASE = os.path.dirname(os.path.abspath(__file__))
FULL = os.path.join(BASE, '..', '01-数据资料', '汉字字库', 'hanzi_full.json')
COMMON = os.path.join(BASE, '..', '01-数据资料', '汉字字库', 'hanzi_common.json')
GSC = os.path.join(BASE, '..', '05-开源项目参考', 'james88-qiming', 'data', 'gsc_pinyin.csv')
STROKES_JSON = os.path.join(BASE, '..', '..', '_downloads', 'kangxi', 'strokes.json')


def load_strokes():
    """加载康熙笔画字典（63,696 字）"""
    with open(STROKES_JSON, encoding='utf-8') as f:
        return json.load(f)


def build_simp_trad_map():
    """从 gsc_pinyin.csv 构建简→繁映射（仅 traditional != word 的对）"""
    mapping = {}
    with open(GSC, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            w = row.get('word', '').strip()
            t = row.get('traditional', '').strip()
            if len(w) == 1 and len(t) == 1 and w != t:
                mapping[w] = t
    return mapping


def resolve_traditional(char, trad_field, simp_trad_map):
    """
    确定一个字的繁体形式，返回 (traditional_form, source)
    source: 'field' / 'map' / 'self'
    """
    # 1. 有 traditional 字段且非空
    if trad_field and len(trad_field) >= 1:
        # 取第一个字符（极少数 traditional 可能为多字，取首字）
        return trad_field[0], 'field'
    # 2. 从简繁映射推得
    if char in simp_trad_map:
        return simp_trad_map[char], 'map'
    # 3. 该字即自身繁体形式（简繁同形，或本就是繁体/异体字）
    return char, 'self'


def main():
    strokes = load_strokes()
    simp_trad_map = build_simp_trad_map()

    with open(FULL, encoding='utf-8') as f:
        full = json.load(f)
    with open(COMMON, encoding='utf-8') as f:
        common = json.load(f)

    # 308 常用字的康熙笔画（人工核对，作为验证基准）
    manual_kx = {c['char']: c['strokes_kangxi'] for c in common['chars']}

    chars = full['chars']
    stats = {
        'total': len(chars),
        'field_lookup': 0,
        'map_lookup': 0,
        'direct_lookup': 0,
        'manual_verified': 0,
        'not_found': 0,
        'filled_new': 0,       # 新填入的（原来为空）
        'updated': 0,          # 原来有值但更新了
        'unchanged': 0,        # 原来有值且一致
    }
    # 验证：308 常用字 vs 新数据
    verify_match = 0
    verify_mismatch = []
    verify_no_data = []

    for c in chars:
        ch = c['char']
        trad_field = c.get('traditional') or ''

        # 常用字优先用人工核对值（最可靠），但仍记录新数据的比对结果
        if ch in manual_kx:
            c['strokes_kangxi'] = manual_kx[ch]
            c['kangxi_source'] = 'manual_verified'
            stats['manual_verified'] += 1
            # 交叉验证：查繁体形式在新数据中的值
            trad_form, src = resolve_traditional(ch, trad_field, simp_trad_map)
            new_val = strokes.get(trad_form)
            if new_val is not None:
                if new_val == manual_kx[ch]:
                    verify_match += 1
                else:
                    verify_mismatch.append((ch, trad_form, manual_kx[ch], new_val))
            else:
                verify_no_data.append((ch, trad_form, manual_kx[ch]))
            continue

        # 非常用字：用新康熙笔画数据填充
        trad_form, src = resolve_traditional(ch, trad_field, simp_trad_map)
        new_val = strokes.get(trad_form)

        old_val = c.get('strokes_kangxi')

        if new_val is not None:
            c['strokes_kangxi'] = new_val
            if src == 'field':
                c['kangxi_source'] = 'traditional_lookup'
                stats['field_lookup'] += 1
            elif src == 'map':
                c['kangxi_source'] = 'simp_trad_map'
                stats['map_lookup'] += 1
            else:
                c['kangxi_source'] = 'direct'
                stats['direct_lookup'] += 1
            # 统计填充情况
            if old_val is None:
                stats['filled_new'] += 1
            elif old_val != new_val:
                stats['updated'] += 1
            else:
                stats['unchanged'] += 1
        else:
            # 新数据中也没有
            c['strokes_kangxi'] = None
            c['kangxi_source'] = None
            stats['not_found'] += 1

    # 更新 meta
    coverage_kx = sum(1 for c in chars if c.get('strokes_kangxi') is not None)
    full['meta']['coverage']['strokes_kangxi_reliable'] = coverage_kx
    full['meta']['coverage']['strokes_kangxi_manual_verified'] = stats['manual_verified']
    full['meta']['coverage']['strokes_kangxi_traditional_lookup'] = stats['field_lookup']
    full['meta']['coverage']['strokes_kangxi_simp_trad_map'] = stats['map_lookup']
    full['meta']['coverage']['strokes_kangxi_direct'] = stats['direct_lookup']
    full['meta']['kangxi_strokes_note'] = (
        f'康熙笔画全量接入：{coverage_kx}/{len(chars)} 字有康熙笔画。'
        f'来源：① 308 常用字人工核对（manual_verified）；'
        f'② {stats["field_lookup"]} 字通过 traditional 字段查繁体形式（traditional_lookup，可靠）；'
        f'③ {stats["map_lookup"]} 字通过 gsc 简繁映射推得繁体形式（simp_trad_map，可靠）；'
        f'④ {stats["direct_lookup"]} 字直接查字本身（direct，该字即自身繁体形式或简繁同形）；'
        f'⑤ {stats["not_found"]} 字无数据（置空）。'
        f'数据源：breezyreeds/kangxi-strokecount（MIT, 63,696 字，_downloads/kangxi/strokes.json）。'
    )
    full['meta']['sources']['kangxi_strokecount'] = 'breezyreeds/kangxi-strokecount (MIT)'

    # 保存
    with open(FULL, 'w', encoding='utf-8') as f:
        json.dump(full, f, ensure_ascii=False, indent=1)

    # 打印报告
    print('=' * 60)
    print('康熙笔画全量接入报告')
    print('=' * 60)
    print(f'总字数: {stats["total"]}')
    print()
    print('【按来源统计】')
    print(f'  人工核对(308常用字): {stats["manual_verified"]}')
    print(f'  traditional字段查繁体: {stats["field_lookup"]}')
    print(f'  gsc简繁映射推繁体: {stats["map_lookup"]}')
    print(f'  直接查字本身: {stats["direct_lookup"]}')
    print(f'  无数据(置空): {stats["not_found"]}')
    print()
    print('【填充情况】')
    print(f'  新填入(原为空): {stats["filled_new"]}')
    print(f'  更新(原有值但变化): {stats["updated"]}')
    print(f'  不变(原有值且一致): {stats["unchanged"]}')
    print()
    print(f'康熙笔画覆盖率: {coverage_kx}/{stats["total"]} ({coverage_kx*100/stats["total"]:.1f}%)')
    print()
    print('【308 常用字交叉验证】')
    print(f'  与新数据一致: {verify_match}')
    print(f'  与新数据不一致: {len(verify_mismatch)}')
    if verify_mismatch:
        print('  不一致明细 (char, trad_form, 人工值, 新数据值):')
        for ch, tf, mv, nv in verify_mismatch:
            print(f'    {ch} (繁{tf}): 人工={mv} vs 新数据={nv}  → 保留人工值')
    print(f'  新数据中无该繁体形式: {len(verify_no_data)}')
    if verify_no_data:
        print('  无数据明细:')
        for ch, tf, mv in verify_no_data:
            print(f'    {ch} (繁{tf}): 人工值={mv}, 新数据无此繁体形式')
    print()
    print('已保存:', FULL)


if __name__ == '__main__':
    main()
