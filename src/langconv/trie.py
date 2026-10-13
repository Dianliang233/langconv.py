from attrs import define, field

# NOTE: If the memory usage ever gets too large, we can use ints instead of strs for keys
# e.g. ord('我') = 25105, sys.getsizeof(25105) = 28, sys.getsizeof('我') = 76
# saves 48 bytes per CJK key


@define(slots=True)
class Node:
    key: str
    value: str
    full_key: str
    parent: 'Node | None' = field(default=None)
    children: dict[str, 'Node'] = field(factory=lambda: {})

    def add_child(self, child: 'Node', key: str) -> None:
        self.children[key] = child

    def get_child(self, key: str) -> 'Node | None':
        return self.children.get(key)


@define
class Trie:
    root: Node = field(factory=lambda: Node('', '', ''))

    def insert(self, key: str, value: str) -> None:
        node = self.root
        for char in key:
            child_node = node.children.get(char)
            if child_node is None:
                child_node = Node(char, '', node.full_key + char, node)
                node.add_child(child_node, char)
            node = child_node
        node.value = value

    def search(self, key: str) -> Node | None:
        node = self.root
        for char in key:
            child_node = node.get_child(char)
            if child_node is None:
                return None
            node = child_node
        return node

    def delete(self, key: str) -> None:
        node = self.search(key)
        if node is None:
            return
        while True:
            if node.parent is None:
                self.root = Node('', '', '')
                break
            node.parent.children.pop(node.key, None)
            if len(node.parent.children) == 0:
                break
            node = node.parent

    def longest_prefix(self, key: str) -> Node | None:
        node = self.root
        longest_match = None
        for char in key:
            child = node.children.get(char)
            if child is None:
                break
            elif child.value:
                longest_match = child
            node = child

        return longest_match

    def longest_prefix_at(self, text: str, start: int, stop: int) -> tuple[int, str] | None:
        """Find the longest prefix of ``text[start:stop]`` stored in the trie.

        ``stop`` is an exclusive upper bound and must not exceed ``len(text)``.
        Returns the exclusive end index and the matched value, or ``None`` when
        no prefix matches. Unlike :meth:`longest_prefix` this avoids allocating
        a slice of the input, which makes it suitable for hot loops.
        """
        children = self.root.children
        end = start
        best_end = -1
        best_value = ''
        while end < stop:
            child = children.get(text[end])
            if child is None:
                break
            end += 1
            children = child.children
            if child.value:
                best_end = end
                best_value = child.value
        if best_end == -1:
            return None
        return best_end, best_value

    def __contains__(self, key: str) -> bool:
        return self.search(key) is not None

    def __getitem__(self, key: str) -> str | None:
        res = self.search(key)
        return None if res is None else res.value

    def __setitem__(self, key: str, value: str) -> None:
        self.insert(key, value)

    def __delitem__(self, key: str) -> None:
        self.delete(key)

    @classmethod
    def from_dict(cls, dictionary: dict[str, str]) -> 'Trie':
        obj = cls()
        for key, value in dictionary.items():
            obj.insert(key, value)
        return obj
