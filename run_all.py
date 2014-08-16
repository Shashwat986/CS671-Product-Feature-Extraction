import glob
import time
import os
import subprocess

lfiles = glob.glob(r'.\data\*')
logfile=open("log.txt","a")
logfile.write("="*80)
logfile.write("\n")
logfile.write(time.strftime("%d %b %Y %H:%M:%S")+"\n")
logfile.write("RUNNING SCRIPT OVER ALL FILES\n")
logfile.write("="*80)
logfile.write("\n")
logfile.close()

lfiles = ['./data/Canon S100.txt','./data/Creative Labs Nomad Jukebox Zen Xtra 40GB.txt','./data/Hitachi router.txt','./data/Nokia 6600.txt','./data/Nokia 6610.txt']

for file in lfiles:
	print ("'%s'" % file)
	#os.system("python '.\\backprop - 1.0.py' '%s'" % file)
	subprocess.call(['python',"backprop - 1.3.py", file])

logfile=open("log.txt","a")
logfile.write("\n")
logfile.write("="*80)
logfile.write("\n")
logfile.write(time.strftime("%d %b %Y %H:%M:%S")+"\n")
logfile.write("SCRIPT RUNNING ENDS\n")
logfile.write("="*80)
logfile.write("\n")

logfile.close()