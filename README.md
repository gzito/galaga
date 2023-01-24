# pyjam-galaga
Remake of 1981's Galaga arcade game written in python

Galaga is a 1981 fixed shooter arcade video game developed and published by Namco.

Since I was a kid I've always been fascinated by Galaga. The insect graphics and the way enemy ships move in formation,
making the most varied evolutions; game sound effects.
The game was created and designed by Shigeru Yokoyama and at that time was clearly written in assembly language.  
The hardware platform included two Z80 CPUs (3.072 Mhz), a Z80 cpu dedicated to sound, a three-channel Namco custom sound chip and
a video resolution of 288x224 pixels in 16 colors.  
In those days the internet didn't exist and there was no way to get even the slightest information about the code behind the game.  
Over the years several conversions of the coin-op have been made, both for gaming consoles, first of all the excellent Galaga "Demons of
Death" for NES, both for the major home computers, among which the version for MSX and for Atari 7800 stand out.
Some excellent unofficial conversions were made, including the one for Atari 2600 and for Commodore 64.  
Until in 2017 Stefan Wessels rewrote the game for AppGameKit (AGK) Tier 1, hence in Basic language. I personally think Stefan did a great job,
making for the first time clear and obvious how the Galaga code works. I studied the code in great detail and I said to myself:
why not make a conversion to Python ? I've used several pieces of Stefan's code and converted to Python language.  
I didn't want to use Pygame to make Galaga, because I think it's a bit outdated. Furthermore, Pygame does not offer real sprites.
So I decided to write a small game engine using the excellent **moderngl** library, the OpenGL Python binding by Szabolcs Dombi and Einar Forselv.
I rewrote some XNA and MonoGame classes in Python, such as the SpriteBatch class.
Thus, “pyjam” was born, my little Python library for writing simple games.

Keys:  
**Enter:** insert coin  
**1 / 2:** start one or two player(s) match  
**Left/right cursor keys:** move the ship  
**Ctrl:** fire  
**Esc:** Exit the game  
**F1:** show/hide FPS indicator  
