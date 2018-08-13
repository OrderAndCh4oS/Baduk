base = './baduk'
ext = '.py'
files = [
    base + '/constants' + ext,
    base + '/enums' + ext,
    base + '/exceptions' + ext,
    base + '/commands/command_types' + ext,
    base + '/commands/chain_of_command' + ext,
    base + '/commands/add_to_adjacent_group_of_stones' + ext,
    base + '/commands/create_group_of_stones' + ext,
    base + '/commands/merge_with_adjacent_group_of_stones' + ext,
    base + '/commands/remove_dead_stones' + ext,
    base + '/stones/stone_link' + ext,
    base + '/stones/group_of_stones' + ext,
    base + '/stones/group_of_stones_collection' + ext,
    base + '/game/point' + ext,
    base + '/validations/move_validation' + ext,
    base + '/game/board_stack' + ext,
    base + '/game/board' + ext,
    base + '/game/player' + ext,
    base + '/game/turn' + ext,
    base + '/move_from_sgf' + ext,
    base + '/main' + ext,
]

copy = open("_current.py", "a")

for file in files:
    f = open(file, "r")
    for line in f:
        copy.write(line)
    f.close()
copy.close()
