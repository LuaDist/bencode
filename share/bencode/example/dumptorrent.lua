#!/usr/bin/env lua
--[[

  This program can be used to dump all information contained in a torrent file
  to stdout because it's always nice to see what information is in there.

]]--

require 'bencode'

-- Print anything - including nested tables
-- code shamelessly copied from http://lua-users.org/wiki/TableSerialization
function table_print (tt, indent, done)
  done = done or {}
  indent = indent or 0
  if type(tt) == "table" then
    for key, value in pairs (tt) do
      io.write(string.rep (" ", indent)) -- indent it
      if type (value) == "table" and not done [value] then
        done [value] = true
        io.write(string.format("[%s] => table\n", tostring (key)));
        io.write(string.rep (" ", indent+4)) -- indent it
        io.write("(\n");
        table_print (value, indent + 7, done)
        io.write(string.rep (" ", indent+4)) -- indent it
        io.write(")\n");
      else
        io.write(string.format("[%s] => %s\n",
            tostring (key), tostring(value)))
      end
    end
  else
    io.write(tt .. "\n")
  end
end
-- and the table serialisation function really is the largest part of this
-- file, because the bencode lib does all the magic.

if arg and arg[1] then
    torrentfile = arg[1]
else
    print("dumptorrent.lua torrentfile")
    os.exit(1)
end

fd = io.open(torrentfile, "r")
data = fd:read("*a")
fd:close()
tab, err, v = bencode.decode(data)

if not tab then
    io.write(torrentfile .. ": cannot be decoded: " .. err)
    if v then
    	io.write(" (" .. v .. ")")
    end
    io.write("\n")
    os.exit(1)
end

-- tab.info.pieces is binary encoded. You don't want it in your
-- terminal, so I won't show it. This entry needs to be present if your torrent
-- file follows the standard by any means.

if type(tab) == "table" and tab.info and tab.info.pieces then
    tab.info.pieces = "(value optimised out)"
end

table_print(tab)
