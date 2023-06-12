class Node:
    def __init__(self, key: str, value: str, parent: 'Node | None' = None):
        self.key = key
        self.parent = parent
        self.value = value
        self.children: dict[str, 'Node'] = {}

    def add_child(self, child: 'Node', key: str) -> None:
        self.children[key] = child

    def get_child(self, key: str) -> 'Node | None':
        return self.children.get(key)

    def get_full_key(self) -> str:
        node = self
        key = ''
        while node is not None:
            key = node.key + key
            node = node.parent
        return key

    def __repr__(self) -> str:
        return f'Node(key={self.key}, value={self.value}, children={self.children})'


class DoubleArrayTrie:
    def __init__(self):
        self.root = Node('', '')

    def insert(self, key: str, value: str) -> None:
        node = self.root
        for char in key:
            child_node = node.get_child(char)
            if child_node is None:
                child_node = Node(char, '', node)
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
        node.value = ''
        while node is not None and (not hasattr(node, 'children') or len(node.children) == 0):
            parent = node.parent
            if parent is None:
                self.root = Node('', '')
                break
            parent.children.pop(node.key, None)
            node = parent
            if hasattr(node, 'children') and len(node.children) > 0:
                break
            node.parent.children.pop(node.key, None)
            node = node.parent

    def longest_prefix(self, key: str) -> Node | None:
        node = self.root
        longest_match = None
        for char in key:
            child_node = node.get_child(char)
            if child_node is None or not key.startswith(child_node.get_full_key()):
                break
            node = child_node
            longest_match = node
        while longest_match is not None and not longest_match.value:
            longest_match = longest_match.parent
        return longest_match

    @classmethod
    def from_dict(cls, dictionary: dict[str, str]) -> 'DoubleArrayTrie':
        obj = cls()
        for key, value in dictionary.items():
            obj.insert(key, value)
        return obj
