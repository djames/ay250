import numpy, urllib
from Queue import Queue
import networkx as nx
import matplotlib.pyplot as plt

percentagemales = .50

def namestartindex(l) :
	for i in range(0, len(l)) :
		if l[i].count("<span>List of Baby Names") : return i + 5
def nameendindex(l) :
	for i in range(0, len(l)) :
		if l[i].count("END CONTENT") : return i - 6

class NamingService :
	alphabet = "abcdefghijklmnopqstuvwxyz"
	def __init__(self) :
		self.allnames = []
		try : self.boynames = open("boynames.txt").read().splitlines()
		except : self.boynames = []
		self.boyindex = -1
		self.bnreturn = Queue()
		try : self.grlnames = open("girlnames.txt").read().splitlines()
		except : self.grlnames = []
		self.grlindex = -1
		self.gnreturn = Queue()
		if (len(self.boynames) == 0) :
			for l in NamingService.alphabet :
				x = urllib.urlopen("http://www.listofbabynames.org/"+l+"_boys.htm").readlines()
				s = namestartindex(x)
				e = nameendindex(x)
				for n in range(s,e) :
					try : 
						name = x[n].strip().split('>')[1].split('<')[0].strip()
						if name and name != "Adam" : self.boynames.append(name)
					except : continue
			f = open("boynames.txt","w")
			for line in self.boynames : f.write(line + "\n")
			f.close()
		if (len(self.grlnames) == 0) :
			for l in NamingService.alphabet :
				x = urllib.urlopen("http://www.listofbabynames.org/"+l+"_girls.htm").readlines()
				s = namestartindex(x)
				e = nameendindex(x)
				for n in range(s,e) :
					try : 
						name = x[n].strip().split('>')[1].split('<')[0].strip()
						if name and name != "Eve" and name != "Mary" : self.grlnames.append(name)
					except : continue
			f = open("girlnames.txt","w")
			for line in self.grlnames : f.write(line + "\n")
			f.close()
	def newgirl(self) :
		if (not self.gnreturn.empty()) : return self.gnreturn.get()
		self.grlindex += 1
		div = self.grlindex/len(self.grlnames)
		return self.grlnames[self.grlindex%len(self.grlnames)] + (str(div) if div else "")
	def newboy(self) :
		if (not self.bnreturn.empty()) : return self.bnreturn.get()
		self.boyindex += 1
		div = self.boyindex/len(self.boynames)
		return self.boynames[self.boyindex%len(self.boynames)] + (str(div) if div else "")
	def newbear(self, male,name=False) :
		if name : n = name
		elif male : n = self.newboy()
		else : n = self.newgirl()
		self.allnames.append(n)
		return n
	def deadbear(self, name, male) :
		if male : self.bnreturn.put(name)
		else : self.gnreturn.put(name)
namingservice = NamingService()
	
class Bear :
	numbears = 0
	allbears = []
	def __init__(self,mom,dad,male,name=False) :
		global namingservice
		self.birthday = generation
		self.lifespan = int(numpy.random.normal(35,5))/5
		self.mom = mom
		self.dad = dad
		self.male = male
		self.ID = Bear.numbears
		Bear.numbears += 1
		if name : self.name = namingservice.newbear(male,name)
		else : self.name = namingservice.newbear(male)
		Bear.allbears.append(self)
	def isdead(self) :
		if self.birthday + self.lifespan < generation :
			namingservice.deadbear(self.name, self.male)
			return True
		return False
	def suitableMate(self, bear) :
		if (self.male and bear.male) or ((not self.male) and (not bear.male)) : return False
		return self.dad != bear.dad or self.mom != bear.mom
	def printbear(self) :
		print "%s(%d) %s(%d) %s(%d) %s Gen:%d" % (self.name, self.ID if self.ID>=0 else -1, namingservice.allnames[self.dad] if self.dad>=0 else "God",self.dad, namingservice.allnames[self.mom] if self.mom>=0 else "God",self.mom, "Male" if self.male else "Female",self.birthday)

numgens = 30 # 5 years per generation
generation = 0
generations = [[]]*(numgens+1)
livingbears = [[]]*(numgens+1)
generations[0] = ([Bear(-3,-3,True,name="Adam"),Bear(-2,-2,False,name="Eve"),Bear(-1,-1,False,name="Mary")])
livingbears[0] = generations[0]
newbirths = []

marriagequeues = []
for i in range(0,numgens+1) : marriagequeues.append(Queue())

def findmate(bear) :
	for i in range(max(bear.birthday-2,0),min(bear.birthday+2,numgens)+1) :
		if not marriagequeues[i].empty() :
			marker = marriagequeues[i].get()
			potmate = marker
			while True :
				if bear.suitableMate(potmate) : return potmate
				marriagequeues[i].put(potmate)
				potmate = marriagequeues[i].get()
				if potmate == marker : break
	return None

def newbear(x,y) :
	male = 1 if numpy.random.random_sample() < percentagemales else 0
	if x.male : cub = Bear(y.ID,x.ID,male)
	else : cub = Bear(x.ID,y.ID,male)
	newbirths.append(cub)

def buildAncestorTree(bid, G) :
	bear = Bear.allbears[bid]
	bear.printbear()
	if bear.mom < 0 : return
	G.add_edge(bid, bear.mom)
	G.add_edge(bid, bear.dad)
	buildAncestorTree(bear.mom,G)
	buildAncestorTree(bear.dad,G)

def printallbears() :
	for b in Bear.allbears : b.printbear()
	print "Total: "+str(Bear.numbears)

def printallalivebears(supress=False) :
	i = 0
	for g in livingbears : 
		for b in g: 
			i += 1
			if not supress : b.printbear()
	if not supress : print "Total: " + str(i)
	return i

while generation < numgens :
	for i in range (0, numgens) : map(lambda x: not x.isdead() and marriagequeues[i].put(x) or 42, livingbears[i])
	for i in range (0, numgens) :
		tmpbears = []
		while not marriagequeues[i].empty() :
			bear = marriagequeues[i].get()
			tmpbears.append(bear)
			mate = findmate(bear)
			if mate == None : continue
			tmpbears.append(mate)
			newbear(bear,mate)
		livingbears[i] = tmpbears
	generation += 1
	generations[generation] = newbirths
	livingbears[generation] = newbirths[:]
	newbirths = []
	print "Generation: "+str(generation)+" Num Bears (Total): " + str(Bear.numbears) + " Num Bears (Alive): " + str(printallalivebears(supress=True))

revallnames = namingservice.allnames[:]
revallnames.reverse()
usage = "Usage:\n\tgentree <name||ID>\tShow geneaology tree for youngest bear with given name, or for bear with given ID\n\tprint <name||ID>\tprint info for given bear\n\tprint all\t\tprint info for all bears\n\tprint living\t\tprint info for living bears\n\tq\t\t\tquit"
print usage
while True :
	b = raw_input("> ")
	if len(b.strip()) == 0 : continue
	if b.strip() == "print all" :
		printallbears()
		continue
	if b.strip() == "print living" :
		printallalivebears()
		continue
	if b.strip() == "q" or b.strip() == "quit" : break
	b = b.split()
	if len(b) < 2 : 
		print usage
		continue
	try : bid = int(b[1])
	except : 
		try :
			bid = (len(revallnames)-1) - revallnames.index(b[1])
		except :
			print "Bear not found"
			continue
	if bid >= len(Bear.allbears) or bid < 0 :
		print "Given ID does not match a bear"
		continue
	if b[0] == "gentree" :
		G = nx.DiGraph()
		buildAncestorTree(bid,G)
		nx.draw_graphviz(G)
		plt.show()
	elif b[0] == "print" :
		Bear.allbears[bid].printbear()
	else : print usage
