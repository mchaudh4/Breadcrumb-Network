#*********************************************************************************************************#
# 						University of North Carolina at Charlotte										  #
#								ECE Department                                                            #
#                                                                                                         #
#                                                                                                         #
#                                                                                                         #
#                                                                                                         #
#	File Name: ToolForInstallation.py 																	  #
#	Project: MSEE Thesis: Wireless Sensor Network Breadcrumb Trail for an Autonomous Vehicle              #
#	Created :  July 2, 2019                                                                               #
#	Created by: Manu Chaudhary                                                                            #
#                                                                                                         #
#                                                                                                         #
#	Description:                                                                                          #
#		(1)This Code helps in the installation of New Node.                                               #
#		(2)It sends Hello Messages to new powered on Node continously and help in its Installation        #
#		(3)XBee is attached to the USB port in Router API2 Mode with a Node Id of -2                      #
#		(4) The USB port name is changed to Xbee to solve port interchangeability Issue                   #
#	                                                                                                      #
#                                                                                                         #
#	References: https://www.digi.com/blog/introducing-the-official-digi-xbee-python-library/              #
#*********************************************************************************************************#
import time
import serial
import sys
from select import select
from digi.xbee.devices import XBeeDevice
from digi.xbee.packets.base import DictKeys
import time
from math import sin, cos, sqrt, atan2, radians



from digi.xbee.models.status import NetworkDiscoveryStatus
from digi.xbee.devices import XBeeDevice

import threading 
from threading import Thread 

import queue

PORT = "/dev/Xbee"
BAUD_RATE = 57600
device = XBeeDevice(PORT, BAUD_RATE)


class test():
 
    def unicastingDataFromQueueOfPreviousCurrentNextNode(self):    
        print("Inside")
        count1=0
        print(count1)
        file= open("myFile.txt","r")
        dataReadInString= file.read()
        dataReadInString = dataReadInString.replace("\n", "")
        print(dataReadInString)
        dataReadAfterRemovingString = dataReadInString.split("  ")
        print(dataReadAfterRemovingString)
        list_number = []
        for mot in dataReadAfterRemovingString:
            # Create list with [id, name]
            list_elt = mot.split(" - ")
            # Append to the list of id the current id
            list_number.append(list_elt[1])
        print(list_number)
            
        list_number_inInt= int(max(list_number))    
        REMOTE_NODE_ID_PREVIOUSNODE= str(list_number_inInt)
        
        
        print(max(list_number))   #  The largest list_number is the LAST NODE Deployed

                
        PORT = "/dev/Xbee"
        BAUD_RATE = 57600
        device = XBeeDevice(PORT, BAUD_RATE)
        DATA_TO_SEND= "Hello Xbee"
        
        
        while True:
            try:

                try:                                # Sending Hello Messages
                        
                    device.open()
                    xbee_network= device.get_network()
                    remote_device= xbee_network.discover_device(REMOTE_NODE_ID_PREVIOUSNODE)
                    if remote_device is None:
                        print("couldnot find the remote device")
                        #time.sleep(4)   # For Debugging
                        exit(1)
                        
                    print("Sending data to %s >> %s..." %(remote_device.get_64bit_addr(),DATA_TO_SEND)) # Data send to newest powerON node
                    #time.sleep(1)
                                                    
                    device.send_data(remote_device,"HELLO")                               
                    print("success")       
                    count=count+1                       
                    print("Sending Hello Message to calculate LOW THRESHOLD RSSI")
                    
                    time.sleep(5)
                except:
                    print("Sending Hello Message to calculate LOW THRESHOLD RSSI not Complete ")
                    time.sleep(5)
                finally:
                    if device is not None and device.is_open():
                        device.close()
                        time.sleep(5)

                
                
             
            except KeyboardInterrupt:
                quit()
                                                                       
            
            except:
                print("Unicasting Function Not Working")



def main():
    print(" +---------------------------------------------+")
    print(" | Discovering all nearbly Xbee Devices |")
    print(" +---------------------------------------------+\n")
    #time.sleep(20)
    f= open("myFile.txt","r+")
    f.truncate(0)    

    device = XBeeDevice(PORT, BAUD_RATE)
    
    try:
        device.open()

        xbee_network = device.get_network()

        xbee_network.set_discovery_timeout(25)  # 15 seconds. 

        xbee_network.clear()


        # Callback for discovered devices.
        def callback_device_discovered(remote):
            file1= open("myFile.txt","a")  #  writing in File in Append Mode
            file1.write(" "+str(remote)+" ")
            file1.close()            
            print("Device discovered: %s" % remote)


        # Callback for discovery finished.
        def callback_discovery_finished(status):
            if status == NetworkDiscoveryStatus.SUCCESS:
                print("Discovery process finished successfully.")
            else:
                print("There was an error discovering devices: %s" % status.description)


        xbee_network.add_device_discovered_callback(callback_device_discovered)
        
        xbee_network.add_discovery_process_finished_callback(callback_discovery_finished)

        xbee_network.start_discovery_process()

        print("Discovering remote XBee devices...")

        while xbee_network.is_discovery_running():
            time.sleep(0.1)

    finally:
        if device is not None and device.is_open():
            device.close()
            print("main function ended")



if __name__=='__main__':
    main()                             #  Starting method to DISCOVER all the NODES Around

    
    testingNow= test()

    
    testingNow.unicastingDataFromQueueOfPreviousCurrentNextNode()
    
    while True:
        pass



    


            


