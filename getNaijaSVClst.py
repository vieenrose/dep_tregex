#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs, re, os,collections,sys

file='all_naija.conll10'
ext='.conll10'
fileout=os.path.splitext(file)[0]+'_svc_list'+ext
fileout2=os.path.splitext(file)[0]+'_svc_bigram'+ext
print('{} -> {}'.format(file,fileout))
print('{} -> {}'.format(file,fileout2))

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
				# export SVC arguments
				if sent.id: sent_id = sent.id
				else: sent_id = 'Unknown'
				out.write('# sent_id = {}\n'.format(sent_id))
				for svc in sent.svcs:
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
						if xlem not in statistics.keys():
							statistics[xlem]=collections.Counter()
						statistics[xlem][ylem]+=1

				out.write('\n')

			sent.reset()

out2 = codecs.open(fileout2,'w',encoding='utf-8')
for x in sorted(statistics.keys()):
	out2.write('{:s}: '.format(x))
	for i,y in enumerate(statistics[x].most_common()):
		lem,cnt=y
		out2.write('{}'.format(lem.strip()))
		if cnt > 1: out2.write('({})'.format(cnt))
		if i<len(statistics[x])-1: out2.write(', ')
	out2.write('\n')
