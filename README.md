# INSProto

## Required
- boost-python
- Python (3.3.6)
- pyserial
- tornado
- numpy

## Setup

### check environment
    $ python --version
    Python 3.3.6
    
### install dependency
    $ sudo aptitude install libboost-python-dev  
    $ sudo pip install pyserial tornado numpy
    
### setup
    $ git submodule init
    $ git submodule update
    $ cd src/vnccpplib/python
    $ make
