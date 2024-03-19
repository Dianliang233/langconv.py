import json

from langconv.trie import DoubleArrayTrie

# pyright: reportOptionalMemberAccess=false


def test_insert_and_search():
    trie = DoubleArrayTrie()
    trie.insert('apple', 'fruit')
    trie.insert('banana', 'fruit')
    trie.insert('carrot', 'vegetable')
    trie.insert('cat', 'animal')
    trie.insert('dog', 'animal')
    trie.insert('zebra', 'animal')
    assert trie.search('apple').value == 'fruit'
    assert trie.search('banana').value == 'fruit'
    assert trie.search('carrot').value == 'vegetable'
    assert trie.search('cat').value == 'animal'
    assert trie.search('dog').value == 'animal'
    assert trie.search('zebra').value == 'animal'
    assert trie.search('pear') is None
    assert trie.search('caterpillar') is None


def test_insert_and_search_single():
    trie = DoubleArrayTrie()
    trie.insert('a', 'single')
    assert trie.search('a').value == 'single'
    assert trie.search('b') is None


def test_insert_and_search_item():
    trie = DoubleArrayTrie()
    trie['apple'] = 'fruit'
    assert trie['apple'] == 'fruit'
    assert 'apple' in trie
    trie.delete('apple')
    assert trie['apple'] is None
    assert 'apple' not in trie


def test_insert_and_search_long():
    trie = DoubleArrayTrie()
    trie.insert('a' * 1000, 'long')
    assert trie.search('a' * 1000).value == 'long'
    assert trie.search('a' * 999 + 'b') is None


def test_insert_and_search_unicode():
    trie = DoubleArrayTrie()
    trie.insert('🍎', 'fruit')
    trie.insert('🍌', 'fruit')
    trie.insert('🥕', 'vegetable')
    trie.insert('🐱', 'animal')
    trie.insert('🐶', 'animal')
    trie.insert('🦓', 'animal')
    assert trie.search('🍎').value == 'fruit'
    assert trie.search('🍌').value == 'fruit'
    assert trie.search('🥕').value == 'vegetable'
    assert trie.search('🐱').value == 'animal'
    assert trie.search('🐶').value == 'animal'
    assert trie.search('🦓').value == 'animal'
    assert trie.search('🍐') is None
    assert trie.search('🐛') is None


def test_delete():
    trie = DoubleArrayTrie()
    trie.insert("apple", "fruit")
    trie.insert("banana", "fruit")
    trie.insert("carrot", "vegetable")

    trie.delete("banana")
    assert trie.search("banana") is None
    assert trie.search("apple").value == "fruit"
    assert trie.search("carrot").value == "vegetable"

    trie.delete("dog")
    assert trie.search("dog") is None
    assert trie.search("apple").value == "fruit"
    assert trie.search("carrot").value == "vegetable"

    trie.delete("apple")
    assert trie.search("apple") is None
    assert trie.search("carrot").value == "vegetable"

    trie.delete("carrot")
    assert trie.search("carrot") is None


def test_insert_overwrite():
    trie = DoubleArrayTrie()
    trie.insert("hello", "world")
    trie.search("hello").value = "new world"
    assert trie.search("hello").value == "new world"


def test_delete_nonexistent():
    trie = DoubleArrayTrie()
    trie.insert("hello", "world")
    trie.delete("goodbye")
    assert trie.search("hello").value == "world"


def test_from_dict():
    dictionary = {'hello': 'world', 'hey': 'there', 'hi': 'everyone'}
    trie = DoubleArrayTrie.from_dict(dictionary)
    assert trie.search('hello').value == 'world'
    assert trie.search('hey').value == 'there'
    assert trie.search('hi').value == 'everyone'
    assert trie.search('invalid') is None


def test_longest_prefix():
    trie = DoubleArrayTrie()
    trie.insert('hello', 'world')
    trie.insert('hey', 'there')
    assert trie.longest_prefix('hello world').value == 'world'
    assert trie.longest_prefix('hey there!').value == 'there'
    assert trie.longest_prefix('not in trie') is None


def test_load_large_json():
    with open('langconv/data/zh/hant.json', encoding='utf-8') as f:
        trie = DoubleArrayTrie.from_dict(json.load(f))
        assert trie.longest_prefix('维基百科繁简处理是中文维基百科的自动转换，目的是以电脑程序适应不同用字模式的差异。').value == '維'
