# AutoStop v1.0

AutoStop was created when I saw a video on [YouTube](https://www.youtube.com/watch?v=dHXoMG2s5yE) by Bellevue Woodshop on his version of the [TigerStop](http://www.tigerstop.com/material/wood/) automatic Miter Saw Stop.  Watch some videos on the TigerStop here:  [Video1](??????????????????) [Video2](??????????????)

??????? stated that having one of these in a home "private" shop is overkill, but I disagree, I'm a maker, with wood, electronics and computers. So when I saw this, a combination of all three, I jumped at it.  ??????? used scrap materials from his job so nothing was written down, so I had to create this from scratch.   Where he used a laptop and Mach3 software to control the "servo" motor, I used a newer age Raspberry Pi with a stepper motor controller.  

The track was the hardest to create, because ????????????????????

Materials I used include:

* _Raspberry Pi 3_ [AdaFruit](????????????????) or [Amazon](???????????????)
* _AdaFruit_ Stepper Motor HAT for Raspberry Pi - Mini Kit [AdaFruit #2348](https://www.adafruit.com/products/2348)
* _AdaFruit_ 7" Backpack LCD touchscreen display [AdaFruit](???????????????)
* _AdaFruit_ Stepper Motor [Adafruit](https://www.adafruit.com/products/324)
* Belt
* Gears
* Track
* Raspberry Pi and LCD case (homemade) [Thingiverse]()

I then created a program in Python to control the stepper motor.  I wanted this to be useful in either Metric millimeters or Imperial Inches.  As I am from the U.S., we use the stupid Imperial system that was very hard to program.   But the display is designed to work on many different screen resolutions including 800x480, 1024x600, etc.  I used the built-in TKinter GUI interface what I had not used before.  Easy to use one I learned the basics.  

> AutoStop was created by Will Travis

> https://github.com/CowboyWill/AutoStop

**This is a work in progress.**

Copyright 2016 - William Travis - All rights reserved.

## Requirements
* _Raspbian Jessie_ running on a Raspberry Pi 2 or Pi 3
* _Adafruit_ Stepper Motor control softwar [AdaFruit](https://www.adafruit.com/products/2441)

## Setup
### AdaFruit Stepper Motor Controller
The ??????????????????

### Installing AutoStop
AutoStop installation is pretty easy. AutoStop requires Python 2.7, git and pip all of which are installed as part of Raspbian.

```
cd ~
git clone https://github.com/cowboywillt/AutoStop.git
cd AutoStop
????????????????????
```

## Settings
If you have a display with a different resolution you can change the size of window using ???????????????? window_width- and ?????????????????? window_height-properties in the configuration file.

## Running AutoStop

Start AutoStop by browsing to the folder of the Python-file and execute 
```
sudo python ./AutoStop.py & 
```

## Settings in AutoStop.cfg
[APIsettings]
* **BaseURL**  the URL to your OctoPrint installation. For instance `http://localhost` or `http://192.168.0.5`.
* **APIkey**  Put your API-key from OctoPrint 

Change any other settings you want

# Set up automatic starting upon bootup, Using Daemon script 
### To install OctoScreen as a daemon (Autostart)
```
sudo sh daemon OctoScreen install
```
### To uninstall OctoScreen as a daemon
```
sudo sh daemon OctoScreen uninstall
```
### To lookup status of running daemon
```
sudo sh daemon OctoScreen ps
        and/or
sudo sh daemon OctoScreen service
```
### Update OctoScreen from github
```
sudo sh daemon OctoScreen uninstall
```
### Start, Stop or Restart daemon
```
sudo sh daemon octoscreen start
sudo sh daemon octoscreen stop
sudo sh daemon octoscreen restart
       or this
sudo service octoscreen {start|stop|restart}
```
### Display daemon log
```
sudo sh daemon OctoScreen dlog
```
### Display OctoScreen log
```
sudo sh daemon OctoScreen log
```
### Delete daemon log
```
sudo sh daemon OctoScreen dlogdelete
```
### Delete OctoScreen log
```
sudo sh daemon OctoScreen logdelete
```

# Thanks
Bellevue Woodworking for his idea to create a personal one.  
