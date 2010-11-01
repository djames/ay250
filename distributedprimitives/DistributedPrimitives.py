import socket, sys, time, xmlrpclib, commands, socket, os, SimpleXMLRPCServer, Queue
from threading import Thread, Lock, Condition

# Small extension to SimpleXMLRPCServer to allow retrieval of client address
class RPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer) :
    def process_request(self, request, client_address) :
        self.client_address = client_address[0]
        return SimpleXMLRPCServer.SimpleXMLRPCServer.process_request(self, request, client_address) 

class DistributedPrimitiveException(Exception) :
    def __init__(self, value) :
        self.value = value
    def __str__(self) :
        return repr(self.value)

class SynchronizedQueue() :
    def __init__(self, values) :
        self.values = values
        self.currentIndex = 0
        self.uniqueRequests = {}
        self.nullsReturned = 0

class Semaphore() :
    def __init__(self, size, timeout) :
        self.size = size
        self.timeout = timeout
        self.waitingQueue = Queue.Queue()
        self.holdingSet = set()
        self.lock = Lock()
        self.failedAgents = set()
        self.timeoutcontroller = TimeoutController(self)
        self.controller = SemaphoreController(self)
        # TODO FORK SEMAPHORE CONTROLLER AND TIMEOUT HANDLER



# Together, SemaphoreTimeout and SemaphoreController allow
# calls to LeaderServer.returnSemaphore to return immediately--
# waking the next agent is passed on to SemaphoreController, and
# timeouts are implemented in SemaphoreTimeout which passes
# waking of agents on to SemaphoreController.

# Thread to keep track of semaphore timeouts. When timeout
# occurs, bookkeeping is done here, and waking is passed
# off to the SemaphoreController.
class TimeoutController(Thread) :
    def __init__(self, s) :
        Thread.__init__(self)
        self.s = s
        self.timeoutqueue = Queue.Queue()
    def run(self) :
        while True :
            (agent, starttime) = self.timeoutqueue.get()
            time.sleep(max(0,self.s.timeout - starttime))
            self.s.lock.acquire()
            if agent in self.s.holdingSet :
                self.s.holdingSet.remove(agent)
                self.s.failedAgents.add(agent)
                self.s.controller.wakeCounter.release()
            self.s.lock.release()
        

# Thread to wake semaphores.
class SemaphoreController(Thread) :
    def __init__(self, s) :
        Thread.__init__(self)
        self.s = s
        # Internal python semaphore. This indicates to the controller
        # how many agents to wake up before waiting again. Initially
        # 0, since nobody waiting on semaphore.
        self.wakeCounter = threading.Semaphore(0)
    def wakeUp() :
        self.s.lock.acquire()
        if self.s.waitingQueue.empty() :
            self.s.size += 1
            self.s.lock.release()
            return
        notify(self.s.waitingQueue.get())
    def run(self) :
        while True :
            wakeCounter.acquire()
            wakeUp()

class LeaderServer(Thread) :
    def __init__(self) :
        Thread.__init__(self)
        self.semaphores = {}
        self.synchronizedQueues = {}
        self.server = RPCServer(("0.0.0.0", port))
        self.server.register_function(self.getFromSynchronizedQueue)
        self.server.register_function(self.waitOnSemaphore)
        self.server.register_function(self.releaseSemaphore)
    def createSynchronizedQueue(name, values) :
        self.synchronizedQueues[name] = synchronizedQueue()
    def getFromSynchronizedQueue(name) :
        # if we haven't seen this client before, store it
        if not (self.server.client_address in self.synchronizedQueues[name].uniqueRequests) :
            self.synchronizedQueues[name].uniqueRequests[self.server.client_address] = []
        # if the queue is empty, add one to the
        # number of nulls returned and return None
        if self.synchronizedQueues[name].currentIndex > len(self.synchronizedQueues[name].values) :
            self.synchronizedQueues[name].nullsReturned += 1
            return None
        rtn = self.synchronizedQueues[name].values[self.synchronizedQueues[name].currentIndex]
        self.synchronizedQueues[name].currentIndex += 1
        self.synchronizedQueues[name].uniqueRequests[self.server.client_address].append(rtn)
        return rtn
#    def getSynchronizedQueueStatus(name) :
#        return (self.synchronizedQueues[name][2], self.synchronizedQueues[name][3])
    def createSemaphore(name, size, timeout) :
        self.semaphores[name] = Semaphore(size, timeout)
    def releaseSemaphore(name) :
        # Remove client from set of clients holding semaphore
        self.semaphores[name].lock.acquire()
        if self.server.client_address in self.semaphores[name].holdingSet :
            self.semaphores[name].holdingSet.remove(self.server.client_address)
            # Notify controller to wake another waiting agent up
            # (This thread never actually acquired wakeCounter; this is
            # intended--I'm using a python semaphore to implement "locked
            # integer" semantics.)
            self.semaphores[name].controller.wakeCounter.release()
        else : # Agent is releasing semaphore after timeout ocurred.
            self.semaphores[name].failedAgents.remove(server.client_address)
        self.semaphores[name].lock.release()
    def acquireSemaphore(name) :
        # TODO IMPLEMENT ME!
    def run(self) :
        self.server.serve_forever()

class DistributedPrimitives() :
    def __init__(self, port, ph1length=20, ph2length=15, remoteserver=None) :
        self.port = port
        self.ip = getIP()
        if remoteserver :
            self.leader = remoteserver
        else :
            self.leader = runLeaderElection(ph1length, ph2length)
        self.proxy = xmlrpclib.ServerProxy("http://"+str(self.leader)+":"+str(port)+"/")
        if self.leader == self.ip :
            
    def thisNodeIsLeader() :
        return self.leader == self.ip
    def createSemaphore(name, size) :
        
    
        
        

#################  Utility Functions  #######################

def getIP() :
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('google.com',0))
	return s.getsockname()[0]

def mode(l) :
	l = sorted(l)
	i = 0
	keyindex = 0
	count = 0
	maxcount = 0
	prev = None
	while i < len(l) :
		if l[i] == prev :
			count += 1
			if count > maxcount :
				keyindex = i
				maxcount = count
		else :
			count = 0
		prev = l[i]
		i += 1
	return l[keyindex]

###################  Global Variables  #################################

myIP = None
port = None
master = None
outfile = None
## Path to file containing list of input files, separated by newlines.
input_files = None
tstormspath = None

####################  Worker Threads  ##################################

## These two threads work as a pair to stage in, analyze, and stage out data.

cfile = None
done = False
workerlock = Lock()
cv = Condition(workerlock)
proxy = None
progressproxy = None

def shutdown(t) :
	if progressproxy : progressproxy.report(str(myIP) + " shutting down")
	os.popen("shutdown +"+str(t)+" -h")

class stagerThread(Thread) :
	def run(self) :
		global cfile, done
		cv.acquire()
		while True :
			while cfile :
				cv.wait()
			cfile = self.stageIn()
			if cfile == None :
				done = True
				cv.notify()
				cv.release()
				return
			cv.notify()
	def stageIn(self) :
		n = proxy.nextInput(myIP)
		if n == -1 : return None
		url = input_files[n]
		fname = "/tmp/" + str(url.split('/').pop())
		cmd = "globus-url-copy -rst-retries 0 " + url + " file:///"+fname
		if progressproxy : progressproxy.report(str(myIP) + " staging in: " + cmd)
		commands.getoutput(cmd)
		return fname

class analyzerThread(Thread) :
	def run(self) :
		global cfile
		while True :
			cv.acquire()
			while cfile == None :
				if done :
					cv.release()
					if master != myIP : shutdown(0)
					return
				cv.wait()
			f = cfile
			cfile = None
			cv.notify()
			cv.release()
			cmd = tstormspath + "scripts/run_tstorms_general " + f + " /tmp/climateout"
			if progressproxy : progressproxy.report(str(myIP) + " analyzing: " + cmd)
			commands.getoutput(cmd)
			cmd = "globus-url-copy -rst-retries 0 file:////tmp/climateout/cyclones_out " + outurl + "cyclones_" + f.split('.')[-2][0:-6]
			commands.getoutput(cmd)
			commands.getoutput("rm " + f)
			commands.getoutput("rm -r /tmp/climateout")

############################  RPC Server  #####################################

## The master VM will fork this thread in addition to his worker threads.
## All worker threads across all VMs will access this RPCServer thread to
## receive the next file in the list of files to analyze.

class RPCServer(Thread) :
	def __init__(self) :
		Thread.__init__(self)
		self.n = 0
		self.uniqueRequests = []
		self.numDoneSent = 0
		self.server = SimpleXMLRPCServer(("0.0.0.0", port))
		self.server.register_function(self.nextInput, "nextInput")
		self.lock = Lock()
	def nextInput(self, ip) :
		self.lock.acquire()
		if self.uniqueRequests.count(ip) == 0 : self.uniqueRequests.append(ip)
		if self.n >= len(input_files) :
			self.numDoneSent += 1
			if self.numDoneSent >= len(self.uniqueRequests) : shutdown(1)
			self.lock.release()
			return -1
		rtn = self.n
		self.n += 1
		self.lock.release()
		return rtn
		
	def run(self) :
		self.server.serve_forever()

####################  Distributed Election Protocol Logic  #######################

## Protocol constants
USE = "u"
AUTH = "a"
ANN = "n"

## Initialize input socket
insock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
insock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
insock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
insock.settimeout(3)
## Initialize output socket
outsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
outsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
outsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
outsock.settimeout(3)

## Utilities to send the various packets in the protocol
def sendUseMyMasterPacket() :
	msg = USE + " " + str(master)
	outsock.sendto(msg, ("<broadcast>",port))
def sendAnnouncePacket() :
	outsock.sendto(ANN, ("<broadcast>",port))

## Get the next UDP packet. Ignore it if its from yourself.
def recvPacket() :
	try :
		while True :
			(msg, addr) = insock.recvfrom(65536)
			if addr[0] == str(myIP) :
				continue
			return (msg, addr)
	except socket.timeout :
		raise

## Agents fork this thread once they are sure of
## who the master agent will be. It receives packets
## and if necessary, responds with an authoritative
## "use my master" packet.
class fixedMasterThread(Thread) :
	def run(self) :
		if progressproxy : progressproxy.report(str(myIP) + " using master " + str(master))
		insock.settimeout(None)
		while True :
			(msg, addr) = insock.recvfrom(65536)
			if msg.split()[0] != AUTH :
				outsock.sendto(AUTH + " " + str(master), ("<broadcast>",port))

def setMasterAndForkThreads() :
	global proxy
	proxy = xmlrpclib.ServerProxy("http://"+str(master)+":"+str(port)+"/")
	fmt = fixedMasterThread()
	fmt.start()
	rpcserverthread = None
	if master == myIP :
		rpcserverthread = RPCServer()
		rpcserverthread.start()
	analyzerthread = analyzerThread()
	stagerthread = stagerThread()
	stagerthread.start()
	analyzerthread.start()
	stagerthread.join()
	analyzerthread.join()
	if RPCServerThread :
		RPCServerThread.join()
	fmt.join()

## Recieve packets for ~3 seconds. At end, set
## master to mode of current master and received possible masters.
## If an authority master packet is received, set master
## and return true immediately. Otherwise, return false.
def receiveUseMyMasterPackets() :
	global master
	insock.settimeout(.3)
	possiblemasters = []
	starttime = time.time()
	while (time.time()-starttime) < 3 :
		try :
			(msg, addr) = recvPacket()
			if msg.split()[0] == AUTH :
				master = msg.split()[1]
				return True
			if msg.split()[0] == USE :
				possiblemasters.append(msg.split()[1])
			if msg.split()[0] == ANN :
				outsock.sendto(USE + " " + str(master), (addr[0],port))
		except socket.timeout :
			pass
	possiblemasters.append(master)
	master = mode(possiblemasters)
	return False

def phase2() :
	global master
	lastmaster = None
	while not (lastmaster == master) :
		sendUseMyMasterPacket()
		lastmaster = master
		if receiveUseMyMasterPackets() : #True indicates authority packet received.
			break

def phase1() :
	numtries = 20
	interval = .2 # seconds
	global master
	while numtries > 0 :
		sendAnnouncePacket()
		try :
			(msg, addr) = recvPacket()
		except socket.timeout :
			numtries -= 1
			continue
		else :
			if msg.split()[0] == USE :
				master = msg.split()[1]
				return False
			if msg.split()[0] == AUTH :
				master = msg.split()[1]
				return True
		numtries -= 1
		time.sleep(interval)
	master = myIP
	return False

def runElectionProtocol() :
	if not phase1() : phase2()
	setMasterAndForkThreads()

#################  Arg Parsing and Main Function  #############################

def parseArgs()
	global insock, port, myIP, outfile, tstormspath, proxy, progressproxy
	myIP = getIP()
	port = int(sys.argv[1])
	insock.bind(("0.0.0.0",port))
	input_files = open(sys.argv[2]).read().splitlines()
	outfile = sys.argv[3]
	if outfile[-1] != '/' : outfile = outfile + '/'
	tstormspath = sys.argv[4]
	if tstormspath[-1] != '/' : tstormspath = tstormspath + '/'
	cmd = "export PATH=$PATH:"+tstormspath+"/source/trajectory/:"+tstormspath+"/source/tstorms/"
	commands.getoutput(cmd)
	if len(sys.argv) == 6 :
		path = sys.argv[5]
		if path[0] != 'h' : path = "http://" + path
		progressproxy = xmlrpclib.ServerProxy(path)
