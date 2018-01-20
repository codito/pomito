pomito
======

|Build Status| |Windows Build status| |Coverage Status| |Code Health|

Simple pomodoro timer with support for tasks and hooks.

Currently under development, you can try out an alpha build `here`_.
Something works, something doesn’t :(

Please file issues at https://github.com/codito/pomito/issues.

Patches are most welcome! :up:

Screenshots
===========

Default state
-------------

.. figure:: https://raw.github.com/codito/pomito/master/docs/images/default.png
   :alt: Default

   Default

Timer running!
--------------

.. figure:: https://raw.github.com/codito/pomito/master/docs/images/timer.png
   :alt: Timer

   Timer

Interruption running!
---------------------

.. figure:: https://raw.github.com/codito/pomito/master/docs/images/interruption.png
   :alt: Interruption

   Interruption

Installation
============

Unzip the acrhive to a temp directory, say ``g:\apps\pomito``.

Configuration
=============

Copy ``docs\sample_config.ini`` to ``~\pomito\config.ini`` in windows.
Copy ``docs\sample_todo.txt`` to ``~\pomito\todo.txt`` and modify
``config.ini`` accordingly.

Run Forrest, Run
================

Start ``pomito.exe`` from unzipped directory. E.g.
``g:\apps\pomito\pomito.exe``.

Credits
=======

-  icons from glyphicons.com

.. _here: https://github.com/codito/pomito/releases/tag/v0.1-alpha

.. |Build Status| image:: https://img.shields.io/travis/codito/pomito.svg
   :target: https://travis-ci.org/codito/pomito
.. |Windows Build status| image:: https://img.shields.io/appveyor/ci/codito/pomito.svg
   :target: https://ci.appveyor.com/project/codito/pomito
.. |Coverage Status| image:: https://img.shields.io/coveralls/github/codito/pomito.svg
   :target: https://coveralls.io/r/codito/pomito?branch=master
.. |Code Health| image:: https://landscape.io/github/codito/pomito/master/landscape.svg?style=flat
   :target: https://landscape.io/github/codito/pomito/master
