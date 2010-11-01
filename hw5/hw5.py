# Daren Hasenkamp
# 19362801

import numpy as np
import sqlite3, os, webbrowser, sys
import matplotlib.pyplot as plt

createdfiles = []

# this function compares dates!
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
days = [31,28,31,30,31,30,31,31,30,31,30,31]
def datecmp(a, b) :
    if months.index(a[0:3]) < months.index(b[0:3]) : return 1
    if months.index(a[0:3]) > months.index(b[0:3]) : return -1
    if int(a[3:]) < int(b[3:]) : return 1
    return -1

# this function takes a list of polls and returns the most recent one!
def mostrecentpoll(polls) :
    mostrecent = polls[0]
    for p in polls :
        if datecmp(mostrecent[3],p[3]) == 1 : mostrecent = p
    return mostrecent

# this returns the day of the year that date ("Sep03" or something) represents!
def dayofyear(date) :
    day = 0
    for n in range(0,months.index(date[0:3])) :
        day += days[n]
    day += int(date[3:])
    return day

# I'm doing everything in memory. I had trouble getting sqlite and python
# to work correctly together saving databases. I think it's a version mismatch;
# I'm using sqlite 2.8 and I should probably be using sqlite 3. Either way,
# it works fine if i do things in memory.
connection = sqlite3.connect(":memory:")
cursor = connection.cursor()

# add table for part A
def partA() :
    polldata = np.loadtxt("senate_polls.raw", dtype=str)
    for row in polldata :
        row[4] = row[4] + row[5]
        row[6] = row[6] + row[7]
        for n in range(9, len(row)) :
            row[8] = row[8] + " "+ row[n]
    cmd = "create table polls (state text, dem integer, gop integer, ind integer, start text, end text, pollster text)"
    cursor.execute(cmd)
    for row in polldata :
        # i know i shouldn't do it like this (sql injection vulnerability). i'd change it but MEH
        cmd = "insert into polls (state, dem, gop, ind, start, end, pollster) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (row[0],row[1],row[2],row[3],row[4],row[6],row[8])
        cursor.execute(cmd)

# add table for part b
def partB() :
    candidates = np.loadtxt("candidate_names.txt",dtype=str,delimiter=',')
    cmd = "create table candidates (state text, dem text, gop text, ind text, incumbent text)"
    cursor.execute(cmd)
    for row in candidates :
        cmd = 'insert into candidates (state, dem, gop, ind, incumbent) values ("%s","%s","%s","%s","%s")' % (row[0],row[1],row[2],row[3],row[4])
        cursor.execute(cmd)

# add table for part C
def partC() :
    # i want to be a cartographer
    candidates = map(lambda s: s.strip(),os.popen("ls -1 candidates").readlines())
    cmd = "create table pictures (cand text, pic text)"
    cursor.execute(cmd)
    for c in candidates :
        cmd = 'insert into pictures (cand, pic) values ("%s","%s")' % (c.split('.')[0], "candidates/"+c)
        cursor.execute(cmd)

def buildpage(state) :
    # tee hee i get off on writing ugly code, ps i'm a virgin
    # Get name and picture for each candidate, also get incumbent
    cmd = "select cand, pic, incumbent from candidates, pictures where state='"+str(state)+"' and cand=dem"
    democrat = cursor.execute(cmd).fetchall()
    cmd = "select cand, pic, incumbent from candidates, pictures where state='"+str(state)+"' and cand=gop"
    republican = cursor.execute(cmd).fetchall()
    cmd = "select cand, pic, incumbent from candidates, pictures where state='"+str(state)+"' and cand=ind"
    independent = cursor.execute(cmd).fetchall()

    # Get most recent poll for state
    cmd = "select dem, gop, ind, end, pollster from polls where state='"+str(state)+"'"
    poll = mostrecentpoll(cursor.execute(cmd).fetchall())

    # build html string
    html = "<html><head><title>SHITDUDETHISISFUN</title></head><body><h1>"+str(state)+" CANDIDATES</h1><br>"
    # add each candidates name/picture in
    if len(democrat) > 0 :
        html += "Democrat: "+democrat[0][0]+"<br><img src='"+democrat[0][1]+"'><br><br><br>"
    if len(republican) > 0 :
        html += "Republican: "+republican[0][0]+"<br><img src='"+republican[0][1]+"'><br><br><br>"
    if len(independent) > 0 :
        html += "Independent: "+independent[0][0]+"<br><img src='"+independent[0][1]+"'><br><br><br>"

    # add the latest poll in
    html += "<h2>LATEST POLL:</h2>Dem: "+str(poll[0])+" GOP: "+str(poll[1])+" Independent: "+str(poll[2])+" Date: "+poll[3]+" Source: "+poll[4]+"<br>"

    # decide whether the incumbent is winning or not
    # (WTF IS READABILITY???)
    if ((poll[0]>poll[1] and poll[0]>poll[2] and democrat[0][2]=="Democrat") or (poll[0]<poll[1] and poll[2]<poll[1] and democrat[0][2]=="Republican")) :
        html += "INCUMBENT IS POISED TO WIN"
    else : html += "INCUMBENT IS POISED TO LOSE"

    #close the html string
    html += "</body></html>"
    
    # write the html to a file and save the filename (for later deletion), then open the html file
    fname = state+".html"
    f = open(fname,"w")
    f.write(html)
    f.close()
    createdfiles.append(fname)
    webbrowser.open(fname)

def partD() :
    while True :
        x = raw_input("Enter a state to build webpage for (capitalized appreviation, ex: CA): ").strip()
        try : buildpage(x)
        except : break

def partE() :
    # get a list of tuples of (state,incumbent) from the database
    cmd = "select state, incumbent from candidates"
    states = cursor.execute(cmd).fetchall()
    # for each state: if incumbant is democrat and democrat is losing, add one to poisedtolose
    # If incumbent is republican and democrat is winning, subtract one from poisedtolose
    poisedtolose = 0
    for state in states :
        cmd = "select dem, gop, ind, end, pollster from polls where state='"+str(state[0])+"'"
        poll = mostrecentpoll(cursor.execute(cmd).fetchall())
        # if incumbant is democrat and democrat is losing:
        if (state[1]=="Democrat" and (poll[0]<poll[1] or poll[0]<poll[2])) : poisedtolose += 1
        # if incumbent is republican and democrat is winning
        if (state[1]=="Republican" and poll[0]>poll[1] and poll[0]>poll[2]) : poisedtolose -= 1
    print "The democrats are poised to lose " + str(poisedtolose) + " seats."

def makeplot(state) :
    # Get all the poll data and read it into a list of tuples
    cmd = "select dem, gop, ind, end from polls where state='"+str(state)+"'"
    polls = cursor.execute(cmd).fetchall()
    gross = []
    for poll in polls :
        gross.append((dayofyear(poll[3]),poll[0],poll[1],poll[2]))
    # sort the list of tuple on day of year
    gross = sorted(gross, key=lambda x: x[0])

    # populate the arrays we will pass to matplotlib
    dates = []
    dems = []
    gops = []
    inds = []
    for t in gross :
        dates.append(t[0])
        dems.append(t[1])
        gops.append(t[2])
        inds.append(t[3])
    
    # get all of the candidates
    cmd = "select dem, gop, ind from candidates where state='"+state+"'"
    cands = cursor.execute(cmd).fetchall()
    dem = cands[0][0]
    gop = cands[0][1]
    ind = cands[0][2]

    # plot that shit
    plt.plot(dates,dems,label=dem,color="blue")
    plt.plot(dates,gops,label=gop,color="red")
    if (ind[0]!=" ") :
        plt.plot(dates,inds,label=ind,color="green")
    plt.ylabel("Percentage")
    plt.xlabel("Day of year")
    plt.legend()
    plt.show()
    
#interactive graph generator loop
def partF() :
    while True:
        x = raw_input("Enter a state to build plot for (capitalized appreviation, ex: CA): ").strip()
        try : makeplot(x)
        except : break

# add a poll to the database
def partG(state, dem, gop, ind, start, end, pollster) :
    cmd = "insert into polls (state, dem, gop, ind, start, end, pollster) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (state,int(dem),int(gop),int(ind),start,end,pollster)
    cursor.execute(cmd)
    

if __name__ == "__main__" :
    # Populate database
    partA()
    partB()
    partC()

    # Add more polls to database if user so desires
    print "Before computing statistics, would you like to insert any extra polls into the database?"
    print "\tUsage:\t<state> <dem percent> <gop percent> <independent percent> <startdate> <enddate> <pollster>"
    print "\t\tStart/end date must be of the form XxxYY, where Xxx is the first three letters of the month with"
    print "\t\tthe first letter capitalized and YY is the day. Pollster can be whatever you want but I'm only gonna"
    print "\t\tparse the first word :P"
    print "\tAny unparsable input will break this prompt loop."
    while True :
        x = raw_input("> ").split()
        try : partG(x[0],x[1],x[2],x[3],x[4],x[5],x[6])
        except : break

    # print number of seats democrats are poised to lose
    partE()
    # interactive webpage generator loop
    partD()
    # interactive graph generator loop
    partF()
