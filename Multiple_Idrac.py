import string
import paramiko
import re
import subprocess,math
from math import *
from subprocess import *
import os
import json
import pandas as pd
from datetime import datetime
from ConfigParser import *
from ConfigParser import (ConfigParser, MissingSectionHeaderError,
                          ParsingError, DEFAULTSECT)
import ConfigParser


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


#print IdracList

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
		print ("ssh.connect not work for %s",IdracList[idracNo][0])
	

#print HwInventoryList
print "Length of HwInventory: %s"%len(HwInventoryList)

search_dimm = "InstanceID: DIMM.Socket"
search_size = "Size ="

search_cpu = "InstanceID: CPU.Socket"
search_nfp = "NumberOfProcessorCores"
search_ht = "HyperThreadingEnabled = Yes"
search_nic = "InstanceID: NIC.Integrated"

dumy_mem=''
dumy_cpu=''
dumy_nic=''

dmem=''
dcpu=''
dcpu=''

dumy_mem_list=[]
dumy_cpu_list=[]
TotalIdracsOutputs=len(HwInventoryList)
Mem_section_list=[]
mem_size_list=[]
Result=[]
for IdracNo in range(0,TotalIdracsOutputs):
	time=datetime.utcnow().strftime("%s")
	filename="Idrac"+str(IdracNo)+"_"+time+".ini"
	fptr= open(filename,"w+")
	for line in HwInventoryList[IdracNo]:
		if "--" in line:
			continue
		fptr.write("%s\n" % line) 
#	fptr.write(HwInventoryList[IdracNo])
	fptr.close()	
	
	Config = ConfigParser.ConfigParser()
	Config.read(filename)
#	print "Config Section ",Config.sections()
	#dumy_result=json.dumps(HwInventoryList[IdracNo])
	#Result.append(dumy_result)	
	
	Mem_section_list = [s for s,s in enumerate(Config.sections()) if "InstanceID: DIMM.Socket" in s]
	
	for mem_sec in Mem_section_list:
		mem_size_list+=[Config.get(str(mem_sec),'Size')]
	
	for index in range(0,len(mem_size_list)):	
		if "MB" in mem_size_list[index]:
			value=mem_size_list[index].replace("MB","")
			mem_size_list[index] = value
		elif "PB" in mem_size_list[index]:
			value=mem_size_list[index].replace("PB","")
			value*= math.pow(1024,3);	
			mem_size_list[index] = value
		elif "TB" in mem_size_list[index]:
			value=mem_size_list[index].replace("TB","")
			value*= math.pow(1024,2);	
			mem_size_list[index] = value
		elif "GB" in mem_size_list[index]:
			value=mem_size_list[index].replace("GB","")
			value*= math.pow(1024,1);	
			mem_size_list[index] = value
		elif "KB" in mem_size_list[index]:
			value=mem_size_list[index].replace("KB","")
			value/=1024	
			mem_size_list[index] = value
	
	T_memory = sum([int(x) for x in mem_size_list])
	print T_memory 
	OutputSize=len(HwInventoryList[IdracNo])
	for OutputIndex in range(0,len(HwInventoryList[IdracNo])):
		if search_dimm in HwInventoryList[IdracNo][OutputIndex]:
			while(OutputIndex<OutputSize):
				dmem+=HwInventoryList[IdracNo][OutputIndex+1]
				Result.append(json.dumps(dmem))
				if search_size in HwInventoryList[IdracNo][OutputIndex+1]:	
					dumy_mem+=(HwInventoryList[IdracNo][OutputIndex+1])
					break
				elif "[" in HwInventoryList[IdracNo][OutputIndex+1]:
					break
				OutputIndex+=1

		elif search_nic in HwInventoryList[IdracNo][OutputIndex]:
			while(OutputIndex<OutputSize):
				
				OutputIndex+=1

		elif search_cpu in HwInventoryList[IdracNo][OutputIndex]:
                	while(OutputIndex<OutputSize):
                       		if search_ht in HwInventoryList[IdracNo][OutputIndex+1]:
                               		hyper_thread=1

				if search_nfp in HwInventoryList[IdracNo][OutputIndex+1]:
                               		dumy_cpu+=(HwInventoryList[IdracNo][OutputIndex+1])	
					break                                
                       		elif "[" in HwInventoryList[IdracNo][OutputIndex+1]:
                            		break
                        	OutputIndex+=1
	#dumy_cpu_list.append(dumy_cpu)
	#dumy_mem_list.append(dumy_mem)
	
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
#print type(Result)
#result=''
#result=''.join(str(x) for x in Result)
#print Result
#df= pd.read_json(dumy_mem)
#df.to_excel('output.xls')	
