# factorycontroller
An implementation of a factory controller. this is part of the application for a coles job

This is written in Python 3 
* python was the preferred choice of client
* python allowed the eaiest packaging and running 
     * requiring only python 3, the src , and a cmdline

tests are written as simple code to facilitate usage 

To Execute:
* ensure python points to python3 
* in the root directory of the cloned repo  
* run **python src/factorycontroller/factoryContoller.py --help**
* the default run as speced is one of the tests it may be run explicitly
    *  **python src/factorycontroller/factoryContoller.py **
*the example json files are in src/factorycontroller  to used these files and to run the default run use
    *   **python src/factorycontroller/factoryContoller.py --inv src/factorycontroller/inv.json --recipes src/factorycontroller/recipes.json --orders "3x electric_engine" "5x electric_circuit"  "3x electric_engine"**

