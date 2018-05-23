#!usr/bin/python
import pantilthat
import picamera
import socket
import time
import threading
import os
import io
import copy



command = ""
ip_port_1 = (('192.168.1.209',8000))
ip_port_2 = (('192.168.1.209',8001))
send_flag = False
file_path = "/home/raspb/output.jpg"
capture_flag = True
dic = {}
commandlist =[]

class InputThread(threading.Thread):
    def __init__(self):
        super(InputThread,self).__init__()


    def run(self):
        while True:
            global command
            command_tmp = raw_input()
            while command != "":
				i = 1
            command = command_tmp



class CommandRecvthread(threading.Thread):
	def __init__(self,comm_socket):
		self.stop_event = threading.Event()
		super(CommandRecvthread,self).__init__()
		self.sk_comm = comm_socket



	def run(self):
		global command
		global commandlist
		while not self.stop_event.is_set():
			if command == "":
				command,addr = self.sk_comm.recvfrom(4)
				commandlist.append(command)
				print(command)


	def stop(self):
		self.stop_event.set()
		self.join()


class Imagesendthread(threading.Thread):
	def __init__(self,socket_camera):
		self.socket_camera = socket_camera
		super(Imagesendthread,self).__init__()

	def run(self):
		global send_flag
		global capture_flag
		global dic
		while True:
			if send_flag == True:
				send_flag = False
				while capture_flag == True:
					i = 1
				buf = dic['jpeg']
				buf_1 = buf[:65000]
				while len(buf) >= 65000:
					self.socket_camera.sendto(buf_1,ip_port_2)
					buf = buf[65000:]
					buf_1 = buf[:65000]
				self.socket_camera.sendto(buf_1,ip_port_2)
				self.socket_camera.sendto("over",ip_port_2)
				#print("Sending over!")
				



class Camerathread(threading.Thread):
	def run(self):
		global send_flag
		global capture_flag
		global dic
		self.stop_event = threading.Event()
		self.pi_camera = picamera.PiCamera()
		self.pi_camera.resolution = (320,240)
		self.pi_camera.vflip = True
		self.pi_camera.hflip = True
		self.pi_camera.start_preview()
		time.sleep(2)
		while not self.stop_event.is_set():
			mys = io.BytesIO()
			self.pi_camera.capture(mys,'jpeg')
			dic['jpeg'] = copy.copy(mys.getvalue())
			capture_flag = False



		self.pi_camera.stop_preview()
		self.pi_camera.close()


	def stop(self):
		self.stop_event.set()
		self.join()

	def stop_camera(self):
		self.pi_camera.close()



c_thread = Camerathread()
c_thread.start()
pantilthat.servo_enable(1,True)
pantilthat.servo_enable(2,True)

v_angle = 0
p_angle = 0

pantilthat.servo_one(v_angle)
pantilthat.servo_two(p_angle)


sk_command = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sk_camera = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sk_command.sendto("Hello",ip_port_1)
time.sleep(1)
sk_camera.sendto("Hello",ip_port_2)
time.sleep(1)
#sk_command.connect(ip_port_1)
#sk_camera.connect(ip_port_2)
comm_thread = CommandRecvthread(comm_socket = sk_command)
comm_thread.start()
input_thread = InputThread()
input_thread.start()
im_thread = Imagesendthread(sk_camera)
im_thread.start()




while True:

	if command == "quit":
		command = ""
		pantilthat.servo_one(0)
		pantilthat.servo_two(0)
		c_thread.stop_camera()
		c_thread.stop()
		time.sleep(1)
		pantilthat.servo_enable(1,False)
		pantilthat.servo_enable(2,False)
		sk_command.close()
		print("over!")

		break
	elif command == "upup":
		command = ""
		v_angle = v_angle - 9
		if v_angle <= -90:
			v_angle = -90
		pantilthat.servo_two(v_angle)
	elif command == "down":
		command = ""
		v_angle = v_angle + 9
		if v_angle >= 90:
			v_angle = 90
		pantilthat.servo_two(v_angle)
	elif command == "left":
		command = ""
		p_angle = p_angle + 9
		if p_angle >= 90:
			p_angle = 90
		pantilthat.servo_one(p_angle)
	elif command == "righ":
		command = ""
		p_angle = p_angle - 9
		if p_angle <= -90:
			p_angle = -90
		pantilthat.servo_one(p_angle)
	elif command == "send":
		command = ""
		send_flag = True
		#print("send received!")
	else:
		#print(command)
		command = ""
