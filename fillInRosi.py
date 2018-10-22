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
        hitTab(sleep=0, count=11)
        for curRow in range(1, len(cvsList)):
            hitEnter(sleepBefore=0, sleepAfter=0)  
        exit()

    if sys.argv[2] == "fillInBase":

        startFromRow = int(sys.argv[3]) if len(sys.argv) > 3 else 0

        for row in cvsList:

            print row
            if int(row[0]) < startFromRow: continue

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

    if sys.argv[2] == "fillInCants":

        startFromRow = int(sys.argv[3]) if len(sys.argv) > 3 else 0

        for row in cvsList:

            print row

            if int(row[0]) < startFromRow: continue

            longCants = int(row[5])
            shortCants = int(row[6])
            hitCantThick = 0
            if row[7] == "0.8": hitCantThick=1
            if row[7] == "2"  : hitCantThick=2

            if longCants+shortCants == 0: continue

            #going to the proper resync button
            hitTab(sleep=0, count=23+(int(row[0])-1)*10 + 7)
            hitEnter(sleepBefore=5, sleepAfter=5)

            mouseClickOn(mouse, (620,580))

            if int(row[1]) > int(row[2]):
 
                #First long cant
                hitTab()
                if longCants > 0:
                     hitEnter()
                     hitKeyDownArrow(hitCantThick)
                     hitEnter()
                     longCants = longCants - 1

                if min(int(row[1]), int(row[2])) >= 100:
                    #First short cant
                    hitTab()
                    if shortCants > 0:
                        hitEnter()
                        hitKeyDownArrow(hitCantThick)
                        hitEnter()
                        shortCants = shortCants - 1

                    #Second short cant
                    hitTab()
                    if shortCants > 0:
                        hitEnter()
                        hitKeyDownArrow(hitCantThick)
                        hitEnter()
                        shortCants = shortCants - 1

                #Second long cant
                hitTab()
                if longCants > 0:
                    hitEnter()
                    hitKeyDownArrow(hitCantThick)
                    hitEnter()
                    longCants = longCants - 1

            if int(row[1]) <= int(row[2]):
 
                #First short cant
                hitTab()
                if shortCants > 0:
                    hitEnter()
                    hitKeyDownArrow(hitCantThick)
                    hitEnter()
                    shortCants = shortCants - 1

                if min(int(row[1]), int(row[2])) >= 100:
                    #First long cant
                    hitTab()
                    if longCants > 0:
                        hitEnter()
                        hitKeyDownArrow(hitCantThick)
                        hitEnter()
                        longCants = longCants - 1

                    #Second long cant
                    hitTab()
                    if longCants > 0:
                        hitEnter()
                        hitKeyDownArrow(hitCantThick)
                        hitEnter()
                        longCants = longCants - 1

                #Second short cant
                hitTab()
                if shortCants > 0:
                    hitEnter()
                    hitKeyDownArrow(hitCantThick)
                    hitEnter()
                    shortCants = shortCants - 1

            hitEscape(sleepBefore=5, sleepAfter=5)
                    
        exit()    
