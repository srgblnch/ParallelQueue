# Yet Another Multiprocessing Pool (yamp)

Python module to manage multiprocessing of a queue. Quite similar to _multiprocessing.Pool_ but more to my liking.

I've needed and reproduced a similar functionality twice in a while and a third was coming the way. That's _enough_ to encapsulate it in a module. Perhaps the name could be better.


## TODO:

- [x] Use python Logging.
- [ ] Extend the ending condition.
- [ ] Improve the input: no need to be build before, but can be generated while needed.
- [x] Control memory usage (psutil).
- [x] Control machine load.
- [ ] Hooks. At least, after the worker target execution allow to execute something, but with in a Lock because is a place to report results in a file (for example).
- [ ] Python 3.5 together with the current 2.7 support.
- [ ] Cythonize.
- [ ] Look on *pkg_resources* to improve version numbering.
- [x] When enter in _pause_ mode, use _psutil_ to suspend the workers until conditions recovers and the work can be resumed (then resume the workers).
  - [ ] This many enter in a loop of _suspend-resume_. Raise the bell to reduce the number of parallel workers.
  - [ ] In the warning sections of memory use and machine load, those workers can be _reniced_ to reduce their priority.


## Usage:

Get the sources as usual.

```
$ git clone git@github.com:srgblnch/yamp.git
```

Build them using the setup tools.

```
$ python setup.py build
$ python setup.py install --prefix ~/usr
```

Use in a python interpreter

```python
>>> import yamp
>>> yamp.version()
    '0.0.4-0'
>>> arginLst = range(20)
>>> checkPeriod = 2
>>> from random import randint
>>> from time import sleep
>>> def tester(argin):
...:     argout = argin**2
...:     sleep(randint(checkPeriod/2, checkPeriod*2))
...:     return argout
>>> pool = yamp.Pool(tester, arginLst)
>>> pool.checkPeriod = checkPeriod
>>> pool.start()
```

The control of the *main thread* will be returned and it can be checked the progress for the procedure:

```python
>>> pool.progress
0.407407
```

