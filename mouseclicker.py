# Globals
# ---------------------



import win32api, win32con
import random


def leftClick():
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
	time.sleep(randrange(.1,.2,.002))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
	print "Left Click."




