import json
import os
import re
from enum import Enum

from attrs import define

# from iso639.iso639 import Lang
from ..trie import DoubleArrayTrie

SECTION_LENGTH = 30 - 1
# We assume that the longest match will be 30 characters long to save mem
# Parse this:
# -{text}-
# -{ flag | variant1 : text1 ; variant2 : text2 ; }-
# -{ flag1 ; flag2 | from => variant : to ; }-
# the spaces between components are optional

FLAG_PATTERN = re.compile(r'-{\s*(?P<flag>.*)\s*\|\s*(.*)\s*}-')


@define
class LanguageConverterMarkup():
    class Flag(Enum):
        HIDDEN = 'H'
        COPY = 'A'
        REMOVE = '-'
        TITLE = 'T'
        DESCRIPTION = 'D'
        RAW = 'R'
        SHOW = 'S'
        SPECIAL_DELIMITER = ';'

    flags: list[Flag]


@define
class Language():
    '''Representation of a language.'''

    code: str
    rules: DoubleArrayTrie
    fallbacks: list[str]

    def convert(self, text: str, *, sequential_global: bool = False, avoid_html_code: bool = False) -> str:
        '''Converts the given text to this language.

        :param text: The text to convert.
        :param sequential_global: Control whether global conversion rules are parsed and added at initialization or at where it first appears.
        :param ignore_html: Whether to ignore "code" HTML tags (<pre>, <code> and <script>).
        '''

        if text.find(r'-{A') or text.find(r'-{H') or text.find(r'-{-'):
            pass
            # TODO: complete this

        output: list[str] = []
        i = 0
        while i < len(text):
            match = self.rules.longest_prefix(text[i:i + SECTION_LENGTH])
            if match:
                output += match.value
                i += len(match.get_full_key())
            else:
                output.append(text[i])
                i += 1
        return ''.join(output)

    @classmethod
    def from_json_files(cls, code: str, files: list[str], fallbacks: list[str]):
        content: dict[str, str] = {}
        for file in files:
            with open(file, encoding='utf-8') as f:
                content = content | json.load(f)
        return cls(code, DoubleArrayTrie.from_dict(content), fallbacks)


def get_data_file_path(filename: str) -> str:
    '''Gets the path to the given data file.'''
    return os.path.join(os.path.dirname(__file__), '../data', filename)


__all__ = ['Language', 'get_data_file_path']
