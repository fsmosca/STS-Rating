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
sts 1 to 15 positions with new points based from stockfish 15 analysis. The top moves are now up to 10. This file in the epd folder.

## Credits
* Dann Corbit and Swaminathan  
https://sites.google.com/site/strategictestsuite/about-1
