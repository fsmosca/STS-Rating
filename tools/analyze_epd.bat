:: This batch file is used when analyzing a single epd.


set engine="F:/Chess/Engines/stockfish/stockfish_15/stockfish_15_modern.exe"
set hash=256
set threads=1
set depth=36

set username=ferdy
set ename=sf15

:: The i or index number from google sheet sts_positions, depends on the epd value
:: If you change the epd, also change the index.
set i=170
set epd="8/3q1pk1/3p4/2pB2p1/P2n4/1P4BP/6P1/4R1K1 b - -"

set out=index_%i%_d%depth%_%username%_%ename%.csv

python analyze.py --epd %epd% ^
--engine %engine% ^
--hash-mb %hash% ^
--threads %threads% ^
--depth %depth% ^
--output %out% ^
--log-file "log_index_%i%_d%depth%_%username%.txt"
