#******************************************************************************************************************#
#                       University of North Carolina at Charlotte                                                  #
#                               ECE Department                                                                     #
#                                                                                                                  #
#                                                                                                                  #
#                                                                                                                  #
#                                                                                                                  #
#   File Name: CoordinatorCode.py                                                                                  #
#   Project: MSEE Thesis: Wireless Sensor Network Breadcrumb Trail for an Autonomous Vehicle                       #
#   Created :  July 2, 2019                                                                                        #
#   Created by: Manu Chaudhary                                                                                     #
#                                                                                                                  #
#                                                                                                                  #
#   Description:                                                                                                   #
#       (1)This Code works in the Static Router Nodes without GPS.                                                 #
#       (2)It receives GPS data of the Previous and Next Node.                                                     #
#       (3)Approximately calculate its GPS Location using GPS data of Previous Node and Next Node.                 #
#       (4)Send the GPS data calculated to Previous and Next Node.                                                 #
#       (3)XBee is attached to the USB port in Router API2 Mode with a Node Id of an Interger(Example 1,2,3,4 etc).#
#       (4) USB ports are named as Xbee and Gps, so that they identify GPS  and Xbee Module on attaching.          #
#                                                                                                                  #
#                                                                                                                  #
#   References: https://www.digi.com/blog/introducing-the-official-digi-xbee-python-library/                       #
#               http://www.catb.org/gpsd/gpsd.html                                                                 #
#*******************************************************************************************************************

import gps 
import time
import serial
import sys
from select import select
from digi.xbee.devices import XBeeDevice
from digi.xbee.packets.base import DictKeys
import time
from gpiozero import LED
from math import sin, cos, sqrt, atan2, radians



from digi.xbee.models.status import NetworkDiscoveryStatus
from digi.xbee.devices import XBeeDevice

import threading 
from threading import Thread 

import queue

PORT = "/dev/Xbee"
BAUD_RATE = 57600
device = XBeeDevice(PORT, BAUD_RATE)

qPreviousNodeData= queue.Queue(maxsize=30)                         #   Inititializing a Queue
qNextNodeData=queue.Queue(maxsize=30)


class test():
 
 #***************** Storing Data Coming from Previous and Next Node into the Queue***************************#
   
    def StoringDataComingFromPreviousNodeNextNode(self):
        PORT = "/dev/Xbee"
        BAUD_RATE = 57600
        device = XBeeDevice(PORT, BAUD_RATE)
        file3= open("myFile.txt","r")
        dataReadInString3= file3.read()
        print("INSIDE RECEIVER")
        dataReadInString3 = dataReadInString3.replace("\n", "")
        #print(dataReadInString3)
        dataReadAfterRemovingString3 = dataReadInString3.split("  ")
        print(dataReadAfterRemovingString3)
        list_number3 = []
        for mot3 in dataReadAfterRemovingString3:
            # Create list with [id, name]
            list_elt3 = mot3.split(" - ")
            # Append to the list of id the current id
            list_number3.append(list_elt3[1])
        print(list_number3)
            
        list_number_inIntPreviousNode= int(max(list_number3))     #  NodeID of Previous Node
        list_number_nodeIdOfTheNextNode= int(list_number_inIntPreviousNode+2)   #  NodeID of Next Node
        

        ReceivedData=0
        
        while ReceivedData<3:
            try:
                print("Entering the Receiver")
                device.open()       
                #time.sleep(1)
                device.flush_queues()
                ReceivedData= ReceivedData+1
               
                #print(ord(rssi))
                data = device.read_data(timeout=30)     # Reads data
                #time.sleep(4)
                print("The Value of DATA is ")
                print(data)

                if data is not None:
                    data1 = data.to_dict()                      # Gets the message information as a 
                    rssi = device.get_parameter("DB")           #Gets RSSI value of the last packet
                    print((data1['Data: ']).decode() +"|"+ "Rssi:"+ str(ord(rssi)))
                    dataReceivedOtherNodes= (data1['Data: ']).decode() +" "+str(ord(rssi))
                    print("The Data Received is   ")
                    print(dataReceivedOtherNodes)  #  For Debugging Purpose

                    list_the_dataReceived= []

                    list_the_dataReceived = dataReceivedOtherNodes.split(" ")
                    print("TRYING TO KNOW THE NODE ID")
                    print(list_the_dataReceived[0])
                    if(int(list_the_dataReceived[0])==list_number_inIntPreviousNode):
                    	qPreviousNodeData.put(dataReceivedOtherNodes)
                                

                    if(int(list_the_dataReceived[0])==list_number_nodeIdOfTheNextNode):
                        qNextNodeData.put(dataReceivedOtherNodes)

                    print(qPreviousNodeData.queue)  # Printing the Queue Storing Previous Node Data
                    print(qNextNodeData.queue)        # printing the Queue Storing Next Node Data
                    #time.sleep(4)

                               
                
                #sem.release()
                time.sleep(2)
        
            except KeyError:
                pass
                #sem.release()
                #time.sleep(4)
            except KeyboardInterrupt:
                quit()
            except StopIteration:
                session = None
                print("No incoming data from the GPS module")
                #sem.release()
    
            except:
                #time.sleep(4)
                #sem.release()
                pass
            finally:
                if device is not None and device.is_open():
                    device.close()


#***************** Haversine Formula*********************#

    def my_distanceCalculate(self,latitudeInfloatPrevious,longitudeInfloatPrevious,latitudeInfloatNext,longitudeInfloatNext):
        R = 6373.0
        lat1 = radians(latitudeInfloatPrevious)
        lon1 = radians(longitudeInfloatPrevious)
        lat2 = radians(latitudeInfloatNext)
        lon2 = radians(longitudeInfloatNext)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c*1000


        print("Distance in m:", distance)
        #print("Should be:", 278.546, "km")

        return distance

#***************** Interpolate to Find the Latitude and Longitude*********************#

    def interpolate(self,p1,p2,r):

        return p1 * r + p2*(1-r)


#***************** Approximate GPS Calculation*********************#

    def calculateApproximateGPSLocation(self):

        print("Entering inside CalculateApprox GPS function")

        latitudeInfloatPrevious=0
        longitudeInfloatPrevious=0
        latitudeInfloatNext=0
        longitudeInfloatNext=0

        if not qPreviousNodeData.empty():

            listStoringPreviousNodeGPS= []
            previousNodeGPS= qPreviousNodeData.get(timeout=2)
            listStoringPreviousNodeGPS= previousNodeGPS.split(" ")
            #print(listStoringPreviousNodeGPS[6])

            print("Trying to find RSSI value..")

            rssiValueinIntPrevious= int(listStoringPreviousNodeGPS[5])
            print("The RSSI value obtained from Previous Node is ...")
            print(rssiValueinIntPrevious)
            # Distance of Previous to Current

            distanceOfPreviousToCurrent= float(10 ** ((rssiValueinIntPrevious- 38)/(10*2))) # Distance of Previous to Current
            print("Distance between Previous to Current "+str(distanceOfPreviousToCurrent))

            latitudeInfloatPrevious= float(listStoringPreviousNodeGPS[1])
            print("PreviousNode Latitude..")
            print(latitudeInfloatPrevious)
            print("Previous Node Longitude..")
            longitudeInfloatPrevious= float(listStoringPreviousNodeGPS[2])
            print(longitudeInfloatPrevious)

            # Again put the Data Back in the qPreviousNodeGPS from where it is Taken
            qPreviousNodeData.put(previousNodeGPS)
            print("Data again put Back to queue qPreviousNodeData")



        if not qNextNodeData.empty():

            listStoringNextNodeGPS= []
            nextNodeGPS= qNextNodeData.get(timeout=2)
            listStoringNextNodeGPS= nextNodeGPS.split(" ")
            #print(listStoringPreviousNodeGPS[6])

            rssiValueinIntNext= int(listStoringNextNodeGPS[5])
            print("The RSSI value obtained from Next Node is ..")
            print(rssiValueinIntNext)

            # Distance of Next to Current
            distanceOfNextToCurrent= float(10 ** ((rssiValueinIntNext- 47)/(10*2))) # Distance of Next to Current
            print("Distance between Next and current "+ str(distanceOfNextToCurrent))


            latitudeInfloatNext= float(listStoringNextNodeGPS[1])
            print("NextNode latitude..")
            print(latitudeInfloatNext)

            longitudeInfloatNext= float(listStoringNextNodeGPS[2])
            print("NextNode longitude..")
            print(longitudeInfloatNext)
            qPreviousNodeData.put(nextNodeGPS)
            print("Data again put Back to queue qPreviousNodeData")


        
        if(latitudeInfloatPrevious!=0 and longitudeInfloatPrevious!=0 and latitudeInfloatNext !=0 and longitudeInfloatNext !=0):
        # Finding Distance using Haversine formula
            distBetPreviousNext=self.my_distanceCalculate(latitudeInfloatPrevious,longitudeInfloatPrevious,latitudeInfloatNext,longitudeInfloatNext)
            print("Distance between Previous and Next node using Haversine "+str(distBetPreviousNext))
            print("Trying to locate Unknown Node from Previous")

            locateUnknownNodeFromPrevious= (distanceOfPreviousToCurrent/(distanceOfPreviousToCurrent+ distanceOfNextToCurrent))* distBetPreviousNext
            print(locateUnknownNodeFromPrevious)

            print("Finding the Ratio of Location from Previous to Total")

            ratioOfLocationFromPreviousToTotal= locateUnknownNodeFromPrevious/distBetPreviousNext
            print(ratioOfLocationFromPreviousToTotal)

            print("Finding P1")

            p1= complex(latitudeInfloatPrevious,longitudeInfloatPrevious)

            print("Finding P2")
            p2=complex(latitudeInfloatNext,longitudeInfloatNext)



            p3= self.interpolate(p1,p2,ratioOfLocationFromPreviousToTotal)

            print("Finding P3")
            print("Approximate Latitude")
        
            approximateLatitude= p3.real 
            print(approximateLatitude)
            print("Approximate Longitude")

            approximateLongitude= p3.imag
            print(approximateLongitude)

            print("Combined Approximate Latitude and Longitude")
            ApproxLatLong= str(approximateLatitude)+" "+str(approximateLongitude)
            print(ApproxLatLong)

            return ApproxLatLong

        return 0 # If above cases fails, then return Zero



#***************** Unicasting Data to Previous Node,Next Node and Moving Node.**************#
#************Unicasting Data Received from Next Node to Moving Vehicle*********************#

    def unicastingDataFromQueueOfPreviousCurrentNextNode(self):
        print("Inside")
        #count1=0
        #print(count1)
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
        list_number_nodeIdOfTheNode= str(list_number_inInt+1)
        print("Node Id of Current Node "+list_number_nodeIdOfTheNode)
        REMOTE_NODE_ID_PREVIOUSNODE= str(list_number_inInt)
        print("Node Id of Previous Node "+ REMOTE_NODE_ID_PREVIOUSNODE)
        REMOTE_NODE_ID_NEXTNODE= str(list_number_inInt +2)
        print("Node Id of the Next Node "+ REMOTE_NODE_ID_NEXTNODE)
        REMOTE_NODE_ID= "-1"                 # This is for the Coordinator

        
        print(max(list_number))   #  The largest list_number is the LAST NODE Deployed

                
        PORT = "/dev/Xbee"
        BAUD_RATE = 57600
        device = XBeeDevice(PORT, BAUD_RATE)
        DATA_TO_SEND= "Hello Xbee"
        

        try:
         
            print("Testing Queue which takes incoming data from own GPS Empty or Not Empty") 
            time.sleep(1)            
            try:
              
                
                print("Going into Calculate Approximate GPS")

                newApproximateLatitudeAndLongitude= self.calculateApproximateGPSLocation()

                if len(newApproximateLatitudeAndLongitude)> 0:

                    approximateGPSData= list_number_nodeIdOfTheNode +" "+newApproximateLatitudeAndLongitude+ "Approx lat long"         

                    # Approximate GPS Data of Current Node Send to MOVING VEHICLE
                    #------------------------------------------------------------
                    device.open()
                    xbee_network= device.get_network()
                    remote_device= xbee_network.discover_device(REMOTE_NODE_ID)
                    if remote_device is None:
                        print("couldnot find the remote device")
                        #time.sleep(4)   # For Debugging
                        exit(1)
                    print("Sending data to %s >> %s..." %(remote_device.get_64bit_addr(),DATA_TO_SEND))
            
                    #time.sleep(4)         # For Debugging
        
                    device.send_data(remote_device,approximateGPSData) # After checking GPS data, it is send
                              

                    print("success")
                    #time.sleep(2)
            
                    print("Sending Data of its own GPS to Coordinator")
            
                    #time.sleep(6)

                    #Approximate GPS of Current Node send to PREVIOUS NODE
                    #-----------------------------------------------------
                    device.open()
                    xbee_network= device.get_network()
                    remote_device= xbee_network.discover_device(REMOTE_NODE_ID)
                    if remote_device is None:
                        print("couldnot find the remote device")
                        #time.sleep(4)   # For Debugging
                        exit(1)
                    print("Sending data to %s >> %s..." %(remote_device.get_64bit_addr(),DATA_TO_SEND))
            
                    #time.sleep(4)         # For Debugging
        
                    device.send_data(remote_device,approximateGPSData) # After checking GPS data, it is send
                              

                    print("success")
                    #time.sleep(2)
            
                    print("Sending Data of its own GPS to Coordinator")
            


                    #Approximate GPS of Current Node send to NEXT NODE
                    #-------------------------------------------------
                    device.open()
                    xbee_network= device.get_network()
                    remote_device= xbee_network.discover_device(REMOTE_NODE_ID)
                    if remote_device is None:
                        print("couldnot find the remote device")
                        
                        exit(1)
                    print("Sending data to %s >> %s..." %(remote_device.get_64bit_addr(),DATA_TO_SEND))
                   
                    device.send_data(remote_device,approximateGPSData) # After checking GPS data, it is send
                              

                    print("success")
                    #time.sleep(2)
            
                    print("Sending Data of its own GPS to Coordinator")
            
                    



                
                else :
                    print("The nextNode of Node is Still not installed for complete Approximate Localization of current Node")
                    
                    device.open()
                    xbee_network= device.get_network()
                    remote_device= xbee_network.discover_device(REMOTE_NODE_ID)
                    if remote_device is None:
                        print("couldnot find the remote device")
                        #time.sleep(4)   # For Debugging
                        exit(1)
                    print("Sending data to %s >> %s..." %(remote_device.get_64bit_addr(),DATA_TO_SEND))
            
                    #time.sleep(4)         # For Debugging
                    approximateGPSData="The Next node "+list_number_nodeIdOfTheNode+ " is Still not Installed"
        
                    device.send_data(remote_device,approximateGPSData) # After checking GPS data, it is send
                              
                    print("success")
                    #time.sleep(2)
            
                    print("Sending Data of its own GPS to Coordinator")
            
                    #time.sleep(6)

            except:
                print("Unicast to Moving Vehicle not Complete")                
            finally:
                if device is not None and device.is_open():
                    device.close()
                     


            if not qPreviousNodeData.empty():          # Data Received from Previous Node is Send to Moving Vehicle
                print("Testing Queue which takes incoming data From Previous/Next Node Empty or Not Empty")     
                time.sleep(1)        
                try:
                    #time.sleep(5)    
                    device.open()
                    xbee_network= device.get_network()
                    remote_device= xbee_network.discover_device(REMOTE_NODE_ID)
                    if remote_device is None:
                        print("couldnot find the remote device")                        
                        exit(1)
                        
                    print("Sending data to %s >> %s..." %(remote_device.get_64bit_addr(),DATA_TO_SEND))                                

                    GpsOfPreviousNode= qPreviousNodeData.get(timeout=2)  # Gps of previous Node put in a Variable
                    device.send_data(remote_device,GpsOfPreviousNode)
                                                
                    print("success")                                            
                    print("Sending Data of Previous/Next Node to Coordinator")  
                    qPreviousNodeData.put(GpsOfPreviousNode)     # Again putting the Gps Data to Queue to save imp data            
                    
                except:
                    print("Unicasting the data of Previous/Next node to Coordinator not Complete ")
                    
                finally:
                    if device is not None and device.is_open():
                        device.close()
                        
            
            if not qNextNodeData.empty():          # Queue qPreviousNodeData stores the Data coming Previous and Next Node
                print("Testing Queue which takes incoming data From Previous/Next Node Empty or Not Empty")     
                time.sleep(1)        
                try:
                    #time.sleep(10)    
                    device.open()
                    xbee_network= device.get_network()
                    remote_device= xbee_network.discover_device(REMOTE_NODE_ID)
                    if remote_device is None:
                        print("couldnot find the remote device")
                        #time.sleep(4)   # For Debugging
                        exit(1)
                        
                    print("Sending data to %s >> %s..." %(remote_device.get_64bit_addr(),DATA_TO_SEND))
                    GpsOfNextNode= qNextNodeData.get(timeout=2)       # Gps of next Node put in a Variable               
                    device.send_data(remote_device,GpsOfNextNode)
                                                
                    print("success")
                                                
                    print("Sending Data of Previous/Next Node to Coordinator")  
                    qNextNodeData.put(GpsOfNextNode)   # Gps of next Node put Back to the Queue              
                    #time.sleep(6)
                except:
                    print("Unicasting the data of Previous/Next node to Coordinator not Complete ")
                    #time.sleep(10)
                finally:
                    if device is not None and device.is_open():
                        device.close()
                                             

         
                                                                                 
        
        except:
            print("Unicasting Function Not Working")



 #*******************Help in Installing the RaspberryPi at  the Location**************************#
    
def helpInInstallingTheRaspberryPi():           
    PORT = "/dev/Xbee"
    BAUD_RATE = 57600
    device = XBeeDevice(PORT, BAUD_RATE)    
    print("INSIDE RECEIVER FOR INSTALLATION")
    
    while True:
        try:
            print("Entering Installation Method")
            from gpiozero import LED
            
            device.open()       
            #time.sleep(1)
            device.flush_queues()   
                                          
            data = device.read_data(timeout=10000)        # Reads data
            rssi = device.get_parameter("DB")           #Gets RSSI value of the last packet Received
            data1 = data.to_dict()                      # Gets the message information as a dictionary
            print((data1['Data: ']).decode() +" "+ "Rssi:"+" " + str(ord(rssi))+"|")
            dataReceivedOtherNodes= (data1['Data: ']).decode() +"|"+ "Rssi:" +"-"+str(ord(rssi))
            device.close()
            
            print("The Data being gathered before Installation to find the Optimal Location for Deployment")
            
            rssiForFindingPlacement= str(ord(rssi))
            print(rssiForFindingPlacement)
            print("Before if")

            
            if int(rssiForFindingPlacement) > 70:
                print("RSSI Lower Threshold Reached. Place the Breadcrumb Node")
                led= LED(18)
                led.on()
                time.sleep(30)        # 30 Seconds is the time till which LED will glow.
                led.off()
                print("LED should stop")
                return
            else:
                print("Move AWAY")
            
            #time.sleep(4)    
            
            
        except KeyError:
            pass
            #time.sleep(4)
        except KeyboardInterrupt:
            quit()
        except StopIteration:
            session = None
            print("No incoming data from the GPS module")
            
        except:
            #time.sleep(4)
            pass



    
    
#********************************** Help in Discovering the Previous Node, Current Node and Next Node****************************#
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

        xbee_network.set_discovery_timeout(15)  # 15 seconds. # I have changed it to 25

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
    main()                             

    #helpInInstallingTheRaspberryPi()

    testingNow= test()

    

    while True:
        print("Storing function starts")
        testingNow.StoringDataComingFromPreviousNodeNextNode()
        print("Storing function Ends")
        print("Unicasting to Previous, Next and Coordinator Node Function Starts")
        testingNow.unicastingDataFromQueueOfPreviousCurrentNextNode()
    
        print("Unicasting to Previous, Next and Coordinator Node Function Ends")
    
    #time.sleep(600)

    while True:
        pass



    


            



