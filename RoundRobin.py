"""
Round Robin
    This program needs take a process
    have it process for a certain amount of cycles for either I/O or cpu bursts
    it also needs to keep track of PID and arrival time and have a round robin queue for it
    should an I/O or CPU burst finish early it will still need to wait for the remainder time to finish before moving on
    in the RR queue if the process is less than the process time it will wait for it until process time finishes and not move on
    if the process is over the process time then it will store the rest of the value in a queue
    if statement to allow for arrival time
"""
from collections import deque
import re
#global varaibles
gtime = 0
total_turnaround =0
total_response =0
total_wait=0
plength = 1000
slice_t = 25
class process():
    def __init__(self,store,pid,ptime,atime): #Defines process and the different parameters in a process
        self.store=store
        self.ptime=ptime
        self.pid=pid
        self.atime=int(atime)
        self.index=0
        self.turnaround_t =0
        self.response_t=-1
        self.wait_t =0
        self.total_store =0
        for t in self.store:
            self.total_store += t
    def run(self): #algorithm which will run each process line
        global gtime
        if self.response_t < 0 or gtime-int(self.atime) < self.response_t:
            self.response_t = gtime - int(self.atime)
        try:
            self.store[self.index]-=slice_t #computes by the round robin time of 10
            gtime+=slice_t #since the round robin computes at 10 at a time then it needs to increment global time by 10
            if(self.store[self.index]<0):
                if(self.index%2==0): #finished a process going into an i/o burst
                    self.index+=1
                    print ("process {:}: io interrupt".format(self.pid))
                    return "incomplete"
                else: #finished io going into process
                    self.index+=1
                    self.store[self.index]+=self.store[self.index-1]
                print ("process {:}: time interrupt".format(self.pid))
                return "incomplete"
        except IndexError: # Will finish when it completes the list
            print ("Process {:} Finished".format(self.pid))
            self.turnaround_t = gtime - int(self.atime)
            self.wait_t = self.turnaround_t - self.total_store
            return "complete"

with open("DataFile.txt") as file: #puts data file into a process table
    plist = deque(process(list(map(int, re.sub('[\n\s,]+$','',data).split(",")[2:])), data.split(",")[0],0,data.rstrip('\n').split(",")[1]) for data in file)
while len(plist) > 0: #runs our process and when done it will return "complete"
    currentp = plist.pop()
    status=currentp.run()
    if status != "complete":
        plist.appendleft(currentp)
    else:
        total_turnaround+=currentp.turnaround_t
        total_wait+=currentp.wait_t
        total_response+=currentp.response_t
avg_turnaround = total_turnaround/plength
avg_wait = total_wait/plength
avg_response = total_response/plength
#prints the variables of average throughput, turnaround, wait, and response time
print(plength/gtime)
print(avg_turnaround)
print(avg_wait)
print(avg_response)