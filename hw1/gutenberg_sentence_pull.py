import nltk
from nltk.corpus import gutenberg
gutenberg_fields = gutenberg.fileids()
allowed_words = [] 

def allowed_sentence(allowed_words, sentence):
    for word in sentence:
        if word not in allowed_words:
            return False
    return True

with open("hw1/allowed_words.txt", 'r') as allowed_words_file:
    [allowed_words.append(line.strip()) for line in allowed_words_file]

output_sentences_list = [] 

for book in gutenberg_fields:
    sentences = gutenberg.sents(book)
    for sentence in sentences:
        if allowed_sentence(allowed_words, sentence) and ' '.join(sentence) not in output_sentences_list and '"' not in sentence:
            output_sentences_list.append(' '.join(sentence))

with open("hw1/gutenberg_allowed_sentences.txt", 'w+') as outfile:
    for sentence in output_sentences_list:
        outfile.write(sentence + '\n')
