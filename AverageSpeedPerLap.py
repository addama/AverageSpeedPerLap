# C:\User\My Documents\Assetto Corsa\logs

import ac
import acsys
from os.path import exists

# CONFIG SETTINGS
title = 'AverageSpeedPerLap'
data_dir = 'apps/python/'+title+'/data/'
use_kph = False
use_background = True
use_border = False

# INTERNAL DATA
com_avg_curr = 0
com_avg_prev = 0
com_avg_best = 0
label_avg_curr = 'CURR'
label_avg_prev = 'PREV'
label_avg_best = 'BEST'
lap = 0
speeds = []
speed = 0
avg_curr = 0
avg_prev = 0
avg_best = 0
prev_best = 0
timer = 0
file = False
state = False

average = lambda a: sum(a) / len(a)
getValidFileName = lambda f: ''.join(c for c in f if c in '-_() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

def acMain(ac_version):
	global title, file, prev_best, avg_best
	global label_avg_best, label_avg_curr, label_avg_prev# , label_speed
	global com_avg_best, com_avg_curr, com_avg_prev# , com_speed
	try:
		app = ac.newApp(title)
		ac.setIconPosition(app, 0, -10000)
		ac.setTitle(app, '')
		ac.setSize(app, 100, 120)
		ac.drawBackground(app, use_background)
		ac.drawBorder(app, use_border)
		com_avg_curr = ac.addLabel(app, label_avg_curr+': '+str(avg_curr));
		com_avg_prev = ac.addLabel(app, label_avg_prev+': '+str(avg_prev));
		com_avg_best = ac.addLabel(app, label_avg_best+': '+str(avg_best));
		# com_speed = ac.addLabel(app, label_speed+': 0');
		ac.setPosition(com_avg_curr, 5, 5)
		ac.setPosition(com_avg_best, 5, 25)
		ac.setPosition(com_avg_curr, 5, 45)
		# ac.setPosition(com_speed, 5, 65)
		car = ac.getCarName(0)
		track = ac.getTrackName(0)
		layout = ac.getTrackConfiguration(0)
		file = data_dir+getValidFileName(car+'-'+track+'-'+layout)+'.txt'
		if (exists(file)):
			with open(file, 'r') as f:
				prev_best = float(f.readline())
				avg_best = prev_best
				ac.log(title+': Found existing best in '+file+': '+str(avg_best))
	except Exception as error:
		ac.log(title+': '+str(error))
	return title

def acUpdate(deltaT):
	global speeds, lap, avg_prev, avg_curr, avg_best, speed, timer
	timer += deltaT
	# 60 times per second
	if (timer > 0.0166):
		timer = 0
		currentLap = ac.getCarState(0, acsys.CS.LapCount)
		speed = ac.getCarState(0, acsys.CS.SpeedKMH) if use_kph else ac.getCarState(0, acsys.CS.SpeedMPH)
		if (currentLap > lap):
			ac.log(title+': '+str(lap)+': '+str(avg_curr))
			lap = currentLap
			avg_prev = avg_curr
			avg_curr = 0
			speeds = []
			if (avg_prev > avg_best):
				avg_best = avg_prev
		else:
			speeds.append(speed)
			avg_curr = average(speeds)
		updateApp()

def updateApp():
	global avg_curr, avg_prev, avg_best, speed
	global com_avg_curr, com_avg_prev, com_avg_best# , com_speed
	global label_avg_curr, label_avg_prev, label_avg_best# , label_speed
	ac.setText(com_avg_curr, label_avg_curr+': '+str(round(avg_curr,1)))
	ac.setText(com_avg_prev, label_avg_prev+': '+str(round(avg_prev,1)))
	ac.setText(com_avg_best, label_avg_best+': '+str(round(avg_best,1)))
	# ac.setText(com_speed, label_speed+': '+str(round(speed,0)))

def acShutdown():
	global title, file, avg_best
	try:
		ac.log(title+': SHUTDOWN')
		if (avg_best > 0 and avg_best > prev_best):
			ac.log(title+': Recording new best speed in '+file+': '+ str(avg_best))
			with open(file, 'w') as f:
				f.write(str(avg_best))
	except Exception as error:
		ac.log(title+': '+str(error))