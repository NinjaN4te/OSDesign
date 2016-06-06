"""
Shortest Remaining Time
    This algorithm will take a process then compute process for a for either its cpu burst, then look at the rest
    of the list and based on the arrival time it will compare itself to those in its list and compute until its finished
    and will look at another process and computer that until another process is shorter
"""
from collections import deque
import re
#global variables
gtime = 0
plist = []
total_turnaround=0
total_response=0
total_wait=0
plength = 1000
class process(): #defines what we want to store in the class
    def __init__(self,store,pid,ptime,atime):
        self.store=store
        self.ptime=ptime
        self.pid=pid
        self.atime=int(atime)
        self.index=0
        self.remaint = 0
        self.turnaround_t=0
        self.response_t=-1
        self.wait_t =0
        self.total_store=0
        for x in self.store:
            self.total_store += x
        for t in self.store:
            self.remaint+=t
    def run(self):
        global gtime
        #algorithm for finding response time
        if self.response_t < 0 or gtime-int(self.atime) < self.response_t:
            self.response_t = gtime - int(self.atime)
        try:
            #increments our timing variables
            self.store[self.index]-=1
            self.remaint-=1
            gtime+=1
            if(self.store[self.index]<=0):
                if(self.index%2==0): #finished a process going into an i/o burst
                    self.index+=1
                    print ("process {:}: io interrupt".format(self.pid))
                    return "incomplete"
                else: #finished io going into process
                    self.index+=1
                    self.store[self.index]+=self.store[self.index-1]
                print ("process {:}: time interrupt".format(self.pid))
                return "incomplete"
        except IndexError:
            print ("Process {:} Finished".format(self.pid))
            self.turnaround_t = gtime - int(self.atime) #calculated turnaround time
            self.wait_t = self.turnaround_t - self.total_store #calculates wait time
            return "complete"

with open("DataFile.txt") as file: #computes our data file and put it into a process table
    notcreated = deque(process(list(map(int, re.sub('[\n\s,]+$','',data).split(",")[2:])), data.split(",")[0],0,data.rstrip('\n').split(",")[1]) for data in file)
while (len(notcreated) > 0 or len(plist)>0):
    gtime+=1
    try:
        if (gtime >= int(notcreated[0].atime)):
            addp = notcreated.popleft()
            plist.append(addp)
    except IndexError:
        pass
    if (len(plist)>0):
        short_t = plist[0].remaint
        index = 0
        for pid in range(0, len(plist)):
            if plist[pid].remaint < short_t:
                short_t = plist[pid].remaint
                index = pid
        status = plist[index].run()
        if status == "complete":
            total_turnaround += plist[index].turnaround_t
            total_wait += plist[index].wait_t
            total_response += plist[index].response_t
            del plist[index]

avg_turnaround = total_turnaround / plength
avg_wait = total_wait / plength
avg_response = total_response / plength
#prints our average throughput, turnaround, wait, and response times
print(plength/gtime)
print(avg_turnaround)
print(avg_wait)
print(avg_response)