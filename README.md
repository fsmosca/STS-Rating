# STS-Rating
A method to rate chess engines using STS test suite.

Sample [test results](https://github.com/fsmosca/STS-Rating/wiki) are in the wiki.

## Current activity

- [ ] [Analyze the original STS positions](https://github.com/fsmosca/STS-Rating/tree/master/tools) with Stockfish 15. Positions that are no longer useful will be replaced. Positions that are no longer suitable for the theme will be replaced or moved to other themes if applicable. All positions will be analyzed with multipv 10 and as much depth as possible. Analysis in csv files and control sheet are in [google drive](https://drive.google.com/drive/folders/1XbIND2VVbmhWbKY6bL17jdbTuSwMbmFT).

## Setup

* Install Python version >= 3.7

## Command line

#### If the test suite has a max point of 10.

```
python sts_rating.py -f "STS1-STS15_LAN_v3.epd" -e Stockfish.exe -t 1 -h 128

python sts_rating.py -f "./epd/STS1-STS15_LAN_v4.epd" -e Stockfish.exe -t 1 -h 128
```

#### If the test suite has a max point of 100.

```
python sts_rating.py -f "./epd/STS1-STS15_LAN_v5.epd" -e Stockfish.exe -t 1 -h 128 --maxpoint 100
```

## Files

* STS1-STS15_LAN_v3.epd  
sts 1 to 15 positions with original points.

* STS1-STS15_LAN_v4.epd  
sts 1 to 15 positions with new points based from stockfish 15 analysis. This file in the epd folder. It is analyzed by Stockfish 15 at 60s per position with multipv 10. Stockfish 15 is run on a single core using cpu i7-2600K, 3.4 Ghz. The test suite has now a top 10 best moves to test the engines or even humans.

* STS1-STS15_LAN_v5.epd  
This is similar to `STS1-STS15_LAN_v4.epd` except the max point in each position is 100.

* STS1-STS15_LAN_v6.epd  
Similar to `STS1-STS15_LAN_v5.epd,` except only those positions are saved if `top1_score` less `top2_score` is greater than or equal to `10 cp`. This would at least assure us there is only 1 best move in the position. There are now only 1188 positions in the test suite. This was 1500.

## Evaluation/Point mapping

The multipv scores obtained from the position analysis are mapped to [1, 10] points for 'STS1-STS15_LAN_v4.epd', and [1, 100] for 'STS1-STS15_LAN_v5.epd'.

Example:  

The top 10 evaluations in centipawn from the given position:  

```
eval = [300, 150, 80, 50, 10, -10, -50, -150, -250, -251]
```

In the [1, 100] mapping, the point will be:  

```
eval: 300, point: 100
eval: 150, point: 73
eval: 80, point: 60
eval: 50, point: 55
eval: 10, point: 48
eval: -10, point: 44
eval: -50, point: 37
eval: -150, point: 19
eval: -250, point: 1
eval: -251, point: 1
```

Interpolation code.

```python
def interpol(e: int, emin: int, emax: int, pmin: int, pmax: int) -> int:
    """Gets the point from a given evaluation.

    Args:
      e: The eval that we want to convert to a point in the range of say [1, 100]
      emin: The minimum eval, e.g -200 cp
      emax: The maximum eval, e.g. 1000 cp
      pmin: The minimum point, e.g. 1
      pmax: The maximum point, e.g. 100

    Returns:
      The point equivalent of e.
    """
    return ((e - emin) * (pmax - pmin)) / max(emax - emin, 0.001) + pmin
```

Sample conversion:  

```python
# The top 10 scores from engine analysis.
eval = [300, 150, 80, 50, 10, -10, -50, -150, -250, -251]
minpt, maxpt = 1, 100

for e in eval:
    pt = interpol(e, min(eval), max(eval), minpt, maxpt)
    pt_int = int(round(pt, 0))
    print(f'eval: {e}, point: {pt_int}')
```

## Notes
* The program `--getrating` flag is only applicable for the `STS1-STS15_LAN_v3.epd` test.

## Credits
* Dann Corbit and Swaminathan  
https://sites.google.com/site/strategictestsuite/about-1
