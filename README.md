# pyjam-galaga
Remake of 1981's Galaga arcade game written in python, based on original work of Stefan Wessels.

Galaga is a 1981 fixed shooter arcade video game developed and published by Namco. In North America, it was released
by Midway.

Since I was a kid I've always been fascinated by Galaga. its innovative concept for the time, the insect graphics
and the way enemy ships move in formation, making the most varied evolutions; its delightful game sound effects.
The game was created and designed by Shigeru Yokoyama and at that time was clearly written in assembly language.  
The hardware platform included three Z80 CPUs running at 3.072 Mhz, a three-channel Namco custom sound chip
and a video resolution of 288 x 224 pixels at 16 colors.  

In those days the internet didn't exist and there was no way to get even the slightest information about the code
behind the game. Over the years several conversions of the coin-op have been made, both for gaming consoles,
first of all the excellent Galaga "Demons of Death" for NES, both for the major home computers, among which the version
for MSX and for Atari 7800 stand out. Some excellent unofficial conversions were made, including the one for Atari 2600
and for Commodore 64.

In 2017 Stefan Wessels rewrote the game for AppGameKit (AGK) using Tier 1, hence in Basic language
(https://github.com/StewBC/Galaga). I personally think Stefan did a great job, making really clear for the first time
how to code Galaga mechanics. I studied the code in great detail and I said myself: why not make a conversion
using Python ? For several pieces of Stefan's code I merely ported them as they are to Python language.
For other parts I did some refactoring and adaptation to pyjam.
I also added the code to complete the captured-fighter sequence, the figher rescue sequence missed in the original
Stefan's work.
However, the game is not yet complete: to get an idea of what's still missing please refer to the current status
section in Stefan Wessel's Galaga repository.

As many of you know it is very challenge to make a game from scratch without an engine and I didn't want to use Pygame
as 2d renderer, Pygame does't come with 2D animations, sprite sheets, sprite batch and so on. I chose to use Pygame for
sound effects, I find that Pygame Mixer is a very cool implementation as sound framework.  
So to get graphics I decided to write a small game library built on the excellent **moderngl** library, the OpenGL
Python binding by Szabolcs Dombi and Einar Forselv.
I rewrote some XNA / MonoGame classes in Python, such as the SpriteBatch class. 
You'll found the library code into **pyjam** folder.

To play Galaga, cd into pyjam-galaga subfolder and run main.py.  

Keys:  
**Enter:** insert coin  
**1 / 2:** start one or two player(s) match  
**Left/right cursor keys:** move the ship  
**Ctrl:** fire  
**Esc:** Exit the game  
**F1:** show/hide FPS indicator  
