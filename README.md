# Coroutine Scheduler

Coroutine scheduler for low-power microcontroller applications. Developed on a [Particle mesh device](https://www.particle.io/mesh) using the [IoTPython](https://github.com/bboser/iotpython) fork of [CircuitPython](https://github.com/adafruit/circuitpython).

API tries to follow [curio](https://curio.readthedocs.io), although many features are missing (e.g. no threads or processes). Andre Caron's [repo](https://github.com/AndreLouisCaron/a-tale-of-event-loops) is helpful for understanding the design of event-loops.

## Documentation

Install Jupyter notebooks and the [Adafruit CircuitPython kernel](https://github.com/adafruit/circuitpython_kernel) to use.

* [Jupyter notebook](doc/circuitpython_kernel.ipynb) for CircuitPython, setup and features [pdf](doc/circuitpython_kernel.pdf)
* [Eventio Tour](doc/eventio_tour.ipynb). Demonstrates running multiple coroutines simultaneously; processor automatically powers down when there is no work. [pdf](doc/eventio_tour.pdf)
* [Eventio Tutorial](doc/eventio_tutorial.ipynb). Eventually.
* [Timer](doc/timer.ipynb). Timer and Chronometer classes.
* [A tale of eventloops](doc/tale_of_event_loops.ipynb)
