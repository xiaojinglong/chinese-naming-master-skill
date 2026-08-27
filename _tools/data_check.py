# -*- coding: utf-8 -*-
"""
数据完整性检查器（V3.3）

用途：启动时/CI 中校验所有数据源是否真正加载，防止
"路径写错→except 吞异常→数据静默为空"的灾难重演。

用法：
    python _tools/data_check.py            # 打印报告，失败返回非零退出码
    from data_check import check_data_integrity   # 程序内调用
"""
import sys
import os
import io

# Windows 控制台 UTF-8 输出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, '_tools'))


def _load_safely(name, loader):
    """安全加载：返回 (ok, detail)"""
    try:
        data = loader()
        ok = bool(data)
        size = len(data) if hasattr(data, '__len__') else 'n/a'
        return ok, f'{size} 项' if ok else '空'
    except Exception as e:
        return False, f'异常: {type(e).__name__}: {e}'


def check_data_integrity(verbose=True):
    """
    校验所有核心数据源。返回 (passed_count, total_count, failures)。
    failures = [(name, detail), ...]
    """
    checks = []

    # 1. 字库
    def load_hanzi():
        from name_generator import load_hanzi_db
        return load_hanzi_db('expanded')
    checks.append(('汉字字库 (expanded)', load_hanzi))

    # 2. 姓氏库
    def load_surnames():
        from name_generator import load_surnames
        return load_surnames()
    checks.append(('姓氏库', load_surnames))

    # 3. 五格数理表
    def load_wuge():
        import json
        p = os.path.join(BASE, '01-数据资料', '三才五格配置表', 'wuge_1to81.json')
        return json.load(open(p, encoding='utf-8'))['numbers']
    checks.append(('五格数理表 1-81', load_wuge))

    # 4. 三才配置表
    def load_sancai():
        import json
        p = os.path.join(BASE, '01-数据资料', '三才五格配置表', 'sancai_full.json')
        return json.load(open(p, encoding='utf-8'))['sancai']
    checks.append(('三才配置表 125 组', load_sancai))

    # 5. 谐音黑名单（关键：曾静默失效）
    def load_blacklist():
        from scoring_engine import _load_homophone_blacklist
        bl = _load_homophone_blacklist()
        return bl.get('bad_words', set())
    checks.append(('谐音黑名单 bad_words', load_blacklist))

    # 6. 声母韵母表
    def load_shengmu():
        from scoring_engine import _load_shengmu_yunmu
        return _load_shengmu_yunmu()
    checks.append(('声母韵母表', load_shengmu))

    # 7. 诗词意象库
    def load_shici():
        import json
        p = os.path.join(BASE, '03-文化资料', '诗词意象库.json')
        return json.load(open(p, encoding='utf-8'))['items']
    checks.append(('诗词意象库 78 条', load_shici))

    # 8. 成语典故库
    def load_chengyu():
        import json
        p = os.path.join(BASE, '03-文化资料', '成语典故库.json')
        return json.load(open(p, encoding='utf-8'))['items']
    checks.append(('成语典故库', load_chengyu))

    # 9. 俗气名库
    def load_tacky():
        from scoring_engine import load_data
        return load_data().get('tacky_names', set())
    checks.append(('俗气名库 (67 个)', load_tacky))

    # 10. 时代感词库
    def load_era():
        from scoring_engine import load_data
        return load_data().get('era', {})
    checks.append(('时代感词库', load_era))

    # 11. 通用规范汉字表（字库每个字应有 tgh_level）
    def load_tgh():
        from name_generator import load_hanzi_db
        h = load_hanzi_db('expanded')
        tagged = [c for c in h.values() if c.get('tgh_level') is not None]
        return tagged
    checks.append(('通规字表分级标注', load_tgh))

    failures = []
    passed = 0
    if verbose:
        print('=' * 56)
        print('数据完整性检查')
        print('=' * 56)
    for name, loader in checks:
        ok, detail = _load_safely(name, loader)
        mark = '✓' if ok else '✗'
        if verbose:
            print(f'  {mark} {name:<28} {detail}')
        if ok:
            passed += 1
        else:
            failures.append((name, detail))

    total = len(checks)
    if verbose:
        print('-' * 56)
        print(f'  结果: {passed}/{total} PASS' + ('' if passed == total else f'  ({total-passed} 项失败)'))
        print('=' * 56)
    return passed, total, failures


if __name__ == '__main__':
    passed, total, failures = check_data_integrity()
    sys.exit(0 if passed == total else 1)
