'''

This file is for rearranging the reversed vocab tags to have the proper format
<number> <tag> <string>

'''

def number_of_lines(lines):

    num_of_lines = 0

    for line in lines:
        if line[0] != '#':
            num_of_lines += 1

    return num_of_lines

filename = "Vocab.gr"
file = open(filename)
fileLines = file.readlines()

numOfLinesInFile = number_of_lines(fileLines)
vocab = [''] * numOfLinesInFile

for i, line in enumerate(fileLines):
    if line[0] != '#':
        strings = line.split(" ")
        #print(strings)
        vocab[i] = "1 " + strings[1].replace("\n","") + " " + strings[0] + "\n"
        print(vocab[i])


rearrangedVocabFile = open('vocab-rearranged.gr', 'w')
for item in vocab:
    rearrangedVocabFile.write(item)

rearrangedVocabFile.close()

print("parsed grammar rules written to vocab-rearranged.gr")
