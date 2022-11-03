:: This batch file is used when analyzing a single epd.


set engine="F:/Chess/Engines/stockfish/stockfish_15/stockfish_15_modern.exe"
set hash=512
set threads=4
set depth=44

set username=ferdy
set ename=sf15

set epd="6r1/4bbk1/p3p1p1/Pp1pPp2/3P1P2/2P2B2/3B2K1/1R6 b - -"

python analyze.py --epd %epd% ^
--username %username% ^
--engine %engine% ^
--hash-mb %hash% ^
--threads %threads% ^
--depth %depth% ^
--log-file "log_%depth%_%username%_%ename%.txt"
