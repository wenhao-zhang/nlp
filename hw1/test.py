

with open('Vocab.gr') as f:
    content = f.readlines()
    

content = [c.strip() for c in content]
content = [c.split() for c in content]

with open('G_Vocab.gr') as f:
    g_content = f.readlines()

g_content = [c.strip() for c in g_content]
g_content = [c.split() for c in g_content]

for x in content:
    for y in g_content:
        if x[2] == y[2]:
            x[0] = y[0]
            break

with open('test.gr', 'wt') as f:
	for c in content:
		f.write(str(c[0]) + " " + c[1] + " " + c[2] + "\n")
