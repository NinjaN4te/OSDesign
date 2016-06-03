"""
This is the First Come First Serve Algorithm which will process our data file

NOTES:
    1. First thing that needs to happen is every process needs to be stored into a queue should a current process not be complete before another arrives
        a. Best way is to use an array with push and pop data structure --need to look to see if python can do that
    2. Current process need to be go through the algorithm and be put into a wait queue to mimic IO bursts
    3. ALSO INCLUDE AN AGING FEEDBACK no priority feedback since its FCFS
    4. Need to figure out how to seperate values
        Givens: I know that the first 2 values are the pid and arrival time
    ??? Do I need a global timer for counting arrival time?
"""
store = 0
ptime = 0
gtime = 0 #need to parse in a global variable
with open("DataFile.txt") as file:
    for line in file:
        process =line.rstrip()#seperates file by whitespace
        data = process.split(",")
        pid = data[0]
        atime = data[1]
        service=data[2:] #The list is also counting the nullspace at the end of the list therefore trueLength=length-1
        for i in range(0,len(service)-1): #iterates through each line based on length of data, len(service)-1 due to empty space '' and end of list
            store = int(service[i]) + store #since this is just FCFS we will treat io bursts and cpu bursts as the same since once in a wait queue it will wait until it is out of it to continue processing
        print("The PID is %s the arrival time is %s and the process time is %i" % (pid,atime,store))
        for j in range (0,store): #actual FCFS processing
            ptime = ptime + 1 #process time increment
            gtime = gtime + 1 #global time increment
        print (ptime , gtime+int(atime))

