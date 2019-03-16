 def ext_order_generate(cipher_vocab, cipher_text, n, weights):
 
    sequences = []
    sequences.append(("",0))

    candidates = []
    cardinality = 0
    while cardinality < len(cipher_vocab):
        for seq in sequences:
            for c in cipher_vocab:
                if not in_part_ord(seq, c):
                    new_candidate = (seq, c)
                    bit_string = generate_bit_string(new_candidate, cipher_text)
                    score = 0
                    for i in range(0,n):
                        ngram_span = get_ngram_span(bit_string, i+1)
                        score += weights[i]*len(ngram_span)
                    candidates.append((new_candidate, score))
            
        candidates = histogramPrune(candidates, 100)
        sequences = candidates
        candidates = []
        cardinality+=1
    return ord_winner(sequences)

 def ord_winner(HS):
    sequence = []
    top = sorted(HS, key=lambda x: x[1], reverse=True)
    if len(top) == 0:
        return []
    flatten_part_ord(top[0], sequence)
    return sequence

def in_part_ord(part_ord, symbol):
    if isinstance(part_ord[1], str):
        return in_part_ord(part_ord[0], symbol) or part_ord[1] == symbol
    if part_ord[0]:
        return in_part_ord(part_ord[0][0], symbol) or part_ord[0][1] == symbol
    else:
        return False;

def get_ngram_span(bit_string, n):
    return {i.span()[0]: i.span()[1] for i in re.finditer("o{" + str(n-1) + "," + str(n-1) + "}n|no{" + str(n-1) + "," + str(n-1) + "}", bit_string)}

def flatten_part_ord(part_ord, flattened):

    if part_ord:
        if isinstance(part_ord[len(part_ord)-1], str):
            flattened.append(part_ord[len(part_ord)-1])
        if isinstance(part_ord[0], tuple):
            return flatten_part_ord(part_ord[0],flattened)
    else:
        return flattened
        
def generate_bit_string(part_ord, cipher_text):

    bit_string = ""
    flattened = []

    flatten_part_ord(part_ord[0], flattened)
    new_symbol = part_ord[1]

    cipher_characters = []
    [cipher_characters.append(c) for c in cipher_text]

    for character in cipher_characters:
        if character == part_ord[1]:
            bit_string = bit_string + "n"
        elif character in flattened:
            bit_string = bit_string + "o"
        else:
            bit_string = bit_string + "."
    return bit_string
