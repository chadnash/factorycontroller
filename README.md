# factorycontroller
An implementation of a factory controller. this is part of the application for a coles job

yes it is one file - sorry 
the output format could be improved
copes with many ways of building things and finds best in terms of recipe execution time
 
this agrees with the given answer on the example case making 4 electric engines in total 
the timings might be diffent as I find other solutions
this copes with orders 
* that must be completely fulfilled or canceled 
* that do and dont put there constucted items back into the inventory
* that do and dont always make new items

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
    *  **python src/factorycontroller/factoryContoller.py --inv src/factorycontroller/inv.json --recipes src/factorycontroller/recipes.json --orders "3x electric_engine" "5x electric_circuit"  "3x electric_engine"**

