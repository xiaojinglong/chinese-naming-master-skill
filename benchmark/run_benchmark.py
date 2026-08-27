# -*- coding: utf-8 -*-
"""
基准回归测试运行器（V3.3）

用法：
    python benchmark/run_benchmark.py
    # 输出每个用例的通过/失败 + 汇总，失败返回非零退出码
"""
import sys
import os
import json
import io
from datetime import date

# Windows 控制台 UTF-8 输出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, '_tools'))

import name_generator as ng
from scoring_engine import score_name, load_data
from bazi_engine import get_bazi

CASES_PATH = os.path.join(BASE, 'benchmark', 'cases.json')


def _ganzhi_of(idx):
    GAN = '甲乙丙丁戊己庚辛壬癸'
    ZHI = '子丑寅卯辰巳午未申酉戌亥'
    return GAN[idx % 10] + ZHI[idx % 12]


def run():
    cases = json.load(open(CASES_PATH, encoding='utf-8'))
    data = load_data()
    hanzi_map = data['hanzi_map']
    surname_map = ng.load_surnames()
    lit_map = ng.load_literature_map()

    passed, failed = 0, 0
    fails = []

    print('=' * 60)
    print('取名引擎基准回归测试')
    print('=' * 60)

    # --- 好名用例 ---
    print('\n[好名用例] 应得高分、五行命中、五格无凶')
    for scenario in cases['good_cases']:
        parts = scenario['birth'].replace(':', ' ').split('-')
        y, mo, d = int(parts[0]), int(parts[1]), int(parts[2].split()[0])
        h = int(parts[2].split()[1])
        for nc in scenario['names']:
            name = nc['name']
            wg = ng.calc_wuge(scenario['surname'], name, hanzi_map, surname_map)
            r = score_name(name, scenario['surname'], data,
                           xiyongshen=scenario['xiyongshen'],
                           zodiac=scenario['zodiac'],
                           wuge_numbers=wg['wuge_numbers'],
                           sancai_wuxing=wg['sancai_wuxing'],
                           literature_map=lit_map,
                           surname_chars=[scenario['surname']],
                           gender=scenario['gender'])
            score = r['total_score']
            wxs = [hanzi_map.get(c, {}).get('wuxing', '') for c in name]
            ok = score >= nc['min_score']
            if nc.get('must_contain_wuxing'):
                ok = ok and nc['must_contain_wuxing'] in wxs
            if nc.get('must_grade'):
                ok = ok and any(g in r['grade'] for g in nc['must_grade'])
            mark = '✓' if ok else '✗'
            print(f"  {mark} {scenario['surname']}{name}  分:{score} 五行:{'+'.join(wxs)} penalty:{r['scores']['penalty']}")
            if ok:
                passed += 1
            else:
                failed += 1
                fails.append(f"{scenario['surname']}{name} 好名用例未达预期 (分{score}<{nc['min_score']})")

    # --- 坏名用例 ---
    print('\n[坏名用例] 应被低分/乘法扣分淘汰')
    for bc in cases['bad_cases']:
        name = bc['name']
        wg = ng.calc_wuge(bc['surname'], name, hanzi_map, surname_map)
        r = score_name(name, bc['surname'], data, xiyongshen='水', zodiac='马',
                       wuge_numbers=wg['wuge_numbers'], sancai_wuxing=wg['sancai_wuxing'],
                       literature_map=lit_map, surname_chars=[bc['surname']], gender='male')
        score = r['total_score']
        pen = r['scores']['penalty']
        ok = score <= bc['max_score']
        if bc.get('must_penalty_below'):
            ok = ok and pen < bc['must_penalty_below']
        mark = '✓' if ok else '✗'
        print(f"  {mark} {bc['surname']}{name}  分:{score} penalty:{pen}  ({bc['reason']})")
        if ok:
            passed += 1
        else:
            failed += 1
            fails.append(f"{bc['surname']}{name} 坏名用例未被淘汰 (分{score}>{bc['max_score']})")

    # --- 日柱用例 ---
    print('\n[八字日柱] 独立推算核验')
    REF = date(2000, 1, 1)  # 戊午 = index 54
    for dc in cases['bazi_day_pillar_cases']:
        yp, mp, dp = dc['date'].split('-')
        idx = (54 + (date(int(yp), int(mp), int(dp)) - REF).days) % 60
        mine = _ganzhi_of(idx)
        theirs = get_bazi(int(yp), int(mp), int(dp), 12).day_ganzhi
        ok = mine == theirs == dc['expected']
        mark = '✓' if ok else '✗'
        print(f"  {mark} {dc['date']} 日柱={theirs} (预期{dc['expected']})")
        if ok:
            passed += 1
        else:
            failed += 1
            fails.append(f"{dc['date']} 日柱 {theirs}≠{dc['expected']}")

    print('\n' + '=' * 60)
    print(f'  结果: {passed} PASS / {failed} FAIL')
    if fails:
        print('  失败用例:')
        for f in fails:
            print(f'    - {f}')
    print('=' * 60)
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(run())
