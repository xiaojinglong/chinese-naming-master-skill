# -*- coding: utf-8 -*-
"""
扩充 hanzi_full.json 的五行属性(wuxing)覆盖率：
1. 修复 55 个非标准值（jin→金、mu→木、shui→水、-→None）
2. 从 wuxing_dict_jianti.json + wuxing_dict_fanti.json 构建全量 char→五行 映射
3. 填充缺失的 wuxing 字段
4. 报告覆盖率变化

五行口径：James88/qiming 的 wuxing_dict 系列以笔画数五行为主（按康熙笔画分组），
与字库现有口径（字义五行为主）存在差异，仅在字库缺失 wuxing 时补充，不覆盖已有值。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
FULL = os.path.join(BASE, '..', '01-数据资料', '汉字字库', 'hanzi_full.json')
WJ = os.path.join(BASE, '..', '05-开源项目参考', 'james88-qiming', 'data', 'wuxing_dict_jianti.json')
WF = os.path.join(BASE, '..', '05-开源项目参考', 'james88-qiming', 'data', 'wuxing_dict_fanti.json')

# pinyin -> chinese
PINYIN_MAP = {'tu': '土', 'mu': '木', 'jin': '金', 'shui': '水', 'huo': '火'}


def build_wuxing_map():
    """从简体+繁体五行字典构建 char→五行 映射"""
    wmap = {}
    for path, label in [(WJ, 'jianti'), (WF, 'fanti')]:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        for wx_pinyin, stroke_dict in data.items():
            wx_cn = PINYIN_MAP.get(wx_pinyin)
            if not wx_cn:
                continue
            if not isinstance(stroke_dict, dict):
                continue
            for stroke, chars in stroke_dict.items():
                if not isinstance(chars, list):
                    continue
                for ch in chars:
                    if len(ch) == 1 and ch not in wmap:
                        wmap[ch] = (wx_cn, label)
    return wmap


def main():
    wmap = build_wuxing_map()
    print(f'五行字典总字数: {len(wmap)}')

    with open(FULL, encoding='utf-8') as f:
        full = json.load(f)

    chars = full['chars']
    total = len(chars)

    # 统计初始状态
    before_valid = sum(1 for c in chars if c.get('wuxing') in ('金', '木', '水', '火', '土'))
    before_none = sum(1 for c in chars if not c.get('wuxing') or c.get('wuxing') in ('-', None))
    before_bad = sum(1 for c in chars if c.get('wuxing') and c['wuxing'] not in ('金', '木', '水', '火', '土', None))

    # 1. 修复非标准值
    fix_map = {'jin': '金', 'mu': '木', 'shui': '水', 'huo': '火', 'tu': '土', '-': None}
    fixed_bad = 0
    for c in chars:
        wx = c.get('wuxing')
        if wx in fix_map:
            new_wx = fix_map[wx]
            if new_wx != wx:
                c['wuxing'] = new_wx
                fixed_bad += 1

    # 2. 填充缺失的 wuxing（不覆盖已有有效值）
    filled = 0
    filled_detail = {'jianti': 0, 'fanti': 0}
    for c in chars:
        wx = c.get('wuxing')
        if wx in ('金', '木', '水', '火', '土'):
            continue  # 已有有效值，不覆盖
        ch = c['char']
        if ch in wmap:
            new_wx, source = wmap[ch]
            c['wuxing'] = new_wx
            c['wuxing_source'] = f'wuxing_dict_{source}'
            filled += 1
            filled_detail[source] += 1
            continue
        # 尝试繁体形式
        trad = c.get('traditional', '')
        if trad and len(trad) >= 1 and trad[0] in wmap:
            new_wx, source = wmap[trad[0]]
            c['wuxing'] = new_wx
            c['wuxing_source'] = f'wuxing_dict_{source}_via_traditional'
            filled += 1
            filled_detail[source] += 1
            continue
        # 仍然没有
        if c.get('wuxing_source') is None:
            c['wuxing_source'] = None

    # 统计结果
    after_valid = sum(1 for c in chars if c.get('wuxing') in ('金', '木', '水', '火', '土'))
    after_none = sum(1 for c in chars if not c.get('wuxing'))

    # 更新 meta
    full['meta']['coverage']['wuxing'] = after_valid
    full['meta']['wuxing_note'] = (
        f'五行属性覆盖：{after_valid}/{total} 字。'
        f'来源：① gsc_pinyin 字义五行（主源，不覆盖）；'
        f'② wuxing_dict_jianti/fanti 笔画五行（补充源，仅填空，{filled} 字）。'
        f'口径差异：笔画五行与字义五行存在差异，仅在缺失时补充，不覆盖已有值。'
    )
    full['meta']['sources']['wuxing_dict'] = 'James88/qiming wuxing_dict_jianti.json + wuxing_dict_fanti.json (笔画五行)'

    with open(FULL, 'w', encoding='utf-8') as f:
        json.dump(full, f, ensure_ascii=False, indent=1)

    # 报告
    print('=' * 60)
    print('五行属性扩充报告')
    print('=' * 60)
    print(f'总字数: {total}')
    print(f'修复非标准值: {fixed_bad} 字 (jin→金/mu→木/shui→水/-→None)')
    print(f'从五行字典填充: {filled} 字 (简体{filled_detail["jianti"]} + 繁体{filled_detail["fanti"]})')
    print()
    print(f'有效五行覆盖: {before_valid} → {after_valid} ({before_valid*100/total:.1f}% → {after_valid*100/total:.1f}%)')
    print(f'无五行: {before_none} → {after_none}')
    print(f'非标准值: {before_bad} → 0 (已修复)')
    print()

    # 五行分布
    from collections import Counter
    wx_dist = Counter(c.get('wuxing') for c in chars if c.get('wuxing') in ('金', '木', '水', '火', '土'))
    print('五行分布:')
    for k in ['金', '木', '水', '火', '土']:
        print(f'  {k}: {wx_dist.get(k, 0)}')
    print()
    print('已保存:', FULL)


if __name__ == '__main__':
    main()
