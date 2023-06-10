from languageconverter.language.zh import zh_cn  # , zh_hk, zh_tw


def test_zh_cn():
  assert zh_cn.convert('中文維基百科繁簡處理是中文維基百科的自動轉換，目的是以電腦程式適應不同用字模式的差異。') \
    == '中文维基百科繁简处理是中文维基百科的自动转换，目的是以电脑程序适应不同用字模式的差异。'
