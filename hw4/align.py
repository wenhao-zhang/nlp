#!/usr/bin/env python
import sys, os, logging
from collections import defaultdict
from itertools import islice
import optparse
import random

def loadData(f_data, e_data, num_sents):
  bitext = [[sentence.strip().split() for sentence in pair] for pair in islice(zip(open(f_data), open(e_data)), num_sents)]
  f_vocab = set()
  e_vocab = set()

  for s in islice(open(f_data), num_sents):
      words = s.strip().split()
      for w in words:
          f_vocab.add(w)

  for s in islice(open(e_data), num_sents):
      words = s.strip().split()
      for w in words:
          e_vocab.add(w)

  return bitext, f_vocab, e_vocab


def train_model_one(bitext, t, lookup):
    for i in range(5):
        e_count = defaultdict(int)
        fe_count = defaultdict(lambda: defaultdict(int))
        for (n, (f, e)) in enumerate(bitext):
            e = ["NULL"] + e
            for (i, f_i) in enumerate(f):
                Z = 0
                for (j, e_j) in enumerate(e):
                    Z += lookup(f_i, e_j)
                for (j, e_j) in enumerate(e):
                    c = lookup(f_i, e_j)/Z
                    fe_count[f_i][e_j] += c
                    e_count[e_j] += c
        for f_i,e_is in fe_count.items():
            for e_i, value in e_is.items():
                t[f_i][e_i] = value/ e_count[e_i]
    return t

def align_model_one(bitext, t, lookup):

    alignment = []

    for (n, (f, e)) in enumerate(bitext):
        current_sentence = ""
        for (i, f_i) in enumerate(f): 
            bestp = t_lookup(f_i, "NULL")
            bestj = -1
            for (j, e_j) in enumerate(e):
                prob = lookup(f_i, e_j)
                if prob > bestp:
                    bestp = prob
                    bestj = j 
            if bestj != -1:
                current_sentence += "%i-%i " % (i ,bestj)
        alignment.append(current_sentence)

    return alignment

def train_model_two(bitext, t, a, t_lookup, a_lookup):
    
    for iteration in range(5):
        e_count = defaultdict(int)
        fe_count = defaultdict(lambda: defaultdict(int))
        ijlm_count = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))
        ilm_count = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        for (n, (f, e)) in enumerate(bitext):
            f_null = ["PLACE HOLDER"] + f
            e_null = ["NULL"] + e 
            l = len(f)
            m = len(e)
            for i in range(1, l + 1):
                Z = 0
                f_i = f_null[i]
                for j in range(0, m + 1):
                    e_j = e_null[j]
                    Z += t_lookup(f_i, e_j)*a_lookup(i,j,len(f),len(e))
                for j in range(0, m + 1):
                    e_j = e_null[j]
                    c = (t_lookup(f_i, e_j)*a_lookup(i,j,len(f),len(e)))/Z
                    fe_count[f_i][e_j] += c
                    e_count[e_j] += c
                    ijlm_count[i][j][len(f)][len(e)] += c
                    ilm_count[i][len(f)][len(e)] += c
        
        for f_i,e_is in fe_count.items():
            for e_j, value in e_is.items():
                t[f_i][e_j] = value/ e_count[e_j]
        
        for i, js in ijlm_count.items():
            for j,ls in js.items():
                for l, ms in ls.items():
                    for m, value in ms.items():
                        a[i][j][l][m] = value/ilm_count[i][l][m]
    return t,a

def align_model_two(bitext, t, a, t_lookup, a_lookup):
    alignment = []

    for (n, (f, e)) in enumerate(bitext):
        current_sentence = ""
        l = len(f)
        m = len(e)
        for (i, f_i) in enumerate(f): 
            bestp = t_lookup(f_i, "NULL") * a_lookup(i + 1, 0, l, m)
            bestj = -1
            for (j, e_j) in enumerate(e):
                prob = t_lookup(f_i, e_j) * a_lookup(i + 1,j + 1,l,m)
                if prob > bestp:
                    bestp = prob
                    bestj = j
            if bestj != -1:
                current_sentence += "%i-%i " % (i ,bestj)
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
    optparser.add_option("-m", "--model", dest="model", default = "m2", help="m1 for model 1 and m2 for model 2")
    (opts, _) = optparser.parse_args()

    f_data = "%s.%s" % (os.path.join(opts.datadir, opts.fileprefix), opts.french)
    e_data = "%s.%s" % (os.path.join(opts.datadir, opts.fileprefix), opts.english)

    if opts.logfile:
        logging.basicConfig(filename=opts.logfile, filemode='w', level=logging.INFO)

    bitext, f_vocab, e_vocab = loadData(f_data, e_data, opts.num_sents)

    size_f_vocab = len(f_vocab)

    def t_lookup(f_i, e_j):
        if f_i in t:
            if e_j in t[f_i]:
                return t[f_i][e_j]
        return 1 / size_f_vocab

    def a_lookup(i,j,l,m):
        if i in a:
            if j in a[i]:
                if l in a[i][j]:
                    if m in a[i][j][l]:
                        return a[i][j][l][m]
        return 1/(m+1)

    t = defaultdict(lambda: defaultdict(int))

    model_one__trained_t = train_model_one(bitext, t, t_lookup)

    if opts.model == "m1":
        alignments = align_model_one(bitext, model_one__trained_t, t_lookup)
        print_alignment(alignments)
        sys.exit()

    a = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))

    model_two_trained_t, model_two_trained_a = train_model_two(bitext, model_one__trained_t, a, t_lookup, a_lookup)
    
    if opts.model == "m2":
        alignments = align_model_two(bitext, model_two_trained_t, model_two_trained_a, t_lookup, a_lookup)
        print_alignment(alignments)
        sys.exit()
