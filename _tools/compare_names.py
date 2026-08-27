# -*- coding: utf-8 -*-
"""
名字对比模式（V3.3）

两两名字多维度对比，输出可读表格 + 风格化推荐结论。

用法：
    from compare_names import compare_names, format_compare
    report = compare_names('陈', ['沐泽', '泽宇'], gender='male',
                           birth_year=2026, birth_month=9, birth_day=1, birth_hour=12)
    print(format_compare(report))

命令行：
    python _tools/compare_names.py 陈 沐泽 泽宇
"""
import sys
import os
import io

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, '_tools'))

import name_generator as ng
from scoring_engine import score_name, load_data

# 对比展示维度（顺序即表格列序）
COMPARE_DIMS = [
    ('wuge_shuli',  '五格数理'),
    ('yinyun',      '音韵流畅'),
    ('yiyi',        '寓意深度'),
    ('zixing',      '字形美观'),
    ('modern_sense','现代语感'),
    ('wuxing_buyi', '五行补益'),
]


def _risk_label(scores):
    """根据分项判断重名/老气风险标签"""
    tags = []
    if scores.get('penalty', 1.0) < 1.0:
        if scores['penalty'] <= 0.3:
            tags.append('高（俗气/谐音命中）')
        elif scores['penalty'] < 1.0:
            tags.append('中（部分扣分）')
    if scores.get('modern_sense', 0) < 50:
        tags.append('高（现代语感低，偏老气）')
    if not tags:
        tags.append('低')
    return ' / '.join(tags)


def compare_names(surname, names, gender='male', birth_year=None, birth_month=None,
                  birth_day=None, birth_hour=12, top_xiyongshen=None):
    """
    对比 2 个以上名字。返回结构化对比报告 dict。

    若提供出生日期，自动排盘取喜用神；否则用 top_xiyongshen 或 None。
    """
    data = load_data()
    hanzi_map = data['hanzi_map']
    surname_map = ng.load_surnames()
    lit_map = ng.load_literature_map()

    xiyongshen = top_xiyongshen
    zodiac = None
    if birth_year:
        from bazi_engine import get_bazi
        bazi = get_bazi(birth_year, birth_month or 1, birth_day or 1, birth_hour)
        xiyongshen = bazi.xiyongshen
        zodiac = bazi.zodiac

    results = []
    for name in names:
        wg = ng.calc_wuge(surname, name, hanzi_map, surname_map)
        r = score_name(name, surname, data, xiyongshen=xiyongshen, zodiac=zodiac,
                       wuge_numbers=wg['wuge_numbers'], sancai_wuxing=wg['sancai_wuxing'],
                       literature_map=lit_map, surname_chars=[surname], gender=gender)
        wxs = [hanzi_map.get(c, {}).get('wuxing', '') for c in name]
        tones = [hanzi_map.get(c, {}).get('tone') for c in (surname + name)]
        results.append({
            'name': name,
            'full_name': surname + name,
            'total_score': r['total_score'],
            'grade': r['grade'],
            'scores': r['scores'],
            'wuxing': '+'.join(wxs),
            'wuge_numbers': wg['wuge_numbers'],
            'tones': '-'.join(str(t) if t else '?' for t in tones),
            'risk': _risk_label(r['scores']),
        })

    # 推荐结论：按总分排，找各自最强维度
    results_sorted = sorted(results, key=lambda x: -x['total_score'])
    best = results_sorted[0]
    # 各名字的"招牌维度"（相对最高分项）
    for r in results:
        r['strengths'] = []
        for key, label in COMPARE_DIMS:
            mine = r['scores'].get(key, 0)
            others_max = max(o['scores'].get(key, 0) for o in results if o is not r)
            if mine > others_max and mine >= 70:
                r['strengths'].append(label)

    return {
        'surname': surname,
        'names': results,
        'best': best,
        'xiyongshen': xiyongshen,
        'zodiac': zodiac,
    }


def format_compare(report):
    """格式化为可读文本表格"""
    out = io.StringIO()
    names = report['names']
    out.write(f"\n名字对比 · 姓氏 {report['surname']} · 喜用神 {report['xiyongshen'] or '未排盘'}\n")
    out.write('=' * 64 + '\n')

    # 表头
    header = f"{'维度':<10}" + ''.join(f"{n['full_name']:<14}" for n in names)
    out.write(header + '\n')
    out.write('-' * 64 + '\n')

    # 总分
    row = f"{'综合分':<10}" + ''.join(
        f"{n['total_score']:<14}" for n in names)
    out.write(row + '\n')
    row = f"{'等级':<10}" + ''.join(f"{n['grade']:<14}" for n in names)
    out.write(row + '\n')
    row = f"{'五行':<10}" + ''.join(f"{n['wuxing']:<14}" for n in names)
    out.write(row + '\n')
    row = f"{'声调':<10}" + ''.join(f"{n['tones']:<14}" for n in names)
    out.write(row + '\n')
    row = f"{'重名风险':<10}" + ''.join(f"{n['risk']:<14}" for n in names)
    out.write(row + '\n')
    out.write('-' * 64 + '\n')

    # 六维分项
    for key, label in COMPARE_DIMS:
        row = f"{label:<10}" + ''.join(
            f"{n['scores'].get(key, 0):<14}" for n in names)
        out.write(row + '\n')

    out.write('=' * 64 + '\n')

    # 推荐结论
    best = report['best']
    out.write(f"\n综合推荐：{best['full_name']}（{best['total_score']} 分）\n")
    for n in names:
        if n['strengths']:
            out.write(f"  · {n['full_name']} 在 {', '.join(n['strengths'])} 上领先\n")

    # 风格化建议
    by_modern = sorted(names, key=lambda x: -x['scores'].get('modern_sense', 0))[0]
    by_wuge = sorted(names, key=lambda x: -x['scores'].get('wuge_shuli', 0))[0]
    out.write(f"\n追求现代自然感：{by_modern['full_name']}\n")
    out.write(f"看重传统数理：{by_wuge['full_name']}\n")
    return out.getvalue()


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('用法: python compare_names.py <姓氏> <名字1> <名字2> [名字3...]')
        sys.exit(1)
    surname = sys.argv[1]
    names = sys.argv[2:]
    report = compare_names(surname, names)
    print(format_compare(report))
