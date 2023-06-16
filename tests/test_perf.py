import cProfile

from langconv.converter import LanguageConverter
from langconv.language.zh import zh_cn


def test_perf(benchmark):
    lc = LanguageConverter.from_language(zh_cn)
    with open('tests/zh_cn.txt', encoding='utf-8') as large_txt:
        content = large_txt.read() * 5
        benchmark(cProfile.runctx, 'lc.convert(content)', None, locals(), 'stats.prof')
