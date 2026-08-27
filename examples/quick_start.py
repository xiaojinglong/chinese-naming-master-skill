# -*- coding: utf-8 -*-
"""
中华取名大师 - 快速开始示例
============================
30 秒内完成一次完整取名。
"""
import sys
import os

# 将 _tools 目录加入路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(SCRIPT_DIR, '..', '_tools')
sys.path.insert(0, TOOLS_DIR)

from name_generator import generate_names


def main():
    print('=' * 50)
    print('中华取名大师 - 快速开始')
    print('=' * 50)

    # 输入参数
    surname = '李'
    gender = 'male'
    birth = (2024, 3, 15, 10)  # 2024年3月15日10点

    print(f'\n姓氏：{surname}')
    print(f'性别：{"男" if gender == "male" else "女"}')
    print(f'出生：{birth[0]}年{birth[1]}月{birth[2]}日 {birth[3]}时')

    # 生成名字
    result = generate_names(
        surname=surname,
        gender=gender,
        birth_year=birth[0], birth_month=birth[1],
        birth_day=birth[2], birth_hour=birth[3],
        name_length=2,
        top_n=5
    )

    # 输出八字信息
    print(f'\n--- 八字排盘 ---')
    bazi = result['bazi']
    print(f'四柱：{bazi["year_ganzhi"]}年 {bazi["month_ganzhi"]}月 '
          f'{bazi["day_ganzhi"]}日 {bazi["hour_ganzhi"]}时')
    print(f'日主：{bazi["day_master"]}（{bazi["day_master_wuxing"]}）')
    print(f'强弱：{bazi["strength"]}（{bazi["strength_score"]}）')
    print(f'喜用神：{result["xiyongshen"]}', end='')
    if result['jiyongshen']:
        print(f' | 忌用神：{result["jiyongshen"]}')
    else:
        print()
    print(f'生肖：{result["zodiac"]} | 纳音：{bazi["nayin"]}')
    print(f'五行：{bazi["wuxing_count"]}')

    # 输出推荐名字
    print(f'\n--- 推荐名字（前{len(result["candidates"])}名）---')
    for i, c in enumerate(result['candidates'], 1):
        print(f'\n{i}. {c["full_name"]}  {c["total_score"]}分 ({c["grade"]})')
        for dim, score in c['scores'].items():
            if not isinstance(score, (int, float)):
                continue
            bar = '█' * (int(score) // 10)
            print(f'   {dim:20s} {score:3.0f} {bar}')


if __name__ == '__main__':
    main()
