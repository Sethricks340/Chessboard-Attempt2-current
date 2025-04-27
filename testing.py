import os

def next_three_chars(char):
    return [chr(ord(char) + i) for i in range(1, 4)]

def get_mock_moves_tree(letter, depth):
    mock_moves = {}
    leaf_list = []
    depth -= 1
    next_three = next_three_chars(letter)
    for char in next_three:
        if depth > 0: mock_moves[char] = get_mock_moves_tree(char, depth)
        else: leaf_list.append(char)
    if leaf_list: return leaf_list
    else: return mock_moves

def clear_screen():
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # macOS/Linux
        os.system('clear')

def main():
    # print_tree(get_mock_moves_tree("a", 1))
    print_tree(get_mock_moves_tree("a", 2))
    # print_tree(get_mock_moves_tree("a", 3))
    # print_tree(get_mock_moves_tree("a", 4))
    # print_tree(get_mock_moves_tree("a", 5))
    # print(get_mock_moves_tree("a", 5))
    # print(get_mock_moves_tree("a", 6))
    # print(get_mock_moves_tree("a", 14)) ##around 14 is where it starts to get large, 15 won't even load. Need alpha-beta pruning in the real thing!!

def print_tree(tree, indent=0, parent_has_more=False):
    if isinstance(tree, dict):
        keys = list(tree.keys())
        for i, key in enumerate(keys):
            is_last = (i == len(keys) - 1)
            connector = '└─ ' if is_last else '├─ '
            print(('│  ' if parent_has_more else '   ') * indent + connector + str(key))
            print_tree(tree[key], indent + 1, not is_last)
    elif isinstance(tree, list):
        for i, item in enumerate(tree):
            is_last = (i == len(tree) - 1)
            connector = '└─ ' if is_last else '├─ '
            print(('│  ' if parent_has_more else '   ') * indent + connector + str(item))

if __name__ == "__main__":
    main()