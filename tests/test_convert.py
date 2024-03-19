from langconv.converter import LanguageConverter
from langconv.language.zh import zh_cn  # , zh_hk, zh_tw


def test_convert_custom_rules():
    lc = LanguageConverter.from_language(zh_cn)
    assert lc.convert('-{H|電腦程式=>zh-cn:电脑程序;}-中文維基百科繁簡處理是中文維基百科的自動轉換，目的是以電腦程式適應不同用字模式的差異。') \
        == '中文维基百科繁简处理是中文维基百科的自动转换，目的是以电脑程序适应不同用字模式的差异。'
    assert lc.convert('中文維基百科繁簡處理是中文維基百科的自動轉換，目的是以-{A|zh-hant: 電腦程式; zh-hans: 电脑程序;}-適應不同用字模式的差異。電腦程式') \
        == '中文维基百科繁简处理是中文维基百科的自动转换，目的是以电脑程序适应不同用字模式的差异。电脑程序'
    assert lc.convert('中文維基百科繁簡處理是中文維基百科的自動轉換，目的是以-{zh-hant: 電腦程式; zh-sg: 电脑程序;}-適應不同用字模式的差異。電腦程式') \
        == '中文维基百科繁简处理是中文维基百科的自动转换，目的是以适应不同用字模式的差异。计算机程序'
    assert lc.convert('中文維基百科繁簡處理是中文維基百科的自動轉換，目的是以-{zh-hant:電腦程式;zh-sg:电脑程序;}-適應不同用字模式的差異。電腦程式') \
        == '中文维基百科繁简处理是中文维基百科的自动转换，目的是以适应不同用字模式的差异。计算机程序'
    assert not lc.convert('-{T|電腦程式=>zh-cn:电脑程序;}-')
    assert lc.convert('-{中文維基百科繁簡處理是中文維基百科的自動轉換，目的是以電腦程式適應不同用字模式的差異。電腦程式}-') \
        == '中文維基百科繁簡處理是中文維基百科的自動轉換，目的是以電腦程式適應不同用字模式的差異。電腦程式'


def test_convert_empty_string():
    lc = LanguageConverter.from_language(zh_cn)
    assert not lc.convert('')  # == ''


def test_convert_special_characters():
    lc = LanguageConverter.from_language(zh_cn)
    assert lc.convert('-') == '-'
    assert lc.convert(' ') == ' '
