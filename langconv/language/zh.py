from ..language import Language, get_data_file_path

zh_cn = Language.from_json_files(
    'zh-cn',
    [get_data_file_path('zh/hans.json'), get_data_file_path('zh/CN.json')],
    ['zh-hans'],
)

zh_hk = Language.from_json_files(
    'zh-hk',
    [get_data_file_path('zh/hant.json'), get_data_file_path('zh/HK.json')],
    ['zh-hant', 'zh-TW'],
)

zh_tw = Language.from_json_files(
    'zh-tw',
    [get_data_file_path('zh/hant.json'), get_data_file_path('zh/TW.json')],
    ['zh-hant', 'zh-HK'],
)

__all__ = ['zh_cn', 'zh_hk', 'zh_tw']
