# C:\User\My Documents\Assetto Corsa\logs

import ac
import acsys
import configparser
from os.path import exists

# CONFIG SETTINGS
title = 'AverageSpeedPerLap'
base_dir = 'apps/python/'+title
config_ini = base_dir+'/config.ini'
config_header = 'SETTINGS'
data_dir = base_dir+'/data/'
data_ext = '.txt'
use_kph = False
use_background = True
use_border = False
is_horizontal = True

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

def parseConfig():
	global config_ini
	global use_kph, use_background, use_border, is_horizontal

	cfg = configparser.ConfigParser()
	cfg.read(config_ini)
	settings = cfg[config_header]

	use_kph = settings.get('use_kph', use_kph)  
	use_background = settings.get('use_background', use_background)  
	use_border = settings.get('use_border', use_border)  
	is_horizontal = settings.get('is_horizontal', is_horizontal)  

def acMain(ac_version):
	global title, file, prev_best, avg_best
	global label_avg_best, label_avg_curr, label_avg_prev
	global com_avg_best, com_avg_curr, com_avg_prev
	try:
		if (exists(config_ini)):
			parseConfig()
		app = ac.newApp(title)
		ac.setSize(app, 100, 120)
		ac.setIconPosition(app, 0, -10000) # Get rid of the icon
		ac.setTitle(app, '') # Get rid of the title
		ac.drawBackground(app, use_background)
		ac.drawBorder(app, use_border)
		com_avg_curr = ac.addLabel(app, label_avg_curr+': '+str(avg_curr))
		com_avg_prev = ac.addLabel(app, label_avg_prev+': '+str(avg_prev))
		com_avg_best = ac.addLabel(app, label_avg_best+': '+str(avg_best))
		ac.setPosition(com_avg_curr, 5, 5)
		ac.setPosition(com_avg_prev, 5, 25)
		ac.setPosition(com_avg_best, 5, 45)
		car = ac.getCarName(0)
		track = ac.getTrackName(0)
		layout = ac.getTrackConfiguration(0)
		file = data_dir+getValidFileName(car+'-'+track+'-'+layout)+data_ext
		if (exists(file)):
			with open(file, 'r') as f:
				prev_best = float(f.readline())
				avg_best = prev_best
				ac.log(title+': Found existing best in '+file+': '+str(avg_best))
	except Exception as error:
		ac.log(title+': '+str(error))
	return title

def acUpdate(deltaT):
	# Receives millisecond updates from AC, recalculates current average speed
	# When a new lap is detected, the previous average speed is stored in avg_prev
	# If avg_prev is higher than avg_best, it's a new record
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
		draw()

def draw():
	# Handles the visual updates
	global avg_curr, avg_prev, avg_best, speed
	global com_avg_curr, com_avg_prev, com_avg_best
	global label_avg_curr, label_avg_prev, label_avg_best
	ac.setText(com_avg_curr, label_avg_curr+': '+str(round(avg_curr,1)))
	ac.setText(com_avg_prev, label_avg_prev+': '+str(round(avg_prev,1)))
	ac.setText(com_avg_best, label_avg_best+': '+str(round(avg_best,1)))

def acShutdown():
	# Write any new bests found for the current car/track/layout configuration
	global title, file, avg_best
	try:
		ac.log(title+': SHUTDOWN')
		if (avg_best > 0 and avg_best > prev_best):
			ac.log(title+': Recording new best speed in '+file+': '+ str(avg_best))
			with open(file, 'w') as f:
				f.write(str(avg_best))
	except Exception as error:
		ac.log(title+': '+str(error))