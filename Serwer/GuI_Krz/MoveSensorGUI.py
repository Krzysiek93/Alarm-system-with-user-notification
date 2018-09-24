#!/usr/bin/python3

from tkinter import *
from PIL import ImageTk
import PIL.Image
import tkinter.messagebox
import time
import tkinter as tk
import sqlite3
from multiprocessing import Queue

import sys
sys.path.append('/home/pi/PycharmProjects/Alarm')
from Creating_threads import Creating_threads




LARGE_FONT=("Verdana", 12)

########################################################################################################################
#------------------------------------------------- MECHANISM CLASS ----------------------------------------------------#
########################################################################################################################

class Mechanism(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight =1)
        container.grid_columnconfigure(0, weight=1)

        # self.tempLabel = tk.Label(text="", bg="yellow", font=("Helvetica ", 14))
        # self.tempLabel.place(x=660, y=30)
        # self.tempLabel['text'] = count

        self.label = tk.Label(text="", bg="yellow", font=("Helvetica ",14))
        self.label.place(x=660, y =0)
        self.update_clock()


        self.frames = {}


        for F in (StartPage, MainMenu, TurnOffMenu):

            frame = F(container, self)
            self.frames[F]= frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

        self.title("MoveSensor")
        # ---------------------------------------------SUBMENU----------------------------------------------------------
        # creating a menu instance
        menu = Menu(self.master)
        self.config(menu=menu)

        # create the file object)
        file = Menu(menu)

        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        file.add_command(label="Exit", command=self.quit())

        # added "file" to our menu
        menu.add_cascade(label="File", menu=file)
        # added "About" to our menu
        menu.add_cascade(label="About")


    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

    def update_clock(self):
        now = time.strftime("%H:%M:%S")
        self.label.configure(text=now)
        self.after(1000, self.update_clock)

########################################################################################################################
#------------------------------------------------ START PAGE CLASS ----------------------------------------------------#
########################################################################################################################

class StartPage(Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        Frame.__init__(self, parent)


        self.tempLabel = Label(self, bg="yellow", font=("Helvetica bold", 14))
        self.tempLabel.place(x=661, y=27)

        self.initWindow()
        self.showImg()
        self.showText()


# DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
        self.Create_Temp_thread()
        self.Create_Sound_thread()


    def Create_Temp_thread(self):
        self.q2 = Queue()
        self.temp = Creating_threads.Temp_thread(self.q2)
        self.temp.start()
        self.check_queue()

    def Create_Sound_thread(self):
        Welcom_sound = Creating_threads.Sound_thread("welcom_sound")
        Welcom_sound.start()


    def check_queue(self):
        try:
            self.temperature = round(self.q2.get(),2)
            self.tempLabel = Label(self,bg="yellow", font=("Helvetica bold", 14))
            self.tempLabel['text'] = (self.temperature,'''\N{DEGREE SIGN}C''')
            self.tempLabel.place(x=661, y=27)
            #print("%.2f" % self.temperature)
            self.controller.after(3000, self.check_queue)
        except:
            pass


    def Create_Serwer_thread(self):
        self.ftp = Creating_threads.FTPserver()
        self.ftp.start()


    def End_program(self):

        try:
            self.temp.end()        # end temperature thread
        except AttributeError:
            pass
        try:
            self.ftp.stop()        # end server thread
        except AttributeError:
            pass
        sys.exit(0)

# DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD

     #Creating of init window
    def initWindow(self):

        # --------------------------------------------- MENU ATRIBUTS --------------------------------------------------

        # creating a label instance
        nameLabel = Label(self, text = "Login")
        nameLabel.place(x = 280, y=150)

        passwordLabel = Label(self, text="Password")
        passwordLabel.place(x=280, y=170)

        # creating a Entry instance
        self.nameEntry = Entry(self)
        self.nameEntry.place(x=350, y=150)

        self.passwordEntry = Entry(self, show = "*")
        self.passwordEntry.place(x=350, y=170)

        self.var = StringVar()
        self.var.set("default")
        checkButton = Checkbutton(self,text="Show password", variable=self.var, onvalue="show", offvalue="hide", command=self.checkCheckbutton)
        checkButton.place(x=350, y=200)

        # creating a button instance
        loginButton = Button(self, text="Log in", command=self.checkUser)
        loginButton.place(x=400, y=220)

        # EXTRA BUTTON
        # cheatButton = Button(self, text="Na skróty", command=lambda: self.controller.show_frame(MainMenu))
        # cheatButton.place(x=550, y=200)

        quitButton = Button(self, text="Quit", command=self.End_program)
        quitButton.place(x=405, y=250)

    def checkCheckbutton(self):
        if self.var.get() == "show":
            self.passwordEntry.delete(0, END)
            self.passwordEntry = Entry(self)
            self.passwordEntry.place(x=350, y=170)
        else:
            self.passwordEntry.delete(0, END)
            self.passwordEntry = Entry(self, show = "*")
            self.passwordEntry.place(x=350, y=170)


    # ---------------------------------------------FRAME IMAGE----------------------------------------------------------
    def showImg(self):
        # logLabel.pack()
        load = PIL.Image.open("klodka.png")
        render = ImageTk.PhotoImage(load)

        # labels can be text or images
        img = Label(self, image=render)
        img.Image = render
        img.place(x=0, y=50)

    # --------------------------------------------- FRAME TEXT ---------------------------------------------------------
    def showText(self):
        text = Label(self, text="Welcome to MoveSensor", font=("Helvetica bold", 16), bg ="yellow", anchor= CENTER)
        text.place(x=280, y=60)

    # ---------------------------------------------- CHECKING USER -----------------------------------------------------
    def checkUser(self):
        while 1:
            username = self.nameEntry.get()
            print(username)
            password = self.passwordEntry.get()
            print(password)
            #SQL
            with sqlite3.connect("Users.db") as db:
                cursor = db.cursor()
            find_user = ("SELECT * FROM user WHERE username = ? AND password =?")
            cursor.execute(find_user, [(username), (password)])
            results = cursor.fetchall()


            if results:
                Welcom_sound = Creating_threads.Sound_thread("logged")
                Welcom_sound.start()

                tkinter.messagebox.showinfo('Information', 'You have been logged in!')


                print("Login done")
                a = 1 # Depends which window we want
                if a == 1:
                    OpenWindow(self.controller)
                else:
                    OpenWindow1(self.controller)

                self.nameEntry.delete(0, 'end')
                self.passwordEntry.delete(0, 'end')
                break

            else:
                tkinter.messagebox.showwarning('Warming', 'Username and password not recognized!')
                print("Login failed")
                break


def OpenWindow(x):
    x.show_frame(MainMenu)

def OpenWindow1(x):
    x.show_frame(TurnOffMenu)

########################################################################################################################
#------------------------------------------------- MAIN MENU CLASS ----------------------------------------------------#
########################################################################################################################
class MainMenu(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        button = Button(self, text="Back Home", command=self.Back_home_button)
        button.place(x=330, y=310)
        addUserButton = Button(self, text="Add user", command=self.showAddUserElements)
        addUserButton.place(x=600, y=50)

        delUserButton = Button(self, text="Delete user", command=self.showDelUserElements)
        delUserButton.place(x=594, y=80)

        self.showText()
        self.showImg()
        self.showStatus()
        self.End_programa()

    def Back_home_button(self):
        global x
        x = False
        self.controller.show_frame(StartPage)
    #--------------------------------------- ADD USER ELEMENTS AND METHODS ---------------------------------------------
    def showAddUserElements(self):
        self.addUserLabel = Label(self, text="Enter username to add")
        self.addUserLabel.place(x=570, y=110)

        self.addUserEntry = Entry(self)
        self.addUserEntry.place(x=565, y=130)

        self.addPINLabel = Label(self, text="Enter your PIN \n(must be a number)")
        self.addPINLabel.place(x=570, y=152)

        self.addPINEntry = Entry(self)
        self.addPINEntry.place(x=565, y=190)

        self.addPassLabel = Label(self, text="Enter your Password")
        self.addPassLabel.place(x=570, y=210)

        self.addPassEntry = Entry(self)
        self.addPassEntry.place(x=565, y=230)

        self.addUserOKButton = Button(self, text="Confirm", command=self.addUser)
        self.addUserOKButton.place(x=570, y=250)

        self.addUserCancelButton = Button(self, text="Cancel", command=self.cancelAdd)
        self.addUserCancelButton.place(x=655, y=250)

    def addUser(self):
        username = self.addUserEntry.get()
        PIN = self.addPINEntry.get()
        password = self.addPassEntry.get()

        found = 0
        while found == 0:
            #SQL
            with sqlite3.connect("Users.db") as db:
                cursor = db.cursor()
            find_user = ("SELECT * FROM user WHERE username = ? ")
            cursor.execute(find_user, [(username)])

            if cursor.fetchall():

                self.addUserEntry.destroy()
                self.addUserEntry = Entry(self, bg='red')
                self.addUserEntry.place(x=565, y=130)
                tkinter.messagebox.showwarning('Warming', 'Username taken, please try again!')

                print(" Username Taken, please try again")
                break

            else:
                found = 1
                self.addUserLabel.destroy()
                self.addUserEntry.destroy()
                self.addPINLabel.destroy()
                self.addPINEntry.destroy()


                self.addPassLabel.destroy()
                self.addPassEntry.destroy()

                self.addUserOKButton.destroy()
                self.addUserCancelButton.destroy()

                insertData = '''INSERT INTO user(username, PIN, password)
                VALUES(?,?,?)'''
                cursor.execute(insertData, [(username), (PIN), (password)])
                tkinter.messagebox.showinfo('Add User', 'User has been added!')
                db.commit()


    def cancelAdd(self):
        self.addUserLabel.destroy()
        self.addUserEntry.destroy()
        self.addPINLabel.destroy()
        self.addPINEntry.destroy()
        self.addPassLabel.destroy()
        self.addPassEntry.destroy()
        self.addUserOKButton.destroy()
        self.addUserCancelButton.destroy()
    #---------------------------------------- DELETE USER ELEMENTS AND METHODS -----------------------------------------
    def showDelUserElements(self):
        self.delUserLabel = Label(self, text="Enter username to delete")
        self.delUserLabel.place(x=570, y=110)

        self.delUserEntry = Entry(self)
        self.delUserEntry.place(x=565, y=130)

        self.delUserOKButton = Button(self, text="Confirm", command=self.delUser)
        self.delUserOKButton.place(x=570, y=150)

        self.delUserCancelButton = Button(self, text="Cancel", command=self.cancelDel)
        self.delUserCancelButton.place(x=660, y=150)

    def delUser(self):
        username = self.delUserEntry.get()

        self.delUserLabel.destroy()
        self.delUserEntry.destroy()
        self.delUserOKButton.destroy()
        self.delUserCancelButton.destroy()

        #SQL
        with sqlite3.connect("Users.db") as db:
            cursor = db.cursor()
        find_user = ("SELECT * FROM user WHERE username = ? ")
        cursor.execute(find_user, [(username)])

        if cursor.fetchall():
            print(" User has been deleted")
            tkinter.messagebox.showinfo('Information', 'User has been deleted!')
            delrecord = ('''DELETE FROM user WHERE username=?''')
            cursor.execute(delrecord, [(username)])
            db.commit()
        else:
            print("Username has not exist")
            tkinter.messagebox.showwarning('Warming', 'Username has not exist! \nPlease try again!')

    def cancelDel(self):
        self.delUserLabel.destroy()
        self.delUserEntry.destroy()
        self.delUserOKButton.destroy()
        self.delUserCancelButton.destroy()





    # --------------------------------------------- FRAME TEXT ---------------------------------------------------------
    def showText(self):
        text = Label(self, text="Sensor Status",bg="yellow", font=("Helvetica bold", 16),anchor=CENTER)
        text.place(x=300, y=10)

    # ---------------------------------------------FRAME IMAGE----------------------------------------------------------
    def showImg(self):
        # logLabel.pack()
        load = PIL.Image.open("mainMenu.png")
        render = ImageTk.PhotoImage(load)

        # labels can be text or images
        img = Label(self, image=render)
        img.Image = render
        img.place(x=0, y=170)

    # ---------------------------------- COUNT DOWN ELEMENTS AND METHODS -----------------------------------------------
    def sel(self):
        selection = "Yours selected time equals " + str(self.var.get()/60)+" min"
        Selection = Label(self, text=selection)
        Selection.place(x = 280, y = 220)
        # ti= (self.var.get() * 60)

        startButton = Button(self, text="Start", command=self.Turn_on_alarm)
        startButton.place(x=350, y=240)

    def showOptions(self):
        self.TurnOnButton.destroy()
        self.TurnOnLabel.destroy()

        chooseLabel= Label(self, text="Select time to count:")
        chooseLabel.place(x=300,y=180)
        self.var = IntVar()

        R1 = Radiobutton(self, text="1 min", variable=self.var, value=60, command=self.sel)
        R1.place(x = 250, y = 200)

        R2 = Radiobutton(self, text="2 min", variable=self.var, value=120, command=self.sel)
        R2.place(x = 350, y = 200)

        R3 = Radiobutton(self, text="5 min", variable=self.var, value=300, command=self.sel)
        R3.place(x = 440, y = 200)


    def countdown(self, count):
        # change text in label
        self.timeLabel.place(x=50, y=10)

        self.label['text'] = count
        self.label.place(x=70, y=40)


        if count== 0:
            OpenWindow1(self.controller)

    # ------------------------------------------ SENSOR STATUS ---------------------------------------------------------
    def showStatus(self):
        if 1:
            self.TurnOnLabel = Label(self, text="Click button below to turn on sensor")
            self.TurnOnLabel.place(x=260, y=180)

            load = PIL.Image.open("offStatus.png")
            render = ImageTk.PhotoImage(load)
            # labels can be text or images
            img = Label(self, image=render)
            img.Image = render
            img.place(x=310, y=45)

            self.load = tk.PhotoImage(file="onnButton.png")
            self.TurnOnButton = Button(self,image=self.load, fg = "green", command = self.showOptions)
            self.TurnOnButton.place(x=335,y=210)

#DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD

    def Turn_on_alarm(self):
        self.q = Queue()
        self.th4_PIR = Creating_threads.PIR_thread("Creating_PIR_thread", self.q, self.var.get())
        self.th4_PIR.start()
        try:
            self.label.destroy()
        except:
            pass
        self.label = Label(self, bg="red", font=("Helvetica bold", 85))
        self.timeLabel = Label(self, text="Time to start sensor:", bg="yellow")
        self.controller.after(200, self.check_queue)


    def check_queue(self):
        try:
            msg = self.q.get(0)
            self.countdown(msg)
            self.controller.after(1000, self.check_queue)
        except:
            pass


    def End_programa(self):
        try:
            global x
            if x == True:
                pass
            else:
                self.label.destroy()
                self.timeLabel.destroy()
                self.th4_PIR.end()  # end temperature thread
                x = True
            self.controller.after(100, self.End_programa)
        except AttributeError:
            pass




#DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD

########################################################################################################################
#-------------------------------------------------- TURN OFF CLASS ----------------------------------------------------#
########################################################################################################################
x = True

class TurnOffMenu(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        self.showText()
        self.showImg()
        self.addElementsOffMenu()

    def Back_home_button(self):
        self.entryPIN()
        global x
        x = False
        self.controller.show_frame(StartPage)


    # --------------------------------------------- FRAME TEXT ---------------------------------------------------------
    def showText(self):
        text = Label(self, text="Sensor Status", font=("Helvetica bold", 16), bg="yellow",anchor=CENTER)
        text.place(x=300, y=10)

    # ---------------------------------------------FRAME IMAGE----------------------------------------------------------
    def showImg(self):
        # logLabel.pack()
        load = PIL.Image.open("mainMenu.png")
        render = ImageTk.PhotoImage(load)

        # labels can be text or images
        img = Label(self, image=render)
        img.Image = render
        img.place(x=0, y=170)

    # ------------------------------------------- ELEMENTS OF OFF MENU METHOD ------------------------------------------
    def addElementsOffMenu(self):
        load = PIL.Image.open("onStatus.png")
        render = ImageTk.PhotoImage(load)

        # labels can be text or images
        img = Label(self, image=render)
        img.Image = render
        img.place(x=330, y=45)

        self.TurnOffLabel = Label(self, text="Click button below to turn off sensor")
        self.TurnOffLabel.place(x=260, y=150)

        self.load = tk.PhotoImage(file="ooffButton.png")
        self.TurnOffButton = Button(self, image=self.load, highlightcolor="red", command=lambda: self.entryPIN("turn_off"))
        self.TurnOffButton.place(x=325, y=180)

        self.button = Button(self, text="Back Home", command=lambda: self.entryPIN("back_home"))
        self.button.place(x=330, y=310)



    def entryPIN(self, action_type):

        Passcode_sound = Creating_threads.Sound_thread("passcode")
        Passcode_sound.start()

        self.action_type = action_type

        self.TurnOffButton.destroy()
        self.TurnOffLabel.destroy()
        self.button.destroy()

        self.userLabel = Label(self, text="Enter Username:")
        self.userLabel.place(x=320, y=160)

        self.UserEntry = Entry(self)
        self.UserEntry.place(x=300, y=180)

        self.PINLabel = Label(self, text="Enter PIN to confirm:")
        self.PINLabel.place(x=320, y=200)

        self.PINEntry = Entry(self, show="*")
        self.PINEntry.place(x=300, y=220)

        self.OKButton = Button(self, text="OK", command=self.checkPIN)
        self.OKButton.place(x=360, y=240)

    # --------------------------------------------- CHECK PIN METHOD ---------------------------------------------------
    def checkPIN(self):
        while 1:

            username = self.UserEntry.get()
            PIN = str(self.PINEntry.get())
            print(PIN)
            print(type(PIN))

            with sqlite3.connect("Users.db") as db:
                cursor = db.cursor()
            find_user = ("SELECT * FROM user WHERE username = ? AND PIN =?")
            cursor.execute(find_user, [ (username), (PIN)])
            results = cursor.fetchall()

            if results:
                global x
                x=False

                Alert_sound = Creating_threads.Sound_thread("end_alert")
                Alert_sound.start()

                Alert_sound = Creating_threads.Sound_thread("set_X_when_tensor_is_ON")
                Alert_sound.start()

                tkinter.messagebox.showinfo('Information', 'You have turned off Sensor!')

                self.userLabel.destroy()
                self.UserEntry.destroy()
                self.PINEntry.delete(0, 'end')

                self.PINLabel.destroy()
                self.PINEntry.destroy()
                self.OKButton.destroy()

                if self.action_type == "back_home":
                    self.controller.show_frame(StartPage)
                    self.addElementsOffMenu()
                elif self.action_type == "turn_off":
                    OpenWindow(self.controller)
                    self.addElementsOffMenu()
                break

            else:
                self.UserEntry.delete(0, 'end')
                self.PINEntry.delete(0, 'end')
                Wrong_password_sound = Creating_threads.Sound_thread("Wrong_password")
                Wrong_password_sound.start()
                tkinter.messagebox.showwarning('Warming', 'You have to entry correct PIN!')
                break







app = Mechanism()
app.geometry("%dx%d%+d%+d" % (750, 350, 400, 125))
app.mainloop()

