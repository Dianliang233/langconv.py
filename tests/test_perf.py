import cProfile
from typing import Callable, ParamSpec, Protocol

import pytest

from langconv.converter import LanguageConverter
from langconv.language.zh import zh_cn

P = ParamSpec('P')


class Benchmark(Protocol):
    def __call__(self, func: Callable[P, object], *args: P.args, **kwargs: P.kwargs): ...


@pytest.mark.slow
def test_perf(benchmark: Benchmark):
    lc = LanguageConverter.from_language(zh_cn)
    with open('tests/zh_cn.txt', encoding='utf-8') as large_txt:
        content = large_txt.read() * 5
        benchmark(cProfile.runctx, 'lc.convert(content)', {}, locals(), 'stats.prof')
