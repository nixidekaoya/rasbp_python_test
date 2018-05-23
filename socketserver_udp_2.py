#!usr/bin/python

import socket
import threading
import time
import sys
import Tkinter as tk
from PIL import Image
from PIL import ImageTk

command = ""
ip_port_1 = (('192.168.1.209',8000))
ip_port_2 = (('192.168.1.209',8001))
file_path = "/home/li/Desktop/python_test/output.jpg"
update_flag = False

class Guis(object):
    def __init__(self,master):
        self.master = master
        frame_1 = tk.Frame(master,width = 20, height = 5)
        frame_2 = tk.Frame(master,width = 200, height = 5)
        frame_3 = tk.Frame(master,width = 20, height = 5)
        frame_1.pack(side = tk.TOP)
        frame_2.pack()
        frame_3.pack(side = tk.BOTTOM)
        self.photo = Image.open(file_path)
        self.photo = ImageTk.PhotoImage(self.photo)
        self.label = tk.Label(master, image = self.photo)
        self.label.pack()

        self.button_up = tk.Button(frame_1, width = 10,height = 5,text = "Up" , command = self.command_w)
        self.button_up.pack(side = tk.TOP)

        self.button_left = tk.Button(frame_2, width = 10,height = 5,text = "Left" , command = self.command_a)
        self.button_left.pack(side = tk.LEFT,anchor = "w")

        self.button_down = tk.Button(frame_2, width = 10,height = 5,text = "Down" , command = self.command_s)
        self.button_down.pack(side = tk.LEFT,anchor = "w")

        self.button_up = tk.Button(frame_2, width = 10,height = 5,text = "Right" , command = self.command_d)
        self.button_up.pack(side = tk.LEFT,anchor = "w")

        self.button_quit = tk.Button(frame_3,width = 10,height =5,text = "Quit" , command = self.command_quit)
        self.button_quit.pack(side = tk.LEFT,anchor = "w")

        self.button_send = tk.Button(frame_3,width = 10,height =5,text = "Refresh" , command = self.command_send)
        self.button_send.pack(side = tk.RIGHT,anchor = "w")

    def command_w(self):
        global command
        command = "upup"
        #print command

    def command_a(self):
        global command
        command = "left"
        #print command

    def command_s(self):
        global command
        command = "down"
        #print command

    def command_d(self):
        global command
        command = "righ"
        #print command

    def command_quit(self):
        global command
        command = "quit"
        #print command

    def command_send(self):
        global command
        command = "send"

    def update_image(self):
        self.label.pack_forget()
        global update_flag
        self.photo = Image.open(file_path)
        self.photo = ImageTk.PhotoImage(self.photo)
        self.label = tk.Label(self.master, image = self.photo)
        print("update_completed!")
        self.label.pack()






class InputThread(threading.Thread):
    def __init__(self):
        super(InputThread,self).__init__()


    def run(self):
        while True:
            global command
            if command == "":
                command = raw_input()

            if command == 'quit':
                print "Bye"
                break;

class GuiThread(threading.Thread):
    def run(self):
        self.gui_root = tk.Tk()
        self.gui_obj = Guis(master = self.gui_root)
        self.gui_root.mainloop()

    def image_update(self):
        self.gui_obj.update_image()

class RecvThread(threading.Thread):
    def __init__(self,conn,client_addr,guiloop):
        self.conn_camera = conn
        self.addr = client_addr
        self.guiloop = guiloop
        self.stop_event = threading.Event()
        super(RecvThread,self).__init__()

    def run(self):
        global update_flag
        global file_path
        global addr
        open_flag = False
        while not self.stop_event.is_set():
            if update_flag == True:
				update_flag = False
                data,self.addr = self.conn_camera.recvfrom(100000)
                if len(data) > 4:
                    image_file = open(file_path,"wb")
                    open_flag = True
                else:
                    data = ""
                while data:
                    if (str(data).endswith("over")) == False :
                        #print data[-6:]
                        image_file.write(data)

                    else:
                        if len(data) >=4 :
                            data = data[:(len(data)-4)]
                        else:
                            data = ""
                        if data != "":
                            #print data[-6:]
                            image_file.write(data)
                        break;
                    data,self.addr = self.conn_camera.recvfrom(100000)
                #print("over received!")
                if open_flag == True:
                    image_file.close()
                    open_flag = False

                self.guiloop.image_update()

        def stop(self):
            self.stop_event.set()
            self.join()






if __name__ == '__main__':
    Inputfunc = InputThread()
    Inputfunc.start()
    Guiloop = GuiThread()
    Guiloop.start()

    socket_command_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    socket_camera_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    socket_command_server.bind(ip_port_1)
    socket_camera_server.bind(ip_port_2)
    #socket_command_server.listen(5)
    #socket_camera_server.listen(5)



    while True:
	datadump,addr_command = socket_command_server.recvfrom(1024)
	print datadump
	print addr_command
	datadump,addr_camera = socket_camera_server.recvfrom(1024)
	print datadump
	print addr_command
        #conn_command,addr_command = socket_command_server.accept()
        #conn_camera,addr_camera = socket_camera_server.accept()
        #print 'Command client:', addr_command
        #print 'Camera client', addr_camera
        recvthread = RecvThread(socket_camera_server,addr_camera,Guiloop)
        recvthread.start()
        #data_recv = conn_command.recv(1024)
        print("Start!")
        while True:

            if command != "":
		if (command == "flar"):
                    update_flag = False
                else:
		    socket_command_server.sendto(command,addr_command)

                if update_flag == False:
                    #print("Sending send")
                    socket_command_server.sendto("send",addr_command)
                    update_flag = True

                print(command)
                if (command == "quit"):
                    socket_command_server.close()
                    socket_camera_server.close()


                #if (command == "upup"):
                #    print update_flag
                command = ""
