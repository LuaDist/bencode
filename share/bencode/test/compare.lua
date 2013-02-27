-- Read, parse and dump a torrent into a string;
-- Ensure that the string is identical to what was originally read. 
-- If not, either the file was broken (e.g. unsorted keys) or there is a bug.

local b = require 'bencode'

local numfail, total = 0,0

for _,v in ipairs(arg) do
	local fd, t1, t2
	fd = io.open(v)
	t1 = fd:read("*a")
	fd:close()
	t2 = b.encode(b.decode(t1))
	if t1 ~= t2 then
		print(v, "FAIL")
		numfail = numfail + 1
	else
		print(v, "OK")
	end
	total = total + 1
end
return numfail, total
