"""
STS Rating
"""

__version__ = '14.2'


import sys
import getopt
import os
import subprocess
import time, datetime
import timeit


# Constants
UCI = 0
WB = 1
MS_TIME_BUFFER = 20
APP_NAME = 'STS Rating'
APP_NAME_VERSION = APP_NAME + " v" + __version__
STS_ID = ['STS(v1.0)', 'STS(v2.2)', 'STS(v3.0)', 'STS(v4.0)', 'STS(v5.0)',\
          'STS(v6.0)', 'STS(v7.0)', 'STS(v8.0)', 'STS(v9.0)', 'STS(v10.0)',\
          'STS(v11.0)', 'STS(v12.0)', 'STS(v13.0)', 'STS(v14.0)', 'STS(v15.0)']
STS_TITLE = ['Undermining',
             'Open Files and Diagonals',
             'Knight Outposts',
             'Square Vacancy',
             'Bishop vs Knight',
             'Re-Capturing',
             'Offer of Simplification',
             'Advancement of f/g/h Pawns',
             'Advancement of a/b/c Pawns',
             'Simplification',
             'Activity of the King',
             'Center Control',
             'Pawn Play in the Center',
             'Queens and Rooks to the 7th rank',
             'Avoid Pointless Exchange'
             ]


# Global result file name
resultFN = "STS_Rating.txt"


def delete_file(input_fn):
    """ Delete fn file if it exists """
    if os.path.isfile(input_fn):
        os.remove(input_fn)

    
def ShowPlatform(title):
    """ Show hardware """
    print(title)


def get_score_percent_key(item):
    """ Sort time """
    return item[3]


def count_positions(fname):
    """ Returns number of lines in a file """
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def usage():
   print('Usage:')
   print('program -f <epdfile> -e <engname> -t <numthreads> --movetime <timeinms>')
   print("\nOptions:")
   print("-f or --file <string value>, for epd file input")
   print("-e or --engine <string value>, name of engine")
   print("-h or --hash <integer value>, hash size in MB, default is 32 MB")
   print("-t or --threads <integer value>, for threads, Cores and Max CPUs setting")
   print("--movetime <integer value>, time in ms, default is 1000ms")
   print("--log, save engine log")
   print("--getrating, calculate CCRL 40/4 rating estimate for uci engines only")
   print("--mps <integer value>, moves per session for winboard engines")
   print("--tc <integer value in minutes or mm:ss>, timce control for winboard engines")
   print("--st <integer or float value>, for winboard engines and")
   print("  search time in seconds, can be 1.2 or 1")
   print("--proto <string, uci or wb>, protocol the engine supports")
   print("--san, will read engine move in SAN format, only for WB engines")
   print("--contempt, for uci engines that supports such option")
   print("--maxpoint, the max point in the position, default is 10")
   
   print("\nExample:")
   print('Ex1. Analyze test.epd with 2 threads and 128 MB hash, at 3s/pos using sf 6.exe')
   print('STS_Rating -f test.epd -e "sf 6.exe" -h 128 -t 2 --movetime 3000\n')

   print('Ex2. Analyze all sts.epd to get CCRL 40/4 rating estimate of engine sf6.exe')
   print('STS_Rating -f "all sts.epd" -e sf6.exe -h 128 --getrating\n')


def analyze_pos(inFile, engineName, hashv, threadsv, stime, debug, numberOfPositions,
                bCalculateRating, nRatingAnaTime, proto, sWBtc, nWBmps, nSt, optionSan,
                contemptOption, maxPoints):
    """ Analyze positions """

    # nSt is an integer by default
    
    # Proto 0 for uci, 1 for winboard
    if bCalculateRating:
        if proto:
            stime = nRatingAnaTime
        else:
            stime = nRatingAnaTime
        threadsv = 1
        
    newEng = engineName[0:-4]
    logfn = newEng + "_stslog.txt"
    logNotSolved = newEng + "_notSolved.epd"

    # simplify time if this is wb
    minutePart = 0
    secondPart = 0
    incPart = 0
    
    if proto:
        if sWBtc != 'None':
            if ":" in sWBtc:
                bt = sWBtc.split(':')
                minPart = bt[0]
                minutePart = int(minPart)

                secPart = bt[1]
                secondPart = int(secPart)
            else:
                minutePart = int(sWBtc)
            

    # Delete these file because the mode is overwrite
    if debug:
        delete_file(logfn)
        delete_file(logNotSolved)
        logfnFO = open(logfn, 'w')
    
    # Run engine
    p = subprocess.Popen(engineName, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True, bufsize=1)
    print("Starting engine " + engineName + " ...")

    if debug:
        logfnFO.write("Starting engine " + engineName + " ...\n")  

    waitTime = 30
    if proto == WB:
        if debug:
            print('Set wait time to %ds' % waitTime)
            logfnFO.write('Set wait time to %ds\n' % waitTime)
        p.stdin.write("xboard\n")
    else:
        p.stdin.write("uci\n")
        
    if debug:
        if proto == WB:
            print('>> xboard')
            logfnFO.write(">> xboard\n")
        else:
            # print '>> uci'
            logfnFO.write(">> uci\n")
            
    ENG_ID_NAME = "engine name"

    # Parse winboard engine output
    if proto == WB:
        bSupportSetboard = False
        wbt1 = time.perf_counter()
        ENG_ID_NAME = engineName[:-4]
        ENG_ID_NAME = ENG_ID_NAME.strip()
        
        p.stdin.write("protover 2\n")
        if debug:
            print('>> protover 2')
            logfnFO.write(">> protover 2\n")

        # Parse engine output        
        for eline in iter(p.stdout.readline, ''):
            eline = eline.strip()
            
            # Print in console
            if debug:
                print('<< %s' % eline)
            
            if debug:
                logfnFO.write("<< " + eline + "\n")
            if "done=0" in eline:
                print('Receive done=0')
                waitTime = waitTime*3
                print('Increase wait time to %ds' % waitTime)             
                if debug:
                    logfnFO.write("Received done=0\n")
                    logfnFO.write('Increase wait time to %ds\n' % waitTime)
            if "setboard=1" in eline:
                bSupportSetboard = True
                if debug:
                    print('Received setboard=1')
                    logfnFO.write("Received setboard=1\n")
            if "done=1" in eline:
                if debug:
                    print('Received done=1')
                    print('Stop parsing engine init output')
                    logfnFO.write('Received done=1\n')
                    logfnFO.write('Stop parsing engine init output\n')
                break             
            # Check if we exceed wait time
            wbt2 = time.perf_counter()
            tdiff = (wbt2 - wbt1)
            if tdiff > waitTime:             
                if debug:
                    print('Did not received done=1 after %ds' % waitTime)
                    print('Stop parsing engine init output')
                    with open(logfn, 'a') as f:
                        f.write('Did not received done=1 after %ds\n' % waitTime)
                        f.write('Stop parsing engine init output\n')
                break

        # Exit if winboard engine does not support setboard command
        if not bSupportSetboard:
            p.stdin.write("quit\n")
            p.stdin.close()
            p.communicate()

            if debug:
                with open(logfn, 'a') as f:
                    f.write("setboard command is not supported\n")
                    f.write("quit engine\n")

            print('setboard command is not supported')
            print('quit the engine')
            return

        p.stdin.write("post\n")
        p.stdin.write("new\n")
        p.stdin.write("hard\n")
        p.stdin.write("easy\n")   
        if debug:
            with open(logfn, 'a') as f:
                f.write(">> post\n")
                f.write(">> new\n")
                f.write(">> hard\n")
                f.write(">> easy\n")        

    else: # Uci
        for eline in iter(p.stdout.readline, ''):
            eline = eline.strip()
            if debug:
                # print '<< %s' % eline
                logfnFO.write("<< " + eline + "\n")

            if "id name" in eline:
                ENG_ID_NAME = eline.strip()
                ENG_ID_NAME = ENG_ID_NAME.split(' ')
                ENG_ID_NAME = ' '.join(ENG_ID_NAME[2:])
                ENG_ID_NAME = ENG_ID_NAME.strip()
                print("id name: %s\n\n" %(ENG_ID_NAME))
            if "uciok" in eline:
                break

        # Validate hash value
        if hashv < 1:
            hashv = 16
        elif hashv > 16000:
            hashv = 16000
        p.stdin.write("setoption name Hash value " + str(hashv) + "\n")
        if debug:
            logfnFO.write(">> setoption name Hash value " + str(hashv) + "\n")

        p.stdin.write("setoption name Contempt value " + str(contemptOption) + "\n")
        if debug:
            logfnFO.write(">> setoption name Contempt value " + str(contemptOption) + "\n")

        # Validate num threads
        if threadsv < 1:
            threadsv = 1
        elif threadsv > 16:
            threadsv = 16

        # Set threads, cores and max cpus
        p.stdin.write("setoption name Threads value " + str(threadsv) + "\n")
        if debug:
            logfnFO.write(">> setoption name Threads value " + str(threadsv) + "\n")

        p.stdin.write("setoption name Cores value " + str(threadsv) + "\n")
        if debug:
            logfnFO.write(">> setoption name Cores value " + str(threadsv) + "\n")

        p.stdin.write("setoption name Max CPUs value " + str(threadsv) + "\n")
        if debug:
            logfnFO.write(">> setoption name Max CPUs value " + str(threadsv) + "\n")
            logfnFO.write("\n")

    ResultData = []

    timeStart = time.perf_counter()

    for idItem in STS_ID:
        pos_num = 0
        score = 0
        bmCnt = 0
    
        with open(inFile, "r") as inFO:
            
            # 1b1r4/3rkp2/p3p2p/4q3/P5P1/2RBP3/P1Q4P/1R3K2 b - - bm Ba7;\
            # c0 "Ba7=10, Qf6+=3, a5=3, h5=5";\
            # id "STS(v2.2) Open Files and Diagonals.001";\
            # c7 "Ba7 Qf6+ a5 h5";
            # c8 "10 3 3 5";\
            # c9 "b8a7 e5f6 a6a5 h6h5";            
            
            for line in inFO:

                scoreList = []
                mvList = []
                
                etime = 0
                escore = -32767
                emate = 1000
                esdepth = 0
                emdepth = 0
                fifty = 0
                move_num = 1
                
                pos = line.strip()

                idt = pos.split(' ')
                i = idt.index("id")
                idv = idt[i+1]
                idv = idv.strip()
                idv = idv[1:]
                idv = idv.strip()

                if idItem != idv:
                    continue
     
                pos_num += 1
                
                a = pos.split(" ")
                fen = " ".join(a[0:4])

                fen = fen + " " + str(fifty) + " " + str(move_num)

                # Show console progress
                print('Id: %s, Position: %d \r' %(idItem, pos_num)),

                # Get score in c8
                if "c8" in pos:
                    a = pos.split(' ')
                    i = a.index("c8")
                    c8Val = ""
                    c8Val = ' '.join(a[i+1:])                    
                    c8Val = c8Val.split(';')
                    c8Val = c8Val[0]                  
                    c8Val = c8Val[1:-1]  # Remove head " and tail "
                    c8Val = c8Val.strip()
                    i = c8Val.split(' ')                   
                    for item in i:
                        val = item.strip()
                        scoreList.append(int(val))
                    
                # Save the epd moves, can be san or lan
                if optionSan:
                    if "c7" in pos:
                        a = pos.split(' ')
                        i = a.index("c7")
                        c7Val = ""
                        c7Val = ' '.join(a[i+1:])
                        c7Val = c7Val.split(';')
                        c7Val = c7Val[0]                    
                        c7Val = c7Val[1:-1]  # Remove head " and tail "
                        c7Val = c7Val.strip()                        
                        i = c7Val.split(' ')
                        for item in i:
                            mv = item.strip()
                            mvList.append(mv)                    
                else:
                    if "c9" in pos:
                        a = pos.split(' ')
                        i = a.index("c9")
                        c9Val = ""
                        c9Val = ' '.join(a[i+1:])
                        c9Val = c9Val[1:-2]  # Remove head " and tails " and ;
                        c9Val = c9Val.strip()                   
                        i = c9Val.split(' ')
                        for item in i:
                            mv = item.strip()
                            mvList.append(mv)                    

                # Log
                if debug:
                    logfnFO.write("Pos %d\n" %(pos_num))
                    logfnFO.write("%s\n\n" %(pos))

                assert(emate == 1000)
                assert(escore == -32767)
                
                # Send commands
                if proto:
                    p.stdin.write("new\n")                    
                    p.stdin.write("setboard " + fen + "\n")
                    if debug:
                        logfnFO.write("%s >> new\n" %(datetime.datetime.now().isoformat()))
                        logfnFO.write("%s >> setboard %s\n" %(datetime.datetime.now().isoformat(), fen))

                    if nSt:
                        if isinstance(nSt, int):
                            p.stdin.write("st %d\n" %(nSt))
                        else:
                            p.stdin.write("st %0.1f\n" %(float(nSt)))                            
                    else:
                        nInc = 0
                        nTime = 0
                        if secondPart == 0:
                            p.stdin.write("level %d %d %d\n" %(nWBmps, minutePart, nInc))
                            nTime = minutePart*60*100  # centisec
                        else:
                            p.stdin.write("level %d %d:%d %d\n" %(nWBmps, minutePart, secondPart, nInc))
                            nTime = ((minutePart*60) + secondPart) * 100  # centisec
                            
                        p.stdin.write("time %d\n" %(nTime))
                    
                    p.stdin.write("go\n")
                    if debug:
                        if nSt:
                            if isinstance(nSt, int):
                                logfnFO.write("%s >> st %d\n" %(datetime.datetime.now().isoformat(), int(nSt)))
                            else:
                                logfnFO.write("%s >> st %0.1f\n" %(datetime.datetime.now().isoformat(), float(nSt)))
                        else:
                            if secondPart == 0:
                                logfnFO.write("%s >> level %d %d %d\n" %(datetime.datetime.now().isoformat(), nWBmps, minutePart, nInc))
                            else:
                                logfnFO.write("%s >> level %d %d:%d %d\n" %(datetime.datetime.now().isoformat(), nWBmps, minutePart, secondPart, nInc))
                            
                            logfnFO.write("%s >> time %d\n" %(datetime.datetime.now().isoformat(), nTime))

                        
                        logfnFO.write("%s >> go\n" %(datetime.datetime.now().isoformat()))
                        
                else:
                    p.stdin.write("isready\n")
                    if debug:
                        logfnFO.write("%s >> isready\n" %(datetime.datetime.now().isoformat()))
                                
                    for rline in iter(p.stdout.readline, ''):
                        rline = rline.strip()
                        if debug:
                            logfnFO.write('%s << %s\n' %(datetime.datetime.now().isoformat(), rline))
                        
                        if "readyok" in rline:
                            break
                        
                    p.stdin.write("ucinewgame\n")
                    if debug:
                        logfnFO.write("%s >> ucinewgame\n" %(datetime.datetime.now().isoformat()))
                        logfnFO.write("%s >> position fen %s\n" %(datetime.datetime.now().isoformat(), fen))

                    p.stdin.write("position fen " + fen + "\n")                    
                    p.stdin.write("go movetime " + str(stime) + "\n")
                    
                    if debug:
                        logfnFO.write("%s >> go movetime %s\n" %(datetime.datetime.now().isoformat(), str(stime)))
                        
                # PARSE ENGINE OUTPUT
                for eline in iter(p.stdout.readline, ''):

                    eline = eline.strip()

                    if proto:
                        if debug:
                            logfnFO.write("%s << %s\n" %(datetime.datetime.now().isoformat(), eline.strip()))
                        if "move" in eline and not "increment" in eline and not "moves_left" in eline\
                                           and not "time" in eline and not "TOURNAMENT" in eline and not "white" in eline\
                                           and not "black" in eline and not "#" in eline:
                            a = eline.strip()
                            a = a.split(" ")
                            bm = a[1]
                            bm = bm.strip()

                            # Compare fen and engine move
                            bmFound = False
                            
                            for i, item in enumerate(mvList):
                                if bm == item:
                                    score += scoreList[i]
                                    if i == 0:
                                        bmCnt += 1
                                        if debug:
                                            logfnFO.write("Engine best move is correct!!\n")
                                            logfnFO.write("Position points earned             : %d\n" %(scoreList[i]))
                                            logfnFO.write("Total points for this theme so far : %d/%d\n\n" %(score, maxPoints*pos_num))
                                    else:
                                        if debug:
                                            logfnFO.write("Engine best move is in alternative moves!\n")
                                            logfnFO.write("Position points earned             : %d\n" %(scoreList[i]))
                                            logfnFO.write("Total points for this theme so far : %d/%d\n\n" %(score, maxPoints*pos_num))
                                    bmFound = True
                                    break

                            if not bmFound:
                                if debug:
                                    with open(logNotSolved, 'a') as wrongEpdFO:
                                        wrongEpdFO.write(pos + "\n")
                                        
                                    logfnFO.write("Engine best move is not one of the solution moves??\n\n")
                                    logfnFO.write("Total points for this theme so far : %d/%d\n\n" %(score, maxPoints*pos_num))
                            
                            break                        
                    else:                    
                        if debug:
                            if "info" in eline or "bestmove" in eline:
                                logfnFO.write("%s << %s\n" %(datetime.datetime.now().isoformat(), eline.strip()))                

                        if "time" in eline and "info" in eline:
                            a = eline.strip()
                            #print('entered time: %s' %(a))
                            a = a.split(" ")
                            i = a.index("time")
                            etime = a[i+1].strip()
                            etime = int(etime)
                            
                        if "score cp" in eline:
                            a = eline.strip().split(" ")
                            i = a.index("cp")
                            escore = a[i+1].strip()
                            escore = int(escore)

                            # Get the depth
                            if "depth" in eline:
                                a = eline.strip().split(" ")
                                i = a.index("depth")
                                esdepth = a[i+1].strip()
                                esdepth = int(esdepth)
                                
                        elif "score mate" in eline:
                            a = eline.strip().split(" ")
                            i = a.index("mate")
                            emate = a[i+1].strip()
                            emate = int(emate)

                            # Get the depth
                            if "depth" in eline:
                                a = eline.strip().split(" ")
                                i = a.index("depth")
                                emdepth = a[i+1].strip()
                                emdepth = int(emdepth)
                                    
                        if "bestmove" in eline:
                            a = eline.strip()
                            a = a.split(" ")
                            bm = a[1]
                            bm = bm.strip()

                            if(esdepth > emdepth):
                                emate = 1000

                            # Compare fen and engine move
                            bmFound = False
                            
                            for i, item in enumerate(mvList):
                                if bm == item:
                                    score += scoreList[i]
                                    if i == 0:
                                        bmCnt += 1
                                        if debug:
                                            logfnFO.write("Engine best move is correct!!\n")
                                            logfnFO.write("Position points earned             : %d\n" %(scoreList[i]))
                                            logfnFO.write("Total points for this theme so far : %d/%d\n\n" %(score, maxPoints*pos_num))
                                    else:
                                        if debug:
                                            logfnFO.write("Engine best move is in alternative moves!\n")
                                            logfnFO.write("Position points earned             : %d\n" %(scoreList[i]))
                                            logfnFO.write("Total points for this theme so far : %d/%d\n\n" %(score, maxPoints*pos_num))
                                    bmFound = True
                                    break

                            if not bmFound:
                                if debug:
                                    with open(logNotSolved, 'a') as wrongEpdFO:
                                        wrongEpdFO.write(pos + "\n")
                                        
                                    logfnFO.write("Engine best move is not one of the solution moves??\n\n")
                                    logfnFO.write("Total points for this theme so far : %d/%d\n\n" %(score, maxPoints*pos_num))
                                    
                            break  # bestmove is found

        # Save the data after given id is done
        if pos_num:
            scorePercent = 100*float(score)/(maxPoints*pos_num)
        else:
            scorePercent = 0.0

        if debug:
            logfnFO.write("Total points for %s: %d/%d\n\n" %(idItem, score, maxPoints*pos_num))

        # Save the data
        ResultData.append([idItem, pos_num, score, scorePercent, bmCnt])
                            

    # Quit the engine
    p.stdin.write("quit\n")
    p.communicate()

    timeEnd = time.perf_counter()

    # Write summary of results
    with open(resultFN, 'a') as resFO:
        totalScore = 0
        totalPos = 0
        r = ResultData
        totalBm = 0

        # ResultData = ([idItem, pos_num, score, scorePercent, bmCnt])
        for item in ResultData:
            totalScore += item[2]
            totalPos += item[1]
            totalBm += item[4]
            
        maxScore = maxPoints*totalPos

        numPositions = count_positions(inFile)

        # Result matrix
        resFO.write('%s v%s\n' %(APP_NAME, __version__))
        resFO.write('Engine: %s\n' %(ENG_ID_NAME))
        if proto == 0:  # UCI
            resFO.write("Hash: %d, Threads: %d, time/pos: %0.3fs\n\n" %(hashv, threadsv, float(stime)/1000))
            resFO.write("Number of positions in %s: %d\n" %(inFile, numPositions))
            resFO.write("Max score = %d x %d = %d\n" %(numPositions, maxPoints, numPositions*maxPoints))
        else:
            if nSt:
                resFO.write("Number of positions in %s: %d\n" %(inFile, numPositions))
                resFO.write("Max score = %d x %d = %d\n" %(numPositions, maxPoints, numPositions*maxPoints))
                resFO.write("Estimated time/pos: %0.3fs\n" %(float(nSt)))
            else:
                resFO.write("Number of positions in %s: %d\n" %(inFile, numPositions))
                resFO.write("Max score = %d x %d = %d\n" %(numPositions, maxPoints, numPositions*maxPoints))
                resFO.write("Estimated time/pos: %0.3fs\n" %(float((minutePart*60) + secondPart)/nWBmps))
        
        seconds = timeEnd - timeStart
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        resFO.write("Test duration: %02dh:%02dm:%02ds\n" % (h, m, s))

        at = 30  # 30ms added time
        if proto:  # WB
            if isinstance(nSt, int):
                pass
            else:
                nSt = float(nSt)
                
            if nSt:
                et = int(totalPos * nSt) + totalPos*at/1000
            else:
                et = totalPos * ((minutePart*60) + secondPart)/nWBmps + totalPos*at/1000
        else:
            et = (totalPos * stime)/1000 + totalPos*at/1000
        m, s = divmod(et, 60)
        h, m = divmod(m, 60)
        resFO.write("Expected time to finish: %02dh:%02dm:%02ds\n" % (h, m, s))
        if proto:  # winboard
            if nSt:
                if isinstance(nSt, int):
                    resFO.write("Command: st %d\n" % (nSt))
                else:
                    resFO.write("Command: st %0.1f\n" % (nSt))                
            else:
                if secondPart:
                    resFO.write("Command: level %d %d:%d %d\n" % (nWBmps, minutePart, secondPart, incPart))
                else:
                    resFO.write("Command: level %d %d %d\n" % (nWBmps, minutePart, incPart))                

        if bCalculateRating:
            slope = 44.523
            intercept = -242.85
            if totalPos:
                sp = 100*float(totalScore)/(maxPoints*totalPos)
                Rating = slope*sp + intercept
                resFO.write('STS rating: %0.0f\n' %(Rating))
                
        resFO.write('\n')  
                
        resFO.write('%8s %6s %6s %6s %6s %6s %6s %6s %6s %6s %6s %6s %6s %6s %6s %6s %6s\n' %('STS ID', 'STS1', 'STS2', 'STS3', 'STS4', 'STS5',\
                                                                                                         'STS6', 'STS7', 'STS8', 'STS9', 'STS10', 'STS11',\
                                                                                                         'STS12', 'STS13', 'STS14', 'STS15', 'ALL'))
        
        resFO.write('%8s %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d\n' %('NumPos', r[0][1], r[1][1], r[2][1], r[3][1], r[4][1],\
                                                                                                         r[5][1], r[6][1], r[7][1], r[8][1],r[9][1], r[10][1],\
                                                                                                         r[11][1], r[12][1], r[13][1], r[14][1],\
                                                                                                               totalPos))

        resFO.write('%8s %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d\n' %('BestCnt', r[0][4], r[1][4], r[2][4], r[3][4], r[4][4],\
                                                                                                         r[5][4], r[6][4], r[7][4], r[8][4],r[9][4], r[10][4],\
                                                                                                         r[11][4], r[12][4], r[13][4], r[14][4],\
                                                                                                               totalBm))
        
        resFO.write('%8s %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d %6d\n' %('Score', r[0][2], r[1][2], r[2][2], r[3][2], r[4][2],\
                                                                                                         r[5][2], r[6][2], r[7][2], r[8][2],r[9][2], r[10][2],\
                                                                                                         r[11][2], r[12][2], r[13][2], r[14][2], totalScore))
        
        if maxScore:
            resFO.write('%8s %6.1f %6.1f %6.1f %6.1f %6.1f %6.1f %6.1f %6.1f %6.1f %6.1f %6.1f %6.1f %6.1f %6.1f %6.1f %6.1f\n' %('Score(%)', r[0][3], r[1][3], r[2][3], r[3][3], r[4][3],\
                                                                                                         r[5][3], r[6][3], r[7][3], r[8][3],r[9][3], r[10][3],\
                                                                                                         r[11][3], r[12][3], r[13][3], r[14][3],\
                                                                                                               100*float(totalScore)/maxScore))
        if bCalculateRating:
            sp = 100*float(totalScore)/(maxPoints*totalPos)
            Rating = slope*sp + intercept
            resFO.write('%8s %6.0f %6.0f %6.0f %6.0f %6.0f %6.0f %6.0f %6.0f %6.0f %6.0f %6.0f %6.0f %6.0f %6.0f %6.0f %6.0f\n' %('Rating', slope*r[0][3]+intercept, slope*r[1][3]+intercept,\
                                                                                                                                 slope*r[2][3]+intercept, slope*r[3][3]+intercept, slope*r[4][3]+intercept,\
                                                                                                                                 slope*r[5][3]+intercept, slope*r[6][3]+intercept, slope*r[7][3]+intercept,\
                                                                                                                                 slope*r[8][3]+intercept,slope*r[9][3]+intercept,slope*r[10][3]+intercept,\
                                                                                                                                 slope*r[11][3]+intercept, slope*r[12][3]+intercept, slope*r[13][3]+intercept,\
                                                                                                                                 slope*r[14][3]+intercept,Rating))

        resFO.write('\n:: STS ID and Titles ::\n')
        for i, n in enumerate(STS_TITLE):
            resFO.write('STS %02d: %s\n' % (i+1, n))

        resFO.write('\n') 

        # Top 5 sts
        # ResultData = ([idItem, pos_num, score, scorePercent, bmCnt])
        ResultDataByScorePercent = sorted(ResultData, key=get_score_percent_key, reverse=True)
        resFO.write(':: Top 5 STS with high result ::\n')
        for i, n, in enumerate(ResultDataByScorePercent):
            idNum = n[0].split('v')
            idNum = idNum[1].split('.')
            idNum = int(idNum[0])
            resFO.write('%d. STS %02d, %4.1f%%, \"%s\"\n' % (i+1, idNum, n[3], STS_TITLE[idNum-1]))
            if i > 3:
                break

        resFO.write('\n') 

        ResultDataByScorePercent = sorted(ResultData, key=get_score_percent_key, reverse=False)
        resFO.write(':: Top 5 STS with low result ::\n')
        for i, n, in enumerate(ResultDataByScorePercent):
            idNum = n[0].split('v')
            idNum = idNum[1].split('.')
            idNum = int(idNum[0])
            resFO.write('%d. STS %02d, %4.1f%%, \"%s\"\n' % (i+1, idNum, n[3], STS_TITLE[idNum-1]))
            if i > 3:
                break
            
        resFO.write('\n')            
        
    if debug:
        logfnFO.write("Test duration: %0.1fs\n" %(float(timeEnd - timeStart)))
        logfnFO.close()
                            

def main(argv):

    ShowPlatform("%s v%s\n" %(APP_NAME, __version__))
    
    sFile = None
    sEngine = None
    nHash = 32  # MB
    nThreads = 1
    nMoveTime = 1000  # 1s default
    bLog = False
    bRate = False
    sProto = 'uci'  # default
    protocol = 0  # 0 uci, 1 for winboard
    stc = '1'
    nmps = 40
    nSt = 0
    bSan = False
    contempt = 0
    maxpoint = 10

    try:
        opts, args = getopt.getopt(argv, "f:e:h:t:", ["file=", "engine=", "hash=", "threads=",
                                                      "movetime=", "log", 'getrating', 'proto=',
                                                      'tc=', 'mps=', 'st=', 'san', 'contempt=',
                                                      'maxpoint='])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("--log"):
            bLog = True
        elif opt in ("-f", "--file"):
            sFile = arg
        elif opt in ("-e", "--engine"):
            sEngine = arg
        elif opt in ("-h", "--hash"):
            nHash = int(arg)
        elif opt in ("-t", "--threads"):
            nThreads = int(arg)
        elif opt in ("--movetime"):
            nMoveTime = int(arg)
        elif opt in ("--getrating"):
            bRate = True
        elif opt in ("--proto"):
            sProto = arg
            if sProto == 'wb':
                protocol = 1
        elif opt in ("--mps"):
            nmps = int(arg)
        elif opt in ("--tc"):
            stc = arg
        elif opt in ("--st"):
            nSt = arg
        elif opt in ("--san"):
            bSan = True
        elif opt in ("--contempt"):
            contempt = int(arg)
        elif opt in ("--maxpoint"):
            maxpoint = int(arg)
         
    # Validate engine, time, depth and file
    if sEngine == None:
        print("Engine was not defined??\n")
        usage()
        input("\nPress enter key to exit")
    elif sFile == None:
        print("EPD file was not defined??\n")
        usage()
        input("\nPress enter key to exit")
    else:
        # Verify engine exists
        if sProto == 'uci' and not os.path.isfile(sEngine):
            print('engine %s is missing' % sEngine)
            input("Press enter key to exit")
            sys.exit(1)
        # Verify if file exists
        if not os.path.isfile(sFile):
            print('test file %s is missing' % sFile)
            input("Press enter key to exit")
            sys.exit(1) 
        print("\nEngine: %s" %(sEngine))
        if protocol == 0:
            print("Hash: %d, Threads: %d, MoveTime: %0.1fs" %(nHash, nThreads, float(nMoveTime)/1000))
        numberOfPositions = count_positions(sFile)
        print("Number of positions in %s: %d\n" %(sFile, numberOfPositions))

        if sProto == 'uci':
            if nMoveTime < 50:
                nMoveTime = 50
        else:
            if nMoveTime < 1000:
                nMoveTime = 1000

        analysisTime = 50
        if bRate:
            myTime = 2.5534  # sec in intel i7-2600k
            yourTime = timeit.timeit('"-".join(str(n) for n in range(100))', number=100000)
            print('Your bench : %0.6fs' %(yourTime))
            print('My bench   : %0.6fs' %(myTime))

            if protocol == WB:
                bRate = False
            else:                
                analysisTime = 200 * yourTime/myTime
                if analysisTime < 50:
                    analysisTime = 50  # ms
                print('Analysis Time to get CCRL 40/4 rating estimate : %0.0fms' %(analysisTime))
                analysisTime = int(analysisTime)

        analyze_pos(sFile, sEngine, nHash, nThreads, nMoveTime, bLog,
                    numberOfPositions, bRate, analysisTime, protocol,
                    stc, nmps, nSt, bSan, contempt, maxpoint)

        print('\nDone!!')
        input("Press enter key to exit")   

if __name__ == "__main__":
   main(sys.argv[1:])
