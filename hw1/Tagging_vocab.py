import nltk

def load_and_tag_words(filename):
    words = []
    with open(filename, 'r') as words_file:
        for line in words_file:
            words.append(line.strip())

    tags = []
    for word in words:
        text = nltk.word_tokenize(word)
        a = nltk.pos_tag(text)
        for item in a:
            tags.append(f'1    {item[1]} {item[0]}')

    tags.sort()
    return tags

if __name__ == "__main__":
    tags = load_and_tag_words('allowed_words.txt')
    with open('G_Vocab.gr', 'w') as vocab_file:
        for tag in tags:
            vocab_file.write(f'{tag}\n')
