-- Test if negative integers can be decoded.
-- Bug (with fix) reported by xopxe on 2012-11-26, fixed in r27:b48fe9ee9f8e

local b = require 'bencode'

return b.decode"i-1e" == nil and 1 or 0, 1
