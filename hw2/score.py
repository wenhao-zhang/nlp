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

def score(lm, phi_prime, cipher_txt):
    """
    Uses the ngram model score_bitsting function to return a log prob score of the phi_prime hypothesis and cipher_txt
    """
    hypothesis_string, bitString = match_symbols(phi_prime, cipher_txt)
    return lm.score_bitstring(hypothesis_string, bitString)

def score_nlm(phi_prime, cipher_txt):

    return