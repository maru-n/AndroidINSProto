# INSProto

## Required
- boost-python
- Python (3.3.6)
- pyserial
- tornado

## Setup

### check environment
    $ python --version
    Python 3.3.6
    
### install dependency
    $ sudo aptitude install libboost-all-dev  
    $ sudo pip install pyserial tornado
    
### setup
    $ git submodule init
    $ git submodule update
    $ cd vnccpplib/python
    $ make
