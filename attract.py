from threading import Thread
import wiringpi as wiringpi
from time import sleep

__flag = False

def getAttractFlag():
    global flag
    return flag

def setAttractFlag():
    global flag
    flag = True
    
def resetAttractFlag():
    global flag
    flag = False

def attractMode():
    Thread(target=attractFormulaOne).start()
    Thread(target=attractS).start()
    Thread(target=attractPopBumper).start()
    Thread(target=attractCenter).start()
    Thread(target=attract100200300).start()
    Thread(target=attractX).start()
    Thread(target=attractBottom).start()
    Thread(target=attractKRight).start()
    Thread(target=attractKLeft).start()
    Thread(target=attractLeft).start()

def attractFormulaOne():
    while getAttractFlag():
        wiringpi.digitalWrite(127, 1)
        sleep(.1)
        wiringpi.digitalWrite(128, 1)
        sleep(.1)
        wiringpi.digitalWrite(129, 1)
        sleep(.1)
        wiringpi.digitalWrite(130, 1)
        sleep(.1)
        wiringpi.digitalWrite(142, 1)
        sleep(.1)
        wiringpi.digitalWrite(143, 1)
        sleep(.1)
        wiringpi.digitalWrite(144, 1)
        sleep(.1)
        wiringpi.digitalWrite(145, 1)
        sleep(.1)
        wiringpi.digitalWrite(146, 1)
        sleep(.1)
        wiringpi.digitalWrite(147, 1)
        sleep(.1)
        wiringpi.digitalWrite(127, 0)
        sleep(.1)
        wiringpi.digitalWrite(128, 0)
        sleep(.1)
        wiringpi.digitalWrite(129, 0)
        sleep(.1)
        wiringpi.digitalWrite(130, 0)
        sleep(.1)
        wiringpi.digitalWrite(142, 0)
        sleep(.1)
        wiringpi.digitalWrite(143, 0)
        sleep(.1)
        wiringpi.digitalWrite(144, 0)
        sleep(.1)
        wiringpi.digitalWrite(145, 0)
        sleep(.1)
        wiringpi.digitalWrite(146, 0)
        sleep(.1)
        wiringpi.digitalWrite(147, 0)
        sleep(.1)
        
def attractS():
    while getAttractFlag():
        wiringpi.digitalWrite(97, 1)
        sleep(.1)
        wiringpi.digitalWrite(98, 1)
        sleep(.1)
        wiringpi.digitalWrite(97, 0)
        sleep(.1)
        wiringpi.digitalWrite(98, 0)
        sleep(.1)
        
def attractPopBumper():
    while getAttractFlag():
        wiringpi.digitalWrite(148, 1)
        sleep(.1)
        wiringpi.digitalWrite(149, 1)
        sleep(.1)
        wiringpi.digitalWrite(150, 1)
        sleep(.1)
        wiringpi.digitalWrite(148, 0)
        sleep(.1)
        wiringpi.digitalWrite(149, 0)
        sleep(.1)
        wiringpi.digitalWrite(150, 0)
        sleep(.1)
        
def attractCenter():
    while getAttractFlag():
        wiringpi.digitalWrite(107, 1)
        sleep(.1)
        wiringpi.digitalWrite(141, 1)
        sleep(.1)
        wiringpi.digitalWrite(124, 1)
        sleep(.1)
        wiringpi.digitalWrite(123, 1)
        sleep(.1)
        wiringpi.digitalWrite(107, 0)
        sleep(.1)
        wiringpi.digitalWrite(141, 0)
        sleep(.1)
        wiringpi.digitalWrite(124, 0)
        sleep(.1)
        wiringpi.digitalWrite(123, 0)
        sleep(.1)
        
def attract100200300():
    while getAttractFlag():
        wiringpi.digitalWrite(135, 1)
        sleep(.1)
        wiringpi.digitalWrite(136, 1)
        sleep(.1)
        wiringpi.digitalWrite(137, 1)
        sleep(.1)
        wiringpi.digitalWrite(135, 0)
        sleep(.1)
        wiringpi.digitalWrite(136, 0)
        sleep(.1)
        wiringpi.digitalWrite(137, 0)
        sleep(.1)
        
def attractX():
    while getAttractFlag():
        wiringpi.digitalWrite(108, 1)
        sleep(.1)
        wiringpi.digitalWrite(109, 1)
        sleep(.1)
        wiringpi.digitalWrite(110, 1)
        sleep(.1)
        wiringpi.digitalWrite(111, 1)
        sleep(.1)
        wiringpi.digitalWrite(112, 1)
        sleep(.1)
        wiringpi.digitalWrite(113, 1)
        sleep(.1)
        wiringpi.digitalWrite(114, 1)
        sleep(.1)
        wiringpi.digitalWrite(115, 1)
        sleep(.1)
        wiringpi.digitalWrite(108, 0)
        sleep(.1)
        wiringpi.digitalWrite(109, 0)
        sleep(.1)
        wiringpi.digitalWrite(110, 0)
        sleep(.1)
        wiringpi.digitalWrite(111, 0)
        sleep(.1)
        wiringpi.digitalWrite(112, 0)
        sleep(.1)
        wiringpi.digitalWrite(113, 0)
        sleep(.1)
        wiringpi.digitalWrite(114, 0)
        sleep(.1)
        wiringpi.digitalWrite(115, 0)
        sleep(.1)
        
def attractBottom():
    while getAttractFlag():
        wiringpi.digitalWrite(99, 1)
        sleep(.1)
        wiringpi.digitalWrite(116, 1)
        sleep(.1)
        wiringpi.digitalWrite(151, 1)
        sleep(.1)
        wiringpi.digitalWrite(99, 0)
        sleep(.1)
        wiringpi.digitalWrite(116, 0)
        sleep(.1)
        wiringpi.digitalWrite(151, 0)
        sleep(.1)
        
def attractKRight():
    while getAttractFlag():
        wiringpi.digitalWrite(117, 1)
        sleep(.1)
        wiringpi.digitalWrite(118, 1)
        sleep(.1)
        wiringpi.digitalWrite(119, 1)
        sleep(.1)
        wiringpi.digitalWrite(120, 1)
        sleep(.1)
        wiringpi.digitalWrite(121, 1)
        sleep(.1)
        wiringpi.digitalWrite(122, 1)
        sleep(.1)
        wiringpi.digitalWrite(117, 0)
        sleep(.1)
        wiringpi.digitalWrite(118, 0)
        sleep(.1)
        wiringpi.digitalWrite(119, 0)
        sleep(.1)
        wiringpi.digitalWrite(120, 0)
        sleep(.1)
        wiringpi.digitalWrite(121, 0)
        sleep(.1)
        wiringpi.digitalWrite(122, 0)
        sleep(.1)
        
def attractKLeft():
    while getAttractFlag():
        wiringpi.digitalWrite(100, 1)
        sleep(.1)
        wiringpi.digitalWrite(101, 1)
        sleep(.1)
        wiringpi.digitalWrite(102, 1)
        sleep(.1)
        wiringpi.digitalWrite(103, 1)
        sleep(.1)
        wiringpi.digitalWrite(104, 1)
        sleep(.1)
        wiringpi.digitalWrite(105, 1)
        sleep(.1)
        wiringpi.digitalWrite(106, 1)
        sleep(.1)
        wiringpi.digitalWrite(100, 0)
        sleep(.1)
        wiringpi.digitalWrite(101, 0)
        sleep(.1)
        wiringpi.digitalWrite(102, 0)
        sleep(.1)
        wiringpi.digitalWrite(103, 0)
        sleep(.1)
        wiringpi.digitalWrite(104, 0)
        sleep(.1)
        wiringpi.digitalWrite(105, 0)
        sleep(.1)
        wiringpi.digitalWrite(106, 0)
        sleep(.1)
        
def attractLeft():
    while getAttractFlag():
        wiringpi.digitalWrite(156, 1)
        sleep(.1)
        wiringpi.digitalWrite(157, 1)
        sleep(.1)
        wiringpi.digitalWrite(131, 1)
        sleep(.1)
        wiringpi.digitalWrite(132, 1)
        sleep(.1)
        wiringpi.digitalWrite(133, 1)
        sleep(.1)
        wiringpi.digitalWrite(134, 1)
        sleep(.1)
        wiringpi.digitalWrite(138, 1)
        sleep(.1)
        wiringpi.digitalWrite(139, 1)
        sleep(.1)
        wiringpi.digitalWrite(140, 1)
        sleep(.1)
        wiringpi.digitalWrite(156, 0)
        sleep(.1)
        wiringpi.digitalWrite(157, 0)
        sleep(.1)
        wiringpi.digitalWrite(131, 0)
        sleep(.1)
        wiringpi.digitalWrite(132, 0)
        sleep(.1)
        wiringpi.digitalWrite(133, 0)
        sleep(.1)
        wiringpi.digitalWrite(134, 0)
        sleep(.1)
        wiringpi.digitalWrite(138, 0)
        sleep(.1)
        wiringpi.digitalWrite(139, 0)
        sleep(.1)
        wiringpi.digitalWrite(140, 0)
        sleep(.1)