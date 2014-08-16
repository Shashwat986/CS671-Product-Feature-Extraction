import nltk
from nltk.corpus import wordnet as wn
import glob
import os
import numpy as np

def ambig_sim_lst(word1,word2,s1,s2):
	try:
		return [w1.path_similarity(w2) for w1 in wn.synsets(word1, pos=s1) for w2 in wn.synsets(word2,pos=s2)]
	except KeyError:
		return []

def ambig_sim(word1,word2):
	'''Given two ADJECTIVES with multiple interpretations, present the maximum path similarity possible between the two words.'''
	
	k=ambig_sim_lst(word1,word2,'a','a')
	k+=ambig_sim_lst(word1,word2,'a','s')
	k+=ambig_sim_lst(word1,word2,'s','a')
	k+=ambig_sim_lst(word1,word2,'s','s')
	try:
		if max(k) is None:
			return 0
		else:
			return max(k)
	except ValueError:
		return 0



print "Import done."

fp=open("./data/Creative Labs Nomad Jukebox Zen Xtra 40GB.txt","r")

lines = fp.readlines()

data={}
i=-1

print "Data reading done."
mPS = nltk.stem.porter.PorterStemmer()


for line in lines:
	if line[0]=="*":
		continue
	if line.strip()=='':
		continue
	if line[0:3]=='[t]':
		i+=1
		data[i]={}
		data[i]['lines']=[]
		data[i]['features']=[]
		data[i]['title']=line[3:]
		continue
	if len(line.split('##'))>1:
		data[i]['lines'].append(line.split('##')[1])
		for feat in line.split('##')[0].split(','):
			#f=feat.split(' ')[-1].split('[')[0]
			if len(feat.split(' '))>1:
				continue
			f=feat.split('[')[0]
			data[i]['features'].append(mPS.stem(f))
		continue

print "Data processing done."

try:
	for i in data:
		#print data[i]
		
		for line in data[i]['lines']:
			tokens = nltk.word_tokenize(line)
			tagged = nltk.pos_tag(tokens)
			#print tagged
			if 'nouns' in data[i].keys():
				data[i]['nouns']+=[t for t,k in tagged if k[:2]=='NN']
			else:
				data[i]['nouns']=[t for t,k in tagged if k[:2]=='NN']
			
			if 'adjectives' in data[i].keys():
				data[i]['adjectives']+=[t for t,k in tagged if k[:2]=='JJ']
			else:
				data[i]['adjectives']=[t for t,k in tagged if k[:2]=='JJ']
			
		#print data[i]['nouns']
		#print data[i]['adjectives']
		'''
		for adj in data[i]['adjectives']+data[i]['nouns']:
			if ambig_sim(adj,'good')>ambig_sim(adj,'bad'):
				#print adj, ":", "Good"
				#print
				pass
			elif ambig_sim(adj,'good')<ambig_sim(adj,'bad'):
				#print adj, ":", "Bad"
				#print
				pass
			else:
				pass
		'''
		#print
		#print "Done."
		#raw_input()
	nouns=[]
	for i in data:
		for k in data[i]['nouns']:
			nouns.append(mPS.stem(k))
	
	features=set([])
	for i in data:
		for k in data[i]['features']:
			features.add(k)
	
	print features
	
	uniqnouns=set([])
	
	freq={}
	for n in nouns:
		if n in uniqnouns:
			freq[n]+=1
		else:
			freq[n]=1
			uniqnouns.add(n)
	
	threshold = int(np.mean(np.array(freq.values()))+np.std(np.array(freq.values())))
	sortfreq = sorted(freq, key = freq.get)
	ctr=0
	ctr_m=len(features)
	ctr_p=0
	for elem in sortfreq:
		if freq[elem]<=threshold:
			continue
		if elem in features:
			print 'YES',
			ctr+=1
		print elem,":",freq[elem]
		ctr_p+=1
	#print freq
	#print threshold
	#print np.mean(np.array(freq.values())),np.std(np.array(freq.values()))
	print "Recall:", ctr,'/',ctr_m, ':', "%.2f%%"%(100.0*ctr/ctr_m)
	print "Precision:", ctr,'/',ctr_p, ':', "%.2f%%"%(100.0*ctr/ctr_p)
	'''
	uniqnouns=set([])
	
	freq={}
	for n in nouns:
		if n in uniqnouns:
			freq[n]+=1
		else:
			freq[n]=1
			uniqnouns.add(n)
	
	#threshold = int(np.mean(np.array(freq.values()))+np.std(np.array(freq.values())))
	
	
	sortfreq = sorted(freq, key = freq.get)
	
	try:
		print sortfreq[-1], sortfreq[-threshold-1:-1]
		return sortfreq[-1], sortfreq[-threshold-1:-1]
	except:
		print sortfreq[-1], sortfreq[:-1]
		return sortfreq[-1], sortfreq[:-1]
	'''
except KeyboardInterrupt:
	pass
