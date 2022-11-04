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

### Analyze from a single epd

In the output `index_1_d26_ferdy_sf15.csv`, the index_1 is the position index found in the sts_positions google sheet. That also means the epd we are analyzing has an index number 1.

Since analyze version 0.6, the --output option is no longer used. The program will generate the output filename automatically.

```
python analyze.py --epd "1kr5/3n4/q3p2p/p2n2p1/PppB1P2/5BP1/1P2Q2P/3R2K1 w - -" --engine "stockfish.exe" --hash-mb 256 --threads 1 --depth 26 --username ferdy --log-file index_1_d26_ferdy_sf15.txt
```

See also the sample batch file `analyze_epd.bat`.

### Analyze positions in the epd file

Be sure to have `epd_index.json` file located in the same folder with analyze.py. The epd's in sample.epd must be in `epd_index.json'. The purpose of this file
is to get the index number given the epd. This index number is found in google sheet sts_positions.

The output csv file will be auto-generated. Notice there is --username option. The output csv file will be auto-generated based from the index, depth and username.

```
python analyze.py --epd-file sample.epd --username ferdy --engine "stockfish.exe" --hash-mb 256 --threads 1 --depth 26 --log-file log.txt
```

See also the sample batch file `analyze_epd_file.bat`.

### Use depth and move time to control the search

This feature is only available from version 0.7.

`python analyze.py --version`

```
--depth 40 --move-time-sec 600
```

* If the depth is reached but there is still time, the search will continue. The output may have more than 40 analysis depth. If the position has a fast search depth/time ratio, this feature will give us confidence that the analysis is fine because the search is terminated by time.
* If depth is not yet reached and there is no more time left, the search will be terminated. This will save resources especially those positions that have a slow search depth/time ratio. Although the target depth is not satisfied, we can be confident that the analysis result is still reliable because the position is evaluated for 600 sec or 10 minutes.

## Help
Send the command help to see the program options, etc.

```
python analyze.py --help
```
