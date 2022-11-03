"""Analyze position with engine.

Save the analysis to csv file.

Requirements:
  pip install chess
  pip install pandas

Example:
  python analyze.py --epd "1kr5/3n4/q3p2p/p2n2p1/PppB1P2/5BP1/1P2Q2P/3R2K1 w - -" --engine "sf15.exe" --hash-mb 512 --threads 1 --depth 24 --output index_1_d24_ferdy_sf15.csv
"""


__version__ = '0.6'


import argparse
import logging
import time
import json
import secrets
import string

import chess.engine
import pandas as pd


alphabet = string.ascii_lowercase + string.digits


def get_random_index():
    return ''.join(secrets.choice(alphabet) for _ in range(8))


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


def read_epd_index():
    """Reads json file and return as a dict.

    analyze.py and epd_index.json should be in same folder.
    """
    with open('epd_index.json') as f:
        data = json.load(f)
        return data


def get_epd(epd_file):
    epds = []
    with open(epd_file) as f:
        for lines in f:
            epd_line = lines.rstrip()
            epds.append(epd_line)

    return epds


def analyze(enginefn, epd, epd_file, depth, hashmb, threads,
            multipv, engine_option, username):
    engine = chess.engine.SimpleEngine.popen_uci(enginefn)
    engine_name = engine.id['name']
    set_engine_options(engine, engine_option, hashmb, threads)

    epi = read_epd_index()

    limit = chess.engine.Limit(depth=depth)

    epds = []
    if epd is not None:
        epds.append(epd)
    else:
        epds = get_epd(epd_file)

    for epd in epds:
        try:
            index_num = epi[epd]
        except KeyError:
            logging.warning(f'Position {epd} is not in epd_index.json. Temp index will be used.')
            index_num = get_random_index()

        logging.info(f'epd: {epd}, index: {index_num}')
        print(f'epd: {epd}, index: {index_num}')

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

        time_end = time.perf_counter()
        print(f'elapse (sec): {time_end - time_start:0.1f}')

        df = pd.DataFrame(data)
        df.columns = ['epd', 'move', 'eval', 'depth', 'pv', 'engine']

        # Build an output filename.
        output = f'index_{index_num}_d{depth}_{username}.csv'
        df.to_csv(output, index=False)

    engine.quit()


def main():
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('--epd', type=str,
                        help='The position in epd format that will be analyzed, '
                        'e.g --epd "1kr5/3n4/q3p2p/p2n2p1/PppB1P2/5BP1/1P2Q2P/3R2K1 w - -"')
    group.add_argument('--epd-file', type=str,
                        help='The file that contains epd to be analyzed, e.g. --epd-file sample.epd')

    parser.add_argument('--username', required=True, type=str,
                        help='username to be used in the output filename, (required).')
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
    parser.add_argument('--log-file', required=False, type=str,
                        help='The log filename, (not required) e.g. --log-file sf15_log.txt. '
                        'Write mode is append if --epd-file is defined otherwise overwrite.')
    parser.add_argument('--engine-option',
                         help='set engine options, e.g. --engine-option "Hash=128,Skill Level=2".')
    parser.add_argument('-v', '--version', action='version', version=f'{__version__}')

    args = parser.parse_args()

    if args.log_file is not None:
        fmode = 'a' if args.epd_file is not None else 'w'
        logging.basicConfig(level=logging.DEBUG, filename=args.log_file, filemode=fmode)

    analyze(args.engine, args.epd, args.epd_file, args.depth,
            args.hash_mb, args.threads, args.multipv,
            args.engine_option, args.username)


if __name__ == '__main__':
    main()
