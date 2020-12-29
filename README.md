# dragraceSim

![An accelerating Tesla Model 3](./static/images/dragraceTesla.png)

A simulator to find desired wheeltorque curves for vehicles

The GUI branch and its sub branch jsplots aim for the simplest possible flask gui, with some Chart.JS plotting.


Some profiling has been done in order to try to get the performance to levels near that of the MATLAB code in the original version. So far the progress has been limited.

The MATLAB code runs four different configurations, including loading some .mat data and plotting in 9.167894 seconds. While the Python is sluggish even for one!

$ python -m cProfile -s 'cumtime' -m dragraceSim > numpy2ProfileOutput

$ head -20 numpy2ProfileOutput
~~~
done printing csv
Power is 125.73131577766736 kW
         134974094 function calls (134768531 primitive calls) in 62.846 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
   1048/1    0.004    0.000   62.881   62.881 {built-in method builtins.exec}
        1    0.000    0.000   62.881   62.881 <string>:1(<module>)
        1    0.000    0.000   62.881   62.881 runpy.py:200(run_module)
        1    0.000    0.000   62.880   62.880 runpy.py:64(_run_code)
        1    0.000    0.000   62.879   62.879 dragraceSim.py:1(<module>)
        1    1.839    1.839   62.228   62.228 dragraceSim.py:44(accelerateVehicle)
   271831    0.357    0.000   39.856    0.000 decorators.py:255(_func)
   271831    0.203    0.000   35.782    0.000 decorators.py:130(binary_op_wrapper)
811956/737966    1.069    0.000   35.538    0.000 cache.py:69(wrapper)
    77734    0.322    0.000   28.408    0.000 dragraceSim.py:8(topGradeSpeed)
116584/116579    0.939    0.000   25.384    0.000 operations.py:46(__new__)
228541/228431    0.360    0.000   23.209    0.000 assumptions.py:452(getit)
    77651    1.079    0.000   22.036    0.000 mul.py:111(flatten)
~~~
