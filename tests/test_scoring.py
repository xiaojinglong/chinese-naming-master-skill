# -*- coding: utf-8 -*-
"""评分引擎测试"""
import sys
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, '_tools'))


def _score(name, surname='陈', xiyongshen='水'):
    import name_generator as ng
    from scoring_engine import score_name, load_data
    data = load_data()
    hanzi_map = data['hanzi_map']
    surname_map = ng.load_surnames()
    lit_map = ng.load_literature_map()
    wg = ng.calc_wuge(surname, name, hanzi_map, surname_map)
    return score_name(name, surname, data, xiyongshen=xiyongshen, zodiac='马',
                      wuge_numbers=wg['wuge_numbers'], sancai_wuxing=wg['sancai_wuxing'],
                      literature_map=lit_map, surname_chars=[surname], gender='male')


def test_good_name_scores_high():
    """好名字应得高分"""
    r = _score('沐泽', '李', '水')
    assert r['total_score'] >= 85, f'李沐泽应≥85，实得{r["total_score"]}'


def test_tacky_name_rejected():
    """俗气名应被乘法扣分淘汰"""
    r = _score('子涵', '陈', '水')
    assert r['total_score'] < 30, f'陈子涵应<30，实得{r["total_score"]}'
    assert r['scores']['penalty'] < 1.0, '陈子涵应有乘法扣分'


def test_homophone_blacklist_rejected():
    """谐音黑名单（沐谦=木钱）应被淘汰"""
    r = _score('沐谦', '陈', '水')
    assert r['total_score'] < 20, f'陈沐谦应<20，实得{r["total_score"]}'
    assert r['scores']['penalty'] < 0.1


def test_wuge_xiong_rejected():
    """五格凶数名字应被压低（陈景行 总格34大凶）"""
    r = _score('景行', '陈', '水')
    assert r['total_score'] < 50, f'陈景行应<50，实得{r["total_score"]}'


def test_six_dimensions_present():
    """评分应含 V3.1 六维分数"""
    r = _score('沐泽', '李', '水')
    scores = r['scores']
    for key in ['wuge_shuli', 'yinyun', 'yiyi', 'zixing', 'modern_sense', 'wuxing_buyi']:
        assert key in scores, f'缺维度 {key}'
