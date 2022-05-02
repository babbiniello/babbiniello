from tkinter import *
from PIL import ImageTk, Image


############################################# GRAPHICS #########################################
class Grafica:
    
    def __init__(self, window, w, h, path):
        print("Resolution: ", w, h)
        
        self.textScore = StringVar()
        self.textBall = StringVar()
        self.textX = StringVar()
        self.textPosition = StringVar()
        self.textTyresTurbo = StringVar()
        self.textInfo = StringVar()

        # ----------------------------------- SFONDO ------------------------------------------
        img = Image.open(path / 'graphics/sfondo.png')  #carica l'immagine
        imgWidth, imgHeight = img.size #size dell'immagine caricata

        # resize photo to full screen
        ratio = min(w/imgWidth, h/imgHeight)
        imgWidthNew = int(imgWidth*ratio)
        imgHeightNew = int(imgHeight*ratio)
        resizedImage = img.resize((imgWidthNew,imgHeightNew), Image.ANTIALIAS)   
        image = ImageTk.PhotoImage(resizedImage)

        sfondo = Label(image=image, borderwidth=0, highlightthickness=0, padx=0, pady=0)
        sfondo.image = image
        sfondo.place(x=0, y=0) # Position image
        # ----------------------------------- SFONDO ------------------------------------------
        
        # ----------------------------------- CANVAS ------------------------------------------
        lunghezzaCanvas = int(w*2360/2560)
        x_position = int((w-lunghezzaCanvas)/2)
        y_position = int(h*1000/1440)
        altezzaCanvas = h-y_position
        canvas1 = Canvas(window, width=lunghezzaCanvas, height=altezzaCanvas, bg="black", borderwidth=0, highlightthickness=0)
        canvas1.place(x=x_position, y=y_position) # Position canvas
        # ----------------------------------- CANVAS ------------------------------------------
        
        # ----------------------------------- INFORMAZIONI ---------------------------------------
        labelInfo = Label(canvas1, textvariable = self.textInfo, font=("LED Dot-Matrix", int(80*w/2560)), fg="orange", bg="black")
        labelInfo.place(x=int(lunghezzaCanvas/2), y=int(altezzaCanvas/6), anchor="center") # Position center
        # ----------------------------------- INFORMAZIONI ---------------------------------------

        # ----------------------------------- PUNTEGGIO ---------------------------------------
        labelPunteggio=Label(canvas1, textvariable = self.textScore, font=("LED Dot-Matrix", int(160*w/2560)), fg="orange", bg="black")
        labelPunteggio.place(x=int(lunghezzaCanvas/2), y=int(altezzaCanvas/1.8), anchor="center") # Position center
        # ----------------------------------- PUNTEGGIO ---------------------------------------
        
        
        # ----------------------------------- SEMAFORO 1 --------------------------------------
        img = Image.open(path / 'graphics/sem1.png')  #carica l'immagine
        imgWidth, imgHeight = img.size #size dell'immagine caricata

        # resize photo
        imgWidthNew = int(imgWidth*ratio)
        imgHeightNew = int(imgHeight*ratio)
        resizedImage = img.resize((imgWidthNew,imgHeightNew), Image.ANTIALIAS)   
        image = ImageTk.PhotoImage(resizedImage)

        self.semaforo1 = Label(image=image, borderwidth=0, highlightthickness=0, padx=0, pady=0)
        self.semaforo1.image = image
        self.x_sem1 = int(w*600/2560)
        self.y_sem1 = int(h*488/1440)
        # ----------------------------------- SEMAFORO 1 --------------------------------------
        
        # ----------------------------------- SEMAFORO 2 --------------------------------------
        img = Image.open(path / 'graphics/sem2.png')  #carica l'immagine
        imgWidth, imgHeight = img.size #size dell'immagine caricata

        # resize photo
        imgWidthNew = int(imgWidth*ratio)
        imgHeightNew = int(imgHeight*ratio)
        resizedImage = img.resize((imgWidthNew,imgHeightNew), Image.ANTIALIAS)   
        image = ImageTk.PhotoImage(resizedImage)

        self.semaforo2 = Label(image=image, borderwidth=0, highlightthickness=0, padx=0, pady=0)
        self.semaforo2.image = image
        self.x_sem2 = int(w*874/2560)
        self.y_sem2= int(h*488/1440)
        # ----------------------------------- SEMAFORO 2 --------------------------------------
        
        # ----------------------------------- SEMAFORO 3 --------------------------------------
        img = Image.open(path / 'graphics/sem3.png')  #carica l'immagine
        imgWidth, imgHeight = img.size #size dell'immagine caricata

        # resize photo
        imgWidthNew = int(imgWidth*ratio)
        imgHeightNew = int(imgHeight*ratio)
        resizedImage = img.resize((imgWidthNew,imgHeightNew), Image.ANTIALIAS)   
        image = ImageTk.PhotoImage(resizedImage)

        self.semaforo3 = Label(image=image, borderwidth=0, highlightthickness=0, padx=0, pady=0)
        self.semaforo3.image = image
        self.x_sem3= int(w*1131/2560)
        self.y_sem3= int(h*488/1440)
        # ----------------------------------- SEMAFORO 3 --------------------------------------

        # ----------------------------------- SEMAFORO 4 --------------------------------------
        img = Image.open(path / 'graphics/sem4.png')  #carica l'immagine
        imgWidth, imgHeight = img.size #size dell'immagine caricata

        # resize photo
        imgWidthNew = int(imgWidth*ratio)
        imgHeightNew = int(imgHeight*ratio)
        resizedImage = img.resize((imgWidthNew,imgHeightNew), Image.ANTIALIAS)   
        image = ImageTk.PhotoImage(resizedImage)

        self.semaforo4 = Label(image=image, borderwidth=0, highlightthickness=0, padx=0, pady=0)
        self.semaforo4.image = image
        self.x_sem4= int(w*1388/2560)
        self.y_sem4= int(h*488/1440)
        # ----------------------------------- SEMAFORO 4 --------------------------------------

        # ----------------------------------- SEMAFORO 5 --------------------------------------
        img = Image.open(path / 'graphics/sem5.png')  #carica l'immagine
        imgWidth, imgHeight = img.size #size dell'immagine caricata

        # resize photo
        imgWidthNew = int(imgWidth*ratio)
        imgHeightNew = int(imgHeight*ratio)
        resizedImage = img.resize((imgWidthNew,imgHeightNew), Image.ANTIALIAS)   
        image = ImageTk.PhotoImage(resizedImage)

        self.semaforo5 = Label(image=image, borderwidth=0, highlightthickness=0, padx=0, pady=0)
        self.semaforo5.image = image
        self.x_sem5= int(w*1644/2560)
        self.y_sem5= int(h*488/1440)
        # ----------------------------------- SEMAFORO 5 --------------------------------------
        
        # -------------------------------------- BALL -----------------------------------------
        labelBall=Label(canvas1, textvariable = self.textBall, font=("LED Dot-Matrix", int(50*w/2560)), fg="orange", bg="black")
        labelBall.place(x=int(lunghezzaCanvas), y=int(altezzaCanvas/9), anchor="e")
        # -------------------------------------- BALL -----------------------------------------
        
        # -------------------------------------- X -----------------------------------------
        labelX=Label(canvas1, textvariable = self.textX, font=("LED Dot-Matrix", int(50*w/2560)), fg="orange", bg="black")
        labelX.place(x=int(lunghezzaCanvas), y=int(altezzaCanvas), anchor="se")
        # -------------------------------------- X -----------------------------------------

        # -------------------------------------- POSITION -----------------------------------------
        labelPosition=Label(canvas1, textvariable = self.textPosition, font=("LED Dot-Matrix", int(50*w/2560)), fg="orange", bg="black")
        labelPosition.place(x=0, y=int(altezzaCanvas/9), anchor="w")
        # -------------------------------------- POSITION -----------------------------------------
        
        # -------------------------------------- TYRES TURBO -----------------------------------------
        labelTyresTurbo=Label(canvas1, textvariable = self.textTyresTurbo, font=("LED Dot-Matrix", int(50*w/2560)), fg="orange", bg="black")
        labelTyresTurbo.place(x=0, y=int(altezzaCanvas), anchor="sw")
        # -------------------------------------- TYRES -----------------------------------------



    def sem1(self):
        self.semaforo1.place(x=self.x_sem1, y=self.y_sem1)
        
    def sem2(self):
        self.semaforo2.place(x=self.x_sem2, y=self.y_sem2)
        
    def sem3(self):
        self.semaforo3.place(x=self.x_sem3, y=self.y_sem3)

    def sem4(self):
        self.semaforo4.place(x=self.x_sem4, y=self.y_sem4)

    def sem5(self):
        self.semaforo5.place(x=self.x_sem5, y=self.y_sem5)
        
    def spegni_sem(self):
        self.semaforo1.place(x=-10000, y=-10000)
        self.semaforo2.place(x=-10000, y=-10000)
        self.semaforo3.place(x=-10000, y=-10000)
        self.semaforo4.place(x=-10000, y=-10000)
        self.semaforo5.place(x=-10000, y=-10000)
        
    def setInfoScore(self, newInfo, newScore):
        self.textInfo.set(newInfo)
        self.textScore.set(newScore)
        
    def setBall(self, ballStatus):
        self.textBall.set(ballStatus)
        
    def setX(self, xx):
        self.textX.set(xx)
        
    def setPosition(self, position):
        self.textPosition.set(position)
    
    def setTyresTurbo(self, tyresTurboStatus):
        self.textTyresTurbo.set(tyresTurboStatus)        
############################################# GRAPHICS #########################################
