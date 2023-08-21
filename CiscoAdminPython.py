import serial.tools.list_ports
from tkinter import *
from functools import partial
import time


ser = serial.Serial()
hostname = "Router"


def get_device_name():
    global hostname
    ser.write("\x1A".encode('utf-8'))
    line = ser.readline()
    line = line.decode('utf-8').strip()
    if line and line != "":
        #get the first word of the line
        line = line.split()[0]
        hostname = line
        print("Hostname : " + hostname)


def list_available_com_ports():
    com_ports = list(serial.tools.list_ports.comports())
    available_ports = []
    
    for port in com_ports:
        available_ports.append(port.device)
    
    return available_ports


def list_available_interfaces():
    global hostname
    ser.write("\x1A".encode('utf-8'))
    time.sleep(1)
    ser.write("enable \r\n".encode('utf-8'))
    time.sleep(1)
    ser.write("show ip int brief \r\n".encode('utf-8'))
    while ser.out_waiting > 0:
        print("sending " + str(ser.in_waiting)+ " bytes")

    print(hostname)
    list_interfaces = []
    headerpassed = False

    while True:
        line = ser.readline()
        line = line.decode('utf-8').strip()
        
        if line :
            if line == "" or line == hostname+"#^Z" or line == hostname+"#" or line == hostname+"#enable" or line == hostname+"#show ip int brief":
                pass
            else:
                if headerpassed == False:
                    headerpassed = True
                else:
                    #check if the line's first word is "Interface" to avoid the header
                    if line.split()[0] != "Interface":
                        line = line.split()
                        list_interfaces.append(line[0])
                    else:
                        pass
        else:
            for i in list_interfaces:
                #add the interface to the spinbox
                int_spinbox.config(values=list_interfaces)
            break

    return list_interfaces


def get_settings_from_interface(interface):
    global hostname
    ser.write("\x1A".encode('utf-8'))
    time.sleep(1)
    ser.write("enable \r\n".encode('utf-8'))
    time.sleep(1)
    ser.write("show run \r\n".encode('utf-8'))
    while ser.out_waiting > 0:
        print("sending " + str(ser.in_waiting) + " bytes")
    interfacefound = False
    while True:
        line = ser.readline()
        line = line.decode('utf-8').strip()
        if line:
            if line == "" or line == hostname+"#^Z" or line == hostname+"#" or line == hostname+"#enable" or line == hostname+"#show run":
                continue
            else:
                if line == "--More--":
                    ser.write("\x20".encode('utf-8'))
                
                if interfacefound == False:
                    if line == "interface " + interface:
                        interfacefound = True
                else:
                    if line.split()[0] == "ip":
                        if line.split()[1] == "address":
                            ip_router_entry.delete(0, END)
                            ip_router_entry.insert(0, line.split()[2])
                            ip_mask_entry.delete(0, END)
                            ip_mask_entry.insert(0, line.split()[3])
                            break


def open_serial_port(port):
    global ser
    ser = serial.Serial(port, 9600, timeout=0.5)
    print("Port {} ouvert.".format(port))
    get_device_name()
    list_available_interfaces()


def close_serial_port():
    ser.close()
    print("Port {} fermé.".format(ser.name))


def setipv4config(int, ip, mask ):
    ser.write("enable\n".encode('utf-8'))
    ser.write("conf t\n".encode('utf-8'))



if __name__ == "__main__":
    root = Tk()

    ip_router_label = Label(root, text="IP :")
    ip_mask_label = Label(root, text="Mask :")
    COMportopen_label = Label(root, text="COM Port :")
    int_label = Label(root, text="Interface :")

    ip_router_entry = Entry(root, width=15, textvariable=StringVar(value=""))
    ip_mask_entry = Entry(root)

    COMportopen_spinbox = Spinbox(root, values=list_available_com_ports())
    int_spinbox = Spinbox(root, values="SELECT_COM_PORT_FIRST")

    COMportopen_button = Button(root, text="Set ", command=lambda:open_serial_port(COMportopen_spinbox.get()))
    COMportclose_button = Button(root, text="Close", command=lambda:close_serial_port())
    int_button = Button(root, text="Get", command=lambda:get_settings_from_interface(int_spinbox.get()))
    setipv4config_button = Button(root, text="Set IP", command=lambda:setipv4config(ip_router_entry.get(), ip_mask_entry.get()))

    COMportopen_label.grid(column=0, row=0)
    COMportopen_spinbox.grid(column=1, row=0)
    COMportopen_button.grid(column=2, row=0)
    COMportclose_button.grid(column=3, row=0)
    int_label.grid(column=0, row=1)
    int_spinbox.grid(column=1, row=1)
    int_button.grid(column=2, row=1)
    ip_router_label.grid(column=0, row=2)
    ip_router_entry.grid(column=0, row=3)
    ip_mask_label.grid(column=2, row=2)
    ip_mask_entry.grid(column=2, row=3)
    setipv4config_button.grid(column=4, row=3)

    root.title("Cisco Admin Python")
    root.mainloop()