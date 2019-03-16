import json

def format_sentences(sentences):
    '''
    Remove all newlines from sentences
    '''
    formatted_sentences =[]
    for sentence in sentences:
        sentence.strip('\n')
        tmp_sentence = sentence.split(" ")
        tmp_sentence[-1].strip('\n')
        tmp_sentence[-1] = tmp_sentence[-1].split('\n')[0]
        formatted_sentences.append(tmp_sentence)
    return formatted_sentences

def is_not_last_word(word, sentence):
    '''
    Check if word is last word in the sentence
    '''
    return sentence.index(word) < len(sentence) - 1

def next_word(word, sentence):
    '''
    Returns next word in the sentence
    '''
    return sentence[sentence.index(word) + 1]

def count_suffix_words(word, sentences, probs):
    '''
    Counts the occurences of suffix words for a given word
    '''
    if word not in probs.keys():
        probs[word] = {}
    for sentence in sentences:
        if word in sentence and is_not_last_word(word, sentence):
            suffix_word = next_word(word, sentence)
            if suffix_word not in probs[word].keys():
                probs[word][suffix_word] = {'count': 1}
            else:
                probs[word][suffix_word]['count'] += 1
    return

def get_probs(probs):
    '''
    Calculate the probability of a suffix word. Format used is to total the counts for each suffix word following a
    given word then divides each suffix count by total
    '''
    for word in probs.keys():
        total = 0
        for suffix in probs[word].keys():
            total += probs[word][suffix]['count']
        for suffix in probs[word].keys():
            probs[word][suffix]['probability'] = probs[word][suffix]['count'] / total
    return

def generate_text_probabilities(allowed_words, sentences):
    probs = {}

    sentences = format_sentences(sentences)

    # count the suffixes
    for word in allowed_words:
        count_suffix_words(word.replace('\n',''), sentences, probs)

    get_probs(probs)
    return probs

if __name__ == "__main__":
    allowed_words = []
    sentences = []

    # gather allowed words and given sentences
    with open("hw1/allowed_words.txt", 'r') as allowed_words_file:
        [allowed_words.append(line.strip()) for line in allowed_words_file]
    with open("hw1/devset.txt", 'r') as devset_file:
        [sentences.append(line.strip()) for line in devset_file]
    with open("hw1/gutenberg_allowed_sentences.txt", 'r') as gutenberg_sentence_file:
        [sentences.append(line.strip()) for line in gutenberg_sentence_file]

    probs = generate_text_probabilities(allowed_words, sentences)

    #write output to file
    with open('hw1/full_suffix_word_probs.json', 'w+') as outfile:
        json.dump(probs, outfile)
