from random import randint
file = open("DataFile.txt","w+")
pid=1
atime=0
cpu=0
io=0
while (pid <= 1000):
    file.write("%i,%i," % (pid,atime))
    pid = pid+1
    atime = atime+5
    y = randint(1,50)
    for y in range (0,y):
        cpu = randint(1,20)
        io = randint(1,20)
        file.write("%i,%i," % (io,cpu))
    file.write("\n")
file.close()
