import collections


def add_spaces(length):
    '''
    Inserts spaces to a string for formatting of Vocab output file
    '''
    spaces = " "
    for i in range(5 - length):
        spaces = spaces + " "
    return spaces

def count_rules(rules):
    counter=collections.Counter(rules)

    rules = counter.keys()

    return [(f'{counter[key]}{add_spaces(len(str(counter[key])))}{key}') for idx, key in enumerate(rules)]

if __name__ == "__main__":
    rules = []
    with open('flattened_grammar_results.txt', 'r') as parsed_tree_file:
        rules = [(line[:len(line)-1]) for line in parsed_tree_file.readlines()]

    counted_rules = count_rules(rules)
    with open('flattened_grammar_count.txt', 'w+') as count_file:
        for rule in counted_rules:
            count_file.write(f'{rule}\n')
