from nltk import Tree


def find_all_starting_points(lines, num_of_lines):

    result = [0] * num_of_lines
    i = 0

    for count, line in enumerate(lines):
        if line[0] == '(':
            result[i] = count
            i = i + 1

    return result


def number_of_starting_lines(lines):

    num_of_lines = 0

    for line in lines:
        if line[0] == '(':
            num_of_lines += 1

    return num_of_lines


def extract_rules_from_tree(data):

    tree_str = Tree.fromstring(data)

    return tree_str.productions()

def process_grammar_rules (tree_rule):

        # Parsing The Resulting Grammar:
        # Change S to S1
        # Change '->' to space
        # Remove the words

        processed_rule = tree_rule.replace(" -> ", "     ")
        processed_rule = processed_rule.replace("S ", "S1 ")

        return processed_rule

def get_total_rules_count(grammar_rules, length):

    count = 0
    for i in range(0, length):
        rules = grammar_rules[i]
        for rule in enumerate(rules):
            count += 1

    return count

def read_tree_file(filename):
    with open(filename) as file:
        fileLines = file.readlines()
    return fileLines

def grammar_from_file(filename):
    fileLines = read_tree_file(filename)
    '''
    The starting points array lists the line where each tree begins
    - Go from the starting line to the next starting line
    1) concatenate each line to build the whole tree string
    2) extract the grammar rules
    3) process the grammar rules
    '''
    startingPoints = find_all_starting_points(fileLines, number_of_starting_lines(fileLines))

    numOfTrees = startingPoints.__len__()
    grammarRules = [''] * numOfTrees

    for treeIndex in range(0, numOfTrees):
        tree = ""
        start = startingPoints[treeIndex]

        # if last starting point then tree reads till end of file
        if treeIndex == numOfTrees - 1:
            stop = fileLines.__len__()
        else:
            stop = startingPoints[treeIndex + 1]

        for currentLineNum in range(start, stop):
            tree += fileLines[currentLineNum]

        grammarRules[treeIndex] = extract_rules_from_tree(tree)

    totalRulesCount = get_total_rules_count(grammarRules, numOfTrees)
    strGrammarRules = [''] * totalRulesCount

    ''' Need to cast into string format from nltk.production class'''
    x = 0
    for tree in range(0, numOfTrees):
        treeRules = grammarRules[tree]
        for rule in treeRules:
            strGrammarRules[x] = rule.unicode_repr()
            x += 1

    for i in range(0, totalRulesCount-1):
        text = strGrammarRules[i]
        strGrammarRules[i] = process_grammar_rules(text)

    grammar = [x for x in strGrammarRules if "'" not in x]
    terminals = [x for x in strGrammarRules if "'" in x]
    return grammar, terminals

if __name__ == "__main__":
    filename = "devset.trees"
    grammar, terminals = grammar_from_file(filename)

    # Write results to file
    with open('grammar_results1.txt', 'w') as file:
        for item in grammar:
            file.write("%s\n" % item)

    with open('terminal_grammar_results1.txt', 'w') as file:
        for item in terminals:
            file.write("%s\n" % item.replace("'", ''))

    print("parsed grammar rules written to grammar_results.txt")
