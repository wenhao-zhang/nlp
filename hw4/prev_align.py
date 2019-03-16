#!/usr/bin/env python
import optparse, sys, os, logging
from collections import defaultdict
from itertools import islice
from decimal import Decimal

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

f_vocab = set()
for s in islice(open(f_data), opts.num_sents):
    words = s.strip().split()
    for w in words:
        f_vocab.add(w)

size_f_vocab = len(f_vocab)

t = defaultdict(lambda: 1/size_f_vocab)

def t_lookup(k):
    if k in t:
        return t[k]
    return 1 / size_f_vocab

# for (f, e) in bitext:
#     for (i, f_i) in enumerate(f):
#         for (j, e_j) in enumerate(e):
#             t[(f_i,e_j)] = 1/size_f_vocab

for i in range(5):
    e_count = defaultdict(int)
    fe_count = defaultdict(int)
    for (n, (f, e)) in enumerate(bitext):
        for f_i in f:
            Z = 0
            for e_j in e:
                # Z += t[(f_i,e_j)]
                Z += t_lookup((f_i,e_j))
            for e_j in e:
                # c = t[(f_i,e_j)]/Z
                c = t_lookup((f_i,e_j))/Z
                fe_count[(f_i,e_j)] += c
                e_count[e_j] += c
    for key,value in fe_count.items():
        t[key] = value/ e_count[key[1]]

alignments = []

for (n, (f, e)) in enumerate(bitext):
    current_alignment = ""
    for (i, f_i) in enumerate(f): 
        bestp = 0
        bestj = 0
        for (j, e_j) in enumerate(e):
            if t[(f_i,e_j)] > bestp:
                bestp = t[(f_i,e_j)]
                bestj = j
        sys.stdout.write("%i-%i " % (i,bestj))
    sys.stdout.write("\n")
            #current_alignment+=("%i-%i " % (i,bestj))
    #alignments.append(current_alignment)

#for a in alignments:
    #sys.stdout.write(a)
    #sys.stdout.write("\n")