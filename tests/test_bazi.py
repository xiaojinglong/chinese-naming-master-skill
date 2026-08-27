# -*- coding: utf-8 -*-
"""八字排盘测试"""
import sys
import os
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, '_tools'))


def _ganzhi_of(idx):
    GAN = '甲乙丙丁戊己庚辛壬癸'
    ZHI = '子丑寅卯辰巳午未申酉戌亥'
    return GAN[idx % 10] + ZHI[idx % 12]


def test_day_pillar_2024_03_15():
    """2024-03-15 日柱应为戊寅（独立推算核验）"""
    from bazi_engine import get_bazi
    REF = date(2000, 1, 1)  # 戊午 index 54
    idx = (54 + (date(2024, 3, 15) - REF).days) % 60
    expected = _ganzhi_of(idx)
    actual = get_bazi(2024, 3, 15, 10).day_ganzhi
    assert actual == expected == '戊寅', f'日柱 {actual} ≠ {expected}'


def test_day_pillar_2026_08_31():
    """2026-08-31 日柱应为丁丑"""
    from bazi_engine import get_bazi
    REF = date(2000, 1, 1)
    idx = (54 + (date(2026, 8, 31) - REF).days) % 60
    expected = _ganzhi_of(idx)
    actual = get_bazi(2026, 8, 31, 12).day_ganzhi
    assert actual == expected == '丁丑', f'日柱 {actual} ≠ {expected}'


def test_xiyongshen_present():
    """排盘应返回喜用神"""
    from bazi_engine import get_bazi
    b = get_bazi(2024, 3, 15, 10)
    assert b.xiyongshen, '喜用神为空'
    assert b.zodiac, '生肖为空'
