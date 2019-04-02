#!/usr/bin/env python -*- coding: utf-8 -*-
import codecs, re, os,collections,sys
import matplotlib.pylab as plt
import seaborn as sns
import numpy as np

# command-line interface
import argparse
parser = argparse.ArgumentParser()

parser.add_argument("--file", "-f", type=str, required=True)
parser.add_argument("--thld", "-t", type=int, required=False)
parser.add_argument("--deprel", "-d", type=str, required=True)
args = parser.parse_args()


deprel=args.deprel
pattern=u'[^\t0-9]*([0-9]+)\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t([0-9]+)\t{}[^\t]*\t.*\n'.format(deprel)
file=args.file
ext='.conll10'
ext2='.txt'
ext3='.png'
fileout=os.path.splitext(file)[0]+u'_{}_list'.format(deprel)+ext
fileout2=os.path.splitext(file)[0]+u'_{}_bigram'.format(deprel)+ext2
print('{} -> {}'.format(file,fileout))
print('{} -> {}'.format(file,fileout2))
#print('{} -> {}'.format(file,figout))

class sentence:
	def __init__(self):
		self.reset()
	def add_rel(self, tid, hid):
		inter = -1
		new_rel = set((tid,hid))
		for i,rel in enumerate(self.rels):
			if rel & new_rel: inter = i; break
		if inter < 0: self.rels.append(new_rel) # rel doublet
		else: self.rels[inter]=self.rels[inter].union(new_rel) # rel n-tuple, n > 2
	def reset(self):
		self.id = ''
		self.rels = []
		self.tokens = []
	def token(self,i):
		for tok in self.tokens:
			tokenid = int(tok.split('\t')[0])
			if i == tokenid :
				return tok
		return None

cnt_sent_tot = 0
cnt_bigram = 0
cnt_sent = 0
cnt_rel = 0
cnt_rel_len = collections.Counter()
with codecs.open(file, encoding='utf-8') as text :
        out = codecs.open(fileout,'w',encoding='utf-8')
	sent = sentence()
	statistics = collections.defaultdict()
	for i,line in enumerate(text):
		# match sent_id = ...
		result = re.match(u'.*sent_id\s*=\s*([^\n]*)', line)
		if result:
			sent_id = result.group(1)
			sent.id = sent_id
			continue
		# match a rel dependent then save its ID pairs (ID, HEAD)
		# eg. 15\tgo\t_\tVERB\t_\t_\t14\tcompound:svc\t_\t74350|74505
		result = re.match(pattern, line)
		if result:
			tokenid, headid = int(result.group(1)),int(result.group(2))
			sent.add_rel(tokenid, headid)
		# match a token and save it a raw string
		if len(line.split('\t')) == 10:
			line=line.replace('\n','')
			sent.tokens.append(line);

		# reach the end of a sentence
		if line == '\n':
                        if sent.rels:
				# count a sentence containing rel(s)
				cnt_sent += 1

				# export relation's arguments
				if sent.id: sent_id = sent.id
				else: sent_id = 'Unknown'
				out.write('# sent_id = {}\n'.format(sent_id))
				for rel in sent.rels:
					# count a rel
					cnt_rel+=1;cnt_rel_len[len(rel)] += 1
					rel_lst = sorted(list(rel))
					for j in rel_lst:
						token = sent.token(j)
						if token:
   	              					out.write(token+'\n')
					# bi-grams
					if len(rel_lst):
						for i in range(len(rel_lst)-1):
							try:
								xform, xlem = sent.token(rel_lst[i]).split('\t')[1:3]
								yform, ylem = sent.token(rel_lst[i+1]).split('\t')[1:3]
								if xlem == '_': xlem = xform
								if ylem == '_': ylem = yform
								#print(xlem,ylem)
								# bigram count
								cnt_bigram += 1
								if xlem not in statistics.keys():
									statistics[xlem]=collections.Counter()
								statistics[xlem][ylem]+=1
							except:
								continue

				out.write('\n')

			sent.reset()
			cnt_sent_tot += 1

# export the list
out2 = codecs.open(fileout2,'w',encoding='utf-8')
for x in sorted(statistics.keys()):
	out2.write('{:s}: '.format(x))
	for i,y in enumerate(statistics[x].most_common()):
		lem,cnt=y
		out2.write('{}'.format(lem.strip()))
		if cnt > 1: out2.write('({})'.format(cnt))
		if i<len(statistics[x])-1: out2.write(', ')
	out2.write('\n')

# show sentence and rel counts
print('cnt_sent',cnt_sent)
print('cnt_rel',cnt_rel)
print('cnt_bigram',cnt_bigram)
print('cnt_rel_len',cnt_rel_len)

# show and save heatmap
if args.thld > 0: thld = args.thld
else: thld = 0
figwid = 13

# figure filename
figout = os.path.splitext(file)[0] + '_{}_bigram_heatmap_thld_{}'.format(deprel,thld) + ext3

# store words appearing as the head (and dependent) more than thld times
v1=sorted([k for k in statistics.keys() if max(statistics[k].values())>thld])
v2=[]
for w in v1:
      for w2 in statistics[w].keys():
          if statistics[w][w2] > thld: v2.append(w2)
v2=sorted(list(set(v2)))

# make data matrix
data = np.array([[statistics[x][y] for y in v2] for x in v1])
mask = np.zeros_like(data)
for i,row in enumerate(data):
      for j,val in enumerate(row):
          if not val:mask[i][j]=True

# config layout
plt.rcParams["figure.figsize"] = [len(v2)/float(len(v1))*figwid, figwid]
fig, ax = plt.subplots()
titl = '\'{}\' in Naija ({} over {} sentences, {} relations'.format(deprel,cnt_sent,cnt_sent_tot,cnt_bigram)
if thld: titl += ', cnt > {})'.format(thld)
else:    titl += ')'
plt.title(titl)
#fig.subplots_adjust(bottom=0.2, left=0.2, top=0.95)
ax = sns.heatmap(data, yticklabels=v1, xticklabels=v2, vmax=data.max(), vmin=data.min(), \
cmap="Blues", cbar=False, \
square=False, annot=True, fmt='d',\
mask=mask, \
linecolor='gray', linewidth=0.005)
plt.ylabel('Head'); plt.xlabel('Dependant')
fig.canvas.set_window_title('Serial verb construction relation in Naija')
plt.tight_layout()
fig.savefig(figout)   # save the figure to file
plt.close(fig)    # close the figure

