#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Title:        AutoStop
# Purpose:      AutoStop is for a custom made automatic Miter Saw cut length system
# Author:       Will Travis
# Version:      0.2
# Modified:     01/14/2017
# Copyright:    (c) William Travis 2017
# License:      Simplified BSD 2-Clause License
# Description:  AutoStop is the GUI interface for the automated Miter Saw cutting system
#               It allows you to enter a dimension and it will move a stepper motor
#               to the correct distance to allow perfect cutting over and over.
#               It can be set up for Millimeter or American Inches
#               It has multiple configuration options
# History:
#
#
# Requirements:
# Sourcecode:   https://github.com/willtravis/AutoStop
# Variables:    All Uppercase = constants that do not change
#               First letter Uppercase = global variable
#               First letter Lowercase = local variable
#-------------------------------------------------------------------------------
__author__ = "William Travis"
__license__ = "Simplified BSD 2-Clause License"

import os
import platform
from functools import partial
from fractions import Fraction
from ConfigParser import RawConfigParser
try:
    from Tkinter import *    # Python2
except ImportError:
    from tkinter import  *   # Python3

import tkMessageBox as mBox
import tkFont

# ----------------------------------------------------------------------------
def numFormat(num):
    """
    DESC:    Converts float to string formatted for display
    ARGS:    Decimal number  i.e. 123.25
    RETURNS: String number formatted as follows
        MM mode: 8 characters, decimal point, 2 decimals, i.e. "   123.45"
        IN mode: 8 characters, with 3 spaces for fraction, i.e. "   123   "
    """
    if UNITS == "MM":
        return '{:>10.2f}'.format(float(num))
    else:
        return ('{:>8}'.format(int(num))) + "  "

# ----------------------------------------------------------------------------
def resizeIcon(image, w, h):
    """
    DESC:    Resize an icon to new size.  Used to resize icons for different screen
              sizes
    ARGS:    Location of image file, new Width and Height
    RETURNS: resized image object
    """
    img = PhotoImage(file=image)
    scale_w = int(img.width()/w)
    scale_h = int(img.height()/h)
    return img.subsample(scale_w, scale_h)

# ----------------------------------------------------------------------------
def setPrecision(value):
    """
    DESC:    In INch mode sets numerator and denominator rounded to PRECISION value
              PRECISION is set in the config file, precision is usually
              1/8, 1/16, 1/32 or 1/64
    ARGS:    Decimal number  i.e. 123.25
    RETURNS: numerator and denominator  i.e.  1,4
    """
    # Set numerator and denominator for IN mode
    decimal = value - int(value)  # remove whole number
    if decimal == 0.0:
        return 0, PRECISION
    else:
        decimal = round(decimal*PRECISION,0)/PRECISION # round decimal to precision value
        fract = Fraction(decimal)  # Fraction creates a fraction from a decimal
        return fract.numerator, fract.denominator

# ----------------------------------------------------------------------------
def setTarget(value):
    """
    DESC:    Sets the global variable TargetVal and TargetValStr to value
              If INch mode rounds numerator and denominator to PRECISION value
              Includes error checking of value range, i.e. <0, >Park Locaion
    ARGS:    Decimal number  i.e. 123.25
    RETURNS: Sets global variables:
              TargetVal, TargetValStr, TargetNumeratorStr, TargetDenominatorStr
    """

    global TargetVal, TargetValStr

    #Check for value limits
    if value <= 0.0:
        value = 0.0     # If value is < 0, set to 0
    if value >= PARKLOCATION:
        value = PARKLOCATION # If value > parklocation, set to parklocation
    if value == TargetVal:
        return         # if value = existing Target do nothing

    # Set new Target value
    TargetVal = value
    TargetValStr.set(numFormat(TargetVal))

    if UNITS == "IN":
        # Set numerator and denominator for INch mode
        global TargetNumeratorStr, TargetDenominatorStr
        n,d = setPrecision(TargetVal)
        TargetNumeratorStr.set(n)
        TargetDenominatorStr.set(d)

# ----------------------------------------------------------------------------
def setActual(value):
    """
    DESC:    Sets the global variable ActualVal and ActualValStr to value
              If INch mode rounds numerator and denominator to PRECISION value
    ARGS:    Decimal number  i.e. 123.25
    RETURNS: Sets global variables:
              ActualVal, ActualValStr, ActualNumeratorStr, ActualDenominatorStr
    """
    global ActualVal, ActualValStr

    ActualVal = value
    ActualValStr.set(numFormat(value))

    if UNITS == "IN":
        # Set numerator and denominator for IN mode
        global ActualNumeratorStr, ActualDenominatorStr
        n,d = setPrecision(ActualVal)
        ActualNumeratorStr.set(n)
        ActualDenominatorStr.set(d)

# ----------------------------------------------------------------------------
def formatJogValue(value):
    """
    DESC:    In INch mode, formats the Jog value to a fraction
              Returns as formatted 9 character string
    ARGS:    decimal number  i.e. 123.25
    RETURNS: INch mode - text formatted to 9 chararcters in fraction notation
             MM mode  - text formatted to 9 characters
    """
    if UNITS == "IN":
        # Set numerator and denominator for IN mode
        n,d = setPrecision(value)
        if n != 0:
            value = '{0}/{1}'.format(n,d)
        else:
            value = int(value)

    return '{:>9}'.format(value)

# ################### READ SETTINGS FROM AutoStop.ini SETTINGS FILE ###########################
class config_file(object):
    """
    DESC:   Read and Write config files
    """

    def __init__(self, ini_filename):
        self.ini_filename = ini_filename
        self.cfg = RawConfigParser()
        self.cfg.readfp( open( self.ini_filename,"r" ) )

    def get_string(self, section, key):
        if self.cfg.has_option(section, key):
            return self.cfg.get(section, key)
        else:
            return None

    def get_int(self, section, key):
        if self.cfg.has_option(section, key):
            return self.cfg.getint(section, key)
        else:
            return None

    def get_float(self, section, key):
        if self.cfg.has_option(section, key):
            return self.cfg.getfloat(section, key)
        else:
            return None

    def set_float(self, section, key, new_value):
        self.cfg.set(section, key, new_value)

    def write_settings(self):
        with open( self.ini_filename, "w") as ini_out:
            self.cfg.write( ini_out )
            ini_out.close()


# DIRECTORY THIS APPLICATION IS LOCATED IN
DIRECTORY = os.path.dirname(os.path.realpath(__file__))
os.chdir(DIRECTORY)

CfgFilename = os.path.basename(__file__)
CfgFilename = os.path.splitext(CfgFilename)[0]+'.ini'
if os.path.exists(CfgFilename) == False:
        # Need to write some better exit code !!!!!!!!!!!!!!!!!!!!!!!!!!!
        print "file does not exist"
        exit()

cfg = config_file(os.path.join(DIRECTORY, CfgFilename))

SCREEN_WIDTH = cfg.get_int('Display', 'ScreenWidth')
SCREEN_HEIGHT =cfg.get_int('Display', 'ScreenHeight')
# #### Root.minsize(width=200, height=200)
# #### Root.maxsize(width=SCREEN_WIDTH, height=screen_heigt)

# Retrieve Color Theme
THEME = cfg.get_string('Display', 'Theme').lower()
# set color based on theme setting, default = blue background
if THEME == 'white':
    TEXTCOLOR = "black"
elif THEME == 'black':
    TEXTCOLOR = "white"
else:
    THEME = "deep sky blue"
    TEXTCOLOR = "black"

# Reteieve setting for measurement units
UNITS = cfg.get_string('Settings', 'Units')

# Retrieve setting for fraction rounding, used only in INch mode
try:
    PRECISION = cfg.get_int('Settings', 'Precision')
    while PRECISION not in [4, 8, 16, 32, 64]:
        PRECISION = 16
except:
    PRECISION = 16

# Retrieve custom jog values
JOGVALUES = []
for a in ['1','2','3']:
    j = cfg.get_float(UNITS, 'JogValue'+a)
    if j == None: j = 1.0   # default value if JogValue1 does not exist in config file
    if UNITS == 'IN':
        if j%.0625 != 0.0: j=0.0625  # if Jog value not divisible by 16, reset to 1/16
    JOGVALUES.append(j)

# Retrieve starting jog value (which jog button to light up)
try:
    CurrentJogValue = cfg.get_int('Settings', 'StartJogValue')-1
except:
    CurrentJogValue = 0

# Retrieve farthest location to park head at
PARKLOCATION = cfg.get_float(UNITS, 'Park')

# Type of Stepper Motor Controller
CONTROLLER = cfg.get_string('Setup', 'Controller')

# Delay in updating readings and display
DELAY_MS = cfg.get_int('Setup', 'DelayMS')

# ###########END READING SETTINGS FROM AutoStop.ini SETTING FILE ##############

# ############## READ MACHINE SETTINGS FROM MachineSetting.ini SETTING FILE #################
machineCfg = config_file(os.path.join(DIRECTORY, 'MachineSettings.ini'))
# Retrieve amount of space the motor moved with each step (in Inches or MM)
# Note this must be calculated initially, next version will allow calibration
MOTORMOVEDEACHSTEP = machineCfg.get_float('Machine Settings', 'distance traveled per step')
# For testing purposes
MOTORMOVEDEACHSTEP = 1.0/64.0   # DEBUG

# ###########END READING MACHINE SETTINGS FROM MachineSetting.ini SETTING FILE ##############

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# INITIALIZE SYSTEMS
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Root = Tk()
Root.title("AutoStop")
# SCREEN_WIDTH = Root.winfo_screenwidth()
# SCREEN_HEIGHT = Root.winfo_screenheight()
Root.geometry(str(SCREEN_WIDTH)+"x"+str(SCREEN_HEIGHT))
Root.configure(background=THEME)   # set background color

# Global variables (starts with capital letter)

# This next section creates two variables that will be used for screen dimensions
#   RowWidth and ColHeight will be used to resize the text and icons to fit multiple
#    screen sizes, this will allow a responsive screen interface
Rows = 8     # Number of rows in interface
Columns = 6  # Number of columns in interface
RowWidth = int(SCREEN_WIDTH*(1.0/Rows))
ColHeight = int(SCREEN_HEIGHT*(1.0/Columns))

# Variables to store Actual head location values
ActualVal = 0.0
ActualValStr = StringVar()
ActualValStr.set(numFormat(ActualVal))
# Set numerator and denominator for IN mode
n,d = setPrecision(ActualVal)
ActualNumeratorStr = StringVar()
ActualNumeratorStr.set(n)
ActualDenominatorStr = StringVar()
ActualDenominatorStr.set(d)

# Variables to store Target head location values
TargetVal = 1/PRECISION
TargetValStr = StringVar()
TargetValStr.set(numFormat(TargetVal))
# Set numerator and denominator for IN mode
n,d = setPrecision(TargetVal)
TargetNumeratorStr = StringVar()
TargetNumeratorStr.set(n)
TargetDenominatorStr = StringVar()
TargetDenominatorStr.set(d)

DecimalMode = 0  # 0 means entering whole numbers, 1 or 2 is number of decimals entered
Moving = "no"  # is head moving?  values = 'no', 'lft', 'rgt'
Buttons = []  # contains buttons in keypad

# Jogging variables
JogBtn = ['', '', '']         # Button objects
JogImg = ['', '', '']         # Images of normal button
JogPressedImg = ['', '', '']  # Images of pressed button

# Create image objects and resize Images to screen size
CloseImg=resizeIcon("images\\close.gif", RowWidth/2, ColHeight/2)
SettingsImg=resizeIcon("images\\setting.gif", RowWidth, ColHeight)
HomeImg=resizeIcon("images\\home.gif", RowWidth, ColHeight)
ParkImg=resizeIcon("images\\park.gif", RowWidth, ColHeight)
GoImg=resizeIcon("images\\go.gif", RowWidth, ColHeight)
JogImg[0]=resizeIcon("images\\jog1.gif", RowWidth, ColHeight/2)
JogImg[1]=resizeIcon("images\\jog2.gif", RowWidth, ColHeight/2)
JogImg[2]=resizeIcon("images\\jog3.gif", RowWidth, ColHeight/2)
JogPressedImg[0]=resizeIcon("images\\jog1pressed.gif", RowWidth, ColHeight/2)
JogPressedImg[1]=resizeIcon("images\\jog2pressed.gif", RowWidth, ColHeight/2)
JogPressedImg[2]=resizeIcon("images\\jog3pressed.gif", RowWidth, ColHeight/2)
LeftImg=resizeIcon("images\\left.gif", RowWidth, ColHeight)
RightImg=resizeIcon("images\\right.gif", RowWidth, ColHeight)
KeypadImg=resizeIcon("images\\keypad.gif", RowWidth/2, ColHeight/2)
ActualImg=resizeIcon("images\\actual.gif", RowWidth, ColHeight/2)
TargetImg=resizeIcon("images\\target.gif", RowWidth, ColHeight/2)

# playing with this using an Image vs. Text
TitleImg=resizeIcon("images\\autostop.gif", RowWidth*2, ColHeight/2)

# Multiplier is used to resize font for screen size, with smallest screen size = 480w
multiplier = SCREEN_HEIGHT / 480.0
# Jog button text
FontFixedJog = tkFont.Font(family="Courier", size=int(26*multiplier), weight='bold')
# Target and Actual field labels
FontFixedLbl = tkFont.Font(family="Courier", size=int(30*multiplier), weight='bold')
# Actual and Target numbers
FontFixed = tkFont.Font(family="Courier", size=int(66*multiplier), weight='bold')
FontNumerator = tkFont.Font(family="Courier", size=int(28*multiplier), weight='bold', underline = True)
FontDenominator = tkFont.Font(family="Courier", size=int(28*multiplier), weight='bold')
# Standard font
FontStd = tkFont.Font(family="Helvetica", size=20, weight="bold")
# Font used for Title of Application
FontTitle=tkFont.Font(family="Helvetica", size=int(40*multiplier), weight="bold")

# set up stepper motor controller
if (platform.system() == 'Linux'):
    ### import Stepper_Pi_AdaFruit as StepDriver
    pass
elif (platform.system() == 'Windows'):
    ### import Stepper_Win as StepDriver
    pass
# Initialize Stepper Driver
### Step = StepDriver.StepperMotor()

# ----------------------------------------------------------------------------
def MoveMotor(dir='no'):
    """
    DESC:   Move Stepper Motor, called by a timer to continiously move motor.
    ARGS:   dir = 'no' or blank - do not move motor
                  'lft' - move motor left
                  'rgt' - move motor right
    RETURNS: nothing, update Moving global var with dir
    """
    global Moving

    if dir != 'no': # Need to figure out why I put this here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        Moving = dir

    # check if moving, if not return, nothing to do.
    if Moving == "no":
        return

    newActual = 0.0

    if Moving == 'rgt':
        newActual = ActualVal - MOTORMOVEDEACHSTEP
        if newActual >= 0.0 and newActual >= TargetVal:
            # ?????????????????????????????????????????
            # call stepper motor driver
            # ?????????????????????????????????????????
            setActual(newActual)
        else:
            Moving = "no"

    elif Moving == 'lft':
        newActual = ActualVal + MOTORMOVEDEACHSTEP
        if newActual <= PARKLOCATION and newActual <= TargetVal:
            # ?????????????????????????????????????????
            # call stepper motor driver
            # ?????????????????????????????????????????
            setActual(newActual)
        else:
            Moving = "no"

    Root.after(DELAY_MS, MoveMotor)
    return

# ==============================================================================
#                   Start here with homeScreen
# ==============================================================================
class AutoStopApp(object):
    """
    Draw the home screen
    Loop until quit
    Execute a command based on the button pressed
    """

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """
        Sets up ...................
        """
        global Jog1Btn, Jog2Btn, Jog3Btn

        self.Root = parent
        self.Root.title("AutoStop")
        self.frame = Frame(parent)
        self.frame.configure(background=THEME) # set background color
        self.frame.grid()

        # ???????????????????? Home the system to zero out the actual ????????????????????????

        # Layout main screen with 9 rows and 6 columns
        settingsBtn = Button(self.frame, image=SettingsImg, relief=FLAT, bg=THEME, activebackground=THEME, borderwidth=0)
        settingsBtn.grid(    row=0, column=0, rowspan=2, sticky=SW)

        titleTextLbl = Label(self.frame, image=TitleImg, bg=THEME)
        # titleTextLbl = Label(self.frame, text="AutoStop", font=FontTitle, bg=THEME, fg=TEXTCOLOR)
        titleTextLbl.grid(   row=0, column=2, columnspan=3, sticky=N)

        closeBtn = Button(self.frame, image=CloseImg, relief=FLAT, command=Root.destroy, bg=THEME, activebackground=THEME, borderwidth=0)
        closeBtn.grid(       row=0, column=5, sticky=E)

        actualTextLbl = Label(self.frame, image=ActualImg, bg=THEME)
        # actualTextLbl = Label(self.frame, text="Actual", font=FontFixedLbl, bg=THEME, fg=TEXTCOLOR)
        actualTextLbl.grid(  row=1, column=4, columnspan=2, sticky=SE)

        homeBtn = Button(self.frame, image=HomeImg, command=self.goHome, relief=FLAT, bg=THEME, activebackground=THEME, borderwidth=0)
        homeBtn.grid(        row=2, column=0, rowspan=2, sticky=W)

        if UNITS == "MM":
            actualLbl = Label(self.frame, bg="gray",  textvariable=ActualValStr, justify=RIGHT, font=FontFixed)
            actualLbl.grid(      row=2, column=2, rowspan=2, columnspan=4, sticky=E)
        else:
            # create gray background
            # ####actualLbl = Label(self.frame, bg="gray", text="          ", justify=RIGHT, font=FontFixed, relief=SUNKEN)
            # ####actualLbl.grid(      row=2, column=2, rowspan=2, columnspan=4, sticky=E)

            # SUNKEN, RAISED, GROOVE, and RIDGE.
            actualLbl = Label(self.frame, bg="gray",  textvariable=ActualValStr, justify=RIGHT, font=FontFixed, relief=SUNKEN)
            actualLbl.grid(      row=2, column=2, rowspan=2, columnspan=4, sticky=E)
            actualLbl = Label(self.frame, bg="gray", textvariable=ActualNumeratorStr, justify=CENTER, font=FontNumerator)
            actualLbl.grid(      row=2, column=5, sticky=N)
            actualLbl = Label(self.frame, bg="gray", textvariable=ActualDenominatorStr, justify=CENTER, font=FontDenominator)
            actualLbl.grid(      row=3, column=5, sticky=N)

        keypadBtn = Button(self.frame, image=KeypadImg, command=self.openKeypad, relief=FLAT, bg=THEME, activebackground=THEME, borderwidth=0)
        keypadBtn.grid(      row=4, column=2, sticky=S)

        targetlTextLbl = Label(self.frame, image=TargetImg, bg=THEME)
        # targetlTextLbl = Label(self.frame, text="Target", font=FontFixedLbl, bg=THEME, fg=TEXTCOLOR)
        targetlTextLbl.grid( row=4, column=4, columnspan=2, sticky=SE)

        parkBtn = Button(self.frame, image=ParkImg, command=self.goPark, relief=FLAT, bg=THEME, activebackground=THEME, borderwidth=0)
        parkBtn.grid(        row=5, column=0, rowspan=2, sticky=W)

        if UNITS == "MM":
            targetlLbl = Label(self.frame, bg="gray", textvariable=TargetValStr, justify=RIGHT, font=FontFixed)
            targetlLbl.grid(     row=5, column=2, rowspan=2, columnspan=4, sticky=E)
        else:
            # create gray background
            # ###targetLbl = Label(self.frame, bg="gray", text="          ", justify=RIGHT, font=FontFixed)
            # ###targetLbl.grid(      row=5, column=2, rowspan=2, columnspan=4, sticky=E)
            targetLbl = Label(self.frame, bg="gray",  textvariable=TargetValStr, justify=RIGHT, font=FontFixed, relief=SUNKEN)
            targetLbl.grid(      row=5, column=2, rowspan=2, columnspan=4, sticky=E)
            targetLbl = Label(self.frame, bg="gray", textvariable=TargetNumeratorStr, justify=CENTER, font=FontNumerator)
            targetLbl.grid(      row=5, column=5, sticky=N)
            targetLbl = Label(self.frame, bg="gray", textvariable=TargetDenominatorStr, justify=CENTER, font=FontDenominator)
            targetLbl.grid(      row=6, column=5, sticky=N)

        # goBtn = Button(self.frame, image=GoImg, command=self.go, relief=FLAT)
        # goBtn.grid(          row=7, column=0, rowspan=2, sticky=SW)

        for self.b in range(3):
            self.cmd = partial(self.jogButtonPressed, self.b)
            if CurrentJogValue == self.b:
                img = JogPressedImg[self.b]
            else:
                img = JogImg[self.b]
            JogBtn[self.b] = Button(self.frame, image=img, text=formatJogValue(JOGVALUES[self.b]),
                                compound=CENTER, fg='white', font=FontStd,
                                command=self.cmd, relief=FLAT, bg=THEME, activebackground=THEME, borderwidth=0)
            JogBtn[self.b].grid(row=7, column=self.b, rowspan=2)

        leftBtn = Button(self.frame, image=LeftImg, command=self.moveLeft, relief=FLAT, bg=THEME, activebackground=THEME, borderwidth=0)
        leftBtn.grid(        row=7, column=4, rowspan=2, sticky=S)

        rightBtn = Button(self.frame, image=RightImg, command=self.moveRight, relief=FLAT, bg=THEME, activebackground=THEME, borderwidth=0)
        rightBtn.grid(       row=7, column=5, rowspan=2, sticky=SE)

        Root.after(5, MoveMotor)
        Root.mainloop()

    # ----------------------------------------------------------------------------
    def jogButtonPressed(self, jogButton):
        """
        Change image of new jog button to appear turned on
        Change image of previous jog button to appeared turned off
        ARGS: Jog Button Pressed
        RETURNS: nothing
        """
        global JogBtn, CurrentJogValue
        self.jogButton = jogButton

        # if current jogging value is the same as the new value, return and do nothing
        if CurrentJogValue == self.jogButton:
            return

        # restore current jog button to not normal image
        JogBtn[CurrentJogValue].configure(image=JogImg[CurrentJogValue])

        # change new jog button to pressed image
        JogBtn[self.jogButton].configure(image=JogPressedImg[self.jogButton])

        CurrentJogValue = self.jogButton

    #----------------------------------------------------------------------
    def hide(self):
        """"""
        self.Root.withdraw()

    #----------------------------------------------------------------------
    def show(self):
        """"""
        self.Root.update()
        self.Root.deiconify()

    #----------------------------------------------------------------------
    def openKeypad(self):
        """"""
        # self.hide()
        keypadFrame = KeypadFrame(self)

    # ----------------------------------------------------------------------------
    def eStop(self):
        """
        Emergency Stop button pressed
        ARGS:
        RETURNS:
        """
        Step(speed=0, coils=1, steps=0, dir=Step.BRAKE)
        # #######################################################
        # Need to blink Stop and wait until Stop is pressed again
        # #######################################################

    # ----------------------------------------------------------------------------
    def goHome(self):
        setTarget(0.0)
        MoveMotor('rgt')

    # ----------------------------------------------------------------------------
    def goPark(self):
        setTarget(PARKLOCATION)
        MoveMotor('lft')

    # ----------------------------------------------------------------------------
    def moveLeft(self):
        setTarget(TargetVal + JOGVALUES[CurrentJogValue])
        MoveMotor('lft')

    # ----------------------------------------------------------------------------
    def moveRight(self):
        setTarget(ActualVal - JOGVALUES[CurrentJogValue])
        MoveMotor('rgt')

    # ----------------------------------------------------------------------------
    def go(self):
        """
        GO button is pressed.  Check if moving forward or backward.
        ARGS: none
        RETURNS: none
        """
        global Moving

        if TargetVal > ActualVal:
            Moving = 'bak'
        elif TargetVal < ActualVal:
            Moving = 'fwd'

        MoveMotor()

# #######################################################################
class KeypadFrame(Toplevel):
    """
    description
    ARGS:
    RETURNS:
    """
    #----------------------------------------------------------------------
    def __init__(self, original):
        """Constructor"""
        self.original_frame = original
        Toplevel.__init__(self)
        # self.geometry("400x300")
        self.keypad = "KeyPad"  # Tracks which keypad currently displaying
        self.title(self.keypad)

        for self.b in range(3):
            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            self.columnconfigure(self.b, pad=8)
            self.rowconfigure(self.b, pad=8)

        if UNITS == 'MM':
            self.btnList = ['1', '2', '3', 'Bksp',
                            '4', '5', '6', 'C',
                            '7', '8', '9', '.',
                            '0', 'Enter' , '' ]
            self.btnColumns = 3 # Number of columns 3
            self.btnWidth = 5 # number of characters each button is wide
        else:
            self.btnList = ['1', '2', '3', 'C', 'Bksp',
                            '4', '5', '6', '1/2','x/4',
                            '7', '8', '9', '', '',
                            '0', 'Enter' , '','' ]
            self.btnColumns = 4 # Number of columns 4
            self.btnWidth = 3 # number of characters each button is wide
            if PRECISION > 4:
                self.btnList[13] = 'x/8'
            if PRECISION > 8:
                self.btnList[14] = 'x/16'
            if PRECISION > 16:
                self.btnList[17] = 'x/32'
            if PRECISION > 32:
                self.btnList[18] = 'x/64'

        self.newKeyLabels = [] # This is used to store modified keypad for Inch fractions

        # color codes of keys
        self.fgKeyColor = "black"
        self.bgKeyColor = "white"

        self.r = 0  # Current row
        self.c = 0  # Current column
        self.btnNumber = 0  # current button
        self.btns = [] # array that holds all the buttons

        # create all buttons with a loop
        for self.b in self.btnList:
            # partial takes care of function and argument
            self.cmd = partial(self.padNum, self.btnNumber)
            if self.b == 'Enter':  # Enter key has special parameters
                self.fg = self.bgKeyColor
                self.bg = self.fgKeyColor
                self.spaces = 2
            else:
                self.fg = self.fgKeyColor
                self.bg = self.bgKeyColor
                self.spaces = 1

            self.btns.append( Button(self,
                text=self.b.center(self.btnWidth*self.spaces),
                relief='raised', font=FontFixedJog,
                command=self.cmd,
                bg=self.bg, fg=self.fg ))
            self.btns[self.btnNumber].grid(row=self.r, column=self.c, sticky=W+E,
                columnspan=self.spaces)
            self.btnNumber += 1
            self.c += self.spaces

            # move to next line if at end of line
            if self.c > self.btnColumns:
                self.c = 0
                self.r += 1

    # ----------------------------------------------------------------------------
    def padNum(self, key):
        """
        This is the command called for each key
        ARGS: what key was pressed
        RETURNS: calls either MM or IN function
        """
        self.key = key
        if UNITS == 'MM':
            self.key = self.btnList[self.key]
            self.add_MM_num(self.key)
        else:
            # ???????????????????????????????????????????????????????????????????????
            if self.keypad == 'KeyPad':
                self.key = self.btnList[self.key]
            else:
                self.key = self.newKeyLabels[self.key]

            self.add_IN_num(self.key)

    #----------------------------------------------------------------------
    def onClose(self):
        """
        Enter button pressed.  Close out keypad window, bring main window back to focus.
        Check if moving forward or backward, start moving.
        ARGS: none
        RETURNS: none
        """
        self.destroy()
        self.original_frame.show()

        if TargetVal > ActualVal:
            MoveMotor('lft')
        elif TargetVal < ActualVal:
            MoveMotor('rgt')

    # ----------------------------------------------------------------------------
    def add_MM_num(self, newNum):
        # Add one number at a time to target value
        # up to two decimal points (hundreds)
        # up to the max MM allowed
        global DecimalMode

        self.newTargetVal = TargetVal
        self.newNum = newNum.strip()  # strip off whitespace from key value
        # Check if character entered is a decimal point
        if self.newNum == '.':
            # check if already in decimal entry mode.
            #     If not: change to decimal entry mode
            #     If so: do nothing
            if DecimalMode == 0:
                DecimalMode = 1   # next character is first decimal number
                # change color of decimal point to show that you pressed it.
                self.btns[11].configure(bg=self.fgKeyColor, fg=self.bgKeyColor)

        # Check if button pressed is Enter, if so return.
        elif self.newNum == 'Enter':
            self.onClose()

        # Check if button pressed is blank, if so do nothing.
        elif self.newNum == '':
            pass

        # Check if button pressed is C for clear all numbers.
        elif self.newNum == 'C':
            DecimalMode = 0
            self.newTargetVal = 0.0
            # restore color of decimal point back to normal
            self.btns[11].configure(bg=self.bgKeyColor, fg=self.fgKeyColor)

        # Check if character entered is Backspace, delete last character entered
        elif self.newNum == 'Bksp':
            if DecimalMode == 0:
                self.newTargetVal = int(float(self.newTargetVal) / 10)
            if DecimalMode == 1:
                self.newTargetVal = int(float(self.newTargetVal) / 10)
                DecimalMode = 0
                # restore color of decimal point back to normal
                self.btns[self.decimalKey].configure(bg=self.bgKeyColor, fg=self.fgKeyColor)
            elif DecimalMode == 2:
                self.newTargetVal = int(self.newTargetVal)
                DecimalMode = 1
            elif DecimalMode == 3:
                self.newTargetVal = int(self.newTargetVal*10)
                self.newTargetVal = self.newTargetVal/10.0
                DecimalMode = 2

        else:
            # numbers 0-9
            self.newNum = int(self.newNum)  # convert to integer
            # intTargetVal = int(float(TargetVal))  # convert to integer
            if DecimalMode == 0:
                self.newTargetVal = (int(float(self.newTargetVal)) * 10) + self.newNum
            elif DecimalMode == 1:
                self.newTargetVal = float(self.newTargetVal) + (self.newNum * .1)
                DecimalMode = 2   # next character is second decimal number
            elif DecimalMode == 2:
                self.newTargetVal = float(self.newTargetVal) + (self.newNum * .01)
                DecimalMode = 3   # no more digits
            else:
                mBox.showerror('Limit Exceeded', 'Only two decimals allowed')
                self.deiconify()  # Bring keypad back to focus
                # self.newTargetVal = float(TargetVal) # ????????????

        # CHECK IF num > maximum length
        if ( self.newTargetVal >= PARKLOCATION):
            mBox.showerror('Limit Exceeded', 'Value exceeds Park Limit')
            self.deiconify()  # Bring keypad back to focus
        else:
            if (TargetVal) != self.newTargetVal:
                setTarget(self.newTargetVal)
        return

    # ----------------------------------------------------------------------------
    def redrawButtons(self):
        """
        Redraws entire keypad with original keys
        ARGS: none
        RETURNS: Nothing
        """
        for self.a in range(self.btnNumber):   # btnNumber = maximum number of buttons
            self.btns[self.a].configure(text=self.btnList[self.a])
            self.btns[self.a].grid()
        self.keypad = 'KeyPad'
        self.title(self.keypad)

    # ----------------------------------------------------------------------------
    def add_IN_num(self, newNum):
        """
        Key pressed, add value to screen, includes fractions
        ARGS: new number to add
        RETURNS: Nothing,
            DecimalMode global set to 0 for whole numbers, 4 for x/4, 8 for x/8, 16 for x/16
        """
        # Add one number at a time to target value
        # up to the max Inch allowed
        global DecimalMode

        self.newTargetVal = TargetVal
        self.newNum = newNum.strip()   # strip off all whitespace
        # Check if button pressed is 1/2
        if self.newNum == '1/2':
            self.newTargetVal = int(self.newTargetVal) + 0.5
        # Check if button pressed is x/4
        elif self.newNum == 'x/4':
            # only display keys 1, 3 and C.  i.e. 1/4, 3/4
            self.newKeyLabels=[' 1 ', ' 3 ', ' C ']
            for self.a in range(len(self.newKeyLabels)):
                self.btns[self.a].configure(text=self.newKeyLabels[self.a])
            for self.a in range(len(self.newKeyLabels),self.btnNumber):
                 self.btns[self.a].grid_remove()
            DecimalMode = 4
            self.keypad = 'x/4'
            self.title(self.keypad)

        elif self.newNum == 'x/8':
            # only display keys 1, 3, 5, 7 and C.  i.e. 1/8, 3/8, 5/8, 7/8
            self.newKeyLabels=[' 1 ', ' 3 ', ' 5 ', ' 7 ', ' C ']
            for self.a in range(len(self.newKeyLabels)):
                self.btns[self.a].configure(text=self.newKeyLabels[self.a])
            for self.a in range(len(self.newKeyLabels),self.btnNumber):
                 self.btns[self.a].grid_remove()
            DecimalMode = 8
            self.keypad = 'x/8'
            self.title(self.keypad)

        elif self.newNum == 'x/16':
            # only display keys 1, 3 and C.  i.e. 1/16, 3/16, 5/16, 7/16, 9/16, 11/16, 13/16, 15/16
            self.newKeyLabels=[' 1 ', ' 3 ', ' 5 ', ' 7 ', ' 9 ', '11 ', '13 ', '15 ', ' C ']
            for self.a in range(len(self.newKeyLabels)):
                self.btns[self.a].configure(text=self.newKeyLabels[self.a])
            for self.a in range(len(self.newKeyLabels),self.btnNumber):
                 self.btns[self.a].grid_remove()
            DecimalMode = 16
            self.keypad = 'x/16'
            self.title(self.keypad)

        elif self.newNum == 'x/32':
            # only display odd keys 1, 3, etc.
            self.newKeyLabels=[' 1 ', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21', '23', '25', '27', '29', '31', 'C']
            for self.a in range(len(self.newKeyLabels)):
                self.btns[self.a].configure(text=self.newKeyLabels[self.a])
            for self.a in range(len(self.newKeyLabels),self.btnNumber):
                 self.btns[self.a].grid_remove()
            DecimalMode = 32
            self.keypad = 'x/32'
            self.title(self.keypad)

        elif self.newNum == 'x/64' or self.newNum == 'Prev':
            # only display odd keys 1, 3, etc.
            self.newKeyLabels=['1', '3', '5', '7', '9', '11', '13', '15', '17', '19', '21', '23', '25', '27', '29', '31', 'Next', 'C']
            for self.a in range(len(self.newKeyLabels)):
                self.btns[self.a].configure(text=self.newKeyLabels[self.a])
            for self.a in range(len(self.newKeyLabels),self.btnNumber):
                 self.btns[self.a].grid_remove()
            DecimalMode = 64
            self.keypad = 'x/64'
            self.title(self.keypad)

        elif self.newNum == 'Next':
            # only display odd keys 1, 3, etc.
            self.newKeyLabels=['33', '35', '37', '39', '41', '43', '45', '47', '49', '51', '53', '55', '57', '59', '61', '63', 'Prev', 'C']
            for self.a in range(len(self.newKeyLabels)):
                self.btns[self.a].configure(text=self.newKeyLabels[self.a])
            for self.a in range(len(self.newKeyLabels),self.btnNumber):
                 self.btns[self.a].grid_remove()
            DecimalMode = 64
            self.keypad = 'x/64'
            self.title(self.keypad)

        # Check if button pressed is Enter, if so return.
        elif self.newNum == 'Enter':
            self.onClose()

        # Check if button pressed is blank, if so do nothing.
        elif self.newNum == '':
            pass

        # Check if button pressed is C for clear all numbers.
        elif self.newNum == 'C':
            self.newTargetVal = 0.0
            DecimalMode = 0 # reset decimal mode to whole number
            self.redrawButtons()

        # Check if character entered is Backspace, delete last character entered
        elif self.newNum == 'Bksp':
            if DecimalMode == 0:
                self.newTargetVal = int(float(self.newTargetVal) / 10)
            else:  # in fraction mode
                self.newTargetVal = int(self.newTargetVal)
                DecimalMode = 0 # reset decimal mode to whole number
                # self.redrawButtons()

        else:
            # numbers 0-9
            self.newNum = int(self.newNum)  # convert to integer
            # intTargetVal = int(float(TargetVal))  # convert to integer
            if DecimalMode == 0:
                # move number (whole) to left and add newNum to right side of number
                self.newTargetVal = (self.newTargetVal*10) + self.newNum

                """
                # move whole number to left and add newNum to right side of whole number
                #    leaving decimal number alone, i.e. 36.0 (newNum=5) becomes 365.0
                self.intTargetVal = int(TargetVal)  # just the whole number
                self.newTargetVal = (self.intTargetVal*10) + self.newNum  # move whole numbers left
                self.decTargetVal = TargetVal - intTargetVal  # only the decimal
                self.newTargetVal = self.newTargetVal + self.decTargetVal # new whole number + decimal
                """
            elif DecimalMode == 4:  # x/4th mode
                self.newTargetVal = int(self.newTargetVal) + self.newNum/4.0
                self.redrawButtons()
            elif DecimalMode == 8:  # x/8th mode
                self.newTargetVal = int(self.newTargetVal) + self.newNum/8.0
                self.redrawButtons()
            elif DecimalMode == 16:  # x/16th mode
                self.newTargetVal = int(self.newTargetVal) + self.newNum/16.0
                self.redrawButtons()
            elif DecimalMode == 32:  # x/32th mode
                self.newTargetVal = int(self.newTargetVal) + self.newNum/32.0
                self.redrawButtons()
            elif DecimalMode == 64:  # x/64th mode
                self.newTargetVal = int(self.newTargetVal) + self.newNum/64.0
                self.redrawButtons()
            else:
                mBox.showerror('Not a defined key', 'Invalid code')
                self.deiconify()  # Bring keypad back to focus
                # self.newTargetVal = float(TargetVal) # ????????????

        # CHECK IF num > maximum length
        if ( self.newTargetVal >= PARKLOCATION):
            mBox.showerror('Limit Exceeded', 'Value exceeds Park Limit')
            self.deiconify()  # Bring keypad back to focus
        else:
            if (TargetVal) != self.newTargetVal:
                setTarget(self.newTargetVal)
        return

# ----------------------------------------------------------------------------
def settings():
    """
    description
    ARGS:
    RETURNS:
    """
    r = 3  # DEBUG
    if r == 1:  # Shutdown
        if shutdown('Shutdown') == True: shutdown("Shutdown")
    elif r == 2: # Reboot
        if shutdown('Reboot') == True: shutdown("Reboot")
    elif r == 3:
        if shutdown('Quit') == True: shutdown("Quit")
    exit(0)

#=============================================================================
def shutdown(todo = 'Quit'):
    """
    Quit program, Shutdown or reboot the Raspberry Pi system
    ARGS:      todo = 'Quit' (default), 'Shutdown' or 'Reboot'
    RETURNS:   True if user agrees to task
    """
    # r = db.displayDialogBox('askToQuit', screen, [todo], DIALOGWAIT)
    # ????????????????????????????????????????????????
    # ask if want to quit
    # ????????????????????????????????????????????????
    if r == 0:  # user pressed Yes button
        if platform.system() == 'Linux':
            if todo == 'Shutdown':
                # ????????????????????????????????????????????????
                # display SHUTDOWN ON SCREEN
                # ????????????????????????????????????????????????
                os.system("shutdown -h 0")
            elif todo == 'Reboot':
                # ????????????????????????????????????????????????
                # display REBOOTING ON SCREEN
                # ????????????????????????????????????????????????
                os.system("reboot")
            else:
                exit(0)  # User just wants to quit program
        else:
            return True  # Windows OS so just return
    else:
        return False  # user does not want to do task

# ============================================================================
if __name__ == '__main__':
    app = AutoStopApp(Root)
    Root.mainloop()
