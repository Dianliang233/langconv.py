# langconv

langconv is a Python library for conversion between Traditional and Simplified Chinese and potentially more languages, inspired by [MediaWiki's LanguageConverter](https://www.mediawiki.org/wiki/Writing_systems/LanguageConverter).

## Install and usage

This library is guaranteed to be working in Python 3.12, and the minimum support target is Python 3.9. If langconv is not working in >= Python 3.9, especially the latest Python version, you may open an issue.

To install, use pip or any other package manager you prefer:

```sh
$ pip install langconv
```

This is a minimal working code example:

```py
from langconv.converter import LanguageConverter
from langconv.language.zh import zh_cn, zh_tw  # zh_hk also supported

lc_cn = LanguageConverter.from_language(zh_cn)  # target variant set to zh-cn
lc_tw = LanguageConverter.from_language(zh_tw)  # target variant set to zh-tw

print(lc_cn.convert('人人生而自由，在尊嚴和權利上一律平等。他們賦有理性和良心，並應以兄弟關係的精神相對待。'))
# Expected:          人人生而自由，在尊严和权利上一律平等。他们赋有理性和良心，并应以兄弟关系的精神相对待。
print(lc_tw.convert('人人生而自由，在尊严和权利上一律平等。他们赋有理性和良心，并应以兄弟关系的精神相对待。'))
# Expected:          人人生而自由，在尊嚴和權利上一律平等。他們賦有理性和良心，並應以兄弟關係的精神相對待。
```

## Documentation

Unfortunately, documentation is not available yet. In the meantime, you may look for some examples inside the [test folder](./tests/). Docstrings for functions are also available for your convenience.

## Design

langconv is designed to mock MediaWiki's LanguageConverter.php mechanism as much as feasible. One big diversions from LanguageConverter is that, to achieve fast conversion speed, langconv comes it own implementation of a [trie](https://en.wikipedia.org/wiki/Trie), instead of search-replacing strings. This makes conversion speed faster, although it comes at some costs e.g. memory cost.

langconv ships with its own set of conversion tables to power Traditional (including Taiwan and Hong Kong variants) and Simplified (including China variant) Chinese conversion. These conversion tables are copied from MediaWiki and they are battle-tested from extensive use on wikis including Chinese Wikipedia and hundreds of Chinese MediaWiki sites. You can learn more about its [licensing here](./langconv/data/zh/LICENSE.md). You may also bring your own table, and it should be fairly straightforward do so.

langconv supports MediaWiki [special conversion syntax](https://www.mediawiki.org/wiki/Writing_systems/Syntax/zh) for more versatile, advanced conversion result. However, not the full set of MediaWiki conversion syntax is available yet. You may file an issue for unsupported syntax.

## Comparison

Currently, the two most commonly used Chinese variant conversion systems are MediaWiki's LanguageConverter, powering Chinese Wikipedia, and OpenCC (Open Chinese Convert). All conversion libraries have endeavored on one thing, that is making conversion result more reliable and accurate. However, this task is not easy, for:

- Simplified Chinese combined multiple characters into one, and this would require some sort of context recognition to properly convert them.
- Because of the many years of geographical, political, and, most importantly, culture division in the last century, many terms the variants chose were different, and that has stuck with us since.

If you compare MediaWiki and OpenCC results, honestly, they are good enough. But they still get things wrong. That's why Wikipedia figured out that granular control, including specified conversion table on topical, page and word level is necessary to give a perfect output. This library, by copying MediaWiki's approach, is about offering perfect conversion results (as long as you want to put more work into it). These are some use cases I recommend:

- Generic Simplified-Traditional conversion
- Mocking MediaWiki conversion behavior and syntax, without actually running a real MediaWiki(the original use case)
- Use cases where a perfect conversion result with no compromise is needed, and you don't mind a little bit of manual work to ensure this (e.g. on a company website)

## To-Do

- [ ] Option to opt-out MediaWiki conversion syntax entirely.
- [ ] Performance improvements.
- [ ] Full support for MediaWiki conversion syntax
- [ ] Support for NoteTA group conversion
