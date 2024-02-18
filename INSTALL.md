# Building from source: Windows

Open up the command prompt, create a virtual environment and activate it:

Create new virtual environment  
`> python -m venv %HOMEPATH%\.virtualenvs\galaga`  

Activate virtual environment  
`> cd %HOMEPATH%\.virtualenvs\galaga\Scripts`  
`> .\activate.bat`  

## Building PyBox2D
pyjam requires [pybox2d](https://github.com/pybox2d/pybox2d) 2.3.10  
pybox2d 2.3.10 provides wheels for Python 2.7 and 3.5 up to 3.8. No wheels for 3.9, 3.10 nor 3.11.  
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

