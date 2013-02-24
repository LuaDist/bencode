Name
====

bencode, lua-bencode or whatever name you call it.


License
=======

The bencode module may be copied under the same terms as Lua.
Please see COPYING for more information.


Installation
============

There are three possible ways install it:

 * your distribution has a package for it (unlikely, unless they like lua)
 * use [luarocks][1] to install it.
 * copy bencode.lua to some place in package.path by hand

What's it all about?
====================

This is a module for the lua programming language for decoding and encoding
bencoded data which can be used to read and write torrent files for bittorrent.
More information on bencoding can be found [here][2].

Authors
=======

 * Kristofer Karlsson, who wrote the decoder, islist and isdictionary
 * Moritz Wilhelmy, who wrote the rest and glued everything together


Project Homepage
================

There is no such thing as a project homepage, you have to live with the
bitbucket page, which is located [here][3].


Bugs
====
bitbucket generously offers [issue tracking][4] to projects hosted by them, so
please use this facility to report any bugs and features you encounter.


Wiki
====
Seriously?

[1]: http://luarocks.org/
[2]: http://wiki.theory.org/BitTorrentSpecification#bencoding
[3]: https://bitbucket.org/wilhelmy/lua-bencode/
[4]: https://bitbucket.org/wilhelmy/lua-bencode/issues
