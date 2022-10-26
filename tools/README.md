# Analyze
A program to analyze the given epd with the uci engine.


## Setup

* Install Python version >= 3.7
* Install pandas  
  pip install pandas
* Install python chess  
  pip install chess

## Command line

In the output `index_1_d26_ferdy_sf15.csv`, the index_1 is the position index found in the sts_positions google sheet.

Sheet and csv folder link: https://drive.google.com/drive/folders/1XbIND2VVbmhWbKY6bL17jdbTuSwMbmFT

```
python analyze.py --epd "1kr5/3n4/q3p2p/p2n2p1/PppB1P2/5BP1/1P2Q2P/3R2K1 w - -" --engine "stockfish.exe" --hash-mb 256 --threads 1 --depth 26 --output "index_1_d26_ferdy_sf15.csv" --log
```

## Help
Send the command help to see the program options, etc.

```
python analyze.py --help
```
