json socket utility
===================

This is a simple python utility for sending json data when using sockets.

It allows sending lists, dictionaries, strings, etc. It can handle very large data (It has been tested with 10GB of data). Any JSON-serializable data is accepted.

these two functions don't require re-write/over-writing the socket library and are python3 compatible.

get a taste for using sockets here: http://tutorialspoint.com/python/python_networking.htm

an example of working with json data over sockets can be found here: http://github.com/chris-rose-one/battleship

thanks @mdebbar this code has been quite helpful
