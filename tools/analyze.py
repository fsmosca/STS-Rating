"""Analyze position with engine.

Save the analysis to csv file.

Requirements:
  pip install chess
  pip install pandas

Example:
  python analyze.py --epd "1kr5/3n4/q3p2p/p2n2p1/PppB1P2/5BP1/1P2Q2P/3R2K1 w - -" --engine "sf15.exe" --hash-mb 512 --threads 1 --depth 24 --output index_1_d24_ferdy_sf15.csv
"""


__version__ = '0.1'


import argparse
import chess.engine
import pandas as pd
import logging


def analyze(enginefn, epd, depth, hashmb, threads, multipv, output):
    engine = chess.engine.SimpleEngine.popen_uci(enginefn)
    engine.configure({'Hash': hashmb})
    engine.configure({'Threads': threads})
    engine_name = engine.id['name']

    limit = chess.engine.Limit(depth=depth)
    board = chess.Board(epd)

    engine_info = engine.analyse(board, limit=limit, multipv=multipv)

    data = []

    # Read engine info.
    for i in range(min(multipv, board.legal_moves.count())):
        m = engine_info[i]['pv'][0]
        s = engine_info[i]['score'].relative.score(mate_score=32000)
        d = engine_info[i]['depth']

        p = engine_info[i]['pv'][0:7]
        p1 = [a.uci() for a in p]
        p2 = ' '.join(p1)

        data.append([epd, m.uci(), s, d, p2, engine_name])

    engine.quit()

    df = pd.DataFrame(data)
    df.columns = ['epd', 'move', 'eval', 'depth', 'pv', 'engine']
    df.to_csv(output, index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epd', required=True, type=str,
                        help='The position in epd format that will be analyzed, e.g --epd "1kr5/3n4/q3p2p/p2n2p1/PppB1P2/5BP1/1P2Q2P/3R2K1 w - -" (required).')
    parser.add_argument('--engine', required=True, type=str,
                        help='The engine file (required).')
    parser.add_argument('--hash-mb', required=False, type=int, default=128,
                        help='The engine hash size in mb (not required, default=128).')
    parser.add_argument('--threads', required=False, type=int, default=1,
                        help='The engine number of threads to use (not required, default=1).')
    parser.add_argument('--depth', required=False, type=int, default=20,
                        help='The analysis depth (not required, default=20).')
    parser.add_argument('--multipv', required=False, type=int, default=10,
                        help='The multipv value the engine will be run (not required, default=10).')
    parser.add_argument('--output', required=True, type=str,
                        help='The output filename of csv file, e.g. --output index_1_d20_sf15.csv (required).')
    parser.add_argument('--log', action='store_true',
                        help='A flag to enable logging. Log file log.txt will be created in overwrite mode.')
    parser.add_argument('-v', '--version', action='version', version=f'{__version__}')

    args = parser.parse_args()

    if args.log:
        logging.basicConfig(level=logging.DEBUG, filename='log.txt', filemode='w')

    analyze(args.engine, args.epd, args.depth, args.hash_mb, args.threads, args.multipv, args.output)


if __name__ == '__main__':
    main()
