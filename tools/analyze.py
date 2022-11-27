"""Analyze position with engine.

Save the analysis to csv file.

Requirements:
  pip install chess
  pip install pandas
"""


__version__ = '0.8.0'


import argparse
import logging
import time
import json
import secrets
import string

import chess.engine
import pandas as pd


ALPHABET = string.ascii_lowercase + string.digits


def get_random_index() -> str:
    """Generates a string as index number.
    """
    return ''.join(secrets.choice(ALPHABET) for _ in range(8))


def set_engine_options(engine, engine_option, hashmb, threads):
    """Sets engine options.
    """
    is_hash_set, is_thread_set = False, False
    if engine_option is not None:
        opt_list = engine_option.split(',')
        for optv in opt_list:
            opt = optv.strip()
            name = opt.split('=')[0].strip()
            value = opt.split('=')[1].strip()

            if name not in engine.options:
                logging.warning('option %s is not supported by the engine', name)
                continue

            engine.configure({name: value})
            logging.debug('%s is set to %s', name, value)

            if name.lower() == 'hash':
                is_hash_set = True
            if name.lower() == 'threads':
                is_thread_set = True

    if not is_hash_set:
        engine.configure({'Hash': hashmb})
    if not is_thread_set:
        engine.configure({'Threads': threads})


def read_epd_index() -> dict:
    """Reads json file and return as a dict.

    analyze.py and epd_index.json should be in same folder.
    """
    with open('epd_index.json', encoding='utf-8') as handle:
        data = json.load(handle)
        return data


def get_epd(epd_file) -> list:
    """Converts epd's in epd file into a list."""
    epds = []
    with open(epd_file, encoding='utf-8') as handle:
        for lines in handle:
            epd_line = lines.rstrip()
            epds.append(epd_line)

    return epds


def get_analysis_data(engine_info, num_moves, epd, engine_name) -> list:
    """Gets engine analysis.
    """
    data = []
    for i in range(num_moves):
        move = engine_info[i]['pv'][0]
        eval_ = engine_info[i]['score'].relative.score(mate_score=32000)
        depth = engine_info[i]['depth']

        pv = engine_info[i]['pv'][0:7]
        pv1 = [a.uci() for a in pv]
        pv2 = ' '.join(pv1)

        if i == 0:
            rdepth = depth

        data.append([epd, move.uci(), eval_, depth, pv2, engine_name])

    return data, rdepth


def analyze(enginefn: str, epd: str, epd_file: str, depth: int,
            hashmb: int, threads: int, multipv: int,
            engine_option: str, username: str, move_time_sec: int):
    """Analyzes the epd or positions in the epd file.

    Position will be analyzed by an engine run at multipv 10. The
    best moves, eval, depth, pv and engine name will be saved in csv file.

    Args:
      enginefn: The engine filename or path/filename.
    """
    engine = chess.engine.SimpleEngine.popen_uci(enginefn)
    engine_name = engine.id['name']
    set_engine_options(engine, engine_option, hashmb, threads)

    epi = read_epd_index()

    if move_time_sec:
        limit = chess.engine.Limit(time=move_time_sec)
    else:
        limit = chess.engine.Limit(depth=depth)

    epds = []
    if epd is not None:
        epds.append(epd)
    else:
        epds = get_epd(epd_file)

    for pos in epds:
        try:
            index_num = epi[pos]
        except KeyError:
            logging.warning('Position %s is not in epd_index.json. Temp index will be used.', pos)
            index_num = get_random_index()

        logging.info('epd: %s, index: %s', pos, str(index_num))
        print(f'epd: {pos}, index: {index_num}')

        board = chess.Board(pos)
        num_moves = min(multipv, board.legal_moves.count())
        adepth = 0  # for csv filename depth info

        time_start = time.perf_counter()

        engine_info = engine.analyse(board, limit=limit, multipv=multipv)
        data, adepth = get_analysis_data(engine_info, num_moves, pos, engine_name)

        time_end = time.perf_counter()
        print(f'elapse (sec): {time_end - time_start:0.1f}')

        df = pd.DataFrame(data)
        df.columns = ['epd', 'move', 'eval', 'depth', 'pv', 'engine']

        # Sort by score and depth
        df = df.sort_values(by=['eval', 'depth'], ascending=[False, False])

        # Build an output filename.
        output = f'index_{index_num}_d{adepth}_{username}.csv'
        df.to_csv(output, index=False)

    engine.quit()


def main():
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('--epd', type=str,
                        help='The position in epd format that will be analyzed, '
                        'e.g --epd "1kr5/3n4/q3p2p/p2n2p1/PppB1P2/5BP1/1P2Q2P/3R2K1 w - -"')
    group.add_argument('--epd-file', type=str,
                        help='The file that contains epd to be analyzed, '
                        'e.g. --epd-file sample.epd')

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
    parser.add_argument(
        '--move-time-sec',
        help='Analysis time in seconds. If this is not specified, the analysis will be '
             'based on the depth. If this is specified, the analysis will be terminated based '
             'on depth and this option. If the depth is reached first and we still have time '
             'then continue the analysis until move time is reached. If depth is not yet reached '
             'and time is already reached, then save and abort the analysis')
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
        logging.basicConfig(
            level=logging.DEBUG,
            filename=args.log_file,
            filemode=fmode,
            format='%(asctime)s : %(levelname)s : %(filename)s: %(message)s')

    move_time_sec = args.move_time_sec
    if move_time_sec is not None:
        move_time_sec = int(move_time_sec)

    analyze(args.engine, args.epd, args.epd_file, args.depth,
            args.hash_mb, args.threads, args.multipv,
            args.engine_option, args.username, move_time_sec)


if __name__ == '__main__':
    main()
