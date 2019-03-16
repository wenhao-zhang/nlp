#!/usr/bin/env python
import optparse, sys, os, logging
from collections import defaultdict
from itertools import islice
from decimal import Decimal

def init(f_data, e_data):
    f_vocab = set()
    e_vocab = set()

    for s in islice(open(f_data), opts.num_sents):
        words = s.strip().split()
        for w in words:
            f_vocab.add(w)

    for s in islice(open(e_data), opts.num_sents):
        words = s.strip().split()
        for w in words:
            e_vocab.add(w)

    size_f_vocab = len(f_vocab)

    t_words = []
    t_probs = []

    for f_i in f_vocab:

        skip = False

        for e_j in e_vocab:
            if f_i == e_j:
                t_words.append(f_i + "-" + e_j)
                t_probs.append(1)
                skip = True
        
        if skip:
            continue

        for e_j in e_vocab:
            t_words.append(f_i + "-" + e_j)
            t_probs.append(1/size_f_vocab)

    return t_words, t_probs

def lookup(arr, val):
    return arr.index(val)

def extract_e(val):
    return val[val.index("-")+1:]

def train_model_one(t_words, t_probs, bitext):
    for i in range(5):
        e_words = []
        fe_words = []
        e_count = []
        fe_count = []
        for (n, (f, e)) in enumerate(bitext):
            for f_i in f:
                for e_j in e:
                    if e_j not in e_words:
                        e_words.append(e_j)
                        e_count.append(0)
                    if f_i + "-" + e_j not in fe_words:
                        fe_words.append(f_i + "-" + e_j)
                        fe_count.append(0)

        for (n, (f, e)) in enumerate(bitext):
            for f_i in f:
                Z = 0
                for e_j in e:
                    index = lookup(t_words, f_i + "-" + e_j)
                    Z += t_probs[index]
                for e_j in e:
                    index = lookup(t_words, f_i + "-" + e_j)
                    index_e = lookup(e_words, f_i + "-" + e_j)
                    index_ej = lookup(fe_words, e_j)
                    c = t_probs[index]/Z
                    fe_count[index_ej] += c
                    e_count[index_e] += c

        for fe in fe_words:
            index = lookup(t_words, fe)
            index_e = lookup(e_words, extract_e(index_ej))
            index_ej = lookup(fe_words, fe)
            t_probs[index] = fe_count[index_ej]/ e_count[index_e]
    
    return t_probs

def align_model_one(t_words, t_probs, bitext):

    alignment = []

    for (n, (f, e)) in enumerate(bitext):
        current_sentence = ""
        for (i, f_i) in enumerate(f): 
            bestp = 0
            bestj = 0
            for (j, e_j) in enumerate(e):
                index = lookup(t_words, f_i + "-" + e_j)
                if t_probs[index] > bestp:
                    bestp = t_probs[index]
                    bestj = j
            current_sentence += "%i-%i " % (i,bestj)
        alignment.append(current_sentence)

    return alignment

def print_alignment(alignments):
    for a in alignments:
        sys.stdout.write(a)
        sys.stdout.write("\n")

if __name__ == "__main__":
    optparser = optparse.OptionParser()
    optparser.add_option("-d", "--datadir", dest="datadir", default="data", help="data directory (default=data)")
    optparser.add_option("-p", "--prefix", dest="fileprefix", default="hansards", help="prefix of parallel data files (default=hansards)")
    optparser.add_option("-e", "--english", dest="english", default="en", help="suffix of English (target language) filename (default=en)")
    optparser.add_option("-f", "--french", dest="french", default="fr", help="suffix of French (source language) filename (default=fr)")
    optparser.add_option("-l", "--logfile", dest="logfile", default=None, help="filename for logging output")
    optparser.add_option("-t", "--threshold", dest="threshold", default=0.5, type="float", help="threshold for alignment (default=0.5)")
    optparser.add_option("-n", "--num_sentences", dest="num_sents", default=sys.maxsize, type="int", help="Number of sentences to use for training and alignment")
    (opts, _) = optparser.parse_args()
    f_data = "%s.%s" % (os.path.join(opts.datadir, opts.fileprefix), opts.french)
    e_data = "%s.%s" % (os.path.join(opts.datadir, opts.fileprefix), opts.english)

    if opts.logfile:
        logging.basicConfig(filename=opts.logfile, filemode='w', level=logging.INFO)

    bitext = [[sentence.strip().split() for sentence in pair] for pair in islice(zip(open(f_data), open(e_data)), opts.num_sents)]

    t_words, t_probs = init(f_data, e_data)
    t_probs = train_model_one(t_words, t_probs, bitext)
    model_one = align_model_one(t_words, t_probs, bitext)
    print_alignment(model_one)
