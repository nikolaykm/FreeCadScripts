# -*- coding: utf-8 -*-

import pynput
import csv
from pynput.mouse import Button
from pynput.keyboard import Key, Controller
import time
from pynput.mouse import Controller as MouseControler
import sys

def typeText(text, hitEnter=False, sleep=1):
    keyboard = Controller()
    keyboard.type(text)
    if hitEnter:
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
    time.sleep(sleep)
    if hitEnter:
        time.sleep(2)

def hitTab(forward=True, sleep=1, count=1):
    keyboard = Controller()
    for c in range(0, count):
        if forward:
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)
        else:
            with keyboard.pressed(Key.shift):
                keyboard.press(Key.tab)
                keyboard.release(Key.tab)
        time.sleep(sleep)

def hitEnter(sleepBefore=1, sleepAfter=1):
    time.sleep(sleepBefore)
    keyboard = Controller()
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    time.sleep(sleepAfter)

def hitKeyDownArrow(count=1):
   for x in range(1, count+1):
       keyboard = Controller()
       keyboard.press(Key.down)
       keyboard.release(Key.down)
       time.sleep(1)

def hitSpace():
    keyboard = Controller()
    keyboard.press(Key.space)
    keyboard.release(Key.space)
    time.sleep(1)

def hitEscape(sleepBefore=1, sleepAfter=1):
    time.sleep(sleepBefore)
    keyboard = Controller()
    keyboard.press(Key.esc)
    keyboard.release(Key.esc)
    time.sleep(sleepAfter)

def mouseClickOn(mouse, pair, sleepBefore=1, sleepAfter=1):
    # Set pointer position
    mouse.position = (pair[0], pair[1])
    time.sleep(sleepBefore)
    mouse.press(Button.left)
    mouse.release(Button.left)
    time.sleep(sleepAfter)

if __name__ == "__main__":

    #sleep a little so the user could place the mouse market in the proper field
    time.sleep(10)

    mouse = MouseControler()

    with open(sys.argv[1], 'rb') as f:
        reader = csv.reader(f)
        cvsList = list(reader)

    if sys.argv[2] == "createRows":
        count = int(sys.argv[3]) if len(sys.argv) > 3 else len(cvsList)
        hitTab(sleep=0, count=11)
        for curRow in range(1, count):
            hitEnter(sleepBefore=0, sleepAfter=0)  
        exit()

    if sys.argv[2] == "fillInBase":

        startFromRow = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        endRow = int(sys.argv[4]) if len(sys.argv) > 4 else 1000000

        for row in cvsList:

            if int(row[0]) < startFromRow or int(row[0]) > endRow: continue
            print row

            #Enter Lenght By the Fladder
            hitTab(sleep=0)
            typeText(row[1], sleep=0)
    
            #Enter Width By the Fladder
            hitTab(sleep=0)
            typeText(row[2], sleep=0)

            #Enter Count
            hitTab(sleep=0)
            typeText(row[3], sleep=0)

            #Enter can rotate
            hitTab(sleep=0)
            if row[4] != "": 
                hitEnter()
                hitKeyDownArrow(1)
                hitEnter()

            #skip joint
            hitTab(sleep=0)

            #enter Description
            hitTab(sleep=0)
            #if row[13] != "":
            #    typeText(row[13], sleep=0)

            #skip to the next line
            hitTab(sleep=1, count=4)

        exit()
