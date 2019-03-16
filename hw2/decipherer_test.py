from collections import defaultdict, Counter
import collections
import pprint
import math
import bz2
from score import score
from ext_limits import check_ext_limits
from ngram import LM 
from score import extract_mappings
import progressbar   

pp = pprint.PrettyPrinter(width=45, compact=True)

def read_file(filename):
    if filename[-4:] == ".bz2":
        with bz2.open(filename, 'rt') as f:
            content = f.read()
            f.close()
    else:
        with open(filename, 'r') as f:
            content = f.read()
            f.close()
    return content

cipher = read_file("data/cipher.txt")
# print(cipher)

def get_statistics(content, cipher=True):
    stats = {}
    content = list(content)
    split_content = [x for x in content if x != '\n' and x!=' ']
    length = len(split_content)
    symbols = set(split_content)
    uniq_sym = len(list(symbols))
    freq = collections.Counter(split_content)
    rel_freq = {}
    for sym, frequency in freq.items():
        rel_freq[sym] = (frequency/length)*100
        
    if cipher:
        stats = {'content':split_content, 'length':length, 'vocab':list(symbols), 'vocab_length':uniq_sym, 'frequencies':freq, 'relative_freq':rel_freq}
    else:
        stats = {'length':length, 'vocab':list(symbols), 'vocab_length':uniq_sym, 'frequencies':freq, 'relative_freq':rel_freq}
    return stats

cipher_desc = get_statistics(cipher, cipher=True)

plaintxt = read_file("data/default.wiki.txt.bz2")
plaintxt_desc = get_statistics(plaintxt, cipher=False)

"""
default : frequency matching heuristic

Notice how the candidate mappings, a.k.a hypotheses, are first scored with a measure of quality and, 
then, the best scoring hypothesis is chosen as the winner. 

The plaintext letters from the winner are then mapped to the respective ciphertext symbols.
"""

def find_mappings(ciphertext, plaintext):
    mappings = defaultdict(dict)
    hypotheses = defaultdict(dict)
    # calculate alignment scores
    for symbol in ciphertext['vocab']:
        for letter in plaintext['vocab']:
            hypotheses[symbol][letter] = abs(math.log((ciphertext['relative_freq'][symbol]/plaintext['relative_freq'][letter])))
    
    # find winner
    for sym in hypotheses.keys():
        #mappings[sym] = min(lemma_alignment[sym], key=lemma_alignment[sym].get)
        winner = sorted(hypotheses[sym].items(), key=lambda kv: kv[1])
        mappings[sym] = winner[1][0]
    
    return mappings

from ngram import LM


def extract_mappings(hypo, mappings):
    """
    Flattens and collects mappings from the partial hypothesis into a list
    """
    if hypo:
        if isinstance(hypo[len(hypo)-1], tuple):
            mappings.append(hypo[len(hypo)-1])
        if isinstance(hypo[0], tuple):
            return extract_mappings(hypo[0],mappings)
    else:
        return mappings

def match_symbols(phi_prime, cipher):
    """
    Matches cipher symbols to partial hypothesis mappings and generates a partially deciphered string as well as
    a bitstring indicating the locations of the deciphered symbols in the string. 

    eg.
        sequence = (('a',"A"), ('e', "E"))
        cipher = "GRAEME"

        return "__a_e_e" , "..o.o.o" 
    """
    bitString = ""
    mappings = {} 
    sequence = []
    extract_mappings(phi_prime, sequence)
    for item in sequence: 
        if item[1] not in mappings.keys():
            mappings[item[1]] = item[0]

    cipher_characters = []
    [cipher_characters.append(c) for c in cipher]
    plaintext = ""
    for character in cipher_characters:
        if character in mappings.keys():
            bitString = bitString + "o"
            plaintext = plaintext + mappings[character]
        else:
            bitString = bitString + "."
            plaintext = plaintext +"_"

    return (plaintext, bitString)

def histogramPrune(HT, beam_size):

    sorted_HT = sorted(HT, key=lambda ht: ht[1], reverse=True)  # Order by scores (index 1), descending.
    pruned_HT = sorted_HT[0:beam_size]  # Select the beam_size number of highest scored hypothesis.

    return pruned_HT

def winner(HS):
    sequence = []
    top = sorted(HS, key=lambda x: x[1], reverse=True)[0]
    extract_mappings(top, sequence)
    return sequence

def beam_search(lm, vf, ve, ext_order, ext_limits, beam_size, cipher):
    bar = progressbar.ProgressBar(maxval=20, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start(54)
    HS = list()
    HT = list()
    HS.append((tuple(),0))
    cardinality = 0
    while cardinality < len(vf):
        f = ext_order[cardinality]
        for phi in HS:
            for e in ve:
                phi_prime = tuple([phi, (e,f)])
                if check_ext_limits(phi_prime, ext_limits):
                    HT.append((phi_prime, score(lm, phi_prime, cipher)))
        HT = histogramPrune(HT, beam_size)
        cardinality += 1
        HS = HT
        HT = list()
        bar.update(cardinality)
    bar.finish()
    return winner(HS)

def decipher(sequence, cipher):
    plaintext = ""
    bitString =""
    mappings = {} 
    for item in sequence: 
        if item[1] not in mappings.keys():
            mappings[item[1]] = item[0]

    cipher_characters = []
    [cipher_characters.append(c) for c in cipher]
    plaintext = ""
    for character in cipher_characters:
        if character in mappings.keys():
            bitString = bitString + "o"
            plaintext = plaintext + mappings[character]
        else:
            bitString = bitString + "."
            plaintext = plaintext +"_"

    return (plaintext, bitString)


ex_order = [i[0] for i in cipher_desc['frequencies'].most_common(len(cipher_desc['frequencies'])) ]
lm = LM("data/6-gram-wiki-char.lm.bz2", n=6, verbose=True)
win = beam_search(lm, cipher_desc['vocab'], plaintxt_desc['vocab'], ex_order, 6, 5000, cipher_desc['content'])
print(win)
decipherment, decrypted_bitstring = decipher(win, cipher_desc['content'])
print(decipherment)
# #################################################################################################
# """
# ATTENTION!
# For grading purposes only. Don't bundle with the assignment. 
# Make sure '_ref.txt' is removed from the 'data' directory before publishing.
# """

def read_gold(gold_file):
    with open(gold_file) as f:
        gold = f.read()
    f.close()
    gold = list(gold.strip())
    return gold

def symbol_error_rate(dec, _gold):
    gold = read_gold(_gold)
    correct = 0
    if len(gold) == len(dec):
        for (d,g) in zip(dec, gold):
            if d==g:
                correct += 1
    wrong = len(gold)-correct
    error = wrong/len(gold)
    
    return error
    
# gold decipherment
gold_file = "data/_ref.txt"
ser = symbol_error_rate(decipherment, gold_file)
print('Error: ', ser*100, 'Accuracy: ', (1-ser)*100)
# # ##################################################################################################