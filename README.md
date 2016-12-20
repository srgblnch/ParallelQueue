# Yet Another Multiprocessing Pool (yamp)

![license GPLv3+](https://img.shields.io/badge/license-GPLv3+-green.svg) ![about](https://img.shields.io/badge/Subject-multiprocessing-orange.svg?style=social) ![2 - Pre-Alpha](https://img.shields.io/badge/Development_Status-2_--_pre--alpha-orange.svg)

Python module to manage multiprocessing of a queue. Quite similar to _multiprocessing.Pool_ but more to my liking.

I've needed and reproduced a similar functionality twice in a while and a third was coming the way. That's _enough_ to encapsulate it in a module.

Perhaps the name could be better but it is a coincidence with [young tramp](http://www.urbandictionary.com/define.php?term=yamp) or young vagabond. No need to mention all respect to homeless.


## TODO:

- [x] Use python Logging.
- [ ] Extend the ending condition.
- [ ] Improve the input: no need to be build before, but can be generated while needed.
- [x] Control memory usage (psutil).
- [x] Control machine load.
  - [ ] Default warning when last minute reach the number of cores
  - [ ] Default limit when the three values reach the number of cores
- [x] Hooks. At least, after the worker target execution allow to execute something, but with in a Lock because is a place to report results in a file (for example).
- [ ] Python 3.5 together with the current 2.7 support.
- [ ] Cythonize.
- [ ] Look on *pkg_resources* to improve version numbering.
- [x] When enter in _pause_ mode, use _psutil_ to suspend the workers until conditions recovers and the work can be resumed (then resume the workers).
  - [ ] This many enter in a loop of _suspend-resume_. Raise the bell to reduce the number of parallel workers.
  - [ ] Trigger the _pause_ when the limit is reached, but _resume_ when warning is clean.
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
    '0.0.5-0'
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

## Known Issues

- It has been saw that, when there are more than 1 _Worker_ in the _Pool_, the '_start event_' is propagated to the last of them almost immediately, but the others will receive it around 58 o 59 seconds later.

The script '_testing/pool.py_' with the parameters '_--samples=10_' and '_--processors=3_' will produce an stdout similar to:

    (...)
    2016-12-06 19:19:43.311158 -    DEBUG - yamp - MainProcess - MainThread - input: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] (10)
    2016-12-06 19:19:43.323326 -    DEBUG - yamp - MainProcess - MainThread - 3 workers ready
    2016-12-06 19:19:44.325203 -    DEBUG - yamp - MainProcess - MainThread - START has been requested to the Pool
    2016-12-06 19:19:44.325444 -    DEBUG - yamp - MainProcess - MainThread - START event emitted
    2016-12-06 19:19:44.325639 -     INFO - yamp - MainProcess - Monitor2 - Start to work: creating the fork
    2016-12-06 19:19:44.327255 -    DEBUG - yamp - MainProcess - Monitor2 - Start monitoring
    2016-12-06 19:19:44.331702 -    DEBUG - yamp - Process2 - Worker2 - Fork starts 0:00:00.006179 after the event trigger
    2016-12-06 19:19:44.331925 -    DEBUG - yamp - Process2 - Worker2 - argin: 0
    (...)
    2016-12-06 19:20:22.369294 -     INFO - yamp - Process2 - Worker2 - argout: 0
    2016-12-06 19:20:22.370414 -    DEBUG - yamp - Process2 - Worker2 - STEP event emitted
    2016-12-06 19:20:22.370479 -    DEBUG - yamp - MainProcess - PoolMonitor - STEP event catch
    2016-12-06 19:20:22.370571 -    DEBUG - yamp - Process2 - Worker2 - argin: 1
    2016-12-06 19:20:22.371047 -    DEBUG - yamp - MainProcess - PoolMonitor - STEP event received
    2016-12-06 19:20:22.371420 -    DEBUG - yamp - MainProcess - PoolMonitor - collect 1 outputs
    2016-12-06 19:20:22.371743 -  WARNING - yamp - MainProcess - PoolMonitor - Worker 0 hasn't start when it should have (event: True, worker: False)
    2016-12-06 19:20:22.371993 -  WARNING - yamp - MainProcess - PoolMonitor - Worker 1 hasn't start when it should have (event: True, worker: False)
    (...)
    2016-12-06 19:20:43.318191 -    DEBUG - yamp - MainProcess - Monitor0 - Waiting to start
    2016-12-06 19:20:43.318308 -     INFO - yamp - MainProcess - Monitor0 - Start to work: creating the fork
    2016-12-06 19:20:43.319511 -    DEBUG - yamp - MainProcess - Monitor0 - Start monitoring
    2016-12-06 19:20:43.320754 -    DEBUG - yamp - MainProcess - Monitor1 - Waiting to start
    2016-12-06 19:20:43.320849 -     INFO - yamp - MainProcess - Monitor1 - Start to work: creating the fork
    2016-12-06 19:20:43.322135 -    DEBUG - yamp - MainProcess - Monitor1 - Start monitoring
    2016-12-06 19:20:43.323962 -    DEBUG - yamp - Process0 - Worker0 - Fork starts 0:00:58.998431 after the event trigger
    2016-12-06 19:20:43.324197 -    DEBUG - yamp - Process0 - Worker0 - argin: 2
    2016-12-06 19:20:43.326832 -    DEBUG - yamp - Process1 - Worker1 - Fork starts 0:00:59.001310 after the event trigger
    2016-12-06 19:20:43.327090 -    DEBUG - yamp - Process1 - Worker1 - argin: 3
    (...)

* Try to use _threading.Event_ instead of _multiprocessing.Event_ for the _start_ (only used by the _MainProcess_) didn't change this behaviour of delayed start.
