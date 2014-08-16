import collections
import itertools
import nltk
import os
import subprocess
import time
import sys
import operator
# PARAMETERS
threshold=11


#


if len(sys.argv)>1:
	if os.path.isfile(sys.argv[1]):
		filename=sys.argv[1]
	else:
		if os.path.isfile("./data/"+sys.argv[1]):
			filename="./data/"+sys.argv[1]
		else:
			filename="./data/Canon S100.txt"
			sys.argv.append(1)
else:
	filename="./data/Canon S100.txt"
	sys.argv.append(1)

# --

logfile=open("log.txt","a")
logfile.write("-"*80)
logfile.write("\n")
logfile.write(time.strftime("%d %b %Y %H:%M:%S")+"\n")
logfile.write("\n"+"Filename: "+filename+"\n")
logfile.write("-"*80)
logfile.write("\n")

def flatten(l):
	for el in l:
		if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
			for sub in flatten(el):
				yield sub
		else:
			yield el

mPS = nltk.stem.porter.PorterStemmer()

print "Import done."

fp=open(filename,"r")
lines = fp.readlines()
fp.close()

print "Data reading done."

data_lines=[]
data_features=set([])
i=-1


for line in lines:
	if line[0]=="*":
		continue
	if line.strip()=='':
		continue
	if line[0:3]=='[t]':
		continue
	if len(line.split('##'))>1:
		data_lines.append(line.split('##')[1])
		for feat in line.split('##')[0].split(','):
			#f=feat.split(' ')[-1].split('[')[0]
			if len(feat.split(' '))>1:
				pass
			f=feat.split('[')[0].split(' ')[0]
			data_features.add(f)	#mPS.stem(f)
		continue

print "Data processing done."
print "Counters are out of %d." % len(data_lines)
fp=open('input.txt','w')

for line in data_lines:
	fp.write(line)

print "Sentence tokenization done."
fp.close()

flag = 'yes'
if len(sys.argv)>2:
	flag='no'
if flag[:1]=='y':
	#subprocess.call(r'java -jar test.jar',stdout=open(os.devnull, "w"))
	os.system(r'java -jar test.jar')

fp=open('output.txt','r')

parsed_well=[[]]
line='0'
nouns=[]
adjectives=[]
ctr=0
while True:
	#print ctr,
	sys.stdout.write("\r%d"%ctr)
	sys.stdout.flush()
	sent_line=fp.readline()		#sentence
	if not sent_line:
		break
	# POS Tag, Get NN and JJ (of sentence)
	tokens = nltk.word_tokenize(sent_line)
	tagged=nltk.pos_tag(tokens)
	
	nouns += [(t,ctr) for t,k in tagged if k[:2]=='NN']
	adjectives += [(t,ctr) for t,k in tagged if k[:2]=='JJ']
	#
	r_line=fp.readline()
	line=r_line.strip()
	if not r_line:
		break
	while len(line)>0:
		parsed_well[ctr].append(line)
		r_line=fp.readline()
		line=r_line.strip()
	parsed_well.append([])
	if not r_line:
		break
	ctr+=1

fp.close()
print
print "Dependancy creation done."

#print nouns
#print adjectives

def get_seeds(lsttup, threshold=5):
	nn=[]
	for k,_ in lsttup:
		#nn.append(mPS.stem(k))
		nn.append(k)
	
	c=collections.Counter(nn)
	if threshold>=0:
		return c.most_common(1)[0][0], [k[0] for k in c.most_common(threshold+1) if k[0]!=c.most_common(1)[0][0]]
	else:
		return c.most_common()

prod, feats = get_seeds(nouns, threshold)
print "-"*80
print "Bag-of-words model extracted product and features"
print "Product:", prod
print "Features:", feats

temp, opins = get_seeds(adjectives,threshold-1)
opins.insert(0,temp)
print
print "Bag-of-words model extracted opinion words"
print "Opinion Words:", opins

logfile.write("Bag-Of-Words Extraction:\nProduct:\n"+str(prod)+"\n")
logfile.write("Features:\n"+str(feats)+"\n")
logfile.write("Opinions:\n"+str(opins)+"\n")
print "Bag-of-words seeding done."

# Gets dependancy values from a line containing the grammar
def getdep(s):
	k=s.split('(')
	l=k[1].split(')')[0].split(',')
	m=l[0].split('-')[0]
	n=l[1].split('-')[0]
	return k[0],m,n

# Display Product accuracy using part-whole relation
# Automatic Discovery of Part-Whole Relations - Girju et. al.
# Extracting and Ranking Product Features in Opinion Documents - Zhang et. al.

prod_phr=[]
for line in flatten(parsed_well):
	#for line in p_line:
	rel, p1, p2 = getdep(line)
	if rel in ['prep_of','prep_in','prep_on']:
		prod_phr.append(p2)
	elif rel in ['prep_with']:
		prod_phr.append(p1)
	elif rel=='nsubj' and p1 in ['has', 'have', 'include', 'includes', 'contain', 'contains', 'consist', 'consists']:
		prod_phr.append(p2)
	elif rel=='poss':
		prod_phr.append(p1)

c=collections.Counter(prod_phr)

print
print "Part-Whole relation extracted product"
print [k[0] for k in c.most_common(5)]
logfile.write("Part Whole Extraction:\n"+str([k[0] for k in c.most_common(5)])+"\n")

# Use Modified Double-Propogation

o_seeds = set(opins)		# Contains words with no repetitions
f_seeds = set(feats)		# Contains words with no repetitions
o_list = adjectives	# Contains tuples (word, line number) with multiple copies
f_list = nouns		# Contains tuples (word, line number) with multiple copies

print "Original Opinions: ", o_seeds
print "Original Features: ", f_seeds

print "-"*80
print
print "Starting Double Propogation"

# Better than calling Porter Stemmer all the time.
stem={}
for f,_ in f_list:
	stem[f]=mPS.stem(f)

stem[prod]=mPS.stem(prod)

for o,_ in o_list:
	stem[o]=mPS.stem(o)


# Testing Number of lines to be called

allines=set([])
allinessum=0
for _,l in f_list:
	allines.add(l)
for _,l in o_list:
	allines.add(l)
for elem in allines:
	for line in parsed_well[elem]:
		allinessum+=1

print len(allines), allinessum

allinessum=0
for p in parsed_well:
	for line in p:
		allinessum+=1

print len(parsed_well), allinessum
#raw_input()

start = time.clock()
ctr=[0,0]
while True:
	ctr[0]+=1
	o_new=set([])
	#o_new=[]
	
	#f_new=set([])
	f_new=[]
	
	# Feature Words
	for f,lineno in f_list:
		rels={}
		p_line=parsed_well[lineno]
		
		for line in p_line:
			rel, p1, p2 = getdep(line)
			if rel in rels.keys():
				rels[rel].append((p1,p2))
			else:
				rels[rel]=[(p1,p2)]
		
		for line in p_line:
			ctr[1]+=1
			rel, p1, p2 = getdep(line)
			# R11:
			if p1==f and p2 in o_seeds and rel=='amod':
				if f not in f_seeds and stem.get(f)!=stem.get(prod):
					try: f_new.add(f)
					except: f_new.append(f)
			# R12:
			if p2==f and stem.get(p1) == stem.get(prod) and rel=='nsubj':
				if 'amod' in rels.keys():
					for q1,q2 in rels['amod']:
						if stem.get(q1) == stem.get(prod) and q2 in o_seeds:
							if f not in f_seeds and stem.get(f)!=stem.get(prod):
								try: f_new.add(f)
								except: f_new.append(f)
			# R31:
			if stem.get(p2)==stem.get(f) and p1 in f_seeds and rel=='conj_and':
				if f not in f_seeds and stem.get(f)!=stem.get(prod):
					try: f_new.add(f) 
					except: f_new.append(f)
			# R31':
			if stem.get(p1)==stem.get(f) and p2 in f_seeds and rel=='conj_and':
				if f not in f_seeds and stem.get(f)!=stem.get(prod):
					try: f_new.add(f) 
					except: f_new.append(f)
			# R32:
			if stem.get(p2)==stem.get(f) and p1 == 'has' and rel=='dobj':
				if 'nsubj' in rels.keys():
					for q1,q2 in rels['nsubj']:
						if q1 == 'has' and q2 in f_seeds:
							if f not in f_seeds and stem.get(f)!=stem.get(prod):
								try: f_new.add(f) 
								except: f_new.append(f)
			# Part-Whole:
			'''
			if rel in ['prep_of','prep_in','prep_on','prep_with'] and p2==f and f not in f_seeds:
				if stem.get(f)!=stem.get(prod):
					try: f_new.add(f) 
					except: f_new.append(f)
			if rel in ['prep_of','prep_in','prep_on','prep_with'] and p1==f and f not in f_seeds:
				if stem.get(f)!=stem.get(prod):
					try: f_new.add(f) 
					except: f_new.append(f)
			if rel=='nsubj' and p1 in ['has', 'have', 'include', 'includes', 'contain', 'contains', 'consist', 'consists'] and p2==f and f not in f_seeds:
				if stem.get(f)!=stem.get(prod):
					try: f_new.add(f) 
					except: f_new.append(f)
			#'''
	
	# Opinion Words
	for o,lineno in o_list:
		rels={}
		p_line=parsed_well[lineno]
		
		for line in p_line:
			rel, p1, p2 = getdep(line)
			if rel in rels.keys():
				rels[rel].append((p1,p2))
			else:
				rels[rel]=[(p1,p2)]
		
		for line in p_line:
			ctr[1]+=1
			rel, p1, p2 = getdep(line)
			# R21:
			if p2==o and p1 in f_seeds and rel=='amod':
				if o not in o_seeds and stem.get(o)!=stem.get(prod):
					o_new.add(o)
			# R22:
			if p2==o and p1 == prod and rel=='amod':
				if 'nsubj' in rels.keys():
					for q1,q2 in rels['nsubj']:
						if stem.get(q1) == stem.get(prod) and q2 in f_seeds:
							if o not in o_seeds and stem.get(o)!=stem.get(prod):
								o_new.add(o)
			# R41:
			if p1==o and p2 in o_seeds and rel=='conj_and':
				if o not in o_seeds and stem.get(o)!=stem.get(prod):
					o_new.add(o)
			# R41':
			if p2==o and p1 in o_seeds and rel=='conj_and':
				if o not in o_seeds and stem.get(o)!=stem.get(prod):
					o_new.add(o)
			# R42:
			if p2==o and stem.get(p1) == stem.get(prod) and rel=='amod':
				if o not in o_seeds and stem.get(o)!=stem.get(prod):
					o_new.add(o)
	
	#Convert opinion list to set
	
	c=collections.Counter(f_new)
	print c.most_common()
	f_new = set([key for key in c.keys() if c[key]>1])
	
	print "Features:",f_new
	print "Opinion:",o_new
	
	o_seeds = o_seeds | o_new
	f_seeds = f_seeds | f_new
	
	if len(f_new)==0 and len(o_new)==0:
		break

end = time.clock() - start
#raw_input("Continue?")
os.system('cls')

print "Double Propogation Complete."
logfile.write("Our Algorithm:\n")
logfile.write("Time Elapsed: %.2f\nSteps: %s\n"%(end,str(ctr)))

print "Features:",f_seeds
our_f = f_seeds
logfile.write("Features:\n"+str(f_seeds)+"\n")
print
print "Opinion:",o_seeds
our_o = o_seeds
logfile.write("Opinions:\n"+str(o_seeds)+"\n")

def score(f_seeds, data_features):
	f_seeds=set([mPS.stem(f) for f in f_seeds])
	data_features=set([mPS.stem(f) for f in data_features])
	ctr_c=0
	for feature in f_seeds:
		for dfeature in data_features:
			if feature == dfeature:
				ctr_c+=1

	print "Precision: ", ctr_c, '/', len(f_seeds), "=", "%.2f%%"%(100.0*ctr_c/len(f_seeds))
	print "Recall: ", ctr_c, '/', len(data_features), "=", "%.2f%%"%(100.0*ctr_c/len(data_features))
	
	logfile.write("Score:\n")
	logfile.write("Precision: %d/%d=%.2f%%"%(ctr_c,len(f_seeds),(100.0*ctr_c/len(f_seeds))))
	logfile.write("\n")
	logfile.write("Recall: %d/%d=%.2f%%"%(ctr_c,len(data_features),(100.0*ctr_c/len(data_features))))
	logfile.write("\n")

print "Done:"
score(f_seeds, data_features)
print "List:"
score([k[0] for k in f_list], data_features)

print "Their features:"
print data_features
logfile.write("Their Features:\n")
logfile.write(str(data_features)+"\n")


#raw_input("Continue?")
# Using Original Double-Propogation

print "-"*80

o_seeds = set(opins)		# Contains words with no repetitions
f_seeds = set(feats)		# Contains words with no repetitions
o_list = []
f_list = []

start = time.clock()
ctr=[0,0]
while True:
	ctr[0]+=1
	o_new=set([])
	f_new=set([])
	flag=0
	
	for p_line in parsed_well:
		rels={}
		for line in p_line:
			rel, p1, p2 = getdep(line)
			if rel in rels.keys():
				rels[rel].append((p1,p2))
			else:
				rels[rel]=[(p1,p2)]
		
		for line in p_line:
			ctr[1]+=1
			rel, p1, p2 = getdep(line)
			# R11:
			if p1 not in f_seeds and p2 in o_seeds and rel=='amod':
				f_new.add(p1)
			# R12:
			if p2 not in f_seeds and rel=='nsubj':
				if 'amod' in rels.keys():
					for q1, q2 in rels['amod']:
						if q1 == p1 and q2 in o_seeds:
							f_new.add(p2)
			# R41:
			if p1 not in o_seeds and p2 in o_seeds and rel=='conj_and':
				o_new.add(p1)
			# R41':
			if p2 not in o_seeds and p1 in o_seeds and rel=='conj_and':
				o_new.add(p2)
			# R42:
			if p2 not in o_seeds and rel=='amod':
				if 'amod' in rels.keys():
					for q1, q2 in rels['amod']:
						if q1 == p1 and q2 in o_seeds:
							o_new.add(p2)
	if len(o_new)>0 or len(f_new)>0:
		flag=1
	o_seeds = o_seeds | o_new
	f_seeds = f_seeds | f_new
	#print o_new
	#print f_new
	
	#o_new=set([])
	#f_new=set([])
	
	for p_line in parsed_well:
		rels={}
		for line in p_line:
			rel, p1, p2 = getdep(line)
			if rel in rels.keys():
				rels[rel].append((p1,p2))
			else:
				rels[rel]=[(p1,p2)]
		
		for line in p_line:
			ctr[1]+=1
			rel, p1, p2 = getdep(line)
			# R31:
			if p2 not in f_seeds and p1 in f_seeds and rel=='conj_and':
				f_new.add(p2)
			# R31':
			if p1 not in f_seeds and p2 in f_seeds and rel=='conj_and':
				f_new.add(p1)
			# R32:
			if p2 not in f_seeds and p1=='has' and rel=='dobj':
				if 'nsubj' in rels.keys():
					for q1, q2 in rels['nsubj']:
						if q1=='has' and q2 in f_seeds:
							f_new.add(p2)
			# R21:
			if p2 not in o_seeds and p1 in f_seeds and rel=='amod':
				o_new.add(p2)
			# R22:
			if p2 not in o_seeds and rel=='amod':
				if 'nsubj' in rels.keys():
					for q1, q2 in rels['nsubj']:
						if q1 == p1 and q2 in f_seeds:
							o_new.add(p2)
	
	if len(o_new)>0 or len(f_new)>0:
		flag=1
	
	o_seeds = o_seeds | o_new
	f_seeds = f_seeds | f_new
	
	print "Features:",f_new
	print "Opinions:",o_new
	
	if flag==0:
		break

end = time.clock()-start
#raw_input("Continue?")
os.system('cls')

print "Double Propogation Complete."
logfile.write("Their Algorithm:\n")
logfile.write("Time Elapsed: %.2f\nSteps: %s\n"%(end,str(ctr)))

print "Features (Fixed):",f_seeds
logfile.write("Features:\n"+str(f_seeds)+"\n")
print
print "Opinion (Fixed):",o_seeds
logfile.write("Opinions:\n"+str(o_seeds)+"\n")
print "Done:"
score(f_seeds, data_features)

print "Their features:"
print data_features


# Popularity Analysis
os.system('cls')

print our_f
print our_o

our_fc=set([])
for elem in our_f:
	if stem.get(elem,mPS.stem(elem)) != stem.get(prod,mPS.stem(prod)):
		our_fc.add(stem.get(elem,mPS.stem(elem)))
our_oc=set([])
for elem in our_o:
	if stem.get(elem,mPS.stem(elem)) != stem.get(prod,mPS.stem(prod)):
		our_oc.add(stem.get(elem,mPS.stem(elem)))

pop_analysis = []

for f in our_fc:
	pop_analysis.append([f,0,[]])
	for p_line in parsed_well:
		flag=0
		for l in p_line:
			if f in l:
				flag=1
		if flag==0:
			continue
		for l in p_line:
			_, p1, p2 = getdep(l)
			if p1 in our_oc:
				pop_analysis[-1][2].append(p1)
			if p2 in our_oc:
				pop_analysis[-1][2].append(p2)
	pop_analysis[-1][1]=len(pop_analysis[-1][2])

pop_analysis = sorted(pop_analysis, key = operator.itemgetter(1), reverse = True)

for i in xrange(len(pop_analysis)):
	c=collections.Counter(pop_analysis[i][2])
	pop_analysis[i][2]=c.most_common()

logfile.write('[\n')
for elem in pop_analysis:
	logfile.write(str(elem)+"\n")
logfile.write(']\n')

ctr=0
for f,freq,ol in pop_analysis:
	print f, freq
	ctr+=1
	if ctr==10:
		break
















logfile.close()