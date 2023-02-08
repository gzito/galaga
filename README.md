# pyjam-galaga
Remake of 1981's Galaga arcade game written in python, pyjam library and moderngl.
Based on original work by Stefan Wessels.

# The story
[**Galaga**](https://en.wikipedia.org/wiki/Galaga) is a 1981 fixed shooter arcade video game developed and published by Namco. In North America, it was released
by Midway.

Since I was a kid I have always been fascinated by Galaga: its innovative concept for the time, the insect graphics
and the way enemy ships move in formation, making the most varied evolutions; its delightful game sound effects.
The game was created and designed by Shigeru Yokoyama and at that time was clearly written in assembly language.  
The hardware platform included three Z80 CPUs running at 3.072 Mhz, a three-channel Namco custom sound chip
and a video resolution of 288 x 224 pixels at 16 colors.  

In those days the internet didn't exist and there was no way to get even the slightest information about the code
behind the game. Over the years several conversions of the coin-op have been made, both for gaming consoles,
first of all the excellent Galaga "Demons of Death" for NES, and for the major home computers, among which the version
for MSX and for Atari 7800 stand out. Some excellent unofficial conversions were made, including the one for Atari 2600
and for Commodore 64.

In 2017 Stefan Wessels wrote a [remake of the game](https://github.com/StewBC/Galaga) using AppGameKit (AGK) & Tier 1,
hence in Basic language.

I personally think Stefan did a great job, making it really clear for the first time how to code Galaga's mechanics.
I studied his code in great detail and I thought to myself: ***why not make a conversion using Python?***

![](https://github.com/gzito/pyjam-galaga/blob/main/screenshot-1.jpg?raw=true)

## pyjam
As many of you know, it is very challenging to make a game from scratch without an engine, and I didn't want to use Pygame
as 2d renderer, as I wanted more than what Pygame offers. I still opted to use Pygame for sound effects, as I find the Pygame Mixer to be a very cool implementation to use as sound framework.
So, to render graphics I decided to write a small game library built on the *excellent* [`moderngl`](https://github.com/moderngl/moderngl) library, the OpenGL
Python binding by Szabolcs Dombi and Einar Forselv. I added 2D animations, spritesheets and rewrote some XNA / MonoGame classes in Python, such as the `SpriteBatch` class.  
I called it **pyjam**.  
> You can find the library code into the [`pyjam` folder!](https://github.com/gzito/pyjam-galaga/tree/main/pyjam)

![](https://github.com/gzito/pyjam-galaga/blob/main/screenshot-2.jpg?raw=true)

## Dependencies
[glcontext](https://github.com/moderngl/glcontext)  
[moderngl](https://github.com/moderngl/moderngl)  
[numpy](https://github.com/numpy/numpy)  
[Pillow](https://github.com/python-pillow/Pillow)  
[pybox2d](https://github.com/pybox2d/pybox2d)  
[pygame](https://github.com/pygame/pygame)  
[PyGLM](https://github.com/Zuzu-Typ/PyGLM)   

### pybox2d prerequisites
> pyjam requires [pybox2d](https://github.com/pybox2d/pybox2d) 2.3.10  
> pybox2d 2.3.10 provides wheels for Python 2.7 and 3.5 up to 3.8. No wheels for 3.9, 3.10 nor 3.11.  
> If using Python 3.9+ please follow build & install instructions [here](https://github.com/pybox2d/pybox2d/blob/master/INSTALL.md).

> Please note that both [swig](https://www.swig.org/) and a C++ compiler are required to be able to build it. 

## Installation
cd into the `root` folder and run:  
```shell
$ pip install -r requirements.txt
```

To play Galaga, cd into the `galaga` subfolder and run `main.py`.  

## pyjam-galaga keys  
**Enter:** insert coin  
**1 / 2:** start one or two player(s) match  
**Left/right cursor keys:** move the ship  
**Ctrl:** fire  
**Esc:** Exit the game  
**F1:** show/hide FPS indicator  

## pyjam-galaga current status
For several pieces of Stefan's code I merely ported them as they are to Python language.
For other parts I did some refactoring and adaptation to Python and pyjam.
I also added the code to complete the `rescue of fighter sequence`, missing in the original
Stefan's work.

By default, the game runs in windowed mode. However, it can also run in fullscreen. Just change the `go_fullscreen` configuration
attribute in the `Galaga` class.

## Here is a brief summary of current the state of the game:

- The hardware startup sequence is complete - it's a trimmed down version of the original as that took too long
when you just wanted to play a quick game. To turn it off completely, set the attribute `skip_hw_startup` to `True`
in the `Galaga` class.

- The demo-attract sequence is blocked in but is not functional past the initial reveal.

- The gameplay is still incomplete and there could be issues, but the basic behaviours are there.  
  - The regular attack stages work pretty well.  
  - Stages greater than `Stage 3` still have to be implemented ; Dragonfly, Satellite and Enterprise need to be put in.  
  - The bees are quite complete. The butterflies and bosses movement patterns could use a bit of tuning.  
  - The attack algorithm needs some refinement.
  - The 1 and 2 player support should be complete, though I've not completely tested it.  
  - Capture / rescue sequence is complete.  
  - Transforms enemies (Scorpion, Bosconian, Galaxian) needs to be implemented.  
  - The on-screen scoring is implemented and quite functional.

- The post-game flow with high-score taking, etc. is complete or quite complete.

- Once a highscore is made, the leaderboard is saved in the user's home folder and automatically reloaded next time.

### Note
> Python code is not as clean as I would like, there is still a lot of work to be done.

See [`CHANGELOG.txt`](./CHANGELOG.txt) to see the history of changes since the first release.  
See [`TODO.txt`](./TODO.txt) to check what still needs to be implemented or improved.

## Acknowledgements
[Stefan Wessels](https://github.com/StewBC)  
[The MonoGame team](https://github.com/MonoGame/MonoGame)
