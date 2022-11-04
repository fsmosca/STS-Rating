@echo off
rem This batch file is used when --epd-file is defined.
rem The positions to be analyzed are in the epd file.

rem The csv analysis output will be saved automatically with filename:
rem index_[index_number]_d[depth]_[username].csv

rem The file epd_index.json should be located in the same location
rem with analyze.py. The index number will be taken from this file
rem based fom the given epd.

rem Use analyze.py version >= 0.7

rem If --log-file is defined, it will be in append mode.

rem If --move-time-sec is defined, the search will be terminated
rem based on depth and move time. If the depth is reached first
rem and there is still time left, then the search will continue
rem until move time is spent. If the depth is not yet reached but
rem there is no more time left, then the search info will be
rem saved and search will be terminated.

set engine="F:/Chess/Engines/stockfish/stockfish_15/stockfish_15_modern.exe"
set hash=512
set threads=4
set depth=40
set movetimesec=1800

set username=ferdy_sf15
set epd_file=sample.epd

python analyze.py --epd-file %epd_file% ^
--username %username% ^
--move-time-sec %movetimesec% ^
--engine %engine% ^
--hash-mb %hash% ^
--threads %threads% ^
--depth %depth% ^
--log-file log.txt
