"""
This program will create a data file in the format of
Process ID, Arrival Time, IO Burst, CPU Burst
"""
from random import randint #imports the random functions
file = open("DataFile3.txt","w+") #creates a datafile w+ to create and modify values
pid=1 #sets the process id to 1
atime=0 # arrival time
cpu=0 # initialize cpu variable
io=0 #initialize I/O variable
while (pid <= 3): #loop for pid to be 1000
    file.write("%i,%i," % (pid,atime)) #writes the first 2 values of of PID and arrival time sperated by commas
    pid = pid+1 #pid++
    atime = atime+5 #increment arrival time by 5
    y = randint(1,5) #select random value to mimic process length
    for y in range (0,y):
        cpu = randint(1,20)
        io = randint(1,20)
        file.write("%i,%i," % (io,cpu)) #writes to file the io and cpu burst times
    file.write("\n") #new line once yrange is finished
file.close() #close file
