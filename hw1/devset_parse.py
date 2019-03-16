import nltk

with open('devset.txt') as f:
	content = f.readlines()

content = [c.strip() for c in content]
parsed = []

for c in content:
	tokens = nltk.word_tokenize(c)
	tags = nltk.pos_tag(tokens)
	for tag in tags:
		if tag not in parsed:
			parsed.append(tag)

with open('devset_vocab.gr', 'wt') as f:
	for p in parsed:
		f.write("1" + " " + p[1] + " " + p[0] + "\n")