clnns
=====

clnns searches newznab providers on the command line.

* configurable for multiple newznab hosts.
* 'send to SABnzbd+' functionality.
* pronounced 'coolness'.

## dependencies:
* Python 2
* [feedparser][feedparser]

## usage:
* getrel.py -q "Search.query" (search for one specific release)
or
* getfav.py (search for all new releases in your fav lists)

## notes:
* currently *nix only - but compatible with Windows too if you fix the config path.
* config is created on first run - requires editing.
* Location: .config/getrel/

[feedparser]: https://pypi.python.org/pypi/feedparser/
