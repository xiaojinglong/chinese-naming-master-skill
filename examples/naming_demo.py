# -*- coding: utf-8 -*-
"""
完整取名示例
============
演示取名全流程，包括不同权重预设、不同性别、不同姓氏的取名。
"""
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(SCRIPT_DIR, '..', '_tools')
sys.path.insert(0, TOOLS_DIR)

from name_generator import generate_names


def demo_case(title, **kwargs):
    """执行一个取名示例"""
    print(f'\n{"=" * 50}')
    print(f'  {title}')
    print(f'{"=" * 50}')

    result = generate_names(top_n=3, **kwargs)

    if result['bazi']:
        bazi = result['bazi']
        print(f'八字：{bazi["year_ganzhi"]}年 {bazi["month_ganzhi"]}月 '
              f'{bazi["day_ganzhi"]}日 {bazi["hour_ganzhi"]}时')
        print(f'日主：{bazi["day_master"]}（{bazi["day_master_wuxing"]}）| '
              f'强弱：{bazi["strength"]}')
        print(f'喜用神：{result["xiyongshen"]} | 生肖：{result["zodiac"]}')

    print(f'\n推荐名字（{len(result["candidates"])}个）：')
    for c in result['candidates']:
        scores_str = ' '.join(f'{k[:4]}={v}' for k, v in c['scores'].items())
        print(f'  {c["full_name"]:8s} {c["total_score"]:5.1f} ({c["grade"]})')


def main():
    print('中华取名大师 - 完整取名示例')

    # 案例1：李姓男宝宝
    demo_case(
        '案例1：李姓男宝宝（2024年3月15日10点）',
        surname='李', gender='male',
        birth_year=2024, birth_month=3, birth_day=15, birth_hour=10,
        name_length=2, weight_preset='default'
    )

    # 案例2：王姓女宝宝（文雅古风预设）
    demo_case(
        '案例2：王姓女宝宝 - 文雅古风（2024年6月20日8点）',
        surname='王', gender='female',
        birth_year=2024, birth_month=6, birth_day=20, birth_hour=8,
        name_length=2, weight_preset='文雅古风'
    )

    # 案例3：张姓男宝宝（八字优先预设）
    demo_case(
        '案例3：张姓男宝宝 - 八字优先（1990年5月20日14点）',
        surname='张', gender='male',
        birth_year=1990, birth_month=5, birth_day=20, birth_hour=14,
        name_length=2, weight_preset='八字优先'
    )

    # 案例4：刘姓女宝宝（现代好听预设）
    demo_case(
        '案例4：刘姓女宝宝 - 现代好听（2024年8月15日10点）',
        surname='刘', gender='female',
        birth_year=2024, birth_month=8, birth_day=15, birth_hour=10,
        name_length=2, weight_preset='现代好听'
    )

    # 案例5：单字名
    demo_case(
        '案例5：陈姓男宝宝 - 单字名（2024年1月10日12点）',
        surname='陈', gender='male',
        birth_year=2024, birth_month=1, birth_day=10, birth_hour=12,
        name_length=1, weight_preset='default'
    )


if __name__ == '__main__':
    main()
