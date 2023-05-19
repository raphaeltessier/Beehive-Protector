#! /usr/bin/env python3

from jetcam.usb_camera import USBCamera
import PIL
from PIL import Image
import numpy as np
import torch
import pandas
import RPi.GPIO as GPIO
import time
import torchvision


#CONSTANTE
PIN_SENS_MOTEUR = 31
PIN_PWM_MOTEUR = 33 #pin pwm1 channel0
PIN_VERIN = 37
FREQUENCE = 20000

#Classes
class Moteur:
	def __init__(self, p_sens, p_pwm):
		self.pin_sens = p_sens
		self.pin_pwm = p_pwm
		GPIO.setup(self.pin_sens, GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(self.pin_pwm, GPIO.OUT, initial=GPIO.LOW)
		self.p = GPIO.PWM(self.pin_pwm, FREQUENCE)
		self.p.start(0)

	
	def monter(self, vitesse, temps): #vitesse entre 0 et 100%, temps en s
		GPIO.output(self.pin_sens, GPIO.HIGH)
		self.p.ChangeDutyCycle(vitesse)
		time.sleep(temps)
		self.p.ChangeDutyCycle(0)
	
	def descendre(self, vitesse, temps): #vitesse entre 0 et 100%, temps en s
		GPIO.output(self.pin_sens, GPIO.LOW)
		self.p.ChangeDutyCycle(vitesse)
		time.sleep(temps)
		self.p.ChangeDutyCycle(0)



class Verin:
	def __init__(self, p):
		self.pin = p

		GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)


	def attirer(self): 
		GPIO.output(self.pin, GPIO.HIGH)
	
	def relacher(self): 
		GPIO.output(self.pin, GPIO.LOW)


		
		





try:
#Initialisation 
	count = 0
	#initializing gpio for motor and electric jack
	GPIO.setmode(GPIO.BOARD)
	moteur = Moteur(PIN_SENS_MOTEUR, PIN_PWM_MOTEUR)
	verin = Verin(PIN_VERIN)
	
	#loading model from local repository
	model = torch.hub.load("/home/pir/Desktop/PIR/yolov5", 'custom', "/home/pir/Desktop/PIR/yolov5/best.pt", source = 'local') 
	
	#creating camera flux entry
	camera = USBCamera(width=640, height=640, capture_width=640, capture_height=480, capture_device=0)
	

#main 	
	while(1):  #around 1sec for each loop execution

		print(time.time())#debug
		image=camera.read()
		#converting image to correct format
		rgb = np.flip(image, 2)
		PILimage = Image.fromarray(rgb)
		
		results = model(PILimage, size = 640) #running IA model 
		df = results.pandas().xyxy[0] #formatting results
		last = df.size -1
		for index, row in df.iterrows(): 
			if (row['class']==0 and row['confidence']>=0.7): 
				#check if we have an hornet above 0.7 tthreshold
				#then stop iterating and count one hronet
				print(row)#debug
				count += 1
				break
			if (index == last):  #reset to 0 if no hornet in the image
				count = 0
		print(count)#debug
		if (count ==3): 
		#active the swatter and stop the detection loop until the swatter is setup back
			verin.attirer()
			time.sleep(5)
			verin.relacher()
			moteur.monter(100,30)
			verin.attirer()
			moteur.monter(50,43)
			verin.relacher()
			time.sleep(3)
			moteur.descendre(50,40)
			moteur.descendre(100,29)
			count = 0


finally:
	#resetting GPIO to avoid problems on Jetson nano 
	moteur.p.stop()
	GPIO.cleanup()
