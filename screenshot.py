import ImageGrab
import os
import time
import ImageOps 
from numpy import *
from ctypes import*
from ctypes.wintypes import *
import win32api, win32con
import random
import Image
import cv2
import math 
from matplotlib import pyplot as plt

x_pad = 0
y_pad = 0
#PADDING INFORMATION 
#---------------------------------------
FIELD_OPP_PADD = (534, 315)
FIELD_SELF_PADD = (534, 510)
HAND_PADD = (550, 925)

#USEFUL IMAGES 
#--------------------------------------
large = 'full_snap__1400023374.png'
large2 = 'full_snap__1400045150.png'
IMG_HAND = 'full_snap__HAND.png'
IMG_ENEMY_MONSTER = 'full_snap__EM.png'
IMG_SELF_MONSTER = 'full_snap__SF.png'

EM = 'EM'
SF = 'SF'
HD = 'HAND'


#USEFUL COORD
#--------------------------
HERO_POWER = (1100,788,1180,865)
HERO_SELF = (900,800,1000,900)
HERO_ENEMY = (900,190,1000,270)
END_TURN = (1508,481,1609,498)
FIELD_OPP = (534,315,1385,489)
FIELD_SELF = (534,500,1385,699)
HAND = (550,925,1295,1073)

# IMAGE TEMPLATE FIELD CARDS
#------------------------------
HS_NM = 'HS_NM.png'
HS_TAUNT = 'HS_TAUNT.png'
HS_EM_TAUNT = 'HS_EM_TAUNT.png'
HS_EM_NM = 'HS_EM_NM.png'
HS_SELF_NM = 'HS_SELF_NM.png'
HS_SELF_TAUNT = 'HS_SELF_TAUNT.png'

MONSTER = [HS_NM, HS_TAUNT, HS_EM_NM, HS_EM_TAUNT, HS_SELF_TAUNT, HS_SELF_NM]

# IMAGES VALUES FOR CARDS
#-------------------------------
HS_MC0 = 'HS_MCVAL_0.png'
HS_MC1 = 'HS_MCVAL_1.png'
HS_MC2 = 'HS_MCVAL_2.png'
HS_MC3 = 'HS_MCVAL_3.png'
HS_MC4 = 'HS_MCVAL_4.png'
HS_MC5 = 'HS_MCVAL_5.png'
HS_MC6 = 'HS_MCVAL_6.png'
HS_MC7 = 'HS_MCVAL_7.png'
HS_MC8 = 'HS_MCVAL_8.png'

MC = [HS_MC0, HS_MC1, HS_MC2, HS_MC3, HS_MC4, HS_MC5, HS_MC6, HS_MC7, HS_MC8]

# GLOBAL DATA VALUES
#-----------------------------
MOVE_DICT = {}
CARD_LOC = []
INPLAY_ENEMY = []
INPLAY_SELF = []


# MOUSE STATE VALUES
#--------------------------------
UP = 'UP'
DOWN = 'DOWN'
MOUSE_STATE = ''


# Basic make move function does not take in account macroes
def makeMove(move):
	global MOUSE_STATE
	move = move.upper()
	resetDICT()

	cmd = move.split()
	print cmd

	if len(cmd) == 2 and 'ENEMY' in move:
		findEnemyMonsters()
	if len(cmd) == 2 and 'SELF' in move:
		findSelfMonsters()
	if len(cmd) == 1:
		findCardsinHand()

	print MOVE_DICT

	if not MOVE_DICT.has_key(move):
		createAvailableMoveDictionary()

	if (MOVE_DICT.has_key(move)):
		move_type = MOVE_DICT[move][0]
		move_loc = randomPT(MOVE_DICT[move][1])
		mousePos(move_loc)
		if move_type == 'LEFT_SINGLE':
			if not MOUSE_STATE == DOWN:
				leftDown()
				MOUSE_STATE = DOWN
			else:
				leftUp()
				MOUSE_STATE = UP
		else:
			leftClick()
	else:
		print "ILLEGAL MOVE! ERROR BACKUP NOT IMPL"


# Complex Move Macroes
def macroMove(move):
	move = move.upper()

	cmdlist = move.split(',')

	for cmd in cmdlist:
		wordlist = cmd.split()

		if 'PLAY' in cmd:
			if len(wordlist) > 1:
				makeMove(wordlist[1])
				makeMove('FIELD')
			else:
				print "NEED CARD ARGUMENT FOLLOWING PLAY:"
		elif 'ATTACK' in cmd:
			if 'WITH' in cmd:
				if len(wordlist) == 6:
					makeMove(str(wordlist[4] + ' ' + wordlist[5]))
					makeMove(str(wordlist[1] + ' ' + wordlist[2]))
				elif len(wordlist) == 5:
					makeMove(str(wordlist[3] + ' ' + wordlist[4]))
					makeMove(str(wordlist[1]))
			elif len(wordlist) == 3:
				makeMove(str('SELF 1'))
				makeMove(str(wordlist[1] + ' ' + wordlist[2]))
			elif len(wordlist) == 2:
				makeMove(str('SELF 1'))
				makeMove(str(wordlist[1]))
			else:
				print "MISSING ADDITIONAL ARGUMENTS FOR ATTACK"
		else:
			makeMove(cmd)


def startGame():
	while(True):
		mousePos((400,400))
		move = raw_input("ENTER MOVE:")
		macroMove(move)

def resetDICT():
	global MOVE_DICT
	MOVE_DICT.clear()
	MOVE_DICT.update({'SELF' : ('LEFT_CLICK', HERO_SELF),
					'ENEMY' : ('LEFT_CLICK', HERO_ENEMY),
					'HERO POWER' : ('LEFT_CLICK', HERO_POWER),
					'FIELD' : ('LEFT_CLICK', FIELD_SELF),
					'END TURN' : ('LEFT_CLICK', END_TURN)})

def createAvailableMoveDictionary():
	global MOVE_DICT
	itemnum = 1

	for card in CARD_LOC:
		MOVE_DICT.update({str(itemnum) : ('LEFT_CLICK', card)})
		itemnum += 1

	itemnum = 1

	for enemy in INPLAY_ENEMY:
		MOVE_DICT.update({str('ENEMY ' + str(itemnum)) : ('LEFT_CLICK', enemy)})
		itemnum += 1

	itemnum = 1

	for self in INPLAY_SELF:
		MOVE_DICT.update({str('SELF ' + str(itemnum)) : ('LEFT_CLICK', self)})
		itemnum += 1


def addPadding(boxlist, padding):
	newlist = []
	for box in boxlist:
		newlist.append((box[0] + padding[0],
						box[1] + padding[1], 
						box[2] + padding[0],
						box[3] + padding[1]))

	return newlist

def randomPT(box):
	PTx = random.randrange(box[0],box[2],1)
	PTy = random.randrange(box[1],box[3],1)
	return (PTx, PTy)

def findSelfMonsters():
	global INPLAY_SELF
	temp = []

	screenGrab(FIELD_SELF, SF)

	for item in MONSTER:
		temp = temp + findImageRaw(item, IMG_SELF_MONSTER)

	INPLAY_SELF = addPadding(reduceList(temp), FIELD_SELF_PADD)
	INPLAY_SELF.sort()
	return INPLAY_SELF

def findEnemyMonsters():
	global INPLAY_ENEMY
	temp = []

	screenGrab(FIELD_OPP, EM)

	for item in MONSTER:
		temp = temp + findImageRaw(item, IMG_ENEMY_MONSTER)

	INPLAY_ENEMY = addPadding(reduceList(temp), FIELD_OPP_PADD)
	INPLAY_ENEMY.sort()
	return INPLAY_ENEMY

def findCardsinHand():
	global CARD_LOC
	temp = []

	screenGrab(HAND, HD)

	for item in MC:
		temp = temp + findImageRotation(item, IMG_HAND)

	CARD_LOC = addPadding(reduceList(temp), HAND_PADD)
	CARD_LOC.sort()
	return CARD_LOC

def doBoundingBoxesOverlap(box1, box2):
	ATLx = box1[0]
	ATLy = box1[1]

	ABRx = box1[2]
	ABRy = box1[3]

	BTLx = box2[0]
	BTLy = box2[1]

	BBRx = box2[2]
	BBRy = box2[3]

	rabx = math.fabs(ATLx + ABRx - BTLx - BBRx)
	raby = math.fabs(ATLy + ABRy - BTLy - BBRy)

	raxPrbx = ABRx - ATLx + BBRx - BTLx

	rayPrby = ATLy - ABRy + BTLy + BBRy

	if rabx <= raxPrbx and raby <= rayPrby:
		return True

	return False

def reduceList(itemlist):
	itemlist = list(set(itemlist))
	reducedlist = []

	if len(itemlist) == 0:
		return reducedlist

	reducedlist.append(itemlist.pop(0))

	itemlist = [item for item in itemlist if not doBoundingBoxesOverlap(reducedlist[-1], item)]

	return reducedlist + reduceList(itemlist)

def rotateImage(image, angle):
	row,col = image.shape
	center=tuple(array([row,col])/2)
	rot_mat = cv2.getRotationMatrix2D(center,angle,1.0)
	new_image = cv2.warpAffine(image, rot_mat, (col,row))
	return new_image

def findImageRaw(simg, limg):
	templist = []
	print simg
	print limg
	img_rgb = cv2.imread(limg)
	img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
	template = cv2.imread(simg,0)
	w, h = template.shape[::-1]

	res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
	threshold = 0.425
	loc = where( res >= threshold)
	for pt in zip(*loc[::-1]):

		templist.append((pt[0],pt[1],pt[0] + w, pt[1] + h))
		cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

	cv2.imwrite('res' + simg, img_rgb)

	return templist

def findImageRotation(simg, limg):
	templist = []

	img_rgb = cv2.imread(limg)
	img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
	template = cv2.imread(simg,0)
	w, h = template.shape[::-1]

	rotation_list = [-20,-10, 0, 10, 20]

	for rotation in rotation_list:
		imageRotationTemp = rotateImage(template, rotation)
		res = cv2.matchTemplate(img_gray,imageRotationTemp,cv2.TM_CCOEFF_NORMED)
		threshold = 0.7
		loc = where( res >= threshold)
		for pt in zip(*loc[::-1]):

			templist.append((pt[0],pt[1],pt[0] + w, pt[1] + h))
			cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

	cv2.imwrite('res' + simg, img_rgb)

	return templist

def screenGrab():
	box = ()
	time.sleep(1)
	im = ImageGrab.grab()
	im.save(os.getcwd() + '\\full_snap__' + str(int(time.time())) + '.png', 'PNG')
	return im

def screenGrab(box, PNGname):
	time.sleep(1)
	im = ImageGrab.grab(box)
	im.save(os.getcwd() + '\\full_snap__' + PNGname + '.png', 'PNG')
	return im

def grab():
	box = ()
	im = ImageOps.grayscale(ImageGrab.grab())
	a = array(im.getcolors())
	a = a.sum()
	print a
	return a

def main():
	pass


def leftClick():
	click()
	print "Left Click."

def leftDown():
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
	time.sleep(.1)
	print 'Left Down.'

def leftUp():
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
	time.sleep(.1)
	print "Left Up."

def mousePos(cord):
	win32api.SetCursorPos((x_pad + cord[0], y_pad + cord[1]))

def getCords():
	x,y = win32api.GetCursorPos()
	x = x - x_pad
	y = y - y_pad
	print x,y


main()
if __name__ == '__main__':
	main()


__all__ = ['click', 'hold', 'release', 'rightclick', 'righthold', 'rightrelease', 'middleclick', 'middlehold', 'middlerelease', 'move', 'slide', 'getpos']

# START SENDINPUT TYPE DECLARATIONS
PUL = POINTER(c_ulong)

class KeyBdInput(Structure):
    _fields_ = [("wVk", c_ushort),
             ("wScan", c_ushort),
             ("dwFlags", c_ulong),
             ("time", c_ulong),
             ("dwExtraInfo", PUL)]

class HardwareInput(Structure):
    _fields_ = [("uMsg", c_ulong),
             ("wParamL", c_short),
             ("wParamH", c_ushort)]

class MouseInput(Structure):
    _fields_ = [("dx", c_long),
             ("dy", c_long),
             ("mouseData", c_ulong),
             ("dwFlags", c_ulong),
             ("time",c_ulong),
             ("dwExtraInfo", PUL)]

class Input_I(Union):
    _fields_ = [("ki", KeyBdInput),
              ("mi", MouseInput),
              ("hi", HardwareInput)]

class Input(Structure):
    _fields_ = [("type", c_ulong),
             ("ii", Input_I)]

class POINT(Structure):
    _fields_ = [("x", c_ulong),
             ("y", c_ulong)]
# END SENDINPUT TYPE DECLARATIONS

  #  LEFTDOWN   = 0x00000002,
  #  LEFTUP     = 0x00000004,
  #  MIDDLEDOWN = 0x00000020,
  #  MIDDLEUP   = 0x00000040,
  #  MOVE       = 0x00000001,
  #  ABSOLUTE   = 0x00008000,
  #  RIGHTDOWN  = 0x00000008,
  #  RIGHTUP    = 0x00000010

MIDDLEDOWN = 0x00000020
MIDDLEUP   = 0x00000040
MOVE       = 0x00000001
ABSOLUTE   = 0x00008000
RIGHTDOWN  = 0x00000008
RIGHTUP    = 0x00000010


FInputs = Input * 2
extra = c_ulong(0)

click = Input_I()
click.mi = MouseInput(0, 0, 0, 2, 0, pointer(extra))
release = Input_I()
release.mi = MouseInput(0, 0, 0, 4, 0, pointer(extra))

x = FInputs( (0, click), (0, release) )
#user32.SendInput(2, pointer(x), sizeof(x[0])) CLICK & RELEASE

x2 = FInputs( (0, click) )
#user32.SendInput(2, pointer(x2), sizeof(x2[0])) CLICK & HOLD

x3 = FInputs( (0, release) )
#user32.SendInput(2, pointer(x3), sizeof(x3[0])) RELEASE HOLD


def move(x,y):
    windll.user32.SetCursorPos(x,y)

def getpos():
    global pt
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return pt.x, pt.y

def slide(a,b,speed=0):
    while True:
        if speed == 'slow':
            sleep(0.005)
            Tspeed = 2
        if speed == 'fast':
            sleep(0.001)
            Tspeed = 5
        if speed == 0:
            sleep(0.001)
            Tspeed = 3

        x = getpos()[0]
        y = getpos()[1]
        if abs(x-a) < 5:
            if abs(y-b) < 5:
                break

        if a < x:
            x -= Tspeed
        if a > x:
            x += Tspeed
        if b < y:
            y -= Tspeed
        if b > y:
            y += Tspeed
        move(x,y)


def click():
    windll.user32.SendInput(2,pointer(x),sizeof(x[0]))

def hold():
    windll.user32.SendInput(2, pointer(x2), sizeof(x2[0]))

def release():
    windll.user32.SendInput(2, pointer(x3), sizeof(x3[0]))


def rightclick():
    windll.user32.mouse_event(RIGHTDOWN,0,0,0,0)
    windll.user32.mouse_event(RIGHTUP,0,0,0,0)

def righthold():
    windll.user32.mouse_event(RIGHTDOWN,0,0,0,0)

def rightrelease():
    windll.user32.mouse_event(RIGHTUP,0,0,0,0)


def middleclick():
    windll.user32.mouse_event(MIDDLEDOWN,0,0,0,0)
    windll.user32.mouse_event(MIDDLEUP,0,0,0,0)

def middlehold():
    windll.user32.mouse_event(MIDDLEDOWN,0,0,0,0)

def middlerelease():
    windll.user32.mouse_event(MIDDLEUP,0,0,0,0)

if __name__ == '__main__':
    while 1:
        move(10,1)
