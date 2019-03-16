from score import score
from ngram import LM 
from score import extract_mappings
    
def histogramPrune(HT, beam_size):
    """
    Takes hypotheses from a beam search stage and keeps on the top `beam_size` hypotheses.
    """
    sorted_HT = sorted(HT, key=lambda ht: ht[1], reverse=True)  # Order by scores (index 1), descending.
    pruned_HT = sorted_HT[0:beam_size]  # Select the beam_size number of highest scored hypothesis.

    return pruned_HT

def checkExtLimits(phi_prime, ext_limits):
    counts = {}
    sequence = []
    extract_mappings(phi_prime, sequence)
    
    for mapping in sequence:
        if len(mapping) < 2 or mapping[0] is None:
            continue
        plaintext = mapping[0]
        if plaintext in counts:
            counts[plaintext] += 1
        else:
            counts[plaintext] = 1
        if counts[plaintext] > ext_limits:
            return False
        
    return True

def winner(HS):
    sequence = []
    top = sorted(HS, key=lambda x: x[1], reverse=True)
    if len(top) == 0:
        return []
    extract_mappings(top[0], sequence)
    return sequence

def beam_search(lm, vf, ve, ext_order, ext_limits, beam_size, cipher):
    HS = list()
    HT = list()
    HS.append((tuple(),0))
    cardinality = 0
    while cardinality < len(vf):
        f = ext_order[cardinality]
        for phi in HS:
            for e in ve:
                phi_prime = tuple([phi, (e,f)])
                if checkExtLimits(phi_prime, ext_limits):
                    HT.append((phi_prime, score(lm, phi_prime, cipher)))
        HT = histogramPrune(HT, beam_size)
        cardinality += 1
        HS = HT
        HT = list()
    return winner(HS)

lm = LM("data/6-gram-wiki-char.lm.bz2", n=6, verbose=True)