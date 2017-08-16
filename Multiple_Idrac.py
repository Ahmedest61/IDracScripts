import string
import paramiko
import re
import subprocess
import math
from math import *
#from subprocess import *
import os
import json
import pandas as pd
from datetime import datetime
from ConfigParser import *
from ConfigParser import (ConfigParser, MissingSectionHeaderError,
                          ParsingError, DEFAULTSECT)
import ConfigParser
import collections
from collections import OrderedDict

NoOfIdracs = input('Enter the number of IDRACs :')

IdracList = []
for i in range(0, NoOfIdracs):
    Idrac = []
    IpAddress = raw_input('Enter the IP Address for IDRAC :')
    Idrac.append(IpAddress)
    User = raw_input('Enter the user name for IDRAC :')
    Idrac.append(User)
    Pass = raw_input('Enter the Password for IDRAC  :')
    Idrac.append(Pass)
    IdracList.append(Idrac)


HwInventoryList = []
for idracNo in range(0, len(IdracList)):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(IdracList[idracNo][0], username=IdracList[idracNo]
                    [1], password=IdracList[idracNo][2])
        stdin, stdout, stderr = ssh.exec_command("racadm hwinventory")
        HwInventoryList.append(stdout.readlines())
        ssh.close()
    except Exception as e:
        print ("ssh.connect not work for %s", IdracList[idracNo][0])


TotalIdracsOutputs = len(HwInventoryList)
TotalIdracsOutputs = 3
iDRAC_list = []
idrac_dumy_dic = OrderedDict()

Outfilename = "Idrac" + ".json"
fptr = open(Outfilename, "a")

for IdracNo in range(0, TotalIdracsOutputs):

    MemoryDictionary = {}
    Mem_section_list, mem_size_list, mem_speed_list, mem_descp_list, mem_serial_list, mem_model_list, mem_status_list = ([
    ]for i in range(0, 7))
    dumy_mem_dic = collections.defaultdict(dict)

    time = datetime.utcnow().strftime("%s")
    filename = "Idrac" + str(IdracNo) + ".ini"
    fptr = open(filename, "w+")

    for line in HwInventoryList[IdracNo]:
        if "--" in line:
            continue
        fptr.write("%s\n" % line)
    fptr.write(HwInventoryList[IdracNo])
    fptr.close()

    Config = ConfigParser.ConfigParser()
    Config.read(filename)
    Mem_section_list = [s for s, s in enumerate(
        Config.sections()) if "InstanceID: DIMM.Socket" in s]
    for mem_sec in Mem_section_list:
        mem_size_list += [Config.get(str(mem_sec), 'Size')]
        mem_speed_list += [Config.get(str(mem_sec), 'speed')]
        mem_descp_list += [Config.get(str(mem_sec), 'Manufacturer')]
        mem_serial_list += [Config.get(str(mem_sec), 'SerialNumber')]
        mem_model_list += [Config.get(str(mem_sec), 'Model')]
        mem_status_list += [Config.get(str(mem_sec), 'PrimaryStatus')]
    for index in range(0, len(mem_size_list)):
        if "MB" in mem_size_list[index]:
            value = mem_size_list[index].replace("MB", "")
            mem_size_list[index] = value
        elif "PB" in mem_size_list[index]:
            value = mem_size_list[index].replace("PB", "")
            value *= math.pow(1024, 3)
            mem_size_list[index] = value
        elif "TB" in mem_size_list[index]:
            value = mem_size_list[index].replace("TB", "")
            value *= math.pow(1024, 2)
            mem_size_list[index] = value
        elif "GB" in mem_size_list[index]:
            value = mem_size_list[index].replace("GB", "")
            value *= math.pow(1024, 1)
            mem_size_list[index] = value
        elif "KB" in mem_size_list[index]:
            value = mem_size_list[index].replace("KB", "")
            value /= 1024
            mem_size_list[index] = value

    mem_slots = len(mem_size_list)
    mem_info_dictionaries = [dict() for x in range(mem_slots)]
    mem_info_list = []

    for i in range(mem_slots):
        mem_info_dictionaries[i]['manufacturer'] = mem_descp_list[i]
        mem_info_dictionaries[i]['speed'] = mem_speed_list[i]
        mem_info_dictionaries[i]['model'] = mem_model_list[i]
        mem_info_dictionaries[i]['serial'] = mem_serial_list[i]
        mem_info_dictionaries[i]['status'] = mem_status_list[i]

    mem_info_list = mem_info_dictionaries

    idrac_dumy_dic['ip'] = str(IdracList[IdracNo][0])
    total_mem = str(sum([int(x) for x in mem_size_list]))
    idrac_dumy_dic['total_memory'] = total_mem + " MB"
    idrac_dumy_dic['memory_slots'] = mem_slots
    idrac_dumy_dic['memory_info'] = mem_info_list

    Cpu_section_list, cpu_processor_list, cpu_family_list, cpu_manufac_list, cpu_curr_clock_list, cpu_model_list = ([
    ]for i in range(6))
    cpu_prim_status_list, cpu_virt_list, cpu_voltag_list, cpu_enabled_thread_list, cpu_max_clock_speed_list = ([
    ]for i in range(5))
    cpu_ex_bus_clock_speed_list, cpu_hyper_thread_list, cpu_status_list = (
        []for i in range(3))

    CpuDictionary = {}
    dumy_cpu_dic = collections.defaultdict(dict)

    Cpu_section_list = [s for s, s in enumerate(
        Config.sections()) if "InstanceID: CPU.Socket" in s]

    for cpu_sec in Cpu_section_list:
        cpu_processor_list += [Config.get(str(cpu_sec),
                                          'NumberOfProcessorCores')]
        cpu_family_list += [Config.get(str(cpu_sec), 'CPUFamily')]
        cpu_manufac_list += [Config.get(str(cpu_sec), 'Manufacturer')]
        cpu_curr_clock_list += [Config.get(str(cpu_sec), 'CurrentClockSpeed')]
        cpu_model_list += [Config.get(str(cpu_sec), 'Model')]
        cpu_prim_status_list += [Config.get(str(cpu_sec), 'PrimaryStatus')]
        cpu_virt_list += [Config.get(str(cpu_sec),
                                     'VirtualizationTechnologyEnabled')]
        cpu_voltag_list += [Config.get(str(cpu_sec), 'Voltage')]
        cpu_enabled_thread_list += [Config.get(
            str(cpu_sec), 'NumberOfEnabledThreads')]
        cpu_max_clock_speed_list += [Config.get(str(cpu_sec), 'MaxClockSpeed')]
        cpu_ex_bus_clock_speed_list += [Config.get(
            str(cpu_sec), 'ExternalBusCLockSpeed')]
        cpu_hyper_thread_list += [Config.get(str(cpu_sec),
                                             'HyperThreadingEnabled')]
        cpu_status_list += [Config.get(str(cpu_sec), 'CPUStatus')]

    cpu_slots = len(cpu_processor_list)
    cpu_info_dictionaries = [dict() for x in range(cpu_slots)]
    cpu_info_list = []
    total_threads = 0
    for i in range(cpu_slots):
        cpu_info_dictionaries[i]['no_of_processors'] = cpu_processor_list[i]
        cpu_info_dictionaries[i]['cpu_family'] = cpu_family_list[i]
        cpu_info_dictionaries[i]['manufacturer'] = cpu_manufac_list[i]
        cpu_info_dictionaries[i]['current_clock_speed'] = cpu_curr_clock_list[i]
        cpu_info_dictionaries[i]['model'] = cpu_model_list[i]
        cpu_info_dictionaries[i]['primary_status'] = cpu_prim_status_list[i]
        cpu_info_dictionaries[i]['virtualization_technology_enabled'] = cpu_virt_list[i]
        cpu_info_dictionaries[i]['voltage'] = cpu_voltag_list[i]
        cpu_info_dictionaries[i]['no_of_enabled_thread'] = cpu_enabled_thread_list[i]
        cpu_info_dictionaries[i]['max_clock_Speed'] = cpu_max_clock_speed_list[i]
        cpu_info_dictionaries[i]['external_bus_clock_speed'] = cpu_ex_bus_clock_speed_list[i]
        cpu_info_dictionaries[i]['hyper_threading_enabled'] = cpu_hyper_thread_list[i]
        if cpu_hyper_thread_list[i] == "Yes":
            total_threads += int(cpu_enabled_thread_list[i])
        cpu_info_dictionaries[i]['cpu_status'] = cpu_status_list[i]

    cpu_info_list = cpu_info_dictionaries
    idrac_dumy_dic['cpu_slots'] = cpu_slots
    idrac_dumy_dic['cpu_threads'] = total_threads

    idrac_dumy_dic['cpu_info'] = cpu_info_list

    Nic_section_list, nic_manufac_list, nic_descrp_list, nic_dev_descrp_list, nic_fqdd_list = ([
    ]for i in range(5))
    nic_pci_sub_device_id_list, nic_pci_sub_vendor_id_list, nic_pci_device_id_list = (
        []for i in range(3))
    nic_pci_vendor_id_list, nic_bus_no_list, nic_slot_typ_list, nic_data_bus_width_list = ([
    ]for i in range(4))
    nic_fun_no_list, nic_dev_no_list = ([]for i in range(2))

    Nic_section_list = [s for s, s in enumerate(
        Config.sections()) if "InstanceID: NIC" in s]

    Nic_set = set()
    port_slots = len(Nic_section_list)
    for section in Nic_section_list:
        nic = section.split(" ")[1].split(".")[0] + "." + section.split(" ")[1].split(
            ".")[1] + "." + section.split(" ")[1].split(".")[2].split("-")[0]
        if nic not in Nic_set:
            Nic_set.add(nic)
    nic_slots = len(Nic_set)
    Nic_set_dic = dict()
    for nic in Nic_set:
        for nic_sec in Nic_section_list:
            if nic in nic_sec:
                if nic not in Nic_set_dic:
                    Nic_set_dic[nic] = list()
                    Nic_set_dic[nic].append(nic_sec)
                else:
                    Nic_set_dic[nic].append(nic_sec)

    NicDictionary = {}
    dumy_nic_dic = collections.defaultdict(dict)

    for nic_sec in Nic_section_list:
        nic_manufac_list += [Config.get(str(nic_sec), 'Manufacturer')]
        nic_descrp_list += [Config.get(str(nic_sec), 'Description')]
        nic_dev_descrp_list += [Config.get(str(nic_sec), 'DeviceDescription')]
        nic_fqdd_list += [Config.get(str(nic_sec), 'FQDD')]
        nic_pci_sub_device_id_list += [
            Config.get(str(nic_sec), 'PCISubDeviceID')]
        nic_pci_sub_vendor_id_list += [
            Config.get(str(nic_sec), 'PCISubVendorID')]
        nic_pci_device_id_list += [Config.get(str(nic_sec), 'PCIDeviceID')]
        nic_pci_vendor_id_list += [Config.get(str(nic_sec), 'PCIVendorID')]
        nic_bus_no_list += [Config.get(str(nic_sec), 'BusNumber')]
        nic_slot_typ_list += [Config.get(str(nic_sec), 'SlotType')]
        nic_data_bus_width_list += [Config.get(str(nic_sec), 'DataBusWidth')]
        nic_fun_no_list += [Config.get(str(nic_sec), 'FunctionNumber')]
        nic_dev_no_list += [Config.get(str(nic_sec), 'DeviceNumber')]

    nic_info_dictionaries = [dict() for x in range(port_slots)]

    for i in range(port_slots):
        nic_info_dictionaries[i]['manufacturer'] = nic_manufac_list[i]
        nic_info_dictionaries[i]['decription'] = nic_descrp_list[i]
        nic_info_dictionaries[i]['device_description'] = nic_dev_descrp_list[i]
        nic_info_dictionaries[i]['fqdd'] = nic_fqdd_list[i]
        nic_info_dictionaries[i]['pci_subdevice_id'] = nic_pci_sub_device_id_list[i]
        nic_info_dictionaries[i]['pci_Subvendor_id'] = nic_pci_sub_vendor_id_list[i]
        nic_info_dictionaries[i]['pci_Dev_id'] = nic_pci_device_id_list[i]
        nic_info_dictionaries[i]['pci_vendor_id'] = nic_pci_vendor_id_list[i]
        nic_info_dictionaries[i]['bus_number'] = nic_bus_no_list[i]
        nic_info_dictionaries[i]['slot_type'] = nic_slot_typ_list[i]
        nic_info_dictionaries[i]['data_bus_width'] = nic_data_bus_width_list[i]
        nic_info_dictionaries[i]['function_number'] = nic_fun_no_list[i]
        nic_info_dictionaries[i]['dev_number'] = nic_dev_no_list[i]

    nic_port_dictionaries = dict()

    for nic in Nic_set:
        dumy_dict = [dict() for x in range(len(Nic_set_dic[nic]))]
        ind = 0
        for nics in Nic_set_dic[nic]:
            for j in range(port_slots):
                if nic_info_dictionaries[j]['fqdd'] in nics:
                    dumy_dict[ind] = nic_info_dictionaries[j]
                    ind += 1
        nic_port_dictionaries[nic] = dumy_dict

    idrac_dumy_dic['nic_slots'] = nic_slots
    idrac_dumy_dic['ports'] = port_slots
    idrac_dumy_dic['nic_info'] = nic_port_dictionaries

    Drive_section_list, driv_dev_list, driv_dev_descrp_list, driv_ppid_list, temp_size_list = ([
    ]for i in range(5))
    driv_sas_address_list, driv_max_cap_speed_list, driv_used_siz_byte_list, driv_media_typ_list = ([
    ]for i in range(4))
    driv_blck_siz_byte_list, driv_bus_protocol_list, driv_serial_no_list, driv_manufacturer_list = ([
    ]for i in range(4))
    driv_fqdd_list, driv_slot_list, driv_raid_status_list, driv_predictiv_fail_status_list = ([
    ]for i in range(4))

    Drive_section_list = [s for s, s in enumerate(
        Config.sections()) if ("InstanceID: Disk") in s]
    i = 0
    drive_list_len = len(Drive_section_list)
    while(i < len(Drive_section_list)):
        if Config.has_option(Drive_section_list[i], "Device Type"):
            if "PhysicalDisk" not in Config.get(Drive_section_list[i], "Device Type"):
                del Drive_section_list[i]
            else:
                i += 1
                continue

    for dev_sec in Drive_section_list:
        driv_dev_list += [Config.get(str(dev_sec), 'Device Type')]
        driv_dev_descrp_list += [Config.get(str(dev_sec), 'DeviceDescription')]
        driv_ppid_list += [Config.get(str(dev_sec), 'PPID')]
        driv_sas_address_list += [Config.get(str(dev_sec), 'SASAddress')]
        driv_max_cap_speed_list += [
            Config.get(str(dev_sec), 'MaxCapableSpeed')]
        driv_used_siz_byte_list += [
            Config.get(str(dev_sec), 'UsedSizeInBytes')]
        temp_size_list += [Config.get(str(dev_sec), 'UsedSizeInBytes')]
        driv_media_typ_list += [Config.get(str(dev_sec), 'MediaType')]
        driv_blck_siz_byte_list += [
            Config.get(str(dev_sec), 'BlockSizeInBytes')]
        driv_bus_protocol_list += [Config.get(str(dev_sec), 'BusProtocol')]
        driv_serial_no_list += [Config.get(str(dev_sec), 'SerialNumber')]
        driv_manufacturer_list += [Config.get(str(dev_sec), 'Manufacturer')]
        driv_fqdd_list += [Config.get(str(dev_sec), 'FQDD')]
        driv_slot_list += [Config.get(str(dev_sec), 'Slot')]
        driv_raid_status_list += [Config.get(str(dev_sec), 'RaidStatus')]
        driv_predictiv_fail_status_list += [
            Config.get(str(dev_sec), 'PredictiveFailureState')]

    for index in range(0, len(temp_size_list)):
        if "Bytes" in driv_used_siz_byte_list[index]:
            value = int(temp_size_list[index].replace("Bytes", ""))
            value /= 1024 * 1024 * 1024
            temp_size_list[index] = value

    total_size = (sum([int(x) for x in temp_size_list]))
    driv_slots = len(Drive_section_list)
    driv_info_dictionaries = [dict() for x in range(driv_slots)]
    driv_info_list = []
    for i in range(driv_slots):
        driv_info_dictionaries[i]['device_type'] = driv_dev_list[i]
        driv_info_dictionaries[i]['device_description'] = driv_dev_descrp_list[i]
        driv_info_dictionaries[i]['ppid'] = driv_ppid_list[i]
        driv_info_dictionaries[i]['sas_address'] = driv_sas_address_list[i]
        driv_info_dictionaries[i]['max_capable_speed'] = driv_max_cap_speed_list[i]
        driv_info_dictionaries[i]['used_size_in_bytes'] = driv_used_siz_byte_list[i]
        driv_info_dictionaries[i]['media_type'] = driv_media_typ_list[i]
        driv_info_dictionaries[i]['block_size_in_bytes'] = driv_blck_siz_byte_list[i]
        driv_info_dictionaries[i]['bus_protocol'] = driv_bus_protocol_list[i]
        driv_info_dictionaries[i]['serial_no'] = driv_serial_no_list[i]
        driv_info_dictionaries[i]['manufacturer'] = driv_manufacturer_list[i]
        driv_info_dictionaries[i]['fqdd'] = driv_fqdd_list[i]
        driv_info_dictionaries[i]['slot'] = driv_slot_list[i]
        driv_info_dictionaries[i]['raid_status'] = driv_raid_status_list[i]
        driv_info_dictionaries[i]['predictive_failure_state'] = driv_predictiv_fail_status_list[i]

    driv_info_list = driv_info_dictionaries
    idrac_dumy_dic['drives'] = driv_slots
    idrac_dumy_dic['total_drives_size'] = str(total_size) + " GB"
    idrac_dumy_dic['drives_info'] = driv_info_list

    iDRAC_list.append(idrac_dumy_dic)


json.dump(iDRAC_list, fptr, indent=4, sort_keys=False, separators=(',', ':'))
fptr.close()

df = pd.read_json(iDRAC_list)
print "writing to file"
df.to_excel('output.xls')
