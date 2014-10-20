easyrel
=====

easyrel searches newznab providers on the command line.

* silent mode automatically picks first match
* send directly to SABnzbd without downloading the nzb
* batch download new relaseses from your xREL favorite lists
* block specific lists from searching, thus downloading
* can now mark grabbed releases as read on xREL

## dependencies:
* Python 2
* [feedparser][feedparser]

## usage:
* getrel.py -q "Search.query" (search for one specific release)
or
* getfav.py (search for all new releases in your fav lists)

## notes:
* config is created on first run - requires editing
* Location: .config/getrel/

[feedparser]: https://pypi.python.org/pypi/feedparser/
