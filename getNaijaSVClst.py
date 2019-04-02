#!/usr/bin/env python -*- coding: utf-8 -*-
import codecs, re, os,collections,sys
import matplotlib.pylab as plt
import seaborn as sns
import numpy as np

# command-line interface
import argparse
parser = argparse.ArgumentParser()

parser.add_argument("--file", "-f", type=str, required=True)
parser.add_argument("--size", "-s", type=int, required=False)
parser.add_argument("--deprel", "-d", type=str, required=True)
args = parser.parse_args()
if args.size:
      vis_data_size = args.size
else:
      vis_data_size = -1 # non restriction

deprel=args.deprel
pattern=u'[^\t0-9]*([0-9]+)\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t([0-9]+)\t{}\t.*\n'.format(deprel)
file=args.file
ext='.conll10'
ext2='.txt'
ext3='.png'
fileout=os.path.splitext(file)[0]+u'_{}_list'.format(deprel)+ext
fileout2=os.path.splitext(file)[0]+u'_{}_bigram'.format(deprel)+ext2
print('{} -> {}'.format(file,fileout))
print('{} -> {}'.format(file,fileout2))
#print('{} -> {}'.format(file,figout))

def reorder_matrix(data, v1, v2):
      v1=np.array(v1)
      v2=np.array(v2)
      v1list = np.array(np.argsort(np.linalg.norm(data,axis=1)))[::-1]
      data=data[v1list]; v1=v1[v1list]
      v2list = np.array(np.argsort(np.linalg.norm(data,axis=0)))[::-1]
      data=(data.transpose()[v2list]).transpose(); v2=v2[v2list]
      return data,v1,v2


class sentence:
	def __init__(self):
		self.reset()
	def add_rel(self, tid, hid):
		inter = -1
		tid, hid = int(tid), int(hid)
		for i,rel in enumerate(self.rels):
			if int(rel[-1]) == hid: inter = i; break # when the head of new relation match the token of a existing one
		if inter < 0: self.rels.append([hid,tid]) # rel doublet
		else:
			#pass
			tmp = self.rels[inter]
			tmp.append(tid)
			self.rels[inter] = tmp # rel n-tuple, n > 2
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
				out.write(u'# sent_id = {}\n'.format(sent_id))
				for rel in sent.rels:
					# count a rel
					cnt_rel+=1
					cnt_rel_len[len(rel)] += 1
					rel_lst = list(rel)
					for j in rel_lst: # [a,b,c] signify that a -dominate--> b -dominate--> c
						token = sent.token(j)
						if token:
   	              					out.write(token+u'\n')
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

				out.write(u'\n')

			sent.reset()
			cnt_sent_tot += 1

# export the list
out2 = codecs.open(fileout2,'w',encoding='utf-8')
for x in sorted(statistics.keys()):
	out2.write(u'{:s}: '.format(x))
	for i,y in enumerate(statistics[x].most_common()):
		lem,cnt=y
		try:
    		    out2.write(u'{}'.format(lem.strip()))
		except:
		    print(lem)
		    raise
		if cnt > 1: out2.write(u'({})'.format(cnt))
		if i<len(statistics[x])-1: out2.write(u', ')
	out2.write(u'\n')

# show sentence and rel counts
print('cnt_sent',cnt_sent)
print('cnt_rel',cnt_rel)
print('cnt_bigram',cnt_bigram)
print('cnt_rel_len',cnt_rel_len)

# show and save heatmap
if args.size > 0: data_vis_size = args.size
else: data_vis_size = 10*10
figwid = 13

# figure filename
figout = os.path.splitext(file)[0] + '_heatmap_{}'.format(deprel) + ext3

# store words appearing as the head (and dependent) more than thld times
thld = 0
v1=sorted([k for k in statistics.keys() if max(statistics[k].values())>thld])
v2=[]
for w in v1:
      for w2 in statistics[w].keys():
          if statistics[w][w2] > thld: v2.append(w2)
v2=sorted(list(set(v2)))

# make data matrix
data = np.array([[statistics[x][y] for y in v2] for x in v1])
# reorder the matrix according by row's norm
data,v1,v2= reorder_matrix(data, v1, v2)
# troncate data to fit vis_data_size
if vis_data_size > 0: 
	while data.shape[0] * data.shape[1] > vis_data_size :
	        if data.shape[0] > data.shape[1]:
                    data = np.delete(data, -1, 0)
                else:
                    data = np.delete(data, -1, 1)
                data,v1,v2= reorder_matrix(data, v1, v2)

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
plt.ylabel('Head'); plt.xlabel('Dependent')
fig.canvas.set_window_title('Serial verb construction relation in Naija')
plt.tight_layout()
fig.savefig(figout)   # save the figure to file
plt.close(fig)    # close the figure

