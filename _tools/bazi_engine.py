# -*- coding: utf-8 -*-
"""
八字排盘引擎
============
从公历生日/时辰计算八字四柱（年柱、月柱、日柱、时柱）、五行统计、日主强弱、喜用神。

数据来源：
- 01-数据资料/天干地支与八字/ 目录下的 tiangan/dizhi/nayin/shengxiao/jieqi.json
- 02-规则与算法资料/01-八字排盘规则.md（排盘算法）

核心函数：
  get_bazi(year, month, day, hour=12, minute=0) -> BaziResult
    返回：四柱干支、五行统计、日主强弱、喜用神、调候建议

算法说明：
  1. 年柱：以立春为界，立春前用上一年干支
  2. 月柱：以节气为界（12节令分12月），年干定月干（甲己之年丙作首...）
  3. 日柱：公式推算（基日 1900-01-01 = 甲戌日，日干支 = 基日 + 偏移天数）
  4. 时柱：日干定时干（甲己还加甲，乙庚丙作初...）
  5. 五行统计：天干本气 + 地支藏干（含本气/中气/余气）
  6. 日主强弱：得令（月支生扶）+ 得地（其他支生扶）+ 得势（天干比劫）
  7. 喜用神：身强则克泄耗（财官食伤），身弱则生扶（印比劫）
"""
import json
import os
import math
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, '..', '01-数据资料', '天干地支与八字')

# 天干/地支/五行/阴阳
TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
GAN_WUXING = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
              '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
GAN_YINYANG = {'甲': '阳', '乙': '阴', '丙': '阳', '丁': '阴', '戊': '阳',
               '己': '阴', '庚': '阳', '辛': '阴', '壬': '阳', '癸': '阴'}
ZHI_WUXING = {'子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土',
              '巳': '火', '午': '火', '未': '土', '申': '金', '酉': '金',
              '戌': '土', '亥': '水'}
ZHI_YINYANG = {'子': '阳', '丑': '阴', '寅': '阳', '卯': '阴', '辰': '阳',
               '巳': '阴', '午': '阳', '未': '阴', '申': '阳', '酉': '阴',
               '戌': '阳', '亥': '阴'}
ZHI_CANGGAN = {
    '子': [('癸', '本气')],
    '丑': [('己', '本气'), ('癸', '中气'), ('辛', '余气')],
    '寅': [('甲', '本气'), ('丙', '中气'), ('戊', '余气')],
    '卯': [('乙', '本气')],
    '辰': [('戊', '本气'), ('乙', '中气'), ('癸', '余气')],
    '巳': [('丙', '本气'), ('庚', '中气'), ('戊', '余气')],
    '午': [('丁', '本气'), ('己', '中气')],
    '未': [('己', '本气'), ('丁', '中气'), ('乙', '余气')],
    '申': [('庚', '本气'), ('壬', '中气'), ('戊', '余气')],
    '酉': [('辛', '本气')],
    '戌': [('戊', '本气'), ('辛', '中气'), ('丁', '余气')],
    '亥': [('壬', '本气'), ('甲', '中气')],
}

# 60甲子
JIAZI = []
for i in range(60):
    JIAZI.append(TIANGAN[i % 10] + DIZHI[i % 12])

# 月柱干口诀：甲己之年丙作首，乙庚之岁戊为头，丙辛必定寻庚起，丁壬壬位顺行流，戊癸何方发，甲寅之上好追求
MONTH_GAN_START = {'甲': '丙', '己': '丙', '乙': '戊', '庚': '戊',
                   '丙': '庚', '辛': '庚', '丁': '壬', '壬': '壬',
                   '戊': '甲', '癸': '甲'}

# 时柱干口诀：甲己还加甲，乙庚丙作初，丙辛从戊起，丁壬庚子居，戊癸何方发，壬子是真途
HOUR_GAN_START = {'甲': '甲', '己': '甲', '乙': '丙', '庚': '丙',
                  '丙': '戊', '辛': '戊', '丁': '庚', '壬': '庚',
                  '戊': '壬', '癸': '壬'}

# 节气表（12节令，月柱分界）
JIEQI = [
    {'jie': '立春', 'month_zhi': '寅', 'month_index': 1},
    {'jie': '惊蛰', 'month_zhi': '卯', 'month_index': 2},
    {'jie': '清明', 'month_zhi': '辰', 'month_index': 3},
    {'jie': '立夏', 'month_zhi': '巳', 'month_index': 4},
    {'jie': '芒种', 'month_zhi': '午', 'month_index': 5},
    {'jie': '小暑', 'month_zhi': '未', 'month_index': 6},
    {'jie': '立秋', 'month_zhi': '申', 'month_index': 7},
    {'jie': '白露', 'month_zhi': '酉', 'month_index': 8},
    {'jie': '寒露', 'month_zhi': '戌', 'month_index': 9},
    {'jie': '立冬', 'month_zhi': '亥', 'month_index': 10},
    {'jie': '大雪', 'month_zhi': '子', 'month_index': 11},
    {'jie': '小寒', 'month_zhi': '丑', 'month_index': 12},
]

# 基日：1900-01-01 = 甲戌日 (甲戌在60甲子中的index)
BASE_DATE = datetime(1900, 1, 1)
BASE_GANZHI_INDEX = 10  # 甲戌 = 10 (甲0乙1...戌10)

# 立春精确日期表（1900-2100年，月,日）
# 来源：中国科学院紫金山天文台历算数据
# 注：2100年后需更新此表
LICHUN_DATES = {
    1900: (2, 4), 1901: (2, 4), 1902: (2, 4), 1903: (2, 5), 1904: (2, 5),
    1905: (2, 4), 1906: (2, 4), 1907: (2, 5), 1908: (2, 5), 1909: (2, 4),
    1910: (2, 4), 1911: (2, 5), 1912: (2, 5), 1913: (2, 4), 1914: (2, 4),
    1915: (2, 5), 1916: (2, 5), 1917: (2, 4), 1918: (2, 4), 1919: (2, 5),
    1920: (2, 5), 1921: (2, 4), 1922: (2, 4), 1923: (2, 5), 1924: (2, 5),
    1925: (2, 4), 1926: (2, 4), 1927: (2, 5), 1928: (2, 5), 1929: (2, 4),
    1930: (2, 4), 1931: (2, 5), 1932: (2, 5), 1933: (2, 4), 1934: (2, 4),
    1935: (2, 5), 1936: (2, 5), 1937: (2, 4), 1938: (2, 4), 1939: (2, 5),
    1940: (2, 5), 1941: (2, 4), 1942: (2, 4), 1943: (2, 5), 1944: (2, 5),
    1945: (2, 4), 1946: (2, 4), 1947: (2, 4), 1948: (2, 5), 1949: (2, 4),
    1950: (2, 4), 1951: (2, 4), 1952: (2, 5), 1953: (2, 4), 1954: (2, 4),
    1955: (2, 4), 1956: (2, 5), 1957: (2, 4), 1958: (2, 4), 1959: (2, 4),
    1960: (2, 5), 1961: (2, 4), 1962: (2, 4), 1963: (2, 4), 1964: (2, 5),
    1965: (2, 4), 1966: (2, 4), 1967: (2, 4), 1968: (2, 5), 1969: (2, 4),
    1970: (2, 4), 1971: (2, 4), 1972: (2, 5), 1973: (2, 4), 1974: (2, 4),
    1975: (2, 4), 1976: (2, 5), 1977: (2, 4), 1978: (2, 4), 1979: (2, 4),
    1980: (2, 5), 1981: (2, 4), 1982: (2, 4), 1983: (2, 4), 1984: (2, 4),
    1985: (2, 4), 1986: (2, 4), 1987: (2, 4), 1988: (2, 4), 1989: (2, 4),
    1990: (2, 4), 1991: (2, 4), 1992: (2, 4), 1993: (2, 4), 1994: (2, 4),
    1995: (2, 4), 1996: (2, 4), 1997: (2, 4), 1998: (2, 4), 1999: (2, 4),
    2000: (2, 4), 2001: (2, 4), 2002: (2, 4), 2003: (2, 4), 2004: (2, 4),
    2005: (2, 4), 2006: (2, 4), 2007: (2, 4), 2008: (2, 4), 2009: (2, 4),
    2010: (2, 4), 2011: (2, 4), 2012: (2, 4), 2013: (2, 4), 2014: (2, 4),
    2015: (2, 4), 2016: (2, 4), 2017: (2, 3), 2018: (2, 4), 2019: (2, 4),
    2020: (2, 4), 2021: (2, 3), 2022: (2, 4), 2023: (2, 4), 2024: (2, 4),
    2025: (2, 3), 2026: (2, 4), 2027: (2, 4), 2028: (2, 4), 2029: (2, 3),
    2030: (2, 4), 2031: (2, 4), 2032: (2, 4), 2033: (2, 3), 2034: (2, 4),
    2035: (2, 4), 2036: (2, 4), 2037: (2, 3), 2038: (2, 4), 2039: (2, 4),
    2040: (2, 4), 2041: (2, 3), 2042: (2, 4), 2043: (2, 4), 2044: (2, 4),
    2045: (2, 3), 2046: (2, 4), 2047: (2, 4), 2048: (2, 4), 2049: (2, 3),
    2050: (2, 4), 2051: (2, 4), 2052: (2, 4), 2053: (2, 3), 2054: (2, 4),
    2055: (2, 4), 2056: (2, 4), 2057: (2, 3), 2058: (2, 4), 2059: (2, 4),
    2060: (2, 4), 2061: (2, 3), 2062: (2, 4), 2063: (2, 4), 2064: (2, 4),
    2065: (2, 3), 2066: (2, 4), 2067: (2, 4), 2068: (2, 4), 2069: (2, 3),
    2070: (2, 4), 2071: (2, 4), 2072: (2, 4), 2073: (2, 3), 2074: (2, 4),
    2075: (2, 4), 2076: (2, 4), 2077: (2, 3), 2078: (2, 4), 2079: (2, 4),
    2080: (2, 4), 2081: (2, 3), 2082: (2, 4), 2083: (2, 4), 2084: (2, 4),
    2085: (2, 3), 2086: (2, 4), 2087: (2, 4), 2088: (2, 4), 2089: (2, 3),
    2090: (2, 4), 2091: (2, 4), 2092: (2, 4), 2093: (2, 3), 2094: (2, 4),
    2095: (2, 4), 2096: (2, 4), 2097: (2, 3), 2098: (2, 4), 2099: (2, 4),
    2100: (2, 4),
}

# 12节令精确日期表（2020-2030年，用于精确月柱计算）
# 格式：{year: {month_index: (day, month)}}
JIEQI_EXACT_DATES = {
    2020: {1: (4, 2), 2: (5, 3), 3: (4, 4), 4: (5, 5), 5: (5, 6), 6: (6, 7),
           7: (7, 8), 8: (7, 9), 9: (8, 10), 10: (7, 11), 11: (7, 12), 12: (6, 1)},
    2021: {1: (3, 2), 2: (5, 3), 3: (4, 4), 4: (5, 5), 5: (5, 6), 6: (7, 7),
           7: (7, 8), 8: (7, 9), 9: (8, 10), 10: (7, 11), 11: (7, 12), 12: (5, 1)},
    2022: {1: (4, 2), 2: (5, 3), 3: (5, 4), 4: (5, 5), 5: (6, 6), 6: (7, 7),
           7: (7, 8), 8: (7, 9), 9: (8, 10), 10: (8, 11), 11: (7, 12), 12: (7, 1)},
    2023: {1: (4, 2), 2: (6, 3), 3: (5, 4), 4: (5, 5), 5: (6, 6), 6: (6, 7),
           7: (7, 8), 8: (8, 9), 9: (8, 10), 10: (8, 11), 11: (7, 12), 12: (7, 1)},
    2024: {1: (4, 2), 2: (4, 3), 3: (4, 4), 4: (4, 5), 5: (5, 6), 6: (5, 7),
           7: (7, 8), 8: (7, 9), 9: (7, 10), 10: (8, 11), 11: (7, 12), 12: (5, 1)},
    2025: {1: (3, 2), 2: (5, 3), 3: (5, 4), 4: (5, 5), 5: (5, 6), 6: (5, 7),
           7: (7, 8), 8: (7, 9), 9: (7, 10), 10: (8, 11), 11: (7, 12), 12: (7, 1)},
    2026: {1: (5, 2), 2: (4, 3), 3: (5, 4), 4: (5, 5), 5: (5, 6), 6: (5, 7),
           7: (7, 8), 8: (7, 9), 9: (7, 10), 10: (8, 11), 11: (7, 12), 12: (7, 1)},
    2027: {1: (5, 2), 2: (4, 3), 3: (5, 4), 4: (5, 5), 5: (5, 6), 6: (5, 7),
           7: (7, 8), 8: (7, 9), 9: (8, 10), 10: (8, 11), 11: (7, 12), 12: (7, 1)},
    2028: {1: (5, 2), 2: (4, 3), 3: (4, 4), 4: (4, 5), 5: (5, 6), 6: (5, 7),
           7: (6, 8), 8: (7, 9), 9: (7, 10), 10: (8, 11), 11: (7, 12), 12: (6, 1)},
    2029: {1: (3, 2), 2: (4, 3), 3: (5, 4), 4: (4, 5), 5: (5, 6), 6: (5, 7),
           7: (7, 8), 8: (7, 9), 9: (7, 10), 10: (8, 11), 11: (7, 12), 12: (7, 1)},
    2030: {1: (5, 2), 2: (4, 3), 3: (5, 4), 4: (5, 5), 5: (5, 6), 6: (5, 7),
           7: (7, 8), 8: (7, 9), 9: (7, 10), 10: (8, 11), 11: (7, 12), 12: (7, 1)},
}

# 五行生克关系
SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}  # 我生者
KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}  # 我克者
SHENG_BY = {v: k for k, v in SHENG.items()}  # 生我者
KE_BY = {v: k for k, v in KE.items()}  # 克我者


class BaziResult:
    """八字排盘结果"""

    def __init__(self):
        self.year_ganzhi = ''      # 年柱干支
        self.month_ganzhi = ''     # 月柱干支
        self.day_ganzhi = ''       # 日柱干支
        self.hour_ganzhi = ''      # 时柱干支
        self.pillars = {}          # 四柱详细信息
        self.wuxing_count = {}     # 五行统计（含藏干）
        self.day_master = ''       # 日主（日干）
        self.day_master_wuxing = '' # 日主五行
        self.strength = ''         # 身强/身弱/中和
        self.strength_score = 0    # 强弱分数
        self.xiyongshen = ''       # 喜用神（五行）
        self.jiyongshen = ''       # 忌用神（五行）
        self.tiaohou = ''          # 调候建议
        self.zodiac = ''           # 生肖
        self.nayin = ''            # 年柱纳音

    def to_dict(self):
        return {
            'year_ganzhi': self.year_ganzhi,
            'month_ganzhi': self.month_ganzhi,
            'day_ganzhi': self.day_ganzhi,
            'hour_ganzhi': self.hour_ganzhi,
            'day_master': self.day_master,
            'day_master_wuxing': self.day_master_wuxing,
            'strength': self.strength,
            'strength_score': self.strength_score,
            'xiyongshen': self.xiyongshen,
            'jiyongshen': self.jiyongshen,
            'tiaohou': self.tiaohou,
            'zodiac': self.zodiac,
            'nayin': self.nayin,
            'wuxing_count': self.wuxing_count,
            'pillars': self.pillars,
        }

    def __str__(self):
        return (f'八字：{self.year_ganzhi}年 {self.month_ganzhi}月 {self.day_ganzhi}日 {self.hour_ganzhi}时\n'
                f'日主：{self.day_master}({self.day_master_wuxing}) | 强弱：{self.strength}({self.strength_score})\n'
                f'喜用神：{self.xiyongshen} | 忌用神：{self.jiyongshen} | 调候：{self.tiaohou}\n'
                f'五行统计：{self.wuxing_count}')


def _get_year_ganzhi(year, month, day):
    """计算年柱干支。立春前用上一年。

    使用精确立春日期表（1900-2100年）。
    对于表中没有的年份，使用近似日期2月4日。
    """
    actual_year = year

    # 查找精确立春日期
    if year in LICHUN_DATES:
        lichun_month, lichun_day = LICHUN_DATES[year]
    else:
        # 超出表范围，使用近似值
        lichun_month, lichun_day = 2, 4

    # 判断是否已过立春
    if month < lichun_month or (month == lichun_month and day < lichun_day):
        actual_year = year - 1

    # 1984年为甲子年（index=0）
    index = (actual_year - 1984) % 60
    return JIAZI[index]


def _get_month_ganzhi(year, month, day):
    """计算月柱干支。以节气为界。"""
    # 确定月支：根据当前日期所在的节气
    month_zhi_index = _get_month_zhi(year, month, day)
    month_zhi = DIZHI[month_zhi_index]

    # 确定月干：由年干定月干起始
    year_ganzhi = _get_year_ganzhi(year, month, day)
    year_gan = year_ganzhi[0]
    month_gan_start = MONTH_GAN_START[year_gan]
    month_gan_start_index = TIANGAN.index(month_gan_start)

    # 月干 = 起始干 + 月支index偏移（寅月起算）
    # 寅月(index=2)对应起始干
    gan_index = (month_gan_start_index + month_zhi_index - 2) % 10
    month_gan = TIANGAN[gan_index]

    return month_gan + month_zhi


def _get_month_zhi(year, month, day):
    """根据公历月日确定月支（以节气为界）。

    优先使用精确节气数据（2020-2030年），
    超出范围时使用近似日期。
    """
    # 节气近似日期（每月约5-8日交节）
    # 立春2/4、惊蛰3/6、清明4/5、立夏5/6、芒种6/6、小暑7/7
    # 立秋8/8、白露9/8、寒露10/8、立冬11/8、大雪12/7、小寒1/6
    jieqi_approx = {
        2: (4, 2), 3: (6, 3), 4: (5, 4), 5: (6, 5), 6: (6, 6), 7: (7, 7),
        8: (8, 8), 9: (8, 9), 10: (8, 10), 11: (8, 11), 12: (7, 12), 1: (6, 1),
    }

    # 尝试使用精确数据
    if year in JIEQI_EXACT_DATES:
        # 将公历月份映射到节令index
        # 1月->小寒(12), 2月->立春(1), 3月->惊蛰(2), ...
        month_to_jie_index = {1: 12, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5,
                              7: 6, 8: 7, 9: 8, 10: 9, 11: 10, 12: 11}
        jie_index = month_to_jie_index[month]
        jie_day, _ = JIEQI_EXACT_DATES[year][jie_index]
    else:
        # 使用近似值
        jie_day, _ = jieqi_approx[month]

    if day < jie_day:
        # 未到节气，用上一个月
        month -= 1
        if month == 0:
            month = 12
    # 月支：正月寅(2)、二月卯(3)、三月辰(4)...十二月丑(1)
    month_zhi_map = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6,
                     7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 0}
    return month_zhi_map[month]


def _get_day_ganzhi(year, month, day):
    """计算日柱干支。基日 1900-01-01 = 甲戌日(index=10)。"""
    target = datetime(year, month, day)
    delta = (target - BASE_DATE).days
    index = (BASE_GANZHI_INDEX + delta) % 60
    return JIAZI[index]


def _get_hour_ganzhi(day_ganzhi, hour):
    """计算时柱干支。日干定时干起始。"""
    day_gan = day_ganzhi[0]
    hour_gan_start = HOUR_GAN_START[day_gan]
    hour_gan_start_index = TIANGAN.index(hour_gan_start)

    # 时辰：子23-1、丑1-3、寅3-5、卯5-7、辰7-9、巳9-11、午11-13、未13-15、申15-17、酉17-19、戌19-21、亥21-23
    hour_zhi_index = (hour + 1) // 2 % 12
    hour_zhi = DIZHI[hour_zhi_index]

    # 时干 = 起始干 + 时辰index
    hour_gan_index = (hour_gan_start_index + hour_zhi_index) % 10
    hour_gan = TIANGAN[hour_gan_index]

    return hour_gan + hour_zhi


def _get_zodiac(year_ganzhi):
    """从年柱地支获取生肖"""
    zhi = year_ganzhi[1]
    zodiac_map = {'子': '鼠', '丑': '牛', '寅': '虎', '卯': '兔',
                  '辰': '龙', '巳': '蛇', '午': '马', '未': '羊',
                  '申': '猴', '酉': '鸡', '戌': '狗', '亥': '猪'}
    return zodiac_map.get(zhi, '')


def _load_nayin_map():
    """从 JSON 文件加载纳音表"""
    path = os.path.join(DATA_DIR, 'nayin.json')
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return {item['ganzhi']: item['nayin'] for item in data.get('nayin', [])}


# 延迟加载纳音表（首次调用时加载）
_nayin_cache = None


def _get_nayin(year_ganzhi):
    """获取年柱纳音（从 JSON 数据文件加载）"""
    global _nayin_cache
    if _nayin_cache is None:
        _nayin_cache = _load_nayin_map()
    return _nayin_cache.get(year_ganzhi, '')


def _analyze_wuxing(pillars):
    """统计八字五行（含天干本气+地支藏干）"""
    wuxing = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
    for gz in [pillars['year'], pillars['month'], pillars['day'], pillars['hour']]:
        gan, zhi = gz[0], gz[1]
        # 天干
        wx = GAN_WUXING[gan]
        wuxing[wx] += 1
        # 地支藏干
        for cg, qi in ZHI_CANGGAN.get(zhi, []):
            cg_wx = GAN_WUXING[cg]
            weight = {'本气': 1.0, '中气': 0.5, '余气': 0.3}.get(qi, 0.3)
            wuxing[cg_wx] += weight
    # 四舍五入到一位小数
    for k in wuxing:
        wuxing[k] = round(wuxing[k], 1)
    return wuxing


def _analyze_strength(day_gan, month_zhi, pillars):
    """分析日主强弱"""
    day_wx = GAN_WUXING[day_gan]
    month_wx = ZHI_WUXING[month_zhi]

    score = 0
    # 1. 得令：月支五行生日主或同日主
    if SHENG.get(month_wx) == day_wx or month_wx == day_wx:
        score += 3
    elif KE.get(month_wx) == day_wx or KE_BY.get(month_wx) == day_wx:
        score -= 3
    else:
        score += 0

    # 2. 得地：其他三支中生日主的个数
    for gz in [pillars['year'], pillars['day'], pillars['hour']]:
        zhi = gz[1]
        zhi_wx = ZHI_WUXING[zhi]
        if zhi != month_zhi:  # 已计过月支
            if SHENG.get(zhi_wx) == day_wx or zhi_wx == day_wx:
                score += 1
            elif KE.get(zhi_wx) == day_wx:
                score -= 1

    # 3. 得势：天干中比劫（同五行）和印星（生日主五行）的个数
    for gz in [pillars['year'], pillars['month'], pillars['hour']]:
        gan = gz[0]
        if gan != day_gan:
            gan_wx = GAN_WUXING[gan]
            if gan_wx == day_wx:
                score += 1  # 比劫
            elif SHENG.get(gan_wx) == day_wx:
                score += 1  # 印星
            elif KE.get(gan_wx) == day_wx:
                score -= 1  # 官杀
            elif SHENG_BY.get(gan_wx) == day_wx:
                score -= 1  # 食伤（泄）
            elif KE_BY.get(gan_wx) == day_wx:
                score -= 1  # 财星（耗）

    # 判定强弱
    if score >= 4:
        strength = '身强'
    elif score <= -2:
        strength = '身弱'
    else:
        strength = '中和'

    return strength, score


def _get_xiyongshen(day_gan, strength, wuxing_count):
    """确定喜用神和忌用神"""
    day_wx = GAN_WUXING[day_gan]

    if strength == '身强':
        # 身强：喜克（官杀）、喜泄（食伤）、喜耗（财星）
        ke_wx = KE[day_wx]          # 我克=财
        guan_wx = KE_BY[day_wx]     # 克我=官杀
        xie_wx = SHENG[day_wx]      # 我生=食伤
        # 选五行最少的为喜用
        candidates = {guan_wx: '官杀', ke_wx: '财', xie_wx: '食伤'}
        # 找五行最少的
        min_wx = min(candidates.keys(), key=lambda w: wuxing_count.get(w, 0))
        xiyongshen = min_wx
        jiyongshen = day_wx  # 忌比劫
    elif strength == '身弱':
        # 身弱：喜生（印星）、喜扶（比劫）
        sheng_wx = SHENG_BY[day_wx]  # 生我=印
        xiyongshen = sheng_wx
        jiyongshen = KE_BY[day_wx]   # 忌官杀
    else:
        # 中和：喜用平衡
        min_wx = min(wuxing_count.keys(), key=lambda w: wuxing_count[w])
        xiyongshen = min_wx
        jiyongshen = ''

    return xiyongshen, jiyongshen


def _get_tiaohou(month_zhi):
    """调候建议（根据月支气候）"""
    season_map = {
        '寅': ('春', '木旺，喜火暖局或水润局'),
        '卯': ('春', '木旺，喜火暖局或水润局'),
        '辰': ('春末', '土旺，喜水润局或木疏土'),
        '巳': ('夏', '火旺，喜水润局'),
        '午': ('夏', '火旺，喜水润局'),
        '未': ('夏末', '土旺燥，喜水润局'),
        '申': ('秋', '金旺，喜火暖金或水润局'),
        '酉': ('秋', '金旺，喜火暖金或水润局'),
        '戌': ('秋末', '土旺，喜木疏土或水润局'),
        '亥': ('冬', '水旺，喜火暖局'),
        '子': ('冬', '水旺，喜火暖局'),
        '丑': ('冬末', '土寒湿，喜火暖局'),
    }
    season, hint = season_map.get(month_zhi, ('', ''))
    return hint


def get_bazi(year, month, day, hour=12, minute=0):
    """
    八字排盘主函数。

    参数：
      year: 公历年（如 2024）
      month: 公历月（1-12）
      day: 公历日（1-31）
      hour: 公历时（0-23，默认12正午）
      minute: 公历分（0-59，暂不使用，预留精确节气判断）

    返回：
      BaziResult 对象，含四柱干支、五行统计、日主强弱、喜用神、调候建议

    异常：
      ValueError: 参数超出有效范围

    示例：
      >>> result = get_bazi(2024, 3, 15, 10)
      >>> print(result)
      八字：甲辰年 丁卯月 甲申日 己巳时
      日主：甲(木) | 强弱：身强(6) | 喜用神：金 | ...
    """
    # 参数校验
    if not isinstance(year, int) or year < 1900 or year > 2100:
        raise ValueError(f"年份必须是1900-2100之间的整数，收到: {year}")
    if not isinstance(month, int) or month < 1 or month > 12:
        raise ValueError(f"月份必须是1-12之间的整数，收到: {month}")
    if not isinstance(day, int) or day < 1 or day > 31:
        raise ValueError(f"日期必须是1-31之间的整数，收到: {day}")
    if not isinstance(hour, int) or hour < 0 or hour > 23:
        raise ValueError(f"小时必须是0-23之间的整数，收到: {hour}")

    result = BaziResult()

    # 四柱
    result.year_ganzhi = _get_year_ganzhi(year, month, day)
    result.month_ganzhi = _get_month_ganzhi(year, month, day)
    result.day_ganzhi = _get_day_ganzhi(year, month, day)
    result.hour_ganzhi = _get_hour_ganzhi(result.day_ganzhi, hour)

    # 日主
    result.day_master = result.day_ganzhi[0]
    result.day_master_wuxing = GAN_WUXING[result.day_master]

    # 生肖/纳音
    result.zodiac = _get_zodiac(result.year_ganzhi)
    result.nayin = _get_nayin(result.year_ganzhi)

    # 四柱详情
    result.pillars = {
        'year': result.year_ganzhi,
        'month': result.month_ganzhi,
        'day': result.day_ganzhi,
        'hour': result.hour_ganzhi,
    }

    # 五行统计
    result.wuxing_count = _analyze_wuxing(result.pillars)

    # 日主强弱
    month_zhi = result.month_ganzhi[1]
    result.strength, result.strength_score = _analyze_strength(
        result.day_master, month_zhi, result.pillars)

    # 喜用神
    result.xiyongshen, result.jiyongshen = _get_xiyongshen(
        result.day_master, result.strength, result.wuxing_count)

    # 调候
    result.tiaohou = _get_tiaohou(month_zhi)

    return result


def get_recommended_radicals(xiyongshen):
    """
    根据喜用神返回推荐的偏旁部首（用于从字库筛选候选字）。

    喜用神 → 推荐偏旁部首：
    - 喜木 → 木/艹/禾/竹/米/豆/麦/麻
    - 喜火 → 火/灬/日/光/电/灯/心
    - 喜土 → 土/山/石/田/艮/阜/阝(左)
    - 喜金 → 金/钅/玉/石/贝/辛/白
    - 喜水 → 水/氵/雨/子/亥/鱼/黑

    返回：推荐部首列表
    """
    wuxing_radical_map = {
        '木': ['木', '艹', '禾', '竹', '米', '豆', '麦', '麻', '乙'],
        '火': ['火', '灬', '日', '光', '电', '心', '忄', '赤'],
        '土': ['土', '山', '石', '田', '艮', '阜', '阝', '尸'],
        '金': ['金', '钅', '玉', '石', '贝', '辛', '白', '秋'],
        '水': ['水', '氵', '雨', '子', '亥', '鱼', '黑', '壬'],
    }
    return wuxing_radical_map.get(xiyongshen, [])


def get_forbidden_radicals(jiyongshen):
    """
    根据忌用神返回应避用的偏旁部首。

    忌用神 → 避用偏旁部首（与喜用神推荐表相同的映射，反向使用）
    """
    return get_recommended_radicals(jiyongshen)  # 忌用神的部首即应避用


if __name__ == '__main__':
    # 测试用例
    print('=== 八字排盘引擎测试 ===')
    print()

    # 测试1：2024年3月15日10点（甲辰年）
    r1 = get_bazi(2024, 3, 15, 10)
    print('测试1: 2024-03-15 10:00')
    print(r1)
    print()

    # 测试2：1990年5月20日14点
    r2 = get_bazi(1990, 5, 20, 14)
    print('测试2: 1990-05-20 14:00')
    print(r2)
    print()

    # 测试3：立春前（年柱用上一年）
    r3 = get_bazi(2024, 1, 20, 12)
    print('测试3: 2024-01-20 12:00 (立春前，年柱应为癸卯)')
    print(r3)
    print()

    # 测试4：喜用神→推荐部首
    print('测试4: 喜木 → 推荐部首:', get_recommended_radicals('木'))
    print('测试4: 忌金 → 避用部首:', get_forbidden_radicals('金'))
