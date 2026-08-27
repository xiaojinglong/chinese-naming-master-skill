# -*- coding: utf-8 -*-
"""数据完整性测试"""
import sys
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, '_tools'))


def test_data_check_passes():
    """所有核心数据源必须加载成功（防止静默失效重演）"""
    from data_check import check_data_integrity
    passed, total, failures = check_data_integrity(verbose=False)
    assert passed == total, f'数据完整性失败: {failures}'


def test_blacklist_loaded():
    """谐音黑名单非空（V3.2 修复的 bug 的回归保护）"""
    from scoring_engine import _load_homophone_blacklist
    bl = _load_homophone_blacklist()
    assert len(bl['bad_words']) > 100, '谐音黑名单为空或过少'
    assert '沐谦' in bl['bad_words'], '沐谦（木钱谐音）应已入黑名单'


def test_tgh_level_tagged():
    """字库应标注通规字表等级"""
    from name_generator import load_hanzi_db
    h = load_hanzi_db('expanded')
    tagged = [c for c in h.values() if c.get('tgh_level') is not None]
    assert len(tagged) > 5000, '通规字表分级标注缺失过多'
    # 王应是一级字
    assert h.get('王', {}).get('tgh_level') == 1
