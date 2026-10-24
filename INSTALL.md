# Building from source: Windows

Open up the command prompt, create a virtual environment and activate it:

Create new virtual environment  
`> python -m venv %HOMEPATH%\.virtualenvs\galaga`  

Activate virtual environment  
`> cd %HOMEPATH%\.virtualenvs\galaga\Scripts`  
`> .\activate.bat`  

## Building PyBox2D
pyjam requires [pybox2d](https://github.com/pybox2d/pybox2d) 2.3.10  
pybox2d 2.3.10 provides wheels for Python 2.7 and 3.5 up to 3.8. No wheels for 3.9, 3.10, 3.11 nor 3.12.  
If using Python 3.9+ please follow build & install instructions below.

Please note that both [swig](https://www.swig.org/) and a C++ compiler are required to be able to build it. 

1. Install the correct version of Microsoft Visual Studio for your version of Python so that you can compile Box2D and pybox2d.
Alternatively download and install Microsoft C++ Build Tools (Visual Studio Build Tools 2022). Goto: https://visualstudio.microsoft.com/visual-cpp-build-tools/ 
run setup and select *Desktop applications development with C++* workload.
2. *Make sure that the compiler is in your PATH*. The best way is to launch x64/x86 Native Tools Command Prompt for VS 2022,
where x64 or x86 depends on your Python version. If you use a new Native Tools Command Prompt for VS, ensure to activate your Python virtual environment.   
3. Install SWIG for making the Python wrapper from [here](https://www.swig.org/download.html). Install it in a location in your PATH, or add the SWIG root directory to your PATH.    
4. Assuming that you want to clone the source into *%HOMEPATH%\src*, point your command prompt into that folder, i.e.:  
`> cd %HOMEPATH%\src`
5. Clone the source from the git repository:    
`> git clone https://github.com/pybox2d/pybox2d`  
`> cd .\pybox2d`
6. Build and install pybox2d:  
`> python setup.py build`  
`> python setup.py install`

## Clone and run pyjam-galaga

1. Cd into a folder where you can clone the source, i.e.:  
`> cd %HOMEPATH%\src`

2. Clone (or fork) the pyjam-galaga source:  
`> git clone https://github.com/gzito/galaga.git`

3. Setup the PYTHONPATH environment variable:  
`> set PYTHONPATH=%HOMEPATH%\src\galaga;%HOMEPATH%\src\galaga\galaga;%HOMEPATH%\src\galaga\pyjam`

4. Install requirements:  
`> pip install -r .\galaga\requirements.txt`

5. Run the game:  
`> cd .\galaga\galaga`  
`> python main.py`

# Building from source: macos

I tested pyjamgalaga on macos with python 3.12. If you haven't installed it yet, open up the terminal and install with:

`$ brew install python@3.12`

Then, create a virtual environment and activate it:

Create new virtual environment  
`$ python3.12 -m venv $HOME/.virtualenvs/galaga`

Activate virtual environment  
`$ source $HOME/.virtualenvs/galaga/bin/activate`  

## Building PyBox2D

1. Install swig:\
`$ brew install swig`

2. Assuming that you want to clone the source into *\$HOME/src*, point your command prompt into that folder, i.e.:\
`$ cd $HOME/src`

3. Clone the source from the git repository:    
`$ git clone https://github.com/pybox2d/pybox2d`  
`$ cd ./pybox2d`

4. Install setuptools:\
`$ pip install setuptools wheel`

5. Build and install pybox2d:  
`$ python3.12 setup.py build`  
`$ python3.12 setup.py install`

## Clone and run pyjam-galaga

1. Cd into a folder where you can clone the source, i.e.:  
`$ cd $HOME/src`

2. Clone (or fork) the pyjam-galaga source:  
`$ git clone https://github.com/gzito/galaga.git`

3. Setup the PYTHONPATH environment variable:  
`$ export PYTHONPATH=$HOME/src/galaga:$HOME/src/galaga/galaga:$HOME/src/galaga/pyjam`

4. Install requirements:  
`$ pip install -r ./galaga/requirements.txt`

5. Run the game:  
`$ cd ./galaga/galaga`  
`$ python3.12 main.py`
