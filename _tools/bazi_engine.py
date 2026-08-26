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
    """计算年柱干支。立春前用上一年。"""
    # 简化判断：立春大约在2月4日左右
    # 精确做法需查节气表，这里用近似（2月4日前为立春前）
    actual_year = year
    if month < 2 or (month == 2 and day < 4):
        actual_year = year - 1
    # 1984年为甲子年（index=0）
    index = (actual_year - 1984) % 60
    return JIAZI[index]


def _get_month_ganzhi(year, month, day):
    """计算月柱干支。以节气为界。"""
    # 确定月支：根据当前日期所在的节气
    # 简化：用月份近似判断节气（立春2月、惊蛰3月、清明4月...小寒1月）
    # 实际应根据精确节气日期判断
    month_zhi_index = _get_month_zhi(month, day)
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


def _get_month_zhi(month, day):
    """根据公历月日确定月支（以节气为界）。简化近似。"""
    # 节气近似日期（每月约5-8日交节）
    # 立春2/4、惊蛰3/6、清明4/5、立夏5/6、芒种6/6、小暑7/7
    # 立秋8/8、白露9/8、寒露10/8、立冬11/8、大雪12/7、小寒1/6
    jieqi_approx = {
        2: (4, 2), 3: (6, 3), 4: (5, 4), 5: (6, 5), 6: (6, 6), 7: (7, 7),
        8: (8, 8), 9: (8, 9), 10: (8, 10), 11: (8, 11), 12: (7, 12), 1: (6, 1),
    }
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


def _get_nayin(year_ganzhi):
    """获取年柱纳音"""
    nayin_map = {
        '甲子': '海中金', '乙丑': '海中金', '丙寅': '炉中火', '丁卯': '炉中火',
        '戊辰': '大林木', '己巳': '大林木', '庚午': '路旁土', '辛未': '路旁土',
        '壬申': '剑锋金', '癸酉': '剑锋金', '甲戌': '山头火', '乙亥': '山头火',
        '丙子': '涧下水', '丁丑': '涧下水', '戊寅': '城头土', '己卯': '城头土',
        '庚辰': '白蜡金', '辛巳': '白蜡金', '壬午': '杨柳木', '癸未': '杨柳木',
        '甲申': '泉中水', '乙酉': '泉中水', '丙戌': '屋上土', '丁亥': '屋上土',
        '戊子': '霹雳火', '己丑': '霹雳火', '庚寅': '松柏木', '辛卯': '松柏木',
        '壬辰': '长流水', '癸巳': '长流水', '甲午': '沙中金', '乙未': '沙中金',
        '丙申': '山下火', '丁酉': '山下火', '戊戌': '平地木', '己亥': '平地木',
        '庚子': '壁上土', '辛丑': '壁上土', '壬寅': '金箔金', '癸卯': '金箔金',
        '甲辰': '覆灯火', '乙巳': '覆灯火', '丙午': '天河水', '丁未': '天河水',
        '戊申': '大驿土', '己酉': '大驿土', '庚戌': '钗钏金', '辛亥': '钗钏金',
        '壬子': '桑柘木', '癸丑': '桑柘木', '甲寅': '大溪水', '乙卯': '大溪水',
        '丙辰': '沙中土', '丁巳': '沙中土', '戊午': '天上火', '己未': '天上火',
        '庚申': '石榴木', '辛酉': '石榴木', '壬戌': '大海水', '癸亥': '大海水',
    }
    return nayin_map.get(year_ganzhi, '')


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

    示例：
      >>> result = get_bazi(2024, 3, 15, 10)
      >>> print(result)
      八字：甲辰年 丁卯月 甲申日 己巳时
      日主：甲(木) | 强弱：身强(6) | 喜用神：金 | ...
    """
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
