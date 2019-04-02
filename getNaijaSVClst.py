#!/usr/bin/env python -*- coding: utf-8 -*-
import codecs, re, os,collections,sys
import matplotlib.pylab as plt
import seaborn as sns
import numpy as np

# command-line interface
import argparse
parser = argparse.ArgumentParser()

parser.add_argument("--file", "-f", type=str, required=True)
args = parser.parse_args()


file=args.file
ext='.conll10'
ext2='.txt'
ext3='.png'
fileout=os.path.splitext(file)[0]+'_svc_list'+ext
fileout2=os.path.splitext(file)[0]+'_svc_bigram'+ext2
figout=os.path.splitext(file)[0]+'_svc_bigram_heatmap'+ext3
print('{} -> {}'.format(file,fileout))
print('{} -> {}'.format(file,fileout2))
print('{} -> {}'.format(file,figout))

class sentence:
	def __init__(self):
		self.reset()
	def add_svc(self, tid, hid):
		inter = -1
		new_svc = set((tid,hid))
		for i,svc in enumerate(self.svcs):
			if svc & new_svc: inter = i; break
		if inter < 0: self.svcs.append(new_svc) # svc doublet
		else: self.svcs[inter]=self.svcs[inter].union(new_svc) # svc n-tuple, n > 2
	def reset(self):
		self.id = ''
		self.svcs = []
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
cnt_svc = 0
cnt_svc_len = collections.Counter()
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
		# match a svc dependent then save its ID pairs (ID, HEAD)
		# eg. 15\tgo\t_\tVERB\t_\t_\t14\tcompound:svc\t_\t74350|74505
		result = re.match(u'[^\t0-9]*([0-9]+)\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t[^\t]*\t([0-9]+)\tcompound:svc\t.*\n', line)
		if result:
			tokenid, headid = int(result.group(1)),int(result.group(2))
			sent.add_svc(tokenid, headid)
		# match a token and save it a raw string
		if len(line.split('\t')) == 10:
			line=line.replace('\n','')
			sent.tokens.append(line);

		# reach the end of a sentence
		if line == '\n':
                        if sent.svcs:
				# count a sentence containing svc(s)
				cnt_sent += 1

				# export SVC arguments
				if sent.id: sent_id = sent.id
				else: sent_id = 'Unknown'
				out.write('# sent_id = {}\n'.format(sent_id))
				for svc in sent.svcs:
					# count a svc
					cnt_svc+=1;cnt_svc_len[len(svc)] += 1
					svc_lst = sorted(list(svc))
					for j in svc_lst:
						token = sent.token(j)
						out.write(token+'\n')
					# bi-grams
					for i in range(len(svc_lst)-1):
						xform, xlem = sent.token(svc_lst[i]).split('\t')[1:3]
						yform, ylem = sent.token(svc_lst[i+1]).split('\t')[1:3]
						if xlem == '_': xlem = xform
						if ylem == '_': ylem = yform
						#print(xlem,ylem)
						# bigram count
						cnt_bigram += 1
						if xlem not in statistics.keys():
							statistics[xlem]=collections.Counter()
						statistics[xlem][ylem]+=1

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

# show sentence and svc counts
print('cnt_sent',cnt_sent)
print('cnt_svc',cnt_svc)
print('cnt_bigram',cnt_bigram)
print('cnt_svc_len',cnt_svc_len)

# show and save heatmap
thld = 0
figwid = 15

v1=sorted([k for k in statistics.keys() if max(statistics[k].values())>thld])
v2=[]
for x in v1:v2 += statistics[x].keys();
v2=sorted([i[0] for i in collections.Counter(v2).items() if i[1]>thld])

data = []
for x in v1: data.append([np.log10(max((int(statistics[x][y])),max(thld,1))) for y in v2])
data = np.array(data)
mask = np.zeros_like(data)
datamax=(max([max(line)for line in data]))
datamin=(min([min(line)for line in data]))
with sns.axes_style("white"):
	plt.rcParams["figure.figsize"] = [len(v2)/float(len(v1))*figwid, figwid]
	fig, ax = plt.subplots()
	ax = sns.heatmap(data, linewidth=0.5, vmax=datamax, vmin=datamin, cmap="OrRd", cbar=False, square=True)
	# ... and label them with the respective list entries
	ax.set_xticklabels(v2)
	ax.set_yticklabels(v1)
	# Rotate the tick labels and set their alignment.
	plt.setp(ax.get_xticklabels(), rotation=90, ha="right", rotation_mode="default")
	plt.setp(ax.get_yticklabels(), rotation=0, ha="right", rotation_mode="default")
	fig.canvas.set_window_title('Serial verb construction relation in Naija')
        plt.ylabel('Head')
        plt.xlabel('Dependant')
	titl = '\'compound:svc\' in Naija ({} / {} sents, {} SVCs'.format(cnt_sent,cnt_sent_tot,cnt_bigram)
	if thld:
		titl += ' cnt > {} )'.format(thld)
	else:
		titl += ')'

	plt.title(titl)
	fig.subplots_adjust(bottom=0.2, left=0.2, top=0.95)
fig.savefig(figout)   # save the figure to file
plt.close(fig)    # close the figure
