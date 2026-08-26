# -*- coding: utf-8 -*-
"""
八字排盘示例
============
演示如何单独使用八字排盘引擎。
"""
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(SCRIPT_DIR, '..', '_tools')
sys.path.insert(0, TOOLS_DIR)

from bazi_engine import get_bazi, get_recommended_radicals, get_forbidden_radicals


def main():
    print('=' * 50)
    print('八字排盘引擎 - 示例')
    print('=' * 50)

    # 示例1：常规排盘
    print('\n--- 示例1：2024年3月15日10点 ---')
    bazi = get_bazi(2024, 3, 15, 10)
    print(bazi)

    # 示例2：立春边界（年柱切换）
    print('\n--- 示例2：立春边界测试 ---')
    print('2024年2月3日（立春前）：')
    bazi1 = get_bazi(2024, 2, 3, 10)
    print(f'  年柱：{bazi1.year_ganzhi}（应为癸卯，上一年）')
    print(f'  生肖：{bazi1.zodiac}（应为兔）')

    print('2024年2月5日（立春后）：')
    bazi2 = get_bazi(2024, 2, 5, 10)
    print(f'  年柱：{bazi2.year_ganzhi}（应为甲辰，本年）')
    print(f'  生肖：{bazi2.zodiac}（应为龙）')

    # 示例3：喜用神 → 推荐部首
    print('\n--- 示例3：喜用神推荐部首 ---')
    bazi3 = get_bazi(1990, 5, 20, 14)
    print(f'排盘：{bazi3.year_ganzhi}年 {bazi3.month_ganzhi}月 '
          f'{bazi3.day_ganzhi}日 {bazi3.hour_ganzhi}时')
    print(f'喜用神：{bazi3.xiyongshen}')
    print(f'推荐部首：{get_recommended_radicals(bazi3.xiyongshen)}')
    if bazi3.jiyongshen:
        print(f'忌用神：{bazi3.jiyongshen}')
        print(f'避用部首：{get_forbidden_radicals(bazi3.jiyongshen)}')

    # 示例4：五行统计
    print('\n--- 示例4：五行统计 ---')
    print(f'五行分布：{bazi3.wuxing_count}')
    max_wx = max(bazi3.wuxing_count, key=bazi3.wuxing_count.get)
    min_wx = min(bazi3.wuxing_count, key=bazi3.wuxing_count.get)
    print(f'最旺：{max_wx}({bazi3.wuxing_count[max_wx]}) | 最弱：{min_wx}({bazi3.wuxing_count[min_wx]})')


if __name__ == '__main__':
    main()
