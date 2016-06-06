"""
This is the First Come First Serve Algorithm
"""
#Global Variables
store = 0
gtime = 0 #need to parse in a global variable
turnaround_t = 0
add_turnaround = 0
wait_t = 0
total_wait = 0
response_t = 0
add_wait_t = 0
avg_throughput = 0
with open("DataFile.txt") as file:
    for line in file:
        process =line.rstrip()#seperates file by whitespace
        data = process.split(",")
        pid = data[0]
        ptime = 0
        atime = data[1]
        add_response = response_t
        response_t = gtime - int(atime) #calculation of response time
        total_response_t = response_t +add_response#calclation of total response time

        service=data[2:] #The list is also counting the nullspace at the end of the list therefore trueLength=length-1
        for i in range(0,len(service)-1): #iterates through each line based on length of data, len(service)-1 due to empty space '' and end of list
            store = int(service[i]) + store #since this is just FCFS we will treat io bursts and cpu bursts as the same since once in a wait queue it will wait until it is out of it to continue processing
        #print("The PID is %s the arrival time is %s and the process time is %i" % (pid,atime,store))
        for j in range (0,store): #actual FCFS processing
            ptime = ptime + 1 #process time increment
            gtime = gtime + 1 #global time increment
        #print ("The process time is %i and the global time is %i" %(ptime , gtime+int(atime)))
        add_turnaround = turnaround_t
        add_wait_t = wait_t
        turnaround_t = gtime-int(atime)
        wait_t = turnaround_t - ptime

        total_turnaround = add_turnaround+turnaround_t # calculation of turnaround time
        total_wait = total_turnaround - store
        avg_throughput = 1000/gtime
    print (total_turnaround/1000)
    print (total_wait/1000)
    print(total_response_t /1000)
    print (avg_throughput)