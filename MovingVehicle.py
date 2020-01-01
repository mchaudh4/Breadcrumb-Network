#********************************************************************************************************************#
#                       University of North Carolina at Charlotte                                                    #
#                               ECE Department                                                                       #
#                                                                                                                    #
#                                                                                                                    #
#                                                                                                                    #
#                                                                                                                    #
#   File Name: MovingVehicle.py                                                                                      #                                                               #
#   Project: MSEE Thesis: Wireless Sensor Network Breadcrumb Trail for an Autonomous VEHICLE                         #
#   Created :  July 2, 2019                                                                                          #
#   Created by: Manu Chaudhary                                                                                       #
#                                                                                                                    #
#                                                                                                                    #
#   Description:                                                                                                     #
#       (1)This Code works in the Moving Node.                                                                       #
#       (2)It Receives the Data coming towards it from different Nodes                                               #
#       (3)The data is stored in MySql Server installed inside the Node                                              #
#       (6) USB ports are named as Xbee and Gps, so that it identify Xbee Module on attaching it to USB port.        #
#                                                                                                                    #
#                                                                                                                    #
#   References: https://www.digi.com/blog/introducing-the-official-digi-xbee-python-library/                         #
#               http://www.catb.org/gpsd/gpsd.html                                                                   #
#*********************************************************************************************************************

import gps 
import time
import serial
import sys
from select import select
from digi.xbee.devices import XBeeDevice
from digi.xbee.packets.base import DictKeys
import time
import MySQLdb
from gpiozero import LED


from digi.xbee.models.status import NetworkDiscoveryStatus
from digi.xbee.devices import XBeeDevice

import threading 
from threading import Thread 
#sem= threading.Semaphore()  # Try and Apply Semaphore on the Queue
import queue
PORT = "/dev/Xbee"
BAUD_RATE = 57600
device = XBeeDevice(PORT, BAUD_RATE)




class test():
#******************************Storing Data Coming from Different Nodes*****************************8#
    def StoringDataComingFromDifferentNodes(self):
        PORT = "/dev/Xbee"
        BAUD_RATE = 57600
        device = XBeeDevice(PORT, BAUD_RATE)  
        #dataReceived=0  
        print("Entering the Receiver")    
        while True:
            try:
                
                device.open()   
                device.flush_queues()    
                
                rssi = device.get_parameter("DB")           #Gets RSSI value of the last packet
                #print(ord(rssi))
                data = device.read_data(timeout=1000)        # Reads data
                if data is not None:
                    data1 = data.to_dict()                      # Gets the message information as a 
                    rssi = device.get_parameter("DB")           #Gets RSSI value of the last packet
                    #print((data1['Data: ']).decode() +" "+ str(ord(rssi)))
                    dataReceivedOtherNodes= (data1['Data: ']).decode() +" "+str(ord(rssi))
                    #print("The Data Received is   ")
                    print(dataReceivedOtherNodes)  #  For Debugging Purpose
                    time.sleep(1)
                
            except KeyError:
                pass
                #sem.release()
                time.sleep(1)
            except KeyboardInterrupt:
                quit()
            except StopIteration:
                session = None
                print("No incoming data from the GPS module")
                #sem.release()
    
            except:
                pass

            finally:
                if device is not None and device.is_open():
                    device.close()

            # Storing the Received Data into MySQL database. Comment out the below try and except, if MySQL is not installed.
            try:
                db=MySQLdb.connect("localhost","root","int3rneT@","intruder")
                #print("Success")

                curs=db.cursor()
                sql = "INSERT INTO coordinatorNode (gpsData, status) VALUES (%s, %s)"
                val = (dataReceivedOtherNodes,"New")
                curs.execute(sql, val)
                #print("success3")

                db.commit()
                

            except Exception as error: 
                print(error)




if __name__=='__main__':

    testingNow= test()
        
    print("Storing all the Data coming to Moving Vehicle Node")
    testingNow.StoringDataComingFromDifferentNodes()
        

    while True:
        pass



    


            


