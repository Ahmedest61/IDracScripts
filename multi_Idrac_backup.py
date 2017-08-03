import string
import paramiko
import re
import subprocess,math
from math import *
from subprocess import *
import os
import json
import pandas as pd
import sys
import time

NoOfIdracs = input('Enter the number of IDRACs :')

IdracList=[]
for i in range(0,NoOfIdracs):
	Idrac=[]
	IpAddress=raw_input('Enter the IP Address for IDRAC :')
        Idrac.append (IpAddress)
        User=raw_input('Enter the user name for IDRAC :')
        Idrac.append (User)
        Pass=raw_input('Enter the Password for IDRAC  :')
        Idrac.append (Pass)
        IdracList.append(Idrac)


print IdracList

HwInventoryList=[]
for idracNo in range(0,len(IdracList)):
	ssh=paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		ssh.connect(IdracList[idracNo][0],username=IdracList[idracNo][1],password=IdracList[idracNo][2])
		stdin,stdout,stderr=ssh.exec_command("racadm hwinventory")
	        HwInventoryList.append(stdout.readlines())
        	ssh.close()

	except Exception as e:
		print "ssh.connect not work for %s" %(IdracList[idracNo][0])
	
if len(HwInventoryList) <1:
	sys.exit()

#print HwInventoryList
#print "Length of HwInventory: %s"%len(HwInventoryList)

search_dimm = "InstanceID: DIMM.Socket"
search_size = "Size ="

search_cpu = "InstanceID: CPU.Socket"
search_nfp = "NumberOfProcessorCores"
search_ht = "HyperThreadingEnabled = Yes"

dumy_mem=''
dumy_cpu=''

search_nic = "InstanceID: NIC.Integrated"

dumy_mem_list=[]
dumy_cpu_list=[]
TotalIdracsOutput=len(HwInventoryList)
yes=1
yes1=0
Result=''
OutputIndex=0
for IdracNo in range(0,TotalIdracsOutput):
	cur_tim = time.strftime("_%Y%m%d_%H%M%S")
	name="OutputIdrac"+str(IdracNo+1)+cur_tim+".xls"
	
	#Result.append(dumy_result)	
	if yes == 0:
		continue
	OutputLength=len(HwInventoryList[IdracNo])
	print ("Inventory length : %d"%OutputLength)	
	for OutputIndex in range(0,len(HwInventoryList[IdracNo])):
		
		with open(name,"w+") as fptr:
			if search_dimm in HwInventoryList[IdracNo][OutputIndex]:
				#print HwInventoryList[IdracNo][OutputIndex]
				while(OutputIndex<OutputLength):
				#	print "Dim "
					if "[" in HwInventoryList[IdracNo][OutputIndex+1]:
						break
				
					#if search_size in HwInventoryList[IdracNo][OutputIndex+1]:	
					#	dumy_mem+=(HwInventoryList[IdracNo][OutputIndex+1])
					#	break
					Result=json.dumps(HwInventoryList[IdracNo][OutputIndex],fptr)
					df= pd.read_json(HwInventoryList[IdracNo][OutputIndex])
					df.to_excel(name)					
					#print HwInventoryList[IdracNo][OutputIndex]
					#print Result
					#el
				
					OutputIndex+=1
			elif search_nic in HwInventoryList[IdracNo][OutputIndex]:
				while(OutputIndex<OutputLength):
					if "[" in HwInventoryList[IdracNo][OutputIndex+1]:
						break
					Result=json.dumps(HwInventoryList[IdracNo][OutputIndex],fptr)
				
				
					OutputIndex+=1
			elif search_cpu in HwInventoryList[IdracNo][OutputIndex]:
		        	while(OutputIndex+1<OutputLength):
					#print "OutputIndex :%d OutputLength :%d"%(OutputIndex,OutputLength) 
					#print HwInventoryList[IdracNo][OutputIndex]
		               		if search_ht in HwInventoryList[IdracNo][OutputIndex+1]:
		                       		hyper_thread=1
					Result=json.dumps(HwInventoryList[IdracNo][OutputIndex],fptr)
					#if search_nfp in HwInventoryList[IdracNo][OutputIndex+1]:
		                       	#	dumy_cpu+=(HwInventoryList[IdracNo][OutputIndex+1])	
					#	break                                
		               		#el
				
		                	OutputIndex+=1
		#print Result
#	df= pd.read_json(Result)
#	df.to_excel(name)
	#dumy_cpu_list.append(dumy_cpu)
	#dumy_mem_list.append(dumy_mem)
	if yes1==0:
		continue
	memorys_array = []
	memorys_array = [int(s) for s in dumy_mem.split() if s.isdigit()]
	Memory_splitLine = dumy_mem.splitlines()
	index=0
	for line in Memory_splitLine:
        	size = line.split()[2]
        	size_type = line.split()[3]

        	if size_type == "PB":
                	memorys_array[index]=size* math.pow(1024,3)
        	elif size_type == "TB":
                	memorys_array[index]=size* math.pow(1024,2)
       		elif size_type == "GB":
			memorys_array[index]=size* math.pow(1024,1)
        	elif size_type == "KB":
                	memorys_array[index]=size/1024
        	index+=1

	total_memory = 0
	total_memory = sum([int(x) for x in memorys_array])

	print "Total Memory: %dMB / %dGB"%(total_memory,total_memory/1024)
	cpu_array = []
	cpu_array = [int(s) for s in dumy_cpu.split() if s.isdigit()]
	total_cpu = 0
	total_cpu = sum([int(x) for x in cpu_array])

	if hyper_thread==1:
		print"Hyper threading enabled; total CPU: %d"%(total_cpu*2)
	else:
		print"Hyper threading disabled; total CPU: %d"%(total_cpu)
	dumy_mem=''
	dumy_cpu=''
#print dumy_cpu_list
#print dumy_mem_list



#print Result

	
