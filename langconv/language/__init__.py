import json
import os

from attr import field
from attrs import define

# from iso639.iso639 import Lang
from langconv.trie import Trie


@define
class Language:
    """Representation of a language."""

    code: str = field(converter=str.lower)
    rules: Trie
    fallbacks: list[str]

    @classmethod
    def from_json_files(cls, code: str, files: list[str], fallbacks: list[str]):
        content: dict[str, str] = {}
        for file in files:
            with open(file, encoding='utf-8') as f:
                content = content | json.load(f)
        return cls(code, Trie.from_dict(content), fallbacks)


def get_data_file_path(filename: str) -> str:
    """Gets the path to the given data file."""
    return os.path.join(os.path.dirname(__file__), '../data', filename)


__all__ = ['Language', 'get_data_file_path']
