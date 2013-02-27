#!/usr/bin/env lua
-- This is a rather stupid CGI bittorrent tracker.
-- It requires cgilua for URL-decoding and gdbm as "database" backend.
-- 
-- See also: http://wiki.theory.org/BitTorrent_Tracker_Protocol
--
---- Configuration: ------------------------------------------------------------
-- gdbm database file. /tmp may or may not be a good choice.
local DATABASE = "/tmp/tracker.db"

-- advise the client to wait this many seconds between announces
local INTERVAL = 60

-- entries which have not been updated since 8 minutes are ignored.
local OUTDATED = 8 * 60
--------------------------------------------------------------------------------

local gdbm  = require "gdbm"
local url   = require "cgilua.urlcode"
local b     = require "bencode"
local ok, p = pcall(require, "posix")
local nanslp

if not ok then
	-- yuck, but I don't want to depend on luaposix
	-- this works on at least FreeBSD and Linux
	-- as an unfortunate side-effect, it can't be interrupted with ^C
	nanslp = function(sec, nsec)
		local nsec = nsec or 0
		os.execute(("sleep %d.%09d"):format(sec, nsec))
	end
else
	nanslp = p.nanosleep
end

local function http_ok(data) -- XXX correct MIME type?
	io.write("Content-Type: application/x-bittorrent\r\n\r\n")
	io.write(data)
end

local function http_err(code, meaning)
	http_ok(b.encode { 
		["failure reason"] = meaning,
		["failure code"]   = code
	})
	os.exit()
end

local function parse_and_check(query)
	local query = {}
	url.parsequery(os.getenv("QUERY_STRING"), query)

	if os.getenv("REQUEST_METHOD") ~= "GET" then
		http_err(100, "Invalid Request")

	elseif not query.info_hash then
		http_err(101, "Missing info_hash")

	elseif not query.peer_id then
		http_err(102, "Missing peer_id")

	elseif not query.port then
		http_err(103, "Missing port")

	elseif not #query.info_hash == 20 then
		http_err(150, "Invalid info_hash")

	elseif not #query.peer_id   == 20 then
		http_err(151, "Invalid peer_id")
	
	elseif query.event 
	   and not (query.event == "started"
		or  query.event == "stopped" 
		or  query.event == "completed")
	then
		http_err(900, "Unknown event")
	end

	-- XXX: Ignore numwant and more fancy features for now, this tracker
	--      is meant to be kept really simple

	return query.info_hash, query.peer_id, query.port, query.event
end

local function obtain_write_lock(fname)
	local db = gdbm.open(fname, "c")
	while not db do -- sleep and retry
		nanslp(0,10e8) -- XXX: 1/100 sec, good enough?
		db = gdbm.open(fname, "w")
	end
	return db
end

local rq_ip = os.getenv("REMOTE_ADDR")
local rq_time = os.time()

--[[ 

   Database format:
   +--------+-----------+-------------------------------------------------------
   | prefix | suffix    | content
   +--------+-----------+-------------------------------------------------------
   |      A | peer id   | peer IP address
   |      P | peer id   | peer port
   |      U | peer id   | peer's last update time
   |      i | info hash | list of peer IDs on this info hash (space separated)
   |      u | info hash | last time the info hash was updated
   +--------+-----------+-------------------------------------------------------

   TODO: - write a script that prunes old entries from the database and runs as
           a cronjob

]]

-- using a different database backend is a matter of changing these functions
local function get_peer(id)
	return db['A'..id], db['P'..id], db['U'..id]
end
local function set_peer(id, addr, port)
	db['A'..id] = addr
	db['P'..id] = port
	db['U'..id] = rq_time
end

local function set_peers(id, new)
	db['i'..id] = new
	db['u'..id] = rq_time
end

local function add_peer(id, peer)
	set_peers(id, db['i'..id] .. " " .. peer)
end

local function get_peers(ih)
	return db['i'..ih]
end

local db = obtain_write_lock(DATABASE) -- yay for no concurrency

local info_hash, peer_id, peer_port, ev = parse_and_check(query)
local peers_ent = get_peers(info_hash)
local peers = {}

if peers_ent then
	local found = false
	for peer in peers_ent:gmatch("[^ ]+") do
		if peer == peer_id then
			found = true
		else
			table.insert(peers, peer)
		end
	end
	if ev == "stopped" then
		local peers = table.concat(peers, " ")
		if #peers == 0 then
			peers = nil
		end
		set_peers(info_hash, peers)
		set_peer(peer_id, nil, nil)
		http_err(900, "Goodbye") -- XXX correct?
	end
	-- XXX actually handle "started" and "completed"?
	if not found then -- new peer, add to info hash
		add_peer(info_hash, peer_id)
	end
else -- new info hash
	set_peers(info_hash, peer_id)
end

set_peer(peer_id, rq_ip, peer_port)

local peertbl = {}
for _,id in ipairs(peers) do
	local ip, port, upd = get_peer(id)
	if tonumber(upd) + OUTDATED < rq_time then
		table.insert(peertbl, {
			id   = id,
			ip   = ip,
			port = tonumber(port)
		})
	end
end

-- FIXME returns ALL the peers.
http_ok(b.encode {
	interval = INTERVAL,
	peers = peertbl 
})

db:close()
