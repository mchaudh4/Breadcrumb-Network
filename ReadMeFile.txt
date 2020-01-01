Introduction
  ------------
  These python3 codes are sufficent to run the entire breadcrumb network, which can be used
  by the autonmous vehicle to navigate.
  There are 4 types of Nodes present. They are as follows:
(1) Coordinator
--------------- 
There should be only one coordinator in the entire system. The python file, 
which should run in the coordinator is =>  CoordinatorCode.py

(2) Static Router Nodes with GPS
--------------------------------
 These nodes are installed after the Coordinator. They have GPS 
and XBee Connected to them. The python file which should run in the Static Router Node with GPS is
=> StaticNodeWithGPSAndApproxGPSCode.py

(3) Static Router Node without GPS
----------------------------------
  This node can be installed between any two Static Router nodes 
with GPS connected to them. The python file which should run in the Static Router Node without GPS
is => StaticNodeWithoutGPS.py 

(4) Moving Node
---------------
This node will collect the GPS data unicasted towards itself. It will keep on storing 
data in the MySQL database. The python file which should run in the moving node is =>MovingVehicle.py

(5) Tool For Installation
-------------------------
 This tool is made using RaspberryPi and Xbee. This tool is very useful
to install the new node at the farthest possible distance. The python file running in the node is=>
ToolForInstallation.py

Note- myFile.txt is used for storing the MAC address and NodeIds. Keep it in all RaspberryPis.
----


Solving the Mounting Problem
----------------------------
(1)In this project, we are using two USB ports of RaspberryPi. There is problem of port interchangeability.
To solve this problem, we need to remotely access the raspberryPi. If the raspberryPi has a Wifi connectivity,
so ssh or use Mobaxterm software to remotely access the RaspberryPi.
(2) On the terminal run
sudo nano /etc/udev/rules.d/99-usb.rules

Write the below lines in the nano file 99-usb.rules
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6015", ATTRS{serial}=="DN05KFQE", SYMLINK+="Xbee", MODE="0666"

SUBSYSTEM=="tty", DRIVERS=="pl2303", SYMLINK+="Gps"
 KERNEL="ttyUSB*", MODE= "0666"


In this file, ATTRS{serial} depends on the XBee USB connector. After connecting the USB connector, one need to check its serial number
and replace it with the sample number i have put.
The command to know this serial number is 
 udevadm info -a -n /dev/ttyUSB0 | grep '{serial}' | head -n1

This will solve the port interchangeability problem.

Installations Required
----------------------
(1) Configure the XBee using XCTU software. All the Routers, Moving Node and Installation Tool are configured in Router API 2 mode.
To run these programs, it is necessary to give Router nodes Node Ids as 1, 2,3,4 etc in increasing order.
	(a) Give the node id of -1 to installation Tool.
	(b) Give the Node id of -2 to moving vehicle.
	(c) Give the node id of 0 to the Coordinator Node.

(2) Install GPS library by =>   pip3 install gps
(3) Install python3 Xbee libary =>  pip3 install digi-xbee
(4) Install GPIO pin library=>  sudo apt-get install python3-gpiozero
(5)  Install GPSD to run GPS 
The following commands need to be executed.
	(a)sudo apt-get install gpsd gpsd-clients python-gps
	(b)sudo gpsd /dev/Gps -F /var/run/gpsd.sock
	(c) cgps -s
	(d) sudo systemctl stop gpsd.socket
	(e) sudo systemctl disable gpsd.socket
	(f) cgps -s
	(g) sudo reboot
	(h) cgps -s
	(i) cd /etc
	(j) sudo default
	(k) sudo nano gpsd
	After opening this file
	GPSD_OPTIONS="\dev\Gps"
	GPSD_SOCKET="\var\run\gpsd.sock"

	(l)sudo systemctl enable gpsd.socket
	(m) sudo systemctl start gpsd.socket
	(n) sudo reboot
	(o) cgps -s

After these installations, the system will run.

How to Start a program with boot
------------------------------------
For making a program run on RaspberryPi after PowerOn, we use crontab.
Go to the terminal and execute the command

crontab -e

Then write

Example,
-------
@reboot sudo python3 /home/pi/MovingVehicle.py &

After power on, the MovingVehicle.py code will run on RaspberryPi.



       