#!/usr/bin/python2
# Copyright (c) 2017 Raphael Druon
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from enum import Enum
import pprint
from pythonArdrone import libardrone
import curses
from curses import wrapper
from time import sleep
import xbox360_controller
import pygame
import logging
__author__ = "Raphael Druon"


min_x = 80
min_y = 24

curr_x = min_x
curr_y = min_y

def print_navdata(stdscr,navdata):
    try:
        data = navdata[0]
        stdscr.addstr(0,stdscr.getmaxyx()[1]-len('battery XXX'),'battery ' + str(data['battery']))
        stdscr.addstr(1,stdscr.getmaxyx()[1]-len('altitude XXX'),'altitude ' + str(data['altitude']))
        stdscr.addstr(2,stdscr.getmaxyx()[1]-len('phi XXX'),'phi ' + str(data['phi']))
        stdscr.addstr(3,stdscr.getmaxyx()[1]-len('psi XXX'),'psi ' + str(data['psi']))
        stdscr.addstr(4,stdscr.getmaxyx()[1]-len('theta XXX'),'theta ' + str(data['theta']))
    except Exception:
        pass




def main(stdscr):
    logging.basicConfig(filename='test.log',level=logging.DEBUG)
    stdscr.clear()
    curr_y,curr_x = stdscr.getmaxyx()
    while curr_y < min_y or curr_x < min_x:
        stdscr.addstr(curr_y/2,(curr_x-len("Please resize your terminal"))/2,"Please resize your terminal")
        stdscr.refresh()
        c = stdscr.getch()
        stdscr.clear()
        curr_y,curr_x = stdscr.getmaxyx()
    stdscr.nodelay(1)
    stdscr.addstr(0,0,"Welcome ! You can control the drone using a controller or a keyboard")
    drone = libardrone.ARDrone(video=False)
    drone.set_speed(0.4)
    first_anim = libardrone.LED_ANIMATIONS.BLINK_GREEN_RED.value
    use_controller=True
    try:
        pygame.init()
        controller = xbox360_controller.Controller(0,dead_zone = 0.5)
    except Exception as e: # No controller found
        use_controller = False
        print(e)
    if use_controller:
        stdscr.addstr(1,0,"Controller")
    else:
        stdscr.addstr(1,0,"ZQSD to move drone")
        stdscr.addstr(2,0,"A to rotate left / E to rotate right")
        stdscr.addstr(3,0,"Space to land / Enter to take off")
        stdscr.addstr(4,0,"b to blink led")
        stdscr.addstr(5,0,"m to exit")
    try:
        while True:
            if use_controller:
                exit = False
                drone.hover()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit=True
                    if event.type == pygame.JOYHATMOTION: # Prevent multiple input
                        pad_up, pad_right, pad_down, pad_left = controller.get_pad()
                        if pad_up:
                            first_anim+=1
                            first_anim%=libardrone.LED_ANIMATIONS.BLINK_STANDARD.value
                        if pad_down:
                            first_anim-=1
                            first_anim%=libardrone.LED_ANIMATIONS.BLINK_STANDARD.value
                        if pad_left:
                            drone.blink_led(libardrone.LED_ANIMATIONS.LEFT_MISSILE,frequency=10.0,duration=1)
                        if pad_right:
                            drone.blink_led(libardrone.LED_ANIMATIONS.RIGHT_MISSILE,frequency=10.0,duration=1)
                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button == xbox360_controller.A:
                            anim = libardrone.LED_ANIMATIONS(first_anim)
                            drone.blink_led(anim)
                            stdscr.addstr(17,25,"Anim : " + str(first_anim) )
                            stdscr.clrtoeol()
                    if event.type == pygame.JOYBUTTONDOWN and event.button == xbox360_controller.B:
                            drone.reset()
                pressed = controller.get_buttons()
                a_btn = pressed[xbox360_controller.A]
                b_btn = pressed[xbox360_controller.B]
                x_btn = pressed[xbox360_controller.X]
                y_btn = pressed[xbox360_controller.Y]
                back = pressed[xbox360_controller.BACK]
                start = pressed[xbox360_controller.START]
                guide = pressed[xbox360_controller.GUIDE]
                lt_bump = pressed[xbox360_controller.LEFT_BUMP]
                rt_bump = pressed[xbox360_controller.RIGHT_BUMP]
                lt_stick_btn = pressed[xbox360_controller.LEFT_STICK_BTN]
                rt_stick_btn = pressed[xbox360_controller.RIGHT_STICK_BTN]

                lt_x, lt_y = controller.get_left_stick()
                rt_x, rt_y = controller.get_right_stick()

                triggers = controller.get_triggers()

                pad_up, pad_right, pad_down, pad_left = controller.get_pad()
                stdscr.addstr(14,0,"")
                stdscr.clrtoeol()
                stdscr.addstr(15,0,"")
                stdscr.clrtoeol()
                stdscr.addstr(16,0,"")
                stdscr.clrtoeol()
                if start:
                    drone.takeoff()
                    stdscr.addstr(23,0,"Takeoff")
                    stdscr.clrtoeol()
                elif back:
                    drone.land()
                    stdscr.addstr(23,0,"Landing")
                    stdscr.clrtoeol()
                if lt_x < 0:
                    drone.move_left()
                    stdscr.addstr(15,0,"Left")
                elif lt_x > 0:
                    drone.move_right()
                    stdscr.addstr(15,17,"Right")
                if lt_y < 0:
                    drone.move_forward()
                    stdscr.addstr(14,7,"Forward")
                elif lt_y > 0:
                    drone.move_backward()
                    stdscr.addstr(16,7,"Backward")
                if lt_bump:
                    drone.turn_left()
                    stdscr.addstr(14,0,"r_left")
                elif rt_bump:
                    drone.turn_right()
                    stdscr.addstr(14,15,"r_right")
                if triggers > 0:
                    drone.move_up()
                    stdscr.addstr(14,25,"Up")
                elif triggers < 0:
                    drone.move_down()
                    stdscr.addstr(15,25,"Down")

                if lt_stick_btn:
                    drone.hover()
                if guide or exit:
                    break
                sleep(0.05)
            else:
                c = stdscr.getch()
                if c == -1:
                    sleep(0.05)
                elif c == ord('q'):
                    drone.move_left()
                elif c == ord('d'):
                    drone.move_right()
                elif c == ord('z'):
                    drone.move_forward()
                elif c == ord('s'):
                    drone.move_backward()
                elif c == ord(' '):
                    stdscr.addstr(23,0,"Landing")
                    stdscr.clrtoeol()
                    drone.land()
                elif c == curses.KEY_ENTER or c == 10 or c == 13:
                    stdscr.addstr(23,0,"Takeoff")
                    stdscr.clrtoeol()
                    drone.takeoff()
                elif c == ord('a'):
                    drone.turn_left()
                elif c == ord('e'):
                    drone.turn_right()
                elif c == ord('1'):
                    drone.move_up()
                elif c == ord('2'):
                    drone.hover()
                elif c == ord('3'):
                    drone.move_down()
                elif c == ord('t'):
                    drone.reset()
                elif c == ord('x'):
                    drone.hover()
                elif c == ord('y'):
                    drone.trim()
                elif c == ord('b'):
                    drone.blink_led(libardrone.LED_ANIMATIONS(first_anim))
                    first_anim+=1
                elif c == ord('p'):
                    drone.navdata[16] = ""
                    logging.debug(pprint.pformat(drone.navdata))
                elif c == ord('m'):
                    break
                elif c == curses.KEY_RESIZE:
                    curr_y,curr_x = stdscr.getmaxyx()
                    stdscr.clear()
            stdscr.refresh()
            print_navdata(stdscr,drone.navdata)
    finally:
        drone.halt()

if __name__ == "__main__":

    wrapper(main)
