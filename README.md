# Yet Another Multiprocessing Pool (yamp)

Python module to manage multiprocessing of a queue. Quite similar to _multiprocessing.Pool_ but more to my liking.

I've needed and reproduced a similar functionality twice in a while and a third was coming the way. That's _enough_ to encapsulate it in a module. Perhaps the name could be better.

## TODO:

- [ ] Use python Logging
- [ ] Extend the ending condition
- [ ] Improve the input: no need to be build before, but can be generated while needed.
- [ ] Control memory usage (psutil)
- [ ] Control machine load (psutil)
- [ ] Hooks. At least, after the worker target execution allow to execute something, but with in a Lock because is a place to report results in a file (for example).