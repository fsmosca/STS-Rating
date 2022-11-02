# Analyze
A program to analyze the given epd with the uci engine.

If you want to contribute analyzing sts positions, send me your gmail so I can give you write access to the google [sts-project](https://drive.google.com/drive/folders/1XbIND2VVbmhWbKY6bL17jdbTuSwMbmFT) folder.


## Setup

* Install Python version >= 3.7
* Install pandas  
  pip install pandas
* Install python chess  
  pip install chess

## Command line

**Analyze from a single epd**  

In the output `index_1_d26_ferdy_sf15.csv`, the index_1 is the position index found in the sts_positions google sheet. That also means the epd we are analyzing has an index number 1.

```
python analyze.py --epd "1kr5/3n4/q3p2p/p2n2p1/PppB1P2/5BP1/1P2Q2P/3R2K1 w - -" --engine "stockfish.exe" --hash-mb 256 --threads 1 --depth 26 --output "index_1_d26_ferdy_sf15.csv" --log-file index_1_d26_ferdy_sf15.txt
```

See also the sample batch file `analyze_epd.bat`.

**Analyze positions in the epd file**  

Be sure to have `epd_index.json` file located in the same folder with analyze.py. The epd's in sample.epd must be in `epd_index.json'. The purpose of this file
is to get the index number given the epd. This index number is found in google sheet sts_positions.

The output csv file will be auto-generated. Notice there is --username option. The output csv file will be auto-generated based from the index, depth and username.

```
python analyze.py --epd-file sample.epd --username ferdy --engine "stockfish.exe" --hash-mb 256 --threads 1 --depth 26 --output tmp.csv --log-file log.txt
```

See also the sample batch file `analyze_epd_file.bat`.

## Help
Send the command help to see the program options, etc.

```
python analyze.py --help
```
