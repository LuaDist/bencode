# Copyright (C) 2007-2012 LuaDist.
# Created by Peter Drahoš, Peter Kapec
# Redistribution and use of this file is allowed according to the terms of the MIT license.
# For details see the COPYRIGHT file distributed with LuaDist.
# Please note that the package source code is licensed under its own license.

project ( bencode NONE )
cmake_minimum_required ( VERSION 2.8 )
include ( cmake/dist.cmake )
include ( lua )

install_lua_module ( bencode bencode.lua )
install_example ( examples/ )
install_test ( tests/ )
install_data ( COPYING RELNOTES README.markdown )