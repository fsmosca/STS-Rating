"""Analyze position with engine.

Save the analysis to csv file.

Requirements:
  pip install chess
  pip install pandas

Example:
  python analyze.py --epd "1kr5/3n4/q3p2p/p2n2p1/PppB1P2/5BP1/1P2Q2P/3R2K1 w - -" --engine "sf15.exe" --hash-mb 512 --threads 1 --depth 24 --output index_1_d24_ferdy_sf15.csv
"""


__version__ = '0.4'


import argparse
import chess.engine
import pandas as pd
import logging
import time


def set_engine_options(engine, engine_option, hashmb, threads):
    """Sets engine options.
    """
    is_hash_set, is_thread_set = False, False
    if engine_option is not None:
        opt_list = engine_option.split(',')
        for o in opt_list:
            opt = o.strip()
            name = opt.split('=')[0].strip()
            value = opt.split('=')[1].strip()

            if name not in engine.options:
                logging.warning(f'option {name} is not supported by the engine')
                continue

            engine.configure({name: value})
            logging.debug(f'{name} is set to {value}')
            
            if name.lower() == 'hash':
                is_hash_set = True
            if name.lower() == 'threads':
                is_thread_set = True

    if not is_hash_set:
        engine.configure({'Hash': hashmb})
    if not is_thread_set:
        engine.configure({'Threads': threads})


def analyze(enginefn, epd, depth, hashmb, threads, multipv, output, engine_option):
    engine = chess.engine.SimpleEngine.popen_uci(enginefn)
    engine_name = engine.id['name']
    set_engine_options(engine, engine_option, hashmb, threads)

    limit = chess.engine.Limit(depth=depth)
    board = chess.Board(epd)

    time_start = time.perf_counter()

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
    time_end = time.perf_counter()
    print(f'elapse (sec): {time_end - time_start:0.1f}')

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
    parser.add_argument('--log-file', required=False, type=str, default=None,
                        help='The log filename, e.g. --log-file sf15_log.txt (not required, default=None).')
    parser.add_argument('--engine-option',
                         help='set engine options, e.g. --engine-option "Hash=128,Skill Level=2".')
    parser.add_argument('-v', '--version', action='version', version=f'{__version__}')

    args = parser.parse_args()

    if args.log_file is not None:
        logging.basicConfig(level=logging.DEBUG, filename=args.log_file, filemode='w')

    analyze(args.engine, args.epd, args.depth,
            args.hash_mb, args.threads, args.multipv,
            args.output, args.engine_option)


if __name__ == '__main__':
    main()
