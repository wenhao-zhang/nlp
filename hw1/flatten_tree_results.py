def add_spaces(length):
    '''
    Inserts spaces to a string for formatting of Vocab output file
    '''
    spaces = " "
    for i in range(5 - length):
        spaces = spaces + " "
    return spaces

def split_rules(firt_symbol, atoms):
    """
    Splits a rule into an array of three token rules. ex: S1 NN NP VP -> ['S1 NN _NP','_NP NP VP']
    """
    first_symbol = "S1"
    rules = []
    subrules = [first_symbol, atoms[0]]
    for idx, item in enumerate(atoms):
        if item != atoms[0] and item != atoms[-1]:
            subrules.append(f'+{item}')
            subrules.append(item)
    subrules.append(atoms[-1])
    for i in range(0, len(subrules)-2, 2):
       rules.append(f'{subrules[i]}{add_spaces(len(subrules[i]))}{subrules[i+1]}   {subrules[i+2]}')
    return rules

def flatten_grammar(grammar):
    flattened_grammar = []

    for rule in grammar:
        rule = rule.split(" ")
        rule = [x for x in rule if x != '']
        if len(rule) > 0:
            first_symbol = rule[0]
            for item in rule[1:]:
                atoms = rule[1:]
                if len(atoms) > 2:
                    [flattened_grammar.append(split_rule) for split_rule in split_rules(first_symbol, atoms)]
                else:
                    flattened_grammar.append(f'{first_symbol}{add_spaces(len(first_symbol))}{item}')

    flattened_grammar.sort()
    return flattened_grammar

if __name__ == "__main__":
    grammar = []
    with open('grammar_results1.txt', 'r') as grammar_file:
        grammar = [line.strip() for line in grammar_file.readlines()]

    flattened_grammar = flatten_grammar(grammar)

    with open('flattened_grammar_results.txt', 'w') as output_file:
        for rule in flattened_grammar:
            output_file.write(f'{rule}\n')
