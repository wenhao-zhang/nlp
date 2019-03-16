# Send file through an OrderedDict to get unique lines while preserving order
# https://stackoverflow.com/a/39835527

from collections import OrderedDict

def uniqueify_lines_in_file(filename):
  lines = []
  with open(filename, 'r') as file:
    lines = [line.strip() for line in file.readlines()]
  lines = list(OrderedDict.fromkeys(lines))
  with open(filename, 'w') as file:
    for line in lines:
      file.write(f'{line}\n')
  return lines

if __name__ == "__main__":
  uniqueify_lines_in_file('G_S1.gr')
  uniqueify_lines_in_file('G_S2.gr')
  uniqueify_lines_in_file('G_Vocab.gr')
