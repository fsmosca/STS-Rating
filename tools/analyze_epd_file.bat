:: This batch file is used when --epd-file is defined. The positions to be analyzed are
:: in the epd file.

:: The file epd_index.json should be located in the same location with analyze.py.
:: The index will be taken from this file from the given epd.

:: Use analyze.py version >= 0.5
:: python analyze.py --version

:: If --log-file is defined, it will be in append mode.

set engine="F:/Chess/Engines/stockfish/stockfish_15/stockfish_15_modern.exe"
set hash=256
set threads=1
set depth=36

set username=ferdy
set epd_file=sample.epd

:: The out filename is ignored in this case. But it should be defined.
:: The output csv filename will be auto-generated based on the epd index, username and depth.
set out=temp.csv

:: Important, use --username your_username, because the output csv file will be auto-generated
:: and username value will be part of the filename.
:: Example csv output, index_167_d36_ferdy.csv

python analyze.py --epd-file %epd_file% ^
--username %username% ^
--engine %engine% ^
--hash-mb %hash% ^
--threads %threads% ^
--depth %depth% ^
--output %out% ^
--log-file log.txt
