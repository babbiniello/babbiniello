# <>
import wiringpi as wiringpi
from time import sleep
from threading import Thread
import vlc
import time
from random import seed
from random import random
import RPi.GPIO as GPIO
import attract
from grafica import Grafica
from tkinter import *
import pathlib
from subprocess import call

#switch
pin_base_0x20 = 65
i2c_addr_0x20 = 0x20
pin_base_0x21 = 81
i2c_addr_0x21 = 0x21
#lamps
pin_base_0x22 = 97
i2c_addr_0x22 = 0x22
pin_base_0x23 = 113
i2c_addr_0x23 = 0x23
pin_base_0x24 = 129
i2c_addr_0x24 = 0x24
pin_base_0x25 = 145
i2c_addr_0x25 = 0x25
#coils
GPIO.setmode(GPIO.BOARD)

wiringpi.wiringPiSetup()
wiringpi.mcp23017Setup(pin_base_0x20, i2c_addr_0x20)
wiringpi.mcp23017Setup(pin_base_0x21, i2c_addr_0x21)
wiringpi.mcp23017Setup(pin_base_0x22, i2c_addr_0x22)
wiringpi.mcp23017Setup(pin_base_0x23, i2c_addr_0x23)
wiringpi.mcp23017Setup(pin_base_0x24, i2c_addr_0x24)
wiringpi.mcp23017Setup(pin_base_0x25, i2c_addr_0x25)

path = pathlib.Path(__file__).parent.resolve() #path del progetto

switch_state = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #32
formulaone_lamps_state = [0,0,0,0,0,0,0,0,0,0] #10
k_lamps_state_orange = [0,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1] #-1 = k non selezionato, 0 = k selezionato, 1 = k ottenuto
center_target_state = [0,0,0] #i 3 target, 2 gialli e 1 rosso
coil_state = [0,0,0,0,0,0,0,0,0]
k_lamps_state_green = 0 #stato dei k verdi
flashingValue = 0 #stato dei flashing value
x=1 #moltiplicatore di score
flashingValueFlag = False
tyres=0 #consumo gomme
box = False
turbo=0
fastlap = False
now = 0.0
shootAgain = False
afterShootAgain = False
balls = -1 #numero palla in gioco
ballsXGame = 3 #numero di palle per partita
fastLapsCounter = 0 #counter di giri veloci

select_media_player = False
mediaPlayer1 = vlc.MediaPlayer()
mediaPlayer2 = vlc.MediaPlayer()
mediaPlayerBackground = vlc.MediaPlayer()

checkKGreen = False
checkK250 = False

extraBallRamp = False
playFieldScoreDouble = False

#semafori
partenza = 0 # 0=falsa partenza, 1=partenza ottima, 2=partenza ritardata

doubleScore = False

altoDX=0 #serve a far parlare i cronisti quando la palla tocca lo switch alto destro a molla
dxsx=0
seed(2) #fa in modo che il random() genera numeri casuali da 0 a 2

resetformulaonelamps = False

score = 0 #punteggio partita
hscore = 0
hscorediv = 0

window = Tk() #nuova finestra
window.attributes('-fullscreen', True) #fullscreen
w, h = window.winfo_screenwidth(), window.winfo_screenheight()

stato_semafori = -1
messaggio = ""

timeTextAttractMode=0 #tempo scritta in attract mode
timeTextInGame=0 #tempo scritta in partita

secondix = 0

pallaPersaDaDX = False
pallaPersaCentro = False

posPrec = 21

shutdown = 0 #conteggio spegnimento

########################################### begin INIT ###########################################

def initSwitchPins(portNumber, ports):
    print("initSwitchPins")
    for _ in range(ports):
        wiringpi.pinMode(portNumber, 0)   #0=input
        wiringpi.pullUpDnControl(portNumber, 2)
        portNumber += 1

def initLampPins(portNumber, ports):
    print("initLampPins")
    for _ in range(ports):
        wiringpi.pinMode(portNumber, 1)   #1=output
        wiringpi.digitalWrite(portNumber, 0)
        portNumber += 1
        
def initCoilPins():
    print("initCoilPins")
    GPIO.setwarnings(False)
    GPIO.setup(26, GPIO.OUT) # OutHole Kicker
    GPIO.setup(29, GPIO.OUT) # Saucer
    GPIO.setup(31, GPIO.OUT) # Fire
    GPIO.setup(32, GPIO.OUT) # Pop Bumper Left
    GPIO.setup(33, GPIO.OUT) # Pop Bumper Right
    GPIO.setup(35, GPIO.OUT) # Ball Release
    GPIO.setup(36, GPIO.OUT) # Sling Right
    GPIO.setup(37, GPIO.OUT) # Sling Left
    GPIO.setup(38, GPIO.OUT) # Pop Bumper Center
    GPIO.setup(40, GPIO.OUT) # Fast Lap
    GPIO.output(26, 0) #tutto disattivato
    GPIO.output(29, 0)
    GPIO.output(31, 0)
    GPIO.output(32, 0)
    GPIO.output(33, 0)
    GPIO.output(35, 0)
    GPIO.output(36, 0)
    GPIO.output(37, 0)
    GPIO.output(38, 0)
    GPIO.output(40, 0)
    
    GPIO.setup(16, GPIO.OUT) # General Illumination (Rele)
    GPIO.output(16, 1)

########################################### end INIT ###########################################
    
    
########################################### begin COIL ###########################################

def activeCoilOutHoleKicker():
    global coil_state
    
    if coil_state[0] == 0:
        coil_state[0] = 1
        sleep(.2)
    
        GPIO.output(26, 1)
        sleep(0.02) #20ms
        GPIO.output(26, 0)
        
        sleep(1)
        coil_state[0] = 0


def activeCoilFire():
    global coil_state
    
    if coil_state[1] == 0:
        coil_state[1] = 1
    
        GPIO.output(31, 1)
        sleep(0.050) #50ms
        GPIO.output(31, 0)
        
        coil_state[1] = 0


def activeCoilPopBumperCenter():
    global coil_state
    
    if coil_state[2] == 0:
        coil_state[2] = 1
    
        GPIO.output(38, 1)
        sleep(0.02) #20ms
        GPIO.output(38, 0)
        
        coil_state[2] = 0


def activeCoilPopBumperRight():
    global coil_state
    
    if coil_state[3] == 0:
        coil_state[3] = 1
    
        GPIO.output(33, 1)
        sleep(0.02) #20ms
        GPIO.output(33, 0)
        
        coil_state[3] = 0


def activeCoilPopBumperLeft():
    global coil_state
    
    if coil_state[4] == 0:
        coil_state[4] = 1
    
        GPIO.output(32, 1)
        sleep(0.02) #20ms
        GPIO.output(32, 0)
        
        coil_state[4] = 0


def activeCoilSaucer():
    global coil_state
    
    if coil_state[5] == 0:
        coil_state[5] = 1
    
        sleep(1)
        
        GPIO.output(29, 1)
        sleep(0.02) #20ms
        GPIO.output(29, 0)
        
        coil_state[5] = 0
        
    
def activeCoilSlingLeft():
    global coil_state
    
    if coil_state[6] == 0:
        coil_state[6] = 1
        
        GPIO.output(37, 1)
        sleep(0.02) #20ms
        GPIO.output(37, 0)
        
        coil_state[6] = 0
    
    
def activeCoilSlingRight():
    global coil_state
    
    if coil_state[7] == 0:
        coil_state[7] = 1
            
        GPIO.output(36, 1)
        sleep(0.02) #20ms
        GPIO.output(36, 0)
        
        coil_state[7] = 0


def activeCoilBallRelease():
    global coil_state
    
    if coil_state[8] == 0:
        coil_state[8] = 1
    
        sleep(1)
            
        GPIO.output(35, 1)
        sleep(0.02) #20ms
        GPIO.output(35, 0)
            
        coil_state[8] = 0

########################################### end COIL ###########################################
        
        
########################################## start LAMPS BLINK ###################################
def formulaoneBlink():
    global formulaone_lamps_state
    global resetformulaonelamps
    global shutdown
    
    while attract.getAttractFlag() == False and shutdown < 200:
        
        if formulaone_lamps_state[0] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(127, 1)
            sleep(.1)

        if formulaone_lamps_state[1] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(128, 1)
            sleep(.1)
            
        if formulaone_lamps_state[2] == 0 and not resetformulaonelamps:    
            wiringpi.digitalWrite(129, 1)
            sleep(.1)
            
        if formulaone_lamps_state[3] == 0 and not resetformulaonelamps:  
            wiringpi.digitalWrite(130, 1)
            sleep(.1)
            
        if formulaone_lamps_state[4] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(142, 1)
            sleep(.1)
            
        if formulaone_lamps_state[5] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(143, 1)
            sleep(.1)
            
        if formulaone_lamps_state[6] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(144, 1)
            sleep(.1)
        
        if formulaone_lamps_state[7] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(145, 1)
            sleep(.1)
            
        if formulaone_lamps_state[8] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(146, 1)
            sleep(.1)
            
        if formulaone_lamps_state[9] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(147, 1)
            sleep(.1)
            
        if formulaone_lamps_state[0] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(127, 0)
            sleep(.1)
            
        if formulaone_lamps_state[1] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(128, 0)
            sleep(.1)
            
        if formulaone_lamps_state[2] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(129, 0)
            sleep(.1)
            
        if formulaone_lamps_state[3] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(130, 0)
            sleep(.1)
            
        if formulaone_lamps_state[4] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(142, 0)
            sleep(.1)
            
        if formulaone_lamps_state[5] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(143, 0)
            sleep(.1)
            
        if formulaone_lamps_state[6] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(144, 0)
            sleep(.1)
            
        if formulaone_lamps_state[7] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(145, 0)
            sleep(.1)
            
        if formulaone_lamps_state[8] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(146, 0)
            sleep(.1)
            
        if formulaone_lamps_state[9] == 0 and not resetformulaonelamps:
            wiringpi.digitalWrite(147, 0)
            sleep(.1)
                    
            
        if resetformulaonelamps:
            resetformulaonelamps = False 
            Thread(target=blinkFormulaoneLamps).start() #lampeggio scritta formulaone
            break
            
     
def blinkFormulaoneLamps():
    global formulaone_lamps_state
    print("START blinkFormulaoneLamps")
    
    for _ in range(15):
        if formulaone_lamps_state[0]==0:
            wiringpi.digitalWrite(127, 1)    
        
        if formulaone_lamps_state[1]==0:
            wiringpi.digitalWrite(128, 1)
            
        if formulaone_lamps_state[2]==0:
            wiringpi.digitalWrite(129, 1)
            
        if formulaone_lamps_state[3]==0:
            wiringpi.digitalWrite(130, 1)
            
        if formulaone_lamps_state[4]==0:
            wiringpi.digitalWrite(142, 1)
            
        if formulaone_lamps_state[5]==0:
            wiringpi.digitalWrite(143, 1)
            
        if formulaone_lamps_state[6]==0:
            wiringpi.digitalWrite(144, 1)
            
        if formulaone_lamps_state[7]==0:
            wiringpi.digitalWrite(145, 1)
            
        if formulaone_lamps_state[8]==0:
            wiringpi.digitalWrite(146, 1)
            
        if formulaone_lamps_state[9]==0:
            wiringpi.digitalWrite(147, 1)
            
        GPIO.output(16, 1) # General Illumination (Rele)
        wiringpi.digitalWrite(107, 1) #auto al centro del playfield
        
        sleep(.2)
        
        if formulaone_lamps_state[0]==0:
            wiringpi.digitalWrite(127, 0)    
        
        if formulaone_lamps_state[1]==0:
            wiringpi.digitalWrite(128, 0)
            
        if formulaone_lamps_state[2]==0:
            wiringpi.digitalWrite(129, 0)
            
        if formulaone_lamps_state[3]==0:
            wiringpi.digitalWrite(130, 0)
            
        if formulaone_lamps_state[4]==0:
            wiringpi.digitalWrite(142, 0)
            
        if formulaone_lamps_state[5]==0:
            wiringpi.digitalWrite(143, 0)
            
        if formulaone_lamps_state[6]==0:
            wiringpi.digitalWrite(144, 0)
            
        if formulaone_lamps_state[7]==0:
            wiringpi.digitalWrite(145, 0)
            
        if formulaone_lamps_state[8]==0:
            wiringpi.digitalWrite(146, 0)
            
        if formulaone_lamps_state[9]==0:
            wiringpi.digitalWrite(147, 0)
            
        GPIO.output(16, 0) # General Illumination (Rele)
        wiringpi.digitalWrite(107, 0) #auto al centro del playfield
        
        sleep(.2)
        
        
    # torna al blink
    Thread(target=formulaoneBlink).start()
    
    print("END blinkFormulaoneLamps")
    
    
    
def fireLamps():
    global k_lamps_state_green
    global doubleScore
    global extraBallRamp
    global flashingValue
    
    wiringpi.digitalWrite(97, 1)
    wiringpi.digitalWrite(98, 1)
    sleep(.04)
    wiringpi.digitalWrite(97, 0)
    wiringpi.digitalWrite(98, 0)
    wiringpi.digitalWrite(100, 1)
    wiringpi.digitalWrite(151, 1)
    sleep(.04)
    wiringpi.digitalWrite(100, 0)
    wiringpi.digitalWrite(151, 0)
    wiringpi.digitalWrite(101, 1)
    wiringpi.digitalWrite(102, 1)
    sleep(.04)
    wiringpi.digitalWrite(101, 0)
    wiringpi.digitalWrite(102, 0)
    wiringpi.digitalWrite(103, 1)
    wiringpi.digitalWrite(108, 1)
    wiringpi.digitalWrite(116, 1)
    sleep(.04)
    wiringpi.digitalWrite(103, 0)
    wiringpi.digitalWrite(108, 0)
    wiringpi.digitalWrite(116, 0)
    wiringpi.digitalWrite(104, 1)
    wiringpi.digitalWrite(109, 1)
    wiringpi.digitalWrite(117, 1)
    wiringpi.digitalWrite(118, 1)
    sleep(.04)
    wiringpi.digitalWrite(104, 0)
    wiringpi.digitalWrite(109, 0)
    wiringpi.digitalWrite(117, 0)
    wiringpi.digitalWrite(118, 0)
    wiringpi.digitalWrite(156, 1)
    wiringpi.digitalWrite(105, 1)
    wiringpi.digitalWrite(110, 1)
    wiringpi.digitalWrite(119, 1)
    wiringpi.digitalWrite(125, 1)
    sleep(.04)
    wiringpi.digitalWrite(156, 0)
    wiringpi.digitalWrite(105, 0)
    wiringpi.digitalWrite(110, 0)
    wiringpi.digitalWrite(119, 0)
    wiringpi.digitalWrite(125, 0)
    wiringpi.digitalWrite(157, 1)
    wiringpi.digitalWrite(106, 1)
    wiringpi.digitalWrite(120, 1)
    wiringpi.digitalWrite(111, 1)
    sleep(.04)
    wiringpi.digitalWrite(157, 0)
    wiringpi.digitalWrite(106, 0)
    wiringpi.digitalWrite(120, 0)
    wiringpi.digitalWrite(111, 0)
    wiringpi.digitalWrite(131, 1)
    wiringpi.digitalWrite(132, 1)
    wiringpi.digitalWrite(133, 1)
    wiringpi.digitalWrite(131, 1)
    wiringpi.digitalWrite(112, 1)
    wiringpi.digitalWrite(126, 1)
    wiringpi.digitalWrite(121, 1)
    wiringpi.digitalWrite(123, 1)
    wiringpi.digitalWrite(107, 1)
    sleep(.04)
    wiringpi.digitalWrite(131, 0)
    wiringpi.digitalWrite(132, 0)
    wiringpi.digitalWrite(133, 0)
    wiringpi.digitalWrite(131, 0)
    wiringpi.digitalWrite(112, 0)
    wiringpi.digitalWrite(126, 0)
    wiringpi.digitalWrite(121, 0)
    wiringpi.digitalWrite(123, 0)
    wiringpi.digitalWrite(107, 0)
    wiringpi.digitalWrite(134, 1)
    wiringpi.digitalWrite(113, 1)
    wiringpi.digitalWrite(122, 1)
    wiringpi.digitalWrite(124, 1)
    wiringpi.digitalWrite(135, 1)
    wiringpi.digitalWrite(136, 1)
    wiringpi.digitalWrite(137, 1)
    sleep(.04)
    wiringpi.digitalWrite(134, 0)
    wiringpi.digitalWrite(113, 0)
    wiringpi.digitalWrite(122, 0)
    wiringpi.digitalWrite(124, 0)
    wiringpi.digitalWrite(135, 0)
    wiringpi.digitalWrite(136, 0)
    wiringpi.digitalWrite(137, 0)
    wiringpi.digitalWrite(114, 1)
    wiringpi.digitalWrite(138, 1)
    sleep(.04)
    wiringpi.digitalWrite(114, 0)
    wiringpi.digitalWrite(138, 0)
    wiringpi.digitalWrite(139, 1)
    wiringpi.digitalWrite(140, 1)
    wiringpi.digitalWrite(115, 1)
    wiringpi.digitalWrite(141, 1)
    sleep(.04)
    wiringpi.digitalWrite(139, 0)
    wiringpi.digitalWrite(140, 0)
    wiringpi.digitalWrite(115, 0)
    wiringpi.digitalWrite(141, 0)
    wiringpi.digitalWrite(149, 1)
    sleep(.04)
    wiringpi.digitalWrite(149, 0)
    wiringpi.digitalWrite(152, 1)
    wiringpi.digitalWrite(150, 1)
    sleep(.04)
    wiringpi.digitalWrite(152, 0)
    wiringpi.digitalWrite(150, 0)
    wiringpi.digitalWrite(153, 1)
    wiringpi.digitalWrite(148, 1)
    sleep(.04)
    wiringpi.digitalWrite(153, 0)
    wiringpi.digitalWrite(148, 0)
    wiringpi.digitalWrite(154, 1)
    wiringpi.digitalWrite(155, 1)
    sleep(.04)
    wiringpi.digitalWrite(154, 0)
    wiringpi.digitalWrite(155, 0)
    
    #a volte alcune luci rimangono accese, rispegnile tutte velocemente
    for i in range(64):
        #se non sono le luci FORMULAONE
        if i+97 != 127 and i+97 != 128 and i+97 != 129 and i+97 != 130 and i+97 != 142 and i+97 != 143 and i+97 != 144 and i+97 != 145 and i+97 != 146 and i+97 != 147:
            wiringpi.digitalWrite(97+i, 0) #spegni
    
    #------------- Restore lamps after blink artwork ----------------------
    # 1. se avevi completato tutte le luci arancioni riaccendile tutte
    if kOrangeCompleted():
        wiringpi.digitalWrite(117, 1)
        wiringpi.digitalWrite(118, 1)
        wiringpi.digitalWrite(119, 1)
        wiringpi.digitalWrite(120, 1)
        wiringpi.digitalWrite(121, 1)
        wiringpi.digitalWrite(122, 1)
        wiringpi.digitalWrite(115, 1)
        wiringpi.digitalWrite(100, 1)
        wiringpi.digitalWrite(101, 1)
        wiringpi.digitalWrite(102, 1)
        wiringpi.digitalWrite(103, 1)
        wiringpi.digitalWrite(104, 1)
        wiringpi.digitalWrite(105, 1)
        wiringpi.digitalWrite(106, 1)
    
    # 2. se avevi completato tutte le luci verdi (25k, 50k, 100k riaccendile tutte
    if k_lamps_state_green==3: #se è 3 ho ottenuto tutto
        wiringpi.digitalWrite(132, 1) #25k
        wiringpi.digitalWrite(133, 1) #50k
        wiringpi.digitalWrite(134, 1) #100k
        
    #3. se avevi acceso "double score", riaccendi la luce blu
    if doubleScore == True:
        wiringpi.digitalWrite(140, 1) #double score
        
    #4. se "extra ball" sulla rampa box era attiva, riaccendila
    if extraBallRamp == True:
        wiringpi.digitalWrite(139, 1) #luce extraball della rampa
        
    #5. ripristina le luci verdi del moltiplicatore, 2x, 3x ......
    restoreX()
    
    #6. ripristina le S lamps dei giri veloci
    Thread(target=sLamps).start()
    
    #7. ripristina 100k, 200k 300k
    if center_target_state[0]==1:
        wiringpi.digitalWrite(135, 1) #100k
    if center_target_state[1]==1:
        wiringpi.digitalWrite(136, 1) #200k
    if center_target_state[2]==1:
        wiringpi.digitalWrite(137, 1) #300k
    
    
########################################## end LAMPS BLINK #####################################
    

def scoreCalculation(s):
    global doubleScore
    global score
    global x
    global window
        
    if playFieldScoreDouble == False:
        score = score+(x*s)
    else:
        score = score+(2*x*s)
        

def resetFormulaone():
    global resetformulaonelamps
    
    for i in range(10):
        formulaone_lamps_state[i] = 0 #resetta
    
    resetformulaonelamps = True
        
        
def checkFormulaone():
    global path
    global box
    global tyres
    
    print("START checkFormulaone")
            
    if formulaoneCompleted():
        resetFormulaone()
        
        box = False
        tyres = 30
        
        incrementX(2)
        
        Thread(target=flashingValueFunction).start() #lampeggio luci 100k, 200k 300k
        
        filename=path / 'audio/formulaonecompleted.mp3'
        Thread(target=audio, args=(filename,)).start()
            
        #multiball
        if wiringpi.digitalRead(65+0): #se è presente la seconda palla in buca  
            t=1.0
            while not wiringpi.digitalRead(65+1) and attract.getAttractFlag() == False: #mentre la palla non sta sulla rampa di lancio
                sleep(.5)
                t=t+0.5
                if t >= 1.0 and not wiringpi.digitalRead(65+1): #ogni secondo riprova a mettere fuori la palla se l'operazione non va a buon fine
                    Thread(target=activeCoilBallRelease).start()
                    t=0.0
                
            Thread(target=activeCoilFire).start() #quindi lanciala
            
            #accensione luci playfield
            Thread(target=fireLamps).start()
    
    Thread(target=updateFormulaoneLamps).start()
    
    print("END checkFormulaone")


def restoreX():
    print("START restoreX")
    global x
    
    if x==1:
        wiringpi.digitalWrite(108, 0)
        wiringpi.digitalWrite(109, 0)
        wiringpi.digitalWrite(110, 0)
        wiringpi.digitalWrite(111, 0)
        wiringpi.digitalWrite(112, 0)
        wiringpi.digitalWrite(113, 0)
        wiringpi.digitalWrite(114, 0)
    
    if x==2:
        wiringpi.digitalWrite(108, 1)
        wiringpi.digitalWrite(109, 0)
        wiringpi.digitalWrite(110, 0)
        wiringpi.digitalWrite(111, 0)
        wiringpi.digitalWrite(112, 0)
        wiringpi.digitalWrite(113, 0)
        wiringpi.digitalWrite(114, 0)
        
    if x==3:
        wiringpi.digitalWrite(108, 1)
        wiringpi.digitalWrite(109, 1)
        wiringpi.digitalWrite(110, 0)
        wiringpi.digitalWrite(111, 0)
        wiringpi.digitalWrite(112, 0)
        wiringpi.digitalWrite(113, 0)
        wiringpi.digitalWrite(114, 0)
        
    if x==4:
        wiringpi.digitalWrite(108, 1)
        wiringpi.digitalWrite(109, 1)
        wiringpi.digitalWrite(110, 1)
        wiringpi.digitalWrite(111, 0)
        wiringpi.digitalWrite(112, 0)
        wiringpi.digitalWrite(113, 0)
        wiringpi.digitalWrite(114, 0)
        
    if x==5:
        wiringpi.digitalWrite(108, 1)
        wiringpi.digitalWrite(109, 1)
        wiringpi.digitalWrite(110, 1)
        wiringpi.digitalWrite(111, 1)
        wiringpi.digitalWrite(112, 0)
        wiringpi.digitalWrite(113, 0)
        wiringpi.digitalWrite(114, 0)
        
    if x==6:
        wiringpi.digitalWrite(108, 1)
        wiringpi.digitalWrite(109, 1)
        wiringpi.digitalWrite(110, 1)
        wiringpi.digitalWrite(111, 1)
        wiringpi.digitalWrite(112, 1)
        wiringpi.digitalWrite(113, 0)
        wiringpi.digitalWrite(114, 0)
        
    if x==7:
        wiringpi.digitalWrite(108, 1)
        wiringpi.digitalWrite(109, 1)
        wiringpi.digitalWrite(110, 1)
        wiringpi.digitalWrite(111, 1)
        wiringpi.digitalWrite(112, 1)
        wiringpi.digitalWrite(113, 1)
        wiringpi.digitalWrite(114, 0)
        
    if x>=8:
        wiringpi.digitalWrite(108, 1)
        wiringpi.digitalWrite(109, 1)
        wiringpi.digitalWrite(110, 1)
        wiringpi.digitalWrite(111, 1)
        wiringpi.digitalWrite(112, 1)
        wiringpi.digitalWrite(113, 1)
        wiringpi.digitalWrite(114, 1)

    print("END restoreX")


def incrementX(w):
    print("START incrementX")
    global x
    
    x=x+w #incrementa a prescindere
    
    if x > 8: #se l'incremento ha superato 8, portalo a 8
        x=8
    
    restoreX() #aggiorna le luci

    print("END incrementX")


def confirmKGreenValue():
    print("START confirmKGreenValue")
    global checkK250
    global k_lamps_state_green
    global shutdown
    
    k_lamps_state_green+=1
        
    if k_lamps_state_green == 3 and checkK250 == False: #se li hai presi tutti e 3...
        checkK250=True
        
        while checkK250 == True and attract.getAttractFlag() == False and shutdown < 200: #mentre non hai ottenuto il 250k, fallo lampeggiare
            wiringpi.digitalWrite(138, 1)
            sleep(.2)
            wiringpi.digitalWrite(138, 0)
            sleep(.2)
            
    print("END confirmKGreenValue")           


def kGreenBlink():
    print("START kGreenBlink")
    global k_lamps_state_green
    global shutdown
    
    while kOrangeCompleted() and attract.getAttractFlag() == False and shutdown < 200:
        if k_lamps_state_green == 0: #se è 0 non ho ottenuto ancora alcun green quindi faccio lampeggiare 25K
            wiringpi.digitalWrite(132, 1)
            sleep(.2)
            wiringpi.digitalWrite(132, 0)
            sleep(.2)
        
        if k_lamps_state_green == 1: #se è 1 ho ottenuto 25k e lo fisso
            wiringpi.digitalWrite(132, 1) #25k
    
            wiringpi.digitalWrite(133, 1) #lampeggio del 50K
            sleep(.2)
            wiringpi.digitalWrite(133, 0)
            sleep(.2)
            
        if k_lamps_state_green == 2: #se è 2 ho ottenuto 25k e 50k e li fisso
            wiringpi.digitalWrite(132, 1) #25k
            wiringpi.digitalWrite(133, 1) #50k
        
            wiringpi.digitalWrite(134, 1) #lampeggio del 100K
            sleep(.2)
            wiringpi.digitalWrite(134, 0)
            sleep(.2)
        
        if k_lamps_state_green==3: #se è 3 ho ottenuto tutto
            wiringpi.digitalWrite(132, 1) #25k
            wiringpi.digitalWrite(133, 1) #50k
            wiringpi.digitalWrite(134, 1) #100k
            incrementX(1)
            break
    
    print("END kGreenBlink")
               
            
def confirmKOrangeValue():
    print("START confirmKOrangeValue")

    global ballsXGame
    global checkKGreen
    global extraBallRamp
    
    k=0
    for i in range(14):
        if k_lamps_state_orange[i]==0:
            k_lamps_state_orange[i]=1
            k=i
            
            if i==0:
                scoreCalculation(1000)
            if i==1:
                scoreCalculation(2000)
            if i==2:
                scoreCalculation(4000)
            if i==3:
                scoreCalculation(8000)
            if i==4:
                scoreCalculation(16000)
            if i==5:
                scoreCalculation(32000)
            if i==6: #hai ottenuto la palla extra
                ballsXGame+=1
                scoreCalculation(100000)
            if i==7:
                scoreCalculation(7000)
            if i==8:
                scoreCalculation(14000)
            if i==9:
                scoreCalculation(21000)
            if i==10:
                scoreCalculation(28000)
            if i==11:
                scoreCalculation(35000)
            if i==12:
                scoreCalculation(42000)
            if i==13:
                scoreCalculation(49000)
                
            break
                
    #ricerca del -1 dopo lo 0 per metterlo a 0            
    trovato = False
    z=k+1
    while z<14 and trovato==False:
        if k_lamps_state_orange[z]==-1:
            trovato=True
            k_lamps_state_orange[z]=0
            break
        else:
            z+=1
            
    if trovato==False:
        z=0
        while z<=k and trovato==False:
            if k_lamps_state_orange[z]==-1:
                trovato=True
                k_lamps_state_orange[z]=0
                break
            else:
                z+=1
    
    
    #se  hai completati tutti i k arancioni allora fai lampeggiare i K verdi 25k, 50k, 100k
    if kOrangeCompleted() and checkKGreen == False:
        checkKGreen=True
        Thread(target=kGreenBlink).start()
        wiringpi.digitalWrite(139, 1) #luce extraball della rampa
        extraBallRamp = True
    print("END confirmKOrangeValue")


def K250():
    print("START K250")
    global checkKGreen
    global checkK250
    global k_lamps_state_orange
    global k_lamps_state_green
    global doubleScore
    
    #resetta tutti i K scores
    k_lamps_state_orange = [0,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1] #-1 = k non selezionato, 0 = k selezionato, 1 = k ottenuto
    k_lamps_state_green = 0 #25k, 50k, 100k
    wiringpi.digitalWrite(138, 0) # quindi spegni la 250k blue
    
    checkKGreen = False
    checkK250 = False
    
    scoreCalculation(250000)

    Thread(target=kOrangeBlink).start() #riparti da capo con i blink
    
    #spegni le luci verdi 25k,50k, 100k
    wiringpi.digitalWrite(132, 0) #25k
    wiringpi.digitalWrite(133, 0) #50k
    wiringpi.digitalWrite(134, 0) #100k
    
    incrementX(1)
    
    #attiva la luce del double score sulla rampa
    wiringpi.digitalWrite(140, 1) #double score
    doubleScore = True

    print("END K250")
    

def kOrangeBlink():
    global shutdown
    print("START kOrangeBlink")
    
    while attract.getAttractFlag() == False and not kOrangeCompleted() and shutdown < 200:
        if k_lamps_state_orange[0]==0:
            wiringpi.digitalWrite(117, 1)
            sleep(.2)
            wiringpi.digitalWrite(117, 0)
            sleep(.2)
        elif k_lamps_state_orange[0]==1:
            wiringpi.digitalWrite(117, 1)
        else:
            wiringpi.digitalWrite(117, 0)
    
        if k_lamps_state_orange[1]==0:
            wiringpi.digitalWrite(118, 1)
            sleep(.2)
            wiringpi.digitalWrite(118, 0)
            sleep(.2)
        elif k_lamps_state_orange[1]==1:
            wiringpi.digitalWrite(118, 1)
        else:
            wiringpi.digitalWrite(118, 0)
    
        if k_lamps_state_orange[2]==0:
            wiringpi.digitalWrite(119, 1)
            sleep(.2)
            wiringpi.digitalWrite(119, 0)
            sleep(.2)
        elif k_lamps_state_orange[2]==1:
            wiringpi.digitalWrite(119, 1)
        else:
            wiringpi.digitalWrite(119, 0)
            
        if k_lamps_state_orange[3]==0:
            wiringpi.digitalWrite(120, 1)
            sleep(.2)
            wiringpi.digitalWrite(120, 0)
            sleep(.2)
        elif k_lamps_state_orange[3]==1:
            wiringpi.digitalWrite(120, 1)
        else:
            wiringpi.digitalWrite(120, 0)
            
        if k_lamps_state_orange[4]==0:
            wiringpi.digitalWrite(121, 1)
            sleep(.2)
            wiringpi.digitalWrite(121, 0)
            sleep(.2)
        elif k_lamps_state_orange[4]==1:
            wiringpi.digitalWrite(121, 1)
        else:
            wiringpi.digitalWrite(121, 0)
        
        if k_lamps_state_orange[5]==0:
            wiringpi.digitalWrite(122, 1)
            sleep(.2)
            wiringpi.digitalWrite(122, 0)
            sleep(.2)
        elif k_lamps_state_orange[5]==1:
            wiringpi.digitalWrite(122, 1)
        else:
            wiringpi.digitalWrite(122, 0)
            
        if k_lamps_state_orange[6]==0:
            wiringpi.digitalWrite(115, 1)
            sleep(.2)
            wiringpi.digitalWrite(115, 0)
            sleep(.2)
        elif k_lamps_state_orange[6]==1:
            wiringpi.digitalWrite(115, 1)
        else:
            wiringpi.digitalWrite(115, 0)
            
        if k_lamps_state_orange[7]==0:
            wiringpi.digitalWrite(100, 1)
            sleep(.2)
            wiringpi.digitalWrite(100, 0)
            sleep(.2)
        elif k_lamps_state_orange[7]==1:
            wiringpi.digitalWrite(100, 1)
        else:
            wiringpi.digitalWrite(100, 0)
            
        if k_lamps_state_orange[8]==0:
            wiringpi.digitalWrite(101, 1)
            sleep(.2)
            wiringpi.digitalWrite(101, 0)
            sleep(.2)
        elif k_lamps_state_orange[8]==1:
            wiringpi.digitalWrite(101, 1)
        else:
            wiringpi.digitalWrite(101, 0)
            
        if k_lamps_state_orange[9]==0:
            wiringpi.digitalWrite(102, 1)
            sleep(.2)
            wiringpi.digitalWrite(102, 0)
            sleep(.2)
        elif k_lamps_state_orange[9]==1:
            wiringpi.digitalWrite(102, 1)
        else:
            wiringpi.digitalWrite(102, 0)
            
        if k_lamps_state_orange[10]==0:
            wiringpi.digitalWrite(103, 1)
            sleep(.2)
            wiringpi.digitalWrite(103, 0)
            sleep(.2)
        elif k_lamps_state_orange[10]==1:
            wiringpi.digitalWrite(103, 1)
        else:
            wiringpi.digitalWrite(103, 0)
        
        if k_lamps_state_orange[11]==0:
            wiringpi.digitalWrite(104, 1)
            sleep(.2)
            wiringpi.digitalWrite(104, 0)
            sleep(.2)
        elif k_lamps_state_orange[11]==1:
            wiringpi.digitalWrite(104, 1)
        else:
            wiringpi.digitalWrite(104, 0)
            
        if k_lamps_state_orange[12]==0:
            wiringpi.digitalWrite(105, 1)
            sleep(.2)
            wiringpi.digitalWrite(105, 0)
            sleep(.2)
        elif k_lamps_state_orange[12]==1:
            wiringpi.digitalWrite(105, 1)
        else:
            wiringpi.digitalWrite(105, 0)
            
        if k_lamps_state_orange[13]==0:
            wiringpi.digitalWrite(106, 1)
            sleep(.2)
            wiringpi.digitalWrite(106, 0)
            sleep(.2)
        elif k_lamps_state_orange[13]==1:
            wiringpi.digitalWrite(106, 1)
        else:
            wiringpi.digitalWrite(106, 0)
            
    #se kOrangeCompleted accendili tutti ed esci
    if kOrangeCompleted():
        wiringpi.digitalWrite(117, 1)
        wiringpi.digitalWrite(118, 1)
        wiringpi.digitalWrite(119, 1)
        wiringpi.digitalWrite(120, 1)
        wiringpi.digitalWrite(121, 1)
        wiringpi.digitalWrite(122, 1)
        wiringpi.digitalWrite(115, 1)
        wiringpi.digitalWrite(100, 1)
        wiringpi.digitalWrite(101, 1)
        wiringpi.digitalWrite(102, 1)
        wiringpi.digitalWrite(103, 1)
        wiringpi.digitalWrite(104, 1)
        wiringpi.digitalWrite(105, 1)
        wiringpi.digitalWrite(106, 1)
        
        incrementX(1)
    
    print("END kOrangeBlink")


def formulaoneLetterObtained():
    print("START formulaoneLetterObtained")

    for i in range(10):
        if formulaone_lamps_state[i]==0: #accende la prima lettera di FORMULAONE ancora non ottenuta ed esce 
            formulaone_lamps_state[i]=1
            Thread(target=checkFormulaone).start() #controlla se FORMULAONE e' stato completato
            break
    print("END formulaoneLetterObtained")
    
    
def formulaoneCompleted(): #ritorna vero se FORMULAONE e' tutto acceso
    flag=True
    for i in range(10):
        if formulaone_lamps_state[i]==0:
            flag=False
            break
        
    return flag
    

def sLamps():
    print("START sLamps")
    global fastLapsCounter
    
    if fastLapsCounter == 1:
        wiringpi.digitalWrite(97, 1) #S destra
    elif fastLapsCounter == 2:
        wiringpi.digitalWrite(98, 1) #S sinistra
        wiringpi.digitalWrite(123, 1) #luce increase ramp
    elif fastLapsCounter == 0:
        wiringpi.digitalWrite(97, 0)
        wiringpi.digitalWrite(98, 0)
        wiringpi.digitalWrite(123, 0) #luce increase ramp

    print("END sLamps")
    

def kOrangeScores():
    print("START kOrangeScores")
    trovatoK = False #cerca lo 0
    
    for i in range(14): #ricerca dello 0
        if k_lamps_state_orange[i]==0:
            k = i
            trovatoK = True
            break
    
    if trovatoK == True:
        trovatoZ = False #cerca il -1 dopo lo 0
        
        j=k+1
        while j<=13 and trovatoZ==False: #ricerca del -1 dopo lo 0
            if k_lamps_state_orange[j]==-1:
                trovatoZ = True
                z = j
            else:
                j+=1
                
        if trovatoZ==False: #ricomincia da capo fino alla posizione k
            j=0
            while j<k and trovatoZ==False: #ricerca del -1 dopo lo 0
                if k_lamps_state_orange[j]==-1:
                    trovatoZ = True
                    z = j
                else:
                    j+=1
                    
        if trovatoZ==True:
            k_lamps_state_orange[k]=-1
            k_lamps_state_orange[z]=0
    
    print(k_lamps_state_orange)
    print("END kOrangeScores")


def resetXLamps():
    print("START resetXLamps")
    wiringpi.digitalWrite(115, 0)
    sleep(.1)
    wiringpi.digitalWrite(114, 0)
    sleep(.1)
    wiringpi.digitalWrite(113, 0)
    sleep(.1)
    wiringpi.digitalWrite(112, 0)
    sleep(.1)
    wiringpi.digitalWrite(111, 0)
    sleep(.1)
    wiringpi.digitalWrite(110, 0)
    sleep(.1)
    wiringpi.digitalWrite(109, 0)
    sleep(.1)
    wiringpi.digitalWrite(108, 0)
    print("END resetXLamps")
    
    return 1


def audio(filename):
    print("START audio")
    global select_media_player
    media = vlc.Media(filename)
    
    if select_media_player == True:
        mediaPlayer2.set_media(media)
        mediaPlayer2.audio_set_volume(150)
        mediaPlayer2.play()
        select_media_player = False
    else:
        mediaPlayer1.set_media(media)
        mediaPlayer1.audio_set_volume(150)
        mediaPlayer1.play()
        select_media_player = True
    
    print("END audio")

    
def flashingValueFunction():
    print("START flashingValueFunction")
    global flashingValueFlag
    global flashingValue
    global shutdown
    
    i=0
    while i<20 and flashingValueFlag == False and attract.getAttractFlag() == False and shutdown < 200:
        wiringpi.digitalWrite(135, 1)
        flashingValue=1
        sleep(.1)
        wiringpi.digitalWrite(135, 0)
        
        wiringpi.digitalWrite(136, 1)
        flashingValue=2
        sleep(.1)
        wiringpi.digitalWrite(136, 0)
        
        wiringpi.digitalWrite(137, 1)
        flashingValue=3
        sleep(.1)
        wiringpi.digitalWrite(137, 0)
        
        i+=1
        
    flashingValueFlag = False
    flashingValue=0
    
    print("END flashingValueFunction")
    

def flashingValuesConfirm(lamp):
    print("START flashingValuesConfirm")
    
    if lamp == 0:
        Thread(target=blinkFlashingValueRear).start()
        sleep(.1)
        wiringpi.digitalWrite(135, 1)
        wiringpi.digitalWrite(136, 0)
        wiringpi.digitalWrite(137, 0)
        sleep(8)
        
    if lamp == 1:
        Thread(target=blinkFlashingValueRear).start()
        sleep(.1)
        wiringpi.digitalWrite(135, 0)
        wiringpi.digitalWrite(136, 1)
        wiringpi.digitalWrite(137, 0)
        sleep(8)
        
    if lamp == 2:
        Thread(target=blinkFlashingValueRear).start()
        sleep(.1)
        wiringpi.digitalWrite(135, 0)
        wiringpi.digitalWrite(136, 0)
        wiringpi.digitalWrite(137, 1)
        sleep(8)
        
    
    wiringpi.digitalWrite(135, 0)
    wiringpi.digitalWrite(136, 0)
    wiringpi.digitalWrite(137, 0)
    
    print("END flashingValuesConfirm")
    

def updateFormulaoneLamps():
    print("START updateFormulaoneLamps")
    sleep(.1)
    if formulaone_lamps_state[0] == 1:
        wiringpi.digitalWrite(127, 1)
    else:
        wiringpi.digitalWrite(127, 0)
        
    if formulaone_lamps_state[1] == 1:
        wiringpi.digitalWrite(128, 1)
    else:
        wiringpi.digitalWrite(128, 0)
        
    if formulaone_lamps_state[2] == 1:
        wiringpi.digitalWrite(129, 1)
    else:
        wiringpi.digitalWrite(129, 0)
        
    if formulaone_lamps_state[3] == 1:
        wiringpi.digitalWrite(130, 1)
    else:
        wiringpi.digitalWrite(130, 0)
        
    if formulaone_lamps_state[4] == 1:
        wiringpi.digitalWrite(142, 1)
    else:
        wiringpi.digitalWrite(142, 0)
        
    if formulaone_lamps_state[5] == 1:
        wiringpi.digitalWrite(143, 1)
    else:
        wiringpi.digitalWrite(143, 0)
        
    if formulaone_lamps_state[6] == 1:
        wiringpi.digitalWrite(144, 1)
    else:
        wiringpi.digitalWrite(144, 0)
        
    if formulaone_lamps_state[7] == 1:
        wiringpi.digitalWrite(145, 1)
    else:
        wiringpi.digitalWrite(145, 0)
        
    if formulaone_lamps_state[8] == 1:
        wiringpi.digitalWrite(146, 1)
    else:
        wiringpi.digitalWrite(146, 0)
        
    if formulaone_lamps_state[9] == 1:
        wiringpi.digitalWrite(147, 1)
    else:
        wiringpi.digitalWrite(147, 0)

    print("END updateFormulaoneLamps")
    

def flashingValueRear(): #le 2 luci bianche dove sta il bonus 100 200 300 vengono accese e spente una sola volta
    print("START flashingValueRear")
    wiringpi.digitalWrite(141, 1)
    sleep(.1)
    wiringpi.digitalWrite(141, 0)
    print("END flashingValueRear")


def blinkFlashingValueRear(): #le 2 luci bianche dove sta il bonus 100 200 300 vengono accese e spente 20 volte
    print("START blinkFlashingValueRear")
    for _ in range(20):
        wiringpi.digitalWrite(141, 1)
        sleep(.1)
        wiringpi.digitalWrite(141, 0)
        sleep(.1)
    print("END blinkFlashingValueRear")


def flashingEnterInRamp():
    print("START flashingEnterInRamp")
    global box
    global x
    global secondix
    global shutdown
    
    secondix = 0.0
    
    while box == True and attract.getAttractFlag() == False and shutdown < 200:
        wiringpi.digitalWrite(124, 1)
        sleep(.1)
        wiringpi.digitalWrite(124, 0)
        sleep(.1)
        
        secondix = secondix + 0.2 #somma il tempo da quando si sono attivati i box
        
        if secondix >= 20.0: #ogni tot secondi decrementa il moltiplicatore x di 1 unità
            secondix = 0.0
            if x > 1:
                x = x-1
                restoreX()
        
    wiringpi.digitalWrite(124, 0)
    print("END flashingEnterInRamp")
    

def flashingRearLamps():
    print("START flashingRearLamps")
    global box
    global shutdown
    
    wiringpi.digitalWrite(156, 1)
    wiringpi.digitalWrite(157, 1)
    wiringpi.digitalWrite(107, 1)
    
    while box == True and attract.getAttractFlag() == False and shutdown < 200:
        wiringpi.digitalWrite(125, 1)
        sleep(.1)
        wiringpi.digitalWrite(125, 0)
        wiringpi.digitalWrite(126, 1)
        sleep(.1)
        wiringpi.digitalWrite(126, 0)
        wiringpi.digitalWrite(152, 1)
        sleep(.1)
        wiringpi.digitalWrite(152, 0)
        wiringpi.digitalWrite(153, 1)
        sleep(.1)
        wiringpi.digitalWrite(153, 0)
        wiringpi.digitalWrite(154, 1)
        sleep(.1)
        wiringpi.digitalWrite(154, 0)
        wiringpi.digitalWrite(155, 1)
        sleep(.1)
        wiringpi.digitalWrite(155, 0)
    print("END flashingRearLamps")
    
        
def flashingBumper(lamp):
    print("START flashingBumper")
    wiringpi.digitalWrite(lamp, 1)
    sleep(.1)
    wiringpi.digitalWrite(lamp, 0)
    print("END flashingBumper")


def popBumperLamps():
    print("START popBumperLamps")
    global fastlap
    
    sleep(.5)
    wiringpi.digitalWrite(148, 1)
    wiringpi.digitalWrite(149, 1)
    wiringpi.digitalWrite(150, 1)
    
    while fastlap == True and attract.getAttractFlag() == False:
        pass #non fare nulla
        
    wiringpi.digitalWrite(148, 0)
    wiringpi.digitalWrite(149, 0)
    wiringpi.digitalWrite(150, 0)
    print("END popBumperLamps")
        
    
def kOrangeCompleted():
    flag=True
    for i in range(14):
        if k_lamps_state_orange[i]==0:
            flag=False
            break
    
    return flag


def semafori():
    global partenza
    global stato_semafori
    global balls
        
    partenza = 0 # 0 = falsa partenza
    attesaCasuale = random()
    
    #audio
    if balls % 4 == 1:
        filename=path / 'audio/start_ITA.mp3'
    elif balls % 4 == 2:
        filename=path / 'audio/start_OLA.mp3'
    elif balls % 4 == 3:
        filename=path / 'audio/start_MEX.mp3'
    else:
        filename=path / 'audio/start_USA.mp3'
    Thread(target=audio, args=(filename,)).start()
    #audio
    
    #si accendono i semafori
    for i in range(5):
        stato_semafori=i
        sleep(1)
        
    sleep(attesaCasuale)
    stato_semafori = -1  #semafori appena spenti
    #da questo momento si apre la finestra per la partenza ottima
    partenza = 1 # 1 = partenza ottima
    sleep(.2)
    
    #dopo lo spegnimento dei semafori e del tempo .2sec
    partenza = 2 # 2 = partenza ritardata


def blinkShootAgain():
    print("START blinkShootAgain")
    global shootAgain
    global afterShootAgain
    global shutdown
    
    if afterShootAgain == False:
        shootAgain = True
        
        i=0
        while i<60 and shootAgain == True and attract.getAttractFlag() == False and shutdown < 200:
            #con questo if accendo la luce una sola volta senza che ad ogni ciclo riaccendo una luce gia' accesa
            if i==0:
                wiringpi.digitalWrite(99, 1)
                
            sleep(.1)
            i+=1
        
        i=0
        while i<10 and shootAgain == True and attract.getAttractFlag() == False and shutdown < 200:
            wiringpi.digitalWrite(99, 1)
            sleep(.1)
            wiringpi.digitalWrite(99, 0)
            sleep(.1)
            i+=1
        
        wiringpi.digitalWrite(99, 0)
        shootAgain = False
    print("END blinkShootAgain")
        
        
def backgroundMusic():
    global mediaPlayerBackground
    global path
    
    i=231.0
    while attract.getAttractFlag() == False:
        sleep(.5)
        i=i+0.5
        if i >= 230.0: #230 sono i sec della musica di sottofondo, quando scadono e sei ancora in partita fai ricominciare la canzone
            mediaBackground = vlc.Media(path / 'audio/sottofondo.mp3')
            mediaPlayerBackground.set_media(mediaBackground)
            mediaPlayerBackground.audio_set_volume(80)
            mediaPlayerBackground.play()
            i=0
            

def boxCompleted():
    global path
    
    sleep(1.5)
    wiringpi.digitalWrite(156, 0)
    wiringpi.digitalWrite(157, 0)
    wiringpi.digitalWrite(107, 0)
    filename= path / 'audio/boxexecuted.mp3'
    Thread(target=audio, args=(filename,)).start()
        
        
def obtainF():
    global formulaone_lamps_state
    global tyres
    global switch_state
    global path
    
    formulaone_lamps_state[0] = 1
    filename=path / 'audio/audioF.mp3'
    Thread(target=audio, args=(filename,)).start()
    tyres-=1
    Thread(target=checkFormulaone).start() #controlla se FORMULAONE è stato completato
    scoreCalculation(10000)
    
    sleep(.2)
    switch_state[7] = 0
    

def obtainO():
    global formulaone_lamps_state
    global tyres
    global switch_state
    global path
    
    formulaone_lamps_state[1] = 1
    filename= path / 'audio/audioO.mp3'
    Thread(target=audio, args=(filename,)).start()
    tyres-=1
    Thread(target=checkFormulaone).start() #controlla se FORMULAONE è stato completato
    scoreCalculation(10000)
    
    sleep(.2)
    switch_state[8] = 0
    

def obtainR():
    global formulaone_lamps_state
    global tyres
    global switch_state
    global path
    
    formulaone_lamps_state[2] = 1
    filename= path / 'audio/audioR.mp3'
    Thread(target=audio, args=(filename,)).start()
    tyres-=1
    Thread(target=checkFormulaone).start() #controlla se FORMULAONE è stato completato
    scoreCalculation(10000)
    
    sleep(.2)
    switch_state[9] = 0
    
    
def obtainM():
    global formulaone_lamps_state
    global tyres
    global switch_state
    global path
    
    formulaone_lamps_state[3] = 1
    filename= path / 'audio/audioM.mp3'
    Thread(target=audio, args=(filename,)).start()
    tyres-=1
    Thread(target=checkFormulaone).start() #controlla se FORMULAONE è stato completato
    scoreCalculation(10000)
    
    sleep(.2)
    switch_state[10] = 0
    

def obtainU():
    global formulaone_lamps_state
    global tyres
    global switch_state
    global path
    
    formulaone_lamps_state[4] = 1
    filename=path / 'audio/audioU.mp3'
    Thread(target=audio, args=(filename,)).start()
    tyres-=1
    Thread(target=checkFormulaone).start() #controlla se FORMULAONE è stato completato
    scoreCalculation(10000)
    
    sleep(.2)
    switch_state[11] = 0
    

def obtainL():
    global formulaone_lamps_state
    global tyres
    global switch_state
    global path
    
    formulaone_lamps_state[5] = 1
    filename=path / 'audio/audioL.mp3'
    Thread(target=audio, args=(filename,)).start()
    tyres-=1
    Thread(target=checkFormulaone).start() #controlla se FORMULAONE è stato completato
    scoreCalculation(10000)
    
    sleep(.2)
    switch_state[12] = 0
    

def obtainA():
    global formulaone_lamps_state
    global tyres
    global switch_state
    global path
    
    formulaone_lamps_state[6] = 1
    filename=path / 'audio/audioA.mp3'
    Thread(target=audio, args=(filename,)).start()
    tyres-=1
    Thread(target=checkFormulaone).start() #controlla se FORMULAONE è stato completato
    scoreCalculation(10000)
    
    sleep(.2)
    switch_state[13] = 0
    

def obtainOO():
    global formulaone_lamps_state
    global tyres
    global switch_state
    global path
    
    formulaone_lamps_state[7] = 1
    filename=path / 'audio/audioOO.mp3'
    Thread(target=audio, args=(filename,)).start()
    tyres-=1
    Thread(target=checkFormulaone).start() #controlla se FORMULAONE è stato completato
    scoreCalculation(10000)
    
    sleep(.2)
    switch_state[15] = 0
    

def obtainN():
    global formulaone_lamps_state
    global tyres
    global switch_state
    global path
    
    formulaone_lamps_state[8] = 1
    filename=path / 'audio/audioN.mp3'
    Thread(target=audio, args=(filename,)).start()
    tyres-=1
    Thread(target=checkFormulaone).start() #controlla se FORMULAONE è stato completato
    scoreCalculation(10000)
    
    sleep(.2)
    switch_state[16] = 0
    

def obtainE():
    global formulaone_lamps_state
    global tyres
    global switch_state
    global path
    
    formulaone_lamps_state[9] = 1
    filename=path / 'audio/audioE.mp3'
    Thread(target=audio, args=(filename,)).start()
    tyres-=1
    Thread(target=checkFormulaone).start() #controlla se FORMULAONE è stato completato
    scoreCalculation(10000)
    
    sleep(.2)
    switch_state[17] = 0
    

def ballLostDX():
    global balls
    global shootAgain
    global afterShootAgain
    global fastLapsCounter
    global switch_state
    global path
    global pallaPersaDaDX
    
    scoreCalculation(1010)
    pallaPersaDaDX = True
        
    if afterShootAgain: #se hai già usufruito della 2nd canche non hai una terza chance, palla definitivamente persa.
        shootAgain = False
        afterShootAgain = False
        
        if balls % 4 == 1:
            filename=path / 'audio/out2.mp3'
        elif balls % 4 == 2:
            filename=path / 'audio/noo2.mp3'
        elif balls % 4 == 3:
            filename=path / 'audio/out1.mp3' 
        else:
            filename=path / 'audio/noo.mp3'
        Thread(target=audio, args=(filename,)).start()
        
    elif shootAgain == True: #se non è una 2nd canche allora controlla se sei ancora nella finestra dello shootAgain
        shootAgain = False
        afterShootAgain = True
        
        balls-=1 #2nd chance
        filename=path / 'audio/keepcalm.mp3'
        Thread(target=audio, args=(filename,)).start()
        
    else:
        if balls % 4 == 1:
            filename=path / 'audio/out2.mp3'
        elif balls % 4 == 2:
            filename=path / 'audio/noo2.mp3'
        elif balls % 4 == 3:
            filename=path / 'audio/out1.mp3' 
        else:
            filename=path / 'audio/noo.mp3'
        Thread(target=audio, args=(filename,)).start()
    
        
    fastLapsCounter = 0
    Thread(target=sLamps).start()
    
    sleep(.5)
    switch_state[5] = 0
    

def ballDX():
    global tyres
    global switch_state
    global path
    global balls
    global dxsx
    
    if dxsx == 0:
        filename=path / 'audio/thanks.mp3'
    elif dxsx == 1:
        filename=path / 'audio/traiettoria.mp3'
    else:
        filename=path / 'audio/turbook.mp3'
        dxsx = -1
    Thread(target=audio, args=(filename,)).start()
    dxsx+=1
    
    scoreCalculation(5010)
    tyres-=1
    
    sleep(.8)
    switch_state[6] = 0
    
    
def ballSX():
    global tyres
    global switch_state
    global path
    global dxsx
    
    if dxsx == 0:
        filename=path / 'audio/thanks.mp3'
    elif dxsx == 1:
        filename=path / 'audio/traiettoria.mp3'
    else:
        filename=path / 'audio/turbook.mp3'
        dxsx = -1
    Thread(target=audio, args=(filename,)).start()
    dxsx+=1
    
    scoreCalculation(5010)
    tyres-=1
    
    sleep(.8)
    switch_state[20] = 0
    

def ballLostCenter():
    global x
    global tyres
    global fastLapsCounter
    global box
    global shootAgain
    global afterShootAgain
    global balls
    global switch_state
    global path
    global pallaPersaDaDX
    global pallaPersaCentro
    global shutdown
    
    pallaPersaCentro = True
    
    if wiringpi.digitalRead(65+0): #se non sono nel multiball
        x = resetXLamps()
        tyres=30
        
        fastLapsCounter = 0
        Thread(target=sLamps).start()
        
        box = False
        wiringpi.digitalWrite(156, 0) #spegni luci box
        wiringpi.digitalWrite(157, 0) #spegni luci box
                     
        if pallaPersaDaDX == False:
            
            if afterShootAgain: #se hai già usufruito della 2nd canche non hai una 3 canche, palla definitivamente persa.
                shootAgain = False
                afterShootAgain = False
                
                if balls % 4 == 1:
                    filename=path / 'audio/out2.mp3'
                elif balls % 4 == 2:
                    filename=path / 'audio/noo2.mp3'
                elif balls % 4 == 3:
                    filename=path / 'audio/out1.mp3' 
                else:
                    filename=path / 'audio/noo.mp3'
                Thread(target=audio, args=(filename,)).start()
                
            elif shootAgain == True: #se non è una 2nd canche allora controlla se sei ancora nella finestra dello shootAgain
                shootAgain = False
                afterShootAgain = True
                
                balls-=1 #2nd chance
                filename=path / 'audio/keepcalm.mp3'
                Thread(target=audio, args=(filename,)).start()
                
            else:
                if balls % 4 == 1:
                    filename=path / 'audio/out2.mp3'
                elif balls % 4 == 2:
                    filename=path / 'audio/noo2.mp3'
                elif balls % 4 == 3:
                    filename=path / 'audio/out1.mp3' 
                else:
                    filename=path / 'audio/noo.mp3'
                Thread(target=audio, args=(filename,)).start()
        else:
            pallaPersaDaDX = False
            

    #se sono o non sono nel multiball, recupera la palla persa
    Thread(target=activeCoilOutHoleKicker).start()
    
    shutdown=0
    sleep(1)
    switch_state[3] = 0
    

def popbumperCenter():
    global tyres
    global checkKGreen
    global checkK250
    global switch_state
    global fastlap
    global turbo
    
    scoreCalculation(15000)
    tyres-=1
    
    Thread(target=activeCoilPopBumperCenter).start()
        
    Thread(target=flashingValueRear).start()
        
    if checkKGreen == True and checkK250==False:
        Thread(target=confirmKGreenValue).start()
        
    if fastlap == False:
        turbo+=1
        Thread(target=flashingBumper, args=(149,)).start()
        
    sleep(.1)
    switch_state[26] = 0
    
    
def popbumperLeft():
    global tyres
    global checkKGreen
    global checkK250
    global switch_state
    global fastlap
    global turbo
    
    scoreCalculation(15000)
    tyres-=1
    
    Thread(target=activeCoilPopBumperLeft).start()
        
    Thread(target=flashingValueRear).start()
        
    if checkKGreen == True and checkK250==False:
        Thread(target=confirmKGreenValue).start()
        
    if fastlap == False:
        turbo+=1
        Thread(target=flashingBumper, args=(150,)).start()
        
    sleep(.1)
    switch_state[25] = 0


def popbumperRight():
    global tyres
    global checkKGreen
    global checkK250
    global switch_state
    global fastlap
    global turbo
    
    scoreCalculation(15000)
    tyres-=1
    
    Thread(target=activeCoilPopBumperRight).start()
        
    Thread(target=flashingValueRear).start()
        
    if checkKGreen == True and checkK250==False:
        Thread(target=confirmKGreenValue).start()
    
    if fastlap == False:
        turbo+=1
        Thread(target=flashingBumper, args=(148,)).start()
        
    sleep(.1)
    switch_state[24] = 0
    

def saucer():
    global tyres
    global checkKGreen
    global checkK250
    global extraBallRamp
    global switch_state
    global altoDX
    
    if altoDX==0:
        filename=path / 'audio/altodx1.mp3'
        Thread(target=audio, args=(filename,)).start()
    elif altoDX==1:
        filename=path / 'audio/altodx2.mp3'
        Thread(target=audio, args=(filename,)).start()
    elif altoDX==2:
        filename=path / 'audio/altodx3.mp3'
        Thread(target=audio, args=(filename,)).start()
    elif altoDX==3:
        filename=path / 'audio/altodx4.mp3'
        Thread(target=audio, args=(filename,)).start()
    elif altoDX==4:
        filename=path / 'audio/altodx5.mp3'
        Thread(target=audio, args=(filename,)).start()
    elif altoDX==5:
        filename=path / 'audio/altodx6.mp3'
        Thread(target=audio, args=(filename,)).start()
    elif altoDX==6:
        filename=path / 'audio/altodx7.mp3'
        Thread(target=audio, args=(filename,)).start()
    elif altoDX==7:
        filename=path / 'audio/altodx8.mp3'
        Thread(target=audio, args=(filename,)).start()
    elif altoDX==8:
        filename=path / 'audio/altodx9.mp3'
        Thread(target=audio, args=(filename,)).start()   
        altoDX = -1
        
    altoDX+=1
    
    scoreCalculation(50000)
    tyres-=1
                        
    Thread(target=activeCoilSaucer).start()
    
    #ottieni un +X score
    incrementX(1)
    
    #ottieni una lettera di FormulaOne
    Thread(target=formulaoneLetterObtained).start()
    
    # ottieni il K_Value arancione selezionato dalle bandierine rotanti
    Thread(target=confirmKOrangeValue).start()
    
    if checkKGreen == True and checkK250==False:
        Thread(target=confirmKGreenValue).start()
        
    sleep(2)
    switch_state[2] = 0
    

def slingLeft():
    global tyres
    global switch_state
    
    scoreCalculation(1010)
    tyres-=1
    
    Thread(target=activeCoilSlingLeft).start()
    kOrangeScores()

    sleep(.3)
    switch_state[22] = 0
    

def slingRight():
    global tyres
    global switch_state
    
    scoreCalculation(1010)
    tyres-=1
    
    Thread(target=activeCoilSlingRight).start()
    kOrangeScores()
    
    sleep(.3)
    switch_state[23] = 0
    
    
def check_center_target_complete():
    global center_target_state
    global score
    
    if center_target_state[0]==1 and center_target_state[1]==1 and center_target_state[2]==1:
        # ottieni il K_Value selezionato dalle bandierine rotanti
        Thread(target=confirmKOrangeValue).start()
        
        #reset stato luci centrali
        center_target_state[0]=0
        center_target_state[1]=0
        center_target_state[2]=0
        
        #spegni le 3 luci
        wiringpi.digitalWrite(135, 0) #spegni 100k
        wiringpi.digitalWrite(136, 0) #spegni 200k
        wiringpi.digitalWrite(137, 0) #spegni 300k
        
        if score % 4 == 1:
            filename=path / 'audio/magico.mp3'
        elif score % 4 == 2:
            filename=path / 'audio/graziemille.mp3'
        elif score % 4 == 3:
            filename=path / 'audio/mattia.mp3'
        else:
            filename=path / 'audio/emozionegrande.mp3'
        Thread(target=audio, args=(filename,)).start()
    
    
def obtain100K():
    global tyres
    global center_target_state
    global x
    
    center_target_state[0] = 1
    wiringpi.digitalWrite(135, 1) #accendi 100k
    
    Thread(target=flashingValueRear).start()
    tyres-=1
    
    scoreCalculation(100*x)
    check_center_target_complete()
    
    sleep(.5)
    switch_state[21] = 0


def obtain200K_or_flashingValue():
    global tyres
    global flashingValue
    global switch_state
    global flashingValueFlag
    global center_target_state
    global path
    global x
    
    Thread(target=flashingValueRear).start()
                        
    tyres-=1
    
    if flashingValue > 0:
        filename=path / 'audio/flashingvalues.mp3'
        Thread(target=audio, args=(filename,)).start()
        flashingValueFlag = True #ferma il thread del lampeggio ciclico
        Thread(target=flashingValuesConfirm, args=(flashingValue-1,)).start()
    
    if flashingValue == 1:
        scoreCalculation(100000*x)
    elif flashingValue == 2:
        scoreCalculation(200000*x)
    elif flashingValue == 3:
        scoreCalculation(300000*x)
    else: #caso base in cui non sono in flashing delle 3 luci una di seguito all'altra
        center_target_state[1] = 1
        wiringpi.digitalWrite(136, 1) #accendi 200k        
        scoreCalculation(200*x)
        check_center_target_complete()
        
    sleep(.2)
    switch_state[28] = 0
    

def obtain300K():
    global tyres
    global center_target_state
    global x
    
    center_target_state[2] = 1
    wiringpi.digitalWrite(137, 1) #accendi 300k
    
    Thread(target=flashingValueRear).start()
    tyres-=1
    
    scoreCalculation(300*x)
    
    check_center_target_complete()
    
    sleep(.5)
    switch_state[18] = 0
    

def boxRamp():
    global tyres
    global box
    global checkK250
    global extraBallRamp
    global ballsXGame
    global doubleScore
    global score
    global fastLapsCounter
    global switch_state
    global path
    global balls
    
    
    scoreCalculation(10000)
    tyres=30
    
    # ottieni il K_Value selezionato
    Thread(target=confirmKOrangeValue).start()
    
    if box==True:
        filename=path / 'audio/box2.mp3'
        Thread(target=audio, args=(filename,)).start()
        
        Thread(target=boxCompleted).start()
    else:
        if balls % 3 == 1:
            filename=path / 'audio/pitanticipato.mp3'
        elif balls % 3 == 2:
            filename=path / 'audio/pitpianob.mp3'
        else:
            filename=path / 'audio/boxlec.mp3'
        Thread(target=audio, args=(filename,)).start()
        
    box=False
    
    if checkK250 == True:
        Thread(target=K250).start()
        
    if extraBallRamp == True:
        extraBallRamp = False
        ballsXGame+=1
        wiringpi.digitalWrite(139, 0) #luce extraball della rampa
        
    if doubleScore == True:
        doubleScore = False
        score = score*2
        wiringpi.digitalWrite(140, 0) #spegni la luce double score
        incrementX(1)
        
        filename=path / 'audio/maidetto.mp3'
        Thread(target=audio, args=(filename,)).start()
        
        
    # se dopo aver completato 2 fastlap mandi la palla sulla rampa
    # 1. azzera fastlap
    # 2. spegni le luci "S" e increase bonus ramp
    # 3. ottieni 10.000.000 di punti
    if fastLapsCounter >= 2:
        fastLapsCounter = 0
        Thread(target=sLamps).start()
        scoreCalculation(10000000)
        
        filename=path / 'audio/rampdopoduefastlap.mp3'
        Thread(target=audio, args=(filename,)).start()
        
        
    sleep(.3)
    switch_state[29] = 0
    

def obtainFastLap():
    global now
    global fastlap
    global tyres
    global turbo
    global playFieldScoreDouble
    global ballsXGame
    global fastLapsCounter
    global switch_state
    global path
    
    if now+15.5 >= time.time() and fastlap==True:
        scoreCalculation(1000000)
        tyres-=1
        
        filename=path / 'audio/fucsia.mp3'
        Thread(target=audio, args=(filename,)).start()
        turbo=0
        sleep(.3)
        GPIO.output(40,0) #ritrai la bandierina del fastlap
        wiringpi.digitalWrite(116, 0) #luce fastlap
        wiringpi.digitalWrite(f131, 0) #luce extraball
        wiringpi.digitalWrite(151, 0) #luce playfield score double
        playFieldScoreDouble = False
        ballsXGame+=1
        incrementX(1)
        fastlap=False
        
        fastLapsCounter+=1
        Thread(target=sLamps).start()
        
    sleep(.3)
    switch_state[14] = 0
    

def rampUpRight():
    global tyres
    global altoDX
    global checkKGreen
    global extraBallRamp
    global switch_state
    global path
    
    # ottieni il K_Value selezionato dalle bandierine rotanti
    Thread(target=confirmKOrangeValue).start()
    
    tyres-=1
    
    if altoDX==0:
        filename=path / 'audio/altodx1.mp3'
        Thread(target=audio, args=(filename,)).start()
    elif altoDX==1:
        filename=path / 'audio/altodx2.mp3'
        Thread(target=audio, args=(filename,)).start()
    elif altoDX==2:
        filename=path / 'audio/altodx3.mp3'
        Thread(target=audio, args=(filename,)).start()
    elif altoDX==3:
        filename=path / 'audio/altodx4.mp3'
        Thread(target=audio, args=(filename,)).start()
    elif altoDX==4:
        filename=path / 'audio/altodx5.mp3'
        Thread(target=audio, args=(filename,)).start()
    elif altoDX==5:
        filename=path / 'audio/altodx6.mp3'
        Thread(target=audio, args=(filename,)).start()
    elif altoDX==6:
        filename=path / 'audio/altodx7.mp3'
        Thread(target=audio, args=(filename,)).start()
    elif altoDX==7:
        filename=path / 'audio/altodx8.mp3'
        Thread(target=audio, args=(filename,)).start()
    elif altoDX==8:
        filename=path / 'audio/altodx9.mp3'
        Thread(target=audio, args=(filename,)).start()   
        altoDX = -1
        
    altoDX+=1
        
    sleep(.3)
    switch_state[27] = 0
    

def rotorFlags():
    global switch_state
    global now
    global fastlap
    
    kOrangeScores()
        
    #colpendo le bandiere rotanti mentre sei nel fastlap recuperi piu' secondi per fare il giro veloce
    if fastlap == True:
        if int(now+15.5 - time.time()) < 19: #cosi il bonus massimo in secondi è 20
            now = now+2
        
    sleep(.2)
    switch_state[19] = 0


def readHighScore():    
    filepath = path / 'hscore.txt'
    fo = open(filepath, "r")
    x = fo.read()
    fo.close()
    return x


def writeHighScore():
    global score
    filepath = path / 'hscore.txt'
    fo = open(filepath, "w")
    fo.write(str(score))
    fo.close()
    
    

if __name__ == "__main__":
    initSwitchPins(65, 32)
    initLampPins(97, 64)
    initCoilPins()
    hscore = readHighScore()
    
    grafica = Grafica(window, w, h, path)
    
    while True:
        
        #------------------SCRITTA IN ATTRACT MODE ----------
        timeTextAttractMode+=1 #tempo scritta in attract mode
        
        if timeTextAttractMode >=0 and timeTextAttractMode < 300:
            grafica.setInfoScore("CHARLES LECLERC", "GRAND PRIX")
        elif timeTextAttractMode >=300 and timeTextAttractMode < 600:
            grafica.setInfoScore("WINNERS DON'T USE DRUGS", "PRESS START")
        elif timeTextAttractMode >=600 and timeTextAttractMode < 900:
            grafica.setInfoScore("HIGH SCORE", format(int(hscore), ","))
        elif timeTextAttractMode >=900 and timeTextAttractMode < 1200:
            if score==0:
                timeTextAttractMode = 1200
            else:
                grafica.setInfoScore("LAST SCORE GAME", format(int(score), ","))
                        
        if timeTextAttractMode == 1200:
            timeTextAttractMode = 0
            
        window.update_idletasks()
        window.update()
        #------------------SCRITTA IN ATTRACT MODE ----------
            
    
        while balls<=ballsXGame and balls!=-1 and balls!=100:
            
            #--------CHECK SWITCHES
            # F di formulaone
            if wiringpi.digitalRead(65+7) and switch_state[7]==0:
                print('Switch activated: ', 7)
                switch_state[7] = 1
                Thread(target=obtainF).start()
                
            # O di formulaone
            if wiringpi.digitalRead(65+8) and switch_state[8]==0:
                print('Switch activated: ', 8)
                switch_state[8] = 1
                Thread(target=obtainO).start()
                
            # R di formulaone
            if wiringpi.digitalRead(65+9) and switch_state[9]==0:
                print('Switch activated: ', 9)
                switch_state[9] = 1
                Thread(target=obtainR).start()
                
            # M di formulaone
            if wiringpi.digitalRead(65+10) and switch_state[10]==0:
                print('Switch activated: ', 10)
                switch_state[10] = 1
                Thread(target=obtainM).start()
                
            # U di formulaone
            if wiringpi.digitalRead(65+11) and switch_state[11]==0:
                print('Switch activated: ', 11)
                switch_state[11] = 1
                Thread(target=obtainU).start()
                
            # L di formulaone
            if wiringpi.digitalRead(65+12) and switch_state[12]==0:
                print('Switch activated: ', 12)
                switch_state[12] = 1
                Thread(target=obtainL).start()
                
            # A di formulaone
            if wiringpi.digitalRead(65+13) and switch_state[13]==0:
                print('Switch activated: ', 13)
                switch_state[13] = 1
                Thread(target=obtainA).start()
                
            # OO seconda O di formulaone
            if wiringpi.digitalRead(65+15) and switch_state[15]==0:
                print('Switch activated: ', 15)
                switch_state[15] = 1
                Thread(target=obtainOO).start()
                
            # N di formulaone
            if wiringpi.digitalRead(65+16) and switch_state[16]==0:
                print('Switch activated: ', 16)
                switch_state[16] = 1
                Thread(target=obtainN).start()
                
            # E di formulaone
            if wiringpi.digitalRead(65+17) and switch_state[17]==0:
                print('Switch activated: ', 17)
                switch_state[17] = 1
                Thread(target=obtainE).start()
                
            # Palla persa lato destro
            if wiringpi.digitalRead(65+5) and switch_state[5]==0:
                print('Switch activated: ', 5)
                switch_state[5] = 1
                
                if shootAgain:
                    messaggio="SHOOT AGAIN!"
                    timeTextInGame=0
                    grafica.setInfoScore(messaggio, format(score, ","))
                    
                Thread(target=ballLostDX).start()
                
                
            # Palla lato destro
            if wiringpi.digitalRead(65+6) and switch_state[6]==0:
                print('Switch activated: ', 6)
                switch_state[6] = 1
                Thread(target=ballDX).start()
                
            # Palla lato sinistro
            if wiringpi.digitalRead(65+20) and switch_state[20]==0:
                print('Switch activated: ', 20)
                switch_state[20] = 1
                Thread(target=ballSX).start()
                
            # Palla persa al centro
            if wiringpi.digitalRead(65+3) and switch_state[3]==0:
                print('Switch activated: ', 3)
                switch_state[3] = 1
                Thread(target=ballLostCenter).start()
                
                if shootAgain:
                    timeTextInGame=0
                    messaggio="SHOOT AGAIN!"
                    grafica.setInfoScore(messaggio, format(score, ","))
                
            # Popbumper center
            if wiringpi.digitalRead(65+26) and switch_state[26]==0:
                print('Switch activated: ', 26)
                switch_state[26] = 1
                Thread(target=popbumperCenter).start()
                
            # Popbumper left
            if wiringpi.digitalRead(65+25) and switch_state[25]==0:
                print('Switch activated: ', 25)
                switch_state[25] = 1
                Thread(target=popbumperLeft).start()
                
            # Popbumper right
            if wiringpi.digitalRead(65+24) and switch_state[24]==0:
                print('Switch activated: ', 24)
                switch_state[24] = 1
                Thread(target=popbumperRight).start()
                
            # Saucer
            if wiringpi.digitalRead(65+2) and switch_state[2]==0:
                print('Switch activated: ', 2)
                switch_state[2] = 1
                Thread(target=saucer).start()
                
            # Sling Left
            if wiringpi.digitalRead(65+22) and switch_state[22]==0:
                print('Switch activated: ', 22)
                switch_state[22] = 1
                Thread(target=slingLeft).start()
                
            # Sling Right
            if wiringpi.digitalRead(65+23) and switch_state[23]==0:
                print('Switch activated: ', 23)
                switch_state[23] = 1
                Thread(target=slingRight).start()
            
            # Flashing Value Left
            if wiringpi.digitalRead(65+21) and switch_state[21]==0:
                print('Switch activated: ', 21)
                switch_state[21] = 1
                Thread(target=obtain100K).start()
                
            # Flashing Value Center
            if wiringpi.digitalRead(65+28) and switch_state[28]==0:
                print('Switch activated: ', 28)
                switch_state[28] = 1
                Thread(target=obtain200K_or_flashingValue).start()
                
            # Flashing Value Right
            if wiringpi.digitalRead(65+18) and switch_state[18]==0:
                print('Switch activated: ', 18)
                switch_state[18] = 1
                Thread(target=obtain300K).start()
                
            # Box Ramp
            if wiringpi.digitalRead(65+29) and switch_state[29]==0:
                print('Switch activated: ', 29)
                switch_state[29] = 1
                Thread(target=boxRamp).start()
                
            # Fast Lap
            if wiringpi.digitalRead(65+14) and switch_state[14]==0:
                print('Switch activated: ', 14)
                switch_state[14] = 1
                Thread(target=obtainFastLap).start()
                
            # Switch alto destro rampa bassa destra
            if wiringpi.digitalRead(65+27) and switch_state[27]==0:
                print('Switch activated: ', 27)
                switch_state[27] = 1
                Thread(target=rampUpRight).start()
                
            # bandiere rotanti
            if not wiringpi.digitalRead(65+19) and switch_state[19]==0:
                print('Switch deactivated: ', 19)
                switch_state[19] = 1
                Thread(target=rotorFlags).start()
                
            #se ci sono le 2 palle nel raccoglitore e sulla rampa non c'è nulla
            if (wiringpi.digitalRead(65+0) and wiringpi.digitalRead(65+31) and not wiringpi.digitalRead(65+1)): #ball release
                
                GPIO.output(40,0) #ritrai la bandierina del fastlap
                wiringpi.digitalWrite(116, 0) #luce fastlap
                wiringpi.digitalWrite(131, 0) #luce extraball
                wiringpi.digitalWrite(151, 0) #luce playfield score double
                playFieldScoreDouble = False
                fastlap = False
                turbo=0
                
                fastLapsCounter = 0
                Thread(target=sLamps).start()
                
                #-----questo controllo va fatto perchè la palla persa potrebbe essere andata direttamente dentro al raccoglitore
                if pallaPersaCentro == False:
                    if afterShootAgain: #se hai già usufruito della 2nd canche non hai una 3 canche, palla definitivamente persa.
                        shootAgain = False
                        afterShootAgain = False
                        
                    elif shootAgain == True: #se non è una 2nd canche allora controlla se sei ancora nella finestra dello shootAgain
                        shootAgain = False
                        afterShootAgain = True
                        
                        balls-=1 #2nd chance
                        filename=path / 'audio/keepcalm.mp3'
                        Thread(target=audio, args=(filename,)).start()
                else:
                    pallaPersaCentro = False
                #-----questo controllo va fatto perchè la palla persa potrebbe essere andata direttamente dentro al raccoglitore
                
                    
                balls+=1
                if balls <= ballsXGame:
                    print("Palla in gioco numero:", balls, "/", ballsXGame)
                                        
                    #mentre la palla non viene a mancare nel raccoglitore (switch 31) e non sta sulla rampa
                    t=1.0
                    while wiringpi.digitalRead(65+31) and not wiringpi.digitalRead(65+1):
                        sleep(0.5) #aspetta
                        t=t+0.5
                        if t >= 1.0 and not wiringpi.digitalRead(65+1): #ogni secondo riprova a mettere fuori la palla se l'operazione non va a buon fine
                            Thread(target=activeCoilBallRelease).start()
                            t=0.0
                    
                    if not afterShootAgain:
                        Thread(target=semafori).start()
                    
            #ball launch
            if wiringpi.digitalRead(65+30) and wiringpi.digitalRead(65+1): #launch ball
                if not afterShootAgain:
                    if partenza == 0:
                        messaggio = "BAD START"
                        Thread(target=activeCoilFire).start()
                    elif partenza == 1:
                        messaggio = "NICE START!"
                        scoreCalculation(1000000)
                        incrementX(1)
                        Thread(target=activeCoilFire).start()
                    elif partenza == 2:
                        messaggio = "START DELAYED"
                        Thread(target=activeCoilFire).start()
                else:
                    messaggio = ""
                    Thread(target=activeCoilFire).start()
                
                
                Thread(target=blinkShootAgain).start()
                
                #accensione luci playfield
                Thread(target=fireLamps).start()
                
            # SPEGNIMENTO RASPBERRY 
            #se premo il tasto FIRE a lungo allora voglio spegnere raspberry    
            if wiringpi.digitalRead(65+30):
                shutdown+=1
                
                if shutdown==200:
                    print("INIZIO PROCEDURA DI SPEGNIMENTO")
                    print(wiringpi.digitalRead(65+31))
                    sleep(5) #aspetta che tutti i thread muoiono
                    
                    #recupero palla in buca
                    #1. mentre le due biglie non sono a riposo simultaneamente
                    while wiringpi.digitalRead(65+31)==0:
                        print("WAITING BALLS")
                        #2. se la biglia sta in buca di perdita
                        if wiringpi.digitalRead(65+3)==1:
                            sleep(1)
                            Thread(target=activeCoilOutHoleKicker).start() #3. recuperala
                            sleep(1)
                            print("BALLS OK")

                    
                    #spegni tutto
                    for i in range(64):
                        wiringpi.digitalWrite(97+i, 0)
                        
                    print("LAMPS OFF")

                        
                    #Spegni General Illumination
                    GPIO.output(16, 1)
                    print("GI OFF")
                    
                    sleep(1)
                                        
                    #spegni raspberry
                    call("sudo shutdown -h now", shell=True) #spegni raspberry
            # SPEGNIMENTO RASPBERRY 
                
            
            #BOX
            if tyres<=0 and not box:
                filename=path / 'audio/box3.mp3'
                Thread(target=audio, args=(filename,)).start()
                box = True
                Thread(target=flashingRearLamps).start()
                Thread(target=flashingEnterInRamp).start()
                
            #ABILITAZIONE FAST LAP
            if turbo>=10 and not fastlap:
                scoreCalculation(10000)
                filename=path / 'audio/mammamia.mp3'
                Thread(target=audio, args=(filename,)).start()
                fastlap = True
                GPIO.output(40, 1) #attivazione coil
                wiringpi.digitalWrite(116, 1) #luce fastlap
                wiringpi.digitalWrite(131, 1) #luce extraball
                wiringpi.digitalWrite(151, 1) #luce playfield score double
                playFieldScoreDouble = True
                Thread(target=popBumperLamps).start()
                now=time.time()
                
            if fastlap == True:
                if now+15.5 < time.time(): #non sono piu' nella finestra dei sec per il fastlap
                    #1.ritira la bandierina del giro veloce disabilitando il solenoide
                    GPIO.output(40, 0)
                    wiringpi.digitalWrite(116, 0) #luce fastlap
                    wiringpi.digitalWrite(131, 0) #luce extraball
                    wiringpi.digitalWrite(151, 0) #luce playfield score double
                    playFieldScoreDouble = False
                    #2. disabilita fastlap
                    fastlap=False
                    #3.resetta il turbo
                    turbo=0
                    
            #------------------------------UPDATE SCREEN GRAPHIC----------------------------
            if not afterShootAgain:
                if stato_semafori == 0:
                    grafica.sem1()
                if stato_semafori == 1:
                    grafica.sem2()
                if stato_semafori == 2:
                    grafica.sem3()
                if stato_semafori == 3:
                    grafica.sem4()
                if stato_semafori == 4:
                    grafica.sem5()
                if stato_semafori == -1:
                    grafica.spegni_sem()
            else:
                grafica.spegni_sem()
                
                
            if len(messaggio) > 0:
                timeTextInGame+=1
                if timeTextInGame >= 200:
                    timeTextInGame = 0
                    messaggio=""
            
            
            if score==0:
                grafica.setInfoScore(messaggio, "00")
            else:
                grafica.setInfoScore(messaggio, format(score, ","))
                
            if fastlap:
                grafica.setInfoScore("FAST LAP: " + str(int(now+15.5 - time.time())) + "sec", format(score, ","))
            elif box:
                grafica.setInfoScore("BOX! BOX! " + str(int(20-secondix)) + "sec", format(score, ","))
            
                
            grafica.setBall("Ball: " + str(balls) + " of " + str(ballsXGame) + " ")
            grafica.setX("Multiplier: " + str(x) + "x ")
            
            if score <= hscorediv:
                pos = 20
                value = (hscorediv - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv and score <=hscorediv*2:
                pos = 19
                value = (hscorediv*2 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv*2 and score <=hscorediv*3:
                pos = 18
                value = (hscorediv*3 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv*3 and score <=hscorediv*4:
                pos = 17
                value = (hscorediv*4 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv*4 and score <=hscorediv*5:
                pos = 16
                value = (hscorediv*5 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv*5 and score <=hscorediv*6: 
                pos = 15
                value = (hscorediv*6 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv*6 and score <=hscorediv*7:
                pos = 14
                value = (hscorediv*7 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv*7 and score <=hscorediv*8:
                pos = 13
                value = (hscorediv*8 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv*8 and score <=hscorediv*9:
                pos = 12
                value = (hscorediv*9 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv*9 and score <=hscorediv*10:
                pos = 11
                value = (hscorediv*10 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv*10 and score <=hscorediv*11:
                pos = 10
                value = (hscorediv*11 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv*11 and score <=hscorediv*12:
                pos = 9
                value = (hscorediv*12 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv*12 and score <=hscorediv*13:
                pos = 8
                value = (hscorediv*13 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv*13 and score <=hscorediv*14:
                pos = 7
                value = (hscorediv*14 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv*14 and score <=hscorediv*15:
                pos = 6
                value = (hscorediv*15 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv*15 and score <=hscorediv*16:
                pos = 5
                value = (hscorediv*16 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv*16 and score <=hscorediv*17:
                pos = 4
                value = (hscorediv*17 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv*17 and score <=hscorediv*18:
                pos = 3
                value = (hscorediv*18 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > hscorediv*18 and score <=hscorediv*19:
                pos = 2
                value = (hscorediv*19 - score) * 3 / hscorediv # 3 = 3secs of gap each time
            elif score > int(hscore):
                pos = 1
                
            if pos != 1:
                grafica.setPosition(" Pos: " + str(pos) + ", %.2f" % value + " sec")
            else:
                grafica.setPosition(" Pos: 1")
            
            #il telecronista parla in base alle posizioni
            if posPrec - pos > 1:
                posPrec = pos+1
                
                if pos == 1:
                    filename=path / 'audio/vince.mp3'  
                elif pos == 2:
                    filename=path / 'audio/bottas2nd.mp3'
                elif pos == 3:
                    filename=path / 'audio/hamloose.mp3'
                elif pos == 4:
                    filename=path / 'audio/highscore1.mp3'
                elif pos == 5:
                    filename=path / 'audio/fantastica.mp3'
                elif pos == 6:
                    filename=path / 'audio/scalando1.mp3'
                elif pos == 7:
                    filename=path / 'audio/comeon.mp3'
                elif pos == 8:
                    filename=path / 'audio/highscore3.mp3'
                elif pos == 9:
                    filename=path / 'audio/highscore4.mp3'
                elif pos == 10:
                    filename=path / 'audio/incredibile.mp3'
                elif pos == 11:
                    filename=path / 'audio/maidetto.mp3'
                elif pos == 12:
                    filename=path / 'audio/piove.mp3'
                elif pos == 13:
                    filename=path / 'audio/thanks.mp3'
                elif pos == 13:
                    filename=path / 'audio/traiettoria.mp3'
                    
                if pos >=1 and pos < 14:
                    Thread(target=audio, args=(filename,)).start()
            #il telecronista parla in base alle posizioni
                    
            
            if tyres > 0:
                grafica.setTyresTurbo(" Tyres: " + str(int(tyres/30*100)) + "%, Turbo: " + str(int(turbo/10*100)) + "%")
            else:
                grafica.setTyresTurbo(" Tyres: 0%, Turbo: " + str(int(turbo/10*100)) + "%")
                
            window.update_idletasks()
            window.update()
            #------------------------------UPDATE SCREEN GRAPHIC----------------------------
        
                
        if balls==-1 or balls>ballsXGame and balls!=100: #fine partita
            balls=100 #questo mi evita che il thread parte un milione di volte
            shutdown = 0
            attract.flag = True
            Thread(target=attract.attractMode).start()
            box = False
            fastlap=False
            GPIO.output(40,0) #ritrai la bandierina del fastlap
            wiringpi.digitalWrite(116, 0) #luce fastlap
            wiringpi.digitalWrite(131, 0) #luce extraball
            wiringpi.digitalWrite(151, 0) #luce playfield score double
            playFieldScoreDouble = False
            
            mediaBackground = vlc.Media(path / 'audio/end.mp3')
            mediaPlayerBackground.set_media(mediaBackground)
            mediaPlayerBackground.audio_set_volume(150)
            mediaPlayerBackground.play()
            
            if score > int(hscore):
                writeHighScore()
                hscore = score
                
                if score % 6 == 1:
                    filename=path / 'audio/highscore1.mp3'
                elif score % 6 == 2:
                    filename=path / 'audio/highscore2.mp3'
                elif score % 6 == 3:
                    filename=path / 'audio/highscore3.mp3'
                elif score % 6 == 4:
                    filename=path / 'audio/highscore4.mp3'
                elif score % 6 == 5:
                    filename=path / 'audio/highscore5.mp3'
                else:
                    filename=path / 'audio/highscore6.mp3'
                Thread(target=audio, args=(filename,)).start()
                
                
            grafica.setBall("")
            grafica.setX("")
            grafica.setTyresTurbo("")
            grafica.setPosition("")
            
            GPIO.output(16, 1) #General Illumination
            
        
        #----------------- START GAME -------------------
        #se hai premuto il tasto start (30) e lo switch 31 e 0 che corrispondono alle biglie a riposo sono sullo stato 1, comincia!
        if wiringpi.digitalRead(65+30) and wiringpi.digitalRead(65+31) and wiringpi.digitalRead(65+0) and attract.getAttractFlag()==True: #start game
            
            attract.flag = False
            coil_state = [0,0,0,0,0,0,0,0,0]
            GPIO.output(16, 0) #General Illumination
            Thread(target=backgroundMusic).start()
            
            balls=0
            score=0
            fastLapsCounter = 0
            ballsXGame=3
            
            x=resetXLamps() #moltiplicatore di score
            
            center_target_state = [0,0,0]
            
            switch_state = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #32
            Thread(target=kOrangeBlink).start()
            
            formulaone_lamps_state = [0,0,0,0,0,0,0,0,0,0] #10
            Thread(target=updateFormulaoneLamps).start()
            
            k_lamps_state_orange = [0,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1] #-1 = k non selezionato, 0 = k selezionato, 1 = k ottenuto
            
            k_lamps_state_green = 0 #25k, 50k, 100k
            wiringpi.digitalWrite(132, 0)
            wiringpi.digitalWrite(133, 0)
            wiringpi.digitalWrite(134, 0)
            
            flashingValue = 0
            flashingValueFlag = False 
            tyres=30 #consumo gomme
            box = False #box 
            turbo=0 #contatore turbo (dato dai pop bumper)
            fastlap = False
            now = 0.0
            shootAgain = False
            afterShootAgain = False
            doubleScore = False
            extraBallRamp = False
            checkKGreen = False
            checkK250 = False
            playFieldScoreDouble = False
            messaggio = ""
            pallaPersaDaDX = False
            pallaPersaCentro = False
            posPrec = 21
            
            
            Thread(target=formulaoneBlink).start()
            
            hscorediv = int(hscore) / 20
            
            shutdown = 0
            
            sleep(.5)
        
        #se la partita non è cominciata e la palla sta in buca la metti nel raccoglitore
        elif wiringpi.digitalRead(65+3)==1 and attract.getAttractFlag()==True:
            sleep(.5)
            Thread(target=activeCoilOutHoleKicker).start()
            sleep(1)
            
        #se la partita non è cominciata e la palla sta nel saucer la espelli
        elif wiringpi.digitalRead(65+2)==1 and attract.getAttractFlag()==True:
            sleep(.5)
            Thread(target=activeCoilSaucer).start()
            sleep(2)
        
        #se la partita non è cominciata e la pallina sta sulla rampa di lancio, la lanci
        elif wiringpi.digitalRead(65+1)==1 and attract.getAttractFlag()==True:
            sleep(.5)
            Thread(target=activeCoilFire).start()
            sleep(1)