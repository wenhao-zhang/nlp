import nltk

with open('allowed_words.txt') as f:
	content = f.readlines()

content = [x.strip() for x in content]

parsed = []

for x in content:
	parsed.extend(nltk.pos_tag([x]))

with open('parsed_file.txt', 'wt') as f:
	for x in parsed:
		f.write(x[0] + " " + x[1] + "\n")
