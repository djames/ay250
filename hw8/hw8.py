# Daren Hasenkamp
# 19362801

import sys

# If user didn't set PYTHONPATH, try adding ../hw5/
# to the path (this is the right place in the directory structure)
try : from hw5 import partA, partB, makeplot, partG
except ImportError :
    sys.path.append("../hw5/")
    from hw5 import partA, partB, makeplot, partG

# Building database in memory; this is how I did hw5.
# You'll be able to add polls using argparse but they
# won't be saved between program invocations.
partA()
partB()

# (state, dem, gop, ind, start, end, pollster)
import argparse
parser = argparse.ArgumentParser(description="Polling application")
parser.add_argument('-p', action='store_true',default=False,dest="addpoll",help="Add a poll")
parser.add_argument('-state', action='store',dest='state',default="CA")
parser.add_argument('-dem',action='store',dest='dem',default=51)
parser.add_argument('-gop',action='store',dest='gop',default=49)
parser.add_argument('-ind',action='store',dest='ind',default=0)
parser.add_argument('-startmonth',action='store',dest='startmonth',default="September")
parser.add_argument('-startday',action='store',dest='startday',default=01)
parser.add_argument('-endmonth',action='store',dest='endmonth',default="October")
parser.add_argument('-endday',action='store',dest='endday',default=31)
parser.add_argument('-pollster',action='store',dest='pollster',default="herpderp")
parser.add_argument('-plot',action='store',dest='plot',default=None,help="show plot for state")
results = parser.parse_args()

if results.addpoll :
    state = results.state[0:2].upper()
    dem = int(results.dem)
    gop = int(results.gop)
    ind = int(results.ind)
    pollster = results.pollster

    # Get start date and coax it into right form
    startmonth = results.startmonth[0:3]
    startmonth = startmonth[0].upper() + startmonth[1:].lower()
    startday = int(results.startday)
    if startday < 10 :
        startdate = startmonth + "0"+str(startday)
    else : startdate = startmonth + str(startday)
    
    # Get endmonth and coax it into right form
    endmonth = results.endmonth[0:3]
    endmonth = endmonth[0].upper() + endmonth[1:].lower()
    endday = int(results.endday)
    if endday < 10 :
        enddate = endmonth + "0"+str(endday)
    else : enddate = endmonth + str(endday)
    
    # add poll in
    partG(state, dem, gop, ind, startdate, enddate, pollster)

if results.plot :
    state = results.plot[0:2].upper()
    makeplot(state)
