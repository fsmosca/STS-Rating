:: This batch file is used when --epd-file is defined. The positions to be analyzed are
:: in the epd file.

:: The file epd_index.json should be located in the same location with analyze.py.
:: The index will be taken from this file from the given epd.

:: Use analyze.py version >= 0.5
:: python analyze.py --version

:: If --log-file is defined, it will be in append mode.

set engine="F:/Chess/Engines/stockfish/stockfish_15/stockfish_15_modern.exe"
set hash=512
set threads=4
set depth=40

set username=ferdy
set epd_file=sample.epd

python analyze.py --epd-file %epd_file% ^
--username %username% ^
--engine %engine% ^
--hash-mb %hash% ^
--threads %threads% ^
--depth %depth% ^
--log-file log.txt
