# pyjam-galaga
Remake of 1981's Galaga arcade game written in python, pyjam library and moderngl.
Based on original work of Stefan Wessels.

# The story
Galaga is a 1981 fixed shooter arcade video game developed and published by Namco. In North America, it was released
by Midway.

Since I was a kid I have always been fascinated by Galaga: its innovative concept for the time, the insect graphics
and the way enemy ships move in formation, making the most varied evolutions; its delightful game sound effects.
The game was created and designed by Shigeru Yokoyama and at that time was clearly written in assembly language.  
The hardware platform included three Z80 CPUs running at 3.072 Mhz, a three-channel Namco custom sound chip
and a video resolution of 288 x 224 pixels at 16 colors.  

In those days the internet didn't exist and there was no way to get even the slightest information about the code
behind the game. Over the years several conversions of the coin-op have been made, both for gaming consoles,
first of all the excellent Galaga "Demons of Death" for NES, both for the major home computers, among which the version
for MSX and for Atari 7800 stand out. Some excellent unofficial conversions were made, including the one for Atari 2600
and for Commodore 64.

In 2017 Stefan Wessels wrote a [remake of the game](https://github.com/StewBC/Galaga) using AppGameKit (AGK) & Tier 1,
hence in Basic language.

I personally think Stefan did a great job, making really clear for the first time
how to code Galaga mechanics. I studied the code in great detail and I said myself: why not make a conversion
using Python ? 

![](https://github.com/gzito/pyjam-galaga/blob/main/screenshot-1.jpg?raw=true)

## pyjam
As many of you know it is very challenge to make a game from scratch without an engine and I didn't want to use Pygame
as 2d renderer. I wanted more than Pygame offers. I chose to use Pygame for sound effects, I find that Pygame Mixer
is a very cool implementation as sound framework.  
To render graphics I decided to write a small game library built on the excellent **moderngl** library, the OpenGL
Python binding by Szabolcs Dombi and Einar Forselv. I added 2D animations, spritesheets and rewrote some XNA / MonoGame
classes in Python, such as the SpriteBatch class.  
I called it **pyjam**.  
You can find the library code into **pyjam** folder.

![](https://github.com/gzito/pyjam-galaga/blob/main/screenshot-2.jpg?raw=true)

## pyjam-galaga current status
For several pieces of Stefan's code I merely ported them as they are to Python language.
For other parts I did some refactoring and adaptation to pyjam.
I also added the code to complete the rescue of fighter sequence missed in the original
Stefan's work.

By default, the game run in a window; however it can also run in fullscreen, just change the proper configuration
attribute in galaga class (i.e. *go_fullscreen*).  

Here is a brief summary of the state of the game:

a) The hardware startup sequence is complete - it's a trimmed down version of the original as that took too long
when you just wanted to play a quick game. To turn it off completely, set the attribute *skip_hw_startup* to *True*
in galaga class.

b) The demo-attract sequence is blocked in but is not functional past the initial reveal.

c) The gameplay is still incomplete and there could be issues, but the basic behaviours are there.  
c.1) The regular attack stages work pretty well.  
c.2) The challenging stages work for the first 3 or so.  
c.3) The bees are quite complete. The butterflies could use a bit of tuning.  
c.4) The bosses still use the butterfly flight logic.  
c.5) the 1 and 2 player support should be complete, though I've not completely tested it.  
c.6) Capture / rescue sequence is complete.

d) The post-game flow with high-score taking, etc. is complete or quite complete.

e) Once a highscore is made, the leaderboard is saved in the user home folder and automatically reloaded next time

f) Python code is not as clean as I would like, there is still a lot of work to be done

To play Galaga, cd into pyjam-galaga subfolder and run main.py.  

## pyjam-galaga keys  
**Enter:** insert coin  
**1 / 2:** start one or two player(s) match  
**Left/right cursor keys:** move the ship  
**Ctrl:** fire  
**Esc:** Exit the game  
**F1:** show/hide FPS indicator  

## Acknowledgements
[Stefan Wessels](https://github.com/StewBC)  
[moderngl](https://github.com/moderngl/moderngl)  
[PyGLM](https://github.com/Zuzu-Typ/PyGLM) and [glm](https://github.com/g-truc/glm)   
[MonoGame](https://github.com/MonoGame/MonoGame)  
[pygame](https://github.com/pygame/pygame)  
