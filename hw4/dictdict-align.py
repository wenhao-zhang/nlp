#!/usr/bin/env python
import sys, os, logging
from collections import defaultdict
from itertools import islice
from decimal import Decimal

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

def run(bitext, f_vocab, e_vocab):
  size_f_vocab = len(f_vocab)

  t = defaultdict(lambda: defaultdict(lambda: 1/size_f_vocab))

  def t_lookup(f_i, e_i):
      if f_i in t:
          if e_i in t[f_i]:
              return t[f_i][e_i]
      return 1 / size_f_vocab

  for i in range(5):
      e_count = defaultdict(int)
      fe_count = defaultdict(lambda: defaultdict(int))
      for (n, (f, e)) in enumerate(bitext):
          for f_i in f:
              Z = 0
              for e_j in e:
                  Z += t_lookup(f_i, e_j)
              for e_j in e:
                  c = t_lookup(f_i, e_j)/Z
                  fe_count[f_i][e_j] += c
                  e_count[e_j] += c
      for f_i,e_is in fe_count.items():
          for e_i, value in e_is.items():
              t[f_i][e_i] = value/ e_count[e_i]

  for (n, (f, e)) in enumerate(bitext):
      for (i, f_i) in enumerate(f):
          bestp = 0
          bestj = 0
          for (j, e_j) in enumerate(e):
              if t_lookup(f_i, e_j) > bestp:
                  bestp = t_lookup(f_i, e_j)
                  bestj = j
          sys.stdout.write("%i-%i " % (i,bestj))
      sys.stdout.write("\n")

if __name__ == "__main__":
  import optparse
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

  bitext, f_vocab, e_vocab = loadData(f_data, e_data, opts.num_sents)

  run(bitext, f_vocab, e_vocab)
