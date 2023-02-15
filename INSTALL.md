# Building from source: Windows

Open up the command prompt, create a virtual enviroment and activate it:

`> python -m venv %HOMEPATH%\.virtualenvs\pyjam-galaga`  
`> cd %HOMEPATH%\.virtualenvs\pyjam-galaga\Scripts`  
`> .\activate.bat`  

## Building PyBox2D
1. Install the correct version of Microsoft Visual Studio for your version of Python so that you can compile Box2D and pybox2d. Alternatively install MinGW and then MSYS. *Make sure that the compiler is in your PATH*.    
2. Install SWIG for making the Python wrapper from [here](https://www.swig.org/download.html). Install it in a location in your PATH, or add the SWIG root directory to your PATH.    
3. Assuming that you want to clone the source into *%HOMEPATH%\src*, point your command prompt into that folder, i.e.:  
`> cd %HOMEPATH%\src`
4. Clone the source from the git repository:    
`> git clone https://github.com/pybox2d/pybox2d`  
`> cd .\pybox2d`
5. Build and install pybox2d:  
`> python setup.py build`  
`> python setup.py install`

## Clone and run pyjam-galaga

1. Cd into a folder where you can clone the source, i.e.:  
`> cd %HOMEPATH%\src`

2. Clone (or fork) the pyjam-galaga source:  
`> git clone https://github.com/gzito/pyjam-galaga.git`

3. Setup the PYTHONPATH environment variable:  
`> set PYTHONPATH=%HOMEPATH%\src\pyjam-galaga;%HOMEPATH%\src\pyjam-galaga\galaga;%HOMEPATH%\src\pyjam-galaga\pyjam`

4. Install requirements:  
`> pip install -r .\pyjam-galaga\requirements.txt`

5. Run the game:  
`> cd .\pyjam-galaga\galaga`  
`> python main.py`

