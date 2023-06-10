import json
import os
import re

from attrs import define

# from iso639.iso639 import Lang
from ..trie import DoubleArrayTrie

SECTION_LENGTH = 30 - 1 # We assume that the longest match will be 30 characters long to save mem
# Parse this:
# -{text}-
# -{ flag | variant1 : text1 ; variant2 : text2 ; }-
# -{ flag1 ; flag2 | from => variant : to ; }-


# class Lang(Lang):
#   @property
#   def full(self):
#     return f'{self.pt1}-{self.pt2b}-{self.pt2t}-{self.pt3}-{self.pt5}'

@define
class Language():
  '''Representation of a language.'''

  code: str
  rules: DoubleArrayTrie
  fallbacks: list[str]

  def convert(self, text: str) -> str:
    '''Converts the given text to this language.'''
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
