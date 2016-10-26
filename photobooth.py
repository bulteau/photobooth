import RPi.GPIO as GPIO 
import time, subprocess, datetime
import cups

GPIO.setmode(GPIO.BCM) 
GPIO.setup(24, GPIO.IN)
GPIO.setup(25, GPIO.OUT)

###################
#Fonction pour enregistrer les informations sur le fichier infos_photobooth. Fichier qui est interpreter par le serveur web
###################
def add_infos(value):
    pfile = open('infos_photobooth', 'w')
    pfile.seek(0)
    pfile.truncate()
    pfile.write(value)
    pfile.close()


count = 0
countPrint = 20
change = 1
conn = cups.Connection()
start_time = 0;

pathPhotoOriginal = "/home/pi/Documents/camera/www/static/photobooth_images/original/"
pathPhotoSmall = "/home/pi/Documents/camera/www/static/photobooth_images/small/"


###################
#ETAPE 0 : READY
###################
add_infos('{"id":"0","value":"Appuyez sur le bouton"}');


while True:
	inputValue = GPIO.input(24) 
	if (inputValue == True and change ==1):
		count = count + 1
		print("Nombre de photo prises dans la session: " + str(count) + ".")
		change = 0

		time.sleep(1.5)
		###################
		#ETAPE 1 : COUNTDOWN
		###################
		add_infos('{"id":"1","value":"5"}')
		time.sleep(1.5)
		add_infos('{"id":"1","value":"4"}')
		time.sleep(1.5)
		add_infos('{"id":"1","value":"3"}')
		time.sleep(1.5)
		add_infos('{"id":"1","value":"2"}')
		time.sleep(1.5)
		add_infos('{"id":"1","value":"1"}')
		time.sleep(1.5)
		add_infos('{"id":"1","value":"0"}')
				
		start_time = str(datetime.datetime.now());
		print(str(datetime.datetime.now()) + " : countdown")		
		GPIO.output(25,GPIO.HIGH)


		filename = "PB_{0}.jpg".format(datetime.datetime.now().strftime("%d_%B_%Y_%I%M%S"))
		print(str(datetime.datetime.now()) + " : Ouistiti!!!")
		gpout = subprocess.check_output("gphoto2 --capture-image-and-download --filename "+pathPhotoOriginal+filename, stderr=subprocess.STDOUT, shell=True)
		
		print(str(datetime.datetime.now()) + " : avant demande d'impression")		
		
		###################
		#ETAPE 2 : PRINT
		###################
		add_infos('{"id":"2", "value":"5", "file":"' + filename + '"}')

		print(str(datetime.datetime.now()) + " : modification du format")
		
		#Change resolution
		gpout2 = subprocess.check_output("convert "+pathPhotoOriginal+filename+" -resize 75% "+pathPhotoSmall+"tmp_"+filename, stderr=subprocess.STDOUT, shell=True)
		#Crop image for format 1196x802 to fit in 10x15cm paper format
		gpout3 = subprocess.check_output("convert "+pathPhotoSmall+"tmp_"+filename+" -gravity Center -crop 1196x802+0+0 +repage "+pathPhotoSmall+"s_"+filename, stderr=subprocess.STDOUT, shell=True)
		#Delete tmp file
		gpout4 = subprocess.check_output("rm "+pathPhotoSmall+"tmp_"+filename, stderr=subprocess.STDOUT, shell=True)

		add_infos('{"id":"2", "value":"10", "file":"' + filename + '"}')

		printid = conn.printFile('PM240', pathPhotoSmall+"s_"+filename, 'photo', {})
		
		print(str(datetime.datetime.now()) + " : Preparation de l'impression")
		add_infos('{"id":"2", "value":"20", "file":"' + filename + '"}')
		
		while conn.getJobs().get(printid, None) is not None:
        		time.sleep(1)
        		if(countPrint<80): 
	        		countPrint = countPrint + 1
        			add_infos('{"id":"2", "value":"' + str(countPrint) + '", "file":"' + filename + '"}')
        		elif countPrint>=80 :
	        		add_infos('{"id":"20", "value":"' + str(countPrint) + '", "file":"' + filename + '"}')
	        		conn.cancelJob(printid)
		
		
		countPrint = 80
 		add_infos('{"id":"2", "value":"80", "file":"' + filename + '"}')
		print(str(datetime.datetime.now()) + " : Impression en cours")	
		
		#Attente de 20s
		while countPrint < 97:
			time.sleep(2)
			countPrint = countPrint + 1
			add_infos('{"id":"2", "value":"' + str(countPrint) + '", "file":"' + filename + '"}')
			
		GPIO.output(25,GPIO.LOW)


		countPrint = 20
		
		print(str(datetime.datetime.now()) + " : Fin")
		add_infos('{"id":"2", "value":"100", "file":"' + filename + '"}')
		time.sleep(5)
		print("debut : " + start_time + " - fin : " + str(datetime.datetime.now())) 	
		
		
		###################
		#RETOUR ETAPE 0 : READY
		###################
		add_infos('{"id":"0","value":"Appuyez sur le bouton"}');
		
	elif (inputValue == False and change ==0):
			change = 1
		
	time.sleep(.01)
