# -*- coding: utf-8 -*-

import pynput
import csv
from pynput.keyboard import Key, Controller
import time
from pynput.mouse import Controller as MouseControler

def typeText(text, hitEnter=False):
    keyboard = Controller()
    keyboard.type(text)
    if hitEnter:
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
    time.sleep(1)
    if hitEnter:
        time.sleep(2)

def hitTab(forward=True, sleep=1):
    keyboard = Controller()
    if forward:
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
    else:
        with keyboard.pressed(Key.shift):
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)
    time.sleep(sleep)

def hitEnter(addSleep=0):
    print "Sleeping before hitting enter"
    time.sleep(1)
    keyboard = Controller()
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    time.sleep(1+addSleep)

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

def hitEscape():
    keyboard = Controller()
    keyboard.press(Key.esc)
    keyboard.release(Key.esc)
    time.sleep(1)


mouse = MouseControler()

with open('XLS/WallnutTropic.csv', 'rb') as f:
    reader = csv.reader(f)
    your_list = list(reader)


time.sleep(5)
firstTime=True
for row in your_list:

    print row

    desc = ''

    #Choose material
    hitEnter()
    hitKeyDownArrow(1)
    hitEnter()
 
    #Enter Lenght By the Fladder
    hitTab()
    typeText(row[1])
    
    #Enter Width By the Fladder
    hitTab()
    typeText(row[2])

    #Enter Count
    hitTab()
    typeText(row[3])

    #Enter can rotate
    hitTab()
    if row[4] != "": 
        hitEnter()
        hitKeyDownArrow(1)
        hitEnter()

    #skip joint
    hitTab()

    #enter Description
    hitTab()
    typeText(row[13])

    #Enter cants
    hitTab()

    longCants = 0
    shortCants = 0
#    longCants = int(row[5])
#    shortCants = int(row[6])

    if longCants + shortCants > 0:
        hitEnter(5)

        hitCantThick = 0
        if row[7] == "0.8": hitCantThick=1
        if row[7] == "2"  : hitCantThick=2

        if int(row[1]) > int(row[2]):

            #First long cant
            if min(int(row[1]), int(row[2])) >= 100: hitTab()
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
            if min(int(row[1]), int(row[2])) >= 100: hitTab()
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

        #Save and exit
        hitTab()
        hitEnter(5)
        for t in range(1,22+(int(row[0])-1)*10 + 7):
            hitTab(sleep=0)
        

    #Enter door holes
    hitTab()
#    if int(row[9]) > 100:
#        hitEnter(5)
#        hitTab()

#        if int(row[1]) > int(row[2]):
#            if row[10] == "д":
#                print "H1"
#                hitSpace()
#            else:
#                print "H2"
#                hitTab()
#                hitSpace()
#        else:
#            if row[10] == "к":
#                print "H3"
#                hitSpace()
#            else:
#                print "H4"
#                hitTab()
#                hitSpace()

#        hitTab()
#        hitKeyDownArrow(2-int(row[9]))

        #Save and exit
#        hitEscape()
#        raw_input("Press Enter to continue...")
#        time.sleep(5)
#        for t in range(1,22+(int(row[0])-1)*10 + 8):
#            hitTab(sleep=0)

        

    #skip delete row
    hitTab()

    #add new row
    hitTab()
    hitEnter()
    for x in range (1,11):
        hitTab(forward=False, sleep=0)

#    typeText(row[8])
#    hitTab()
#    if row[9] != "": desc = desc + "Отвори за панти: " + int(row[9]) + " бр., страна за дупчене: " + row[10]
#    hitTab()
#    if not firstTime:
#        hitTab()
#    hitEnter()
#    for x in range (1,10):
#        hitTab(forward=False)

    mouse.scroll(0, -2)

    firstTime=False
