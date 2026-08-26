# -*- coding: utf-8 -*-
"""
中华取名大师 - 取名+HTML报告示例
=================================
演示完整的取名流程，生成精致的HTML报告。
"""
import sys
import os

# 将 _tools 目录加入路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(SCRIPT_DIR, '..', '_tools')
sys.path.insert(0, TOOLS_DIR)

from name_generator import generate_names_with_report


def main():
    print('=' * 50)
    print('中华取名大师 - 取名 + HTML报告')
    print('=' * 50)

    # 输入参数
    surname = '李'
    gender = 'male'
    birth = (2024, 3, 15, 10)  # 2024年3月15日10点
    style = '大气'

    print(f'\n姓氏：{surname}')
    print(f'性别：{"男" if gender == "male" else "女"}')
    print(f'出生：{birth[0]}年{birth[1]}月{birth[2]}日 {birth[3]}时')
    print(f'风格：{style}')

    # 生成名字 + HTML报告
    result = generate_names_with_report(
        surname=surname,
        gender=gender,
        birth_year=birth[0], birth_month=birth[1],
        birth_day=birth[2], birth_hour=birth[3],
        name_length=2,
        top_n=10,  # 至少10个候选名
        style=style,
        output_path='naming_report.html'
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

    # 输出推荐名字
    print(f'\n--- 推荐名字（前{len(result["candidates"])}名）---')
    for i, c in enumerate(result['candidates'], 1):
        print(f'{i:2d}. {c["full_name"]:6s}  {c["total_score"]}分 ({c["grade"]})')

    # 输出报告路径
    print(f'\n--- HTML报告已生成 ---')
    print(f'报告路径：{os.path.abspath(result["report_path"])}')
    print('请用浏览器打开查看详细报告')


if __name__ == '__main__':
    main()
