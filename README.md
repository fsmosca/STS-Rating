# STS-Rating
A method to rate chess engines using STS test suite.

Sample [test results](https://github.com/fsmosca/STS-Rating/wiki) are in the wiki.

## Setup

* Install Python version >= 3.7

## Command line
```
python sts_rating.py -f "STS1-STS15_LAN_v3.epd" -e Stockfish.exe -t 1 -h 128
```

## Files
* STS1-STS15_LAN_v3.epd  
sts 1 to 15 positions with original points.

* STS1-STS15_LAN_v4.epd  
sts 1 to 15 positions with new points based from stockfish 15 analysis. This file in the epd folder. It is analyzed by Stockfish 15 at 60s per position with multipv 10. Stockfish 15 is run on a single core using cpu i7-2600K, 3.4 Ghz. The test suite has now a top 10 best moves to test the engines or even humans.

* STS1-STS15_LAN_v5.epd  
This is similar to `STS1-STS15_LAN_v4.epd` except the max point in each position is 100.

## Notes
* The program `--getrating` flag is only applicable for the `STS1-STS15_LAN_v3.epd` test.

## Credits
* Dann Corbit and Swaminathan  
https://sites.google.com/site/strategictestsuite/about-1
