import re
import sys
import datetime
from shutil import copyfile
import os

filename = ''
if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    print('Wrong arguments')

data = {}
startrange = ''
endrange = ''
optimCounter = []
revNumber = ''
actionDictionary = {'insert': 0,
                    'commit': 0,
                    'truncate': 0,
                    'analyze': 0}

if len(filename) > 0:
    with open(filename) as fileForParse:
        textStrings = fileForParse.readlines()
        tableRange = True
        revValue = True
        findTables = re.compile(r'(FROM|JOIN|INSERT INTO|insert into|from|join|,)'
                                r'[ \t]?(~p_)?(edw_stg_dds|edw_ods|edw_odl|edw_stg_ddl)~?\.(.*?)[ \t\n;)]')
        findOptims = re.compile(r'set optimizer( ){0,3}=( ){0,3}(.*?);')
        findInserts = re.compile(r'insert into')
        findCommit = re.compile(r'commit;')
        findTruncate = re.compile(r'truncate table')
        findAnalyze = re.compile(r'analyze')
        n = 0

        for text in textStrings:
            n += 1
            # Searching for a start and an end of range
            if tableRange:
                start = re.search(r'v_src_id_start( ){0,5}:=(.*?);', text)
                end = re.search(r'v_src_id_end( ){0,5}:=(.*?);', text)
                if start:
                    startrange = start.group(2)
                if end:
                    endrange = end.group(2)
                    tableRange = False
            # Searching for a rev parametr
            if revValue:
                revSearch = re.search('rev\.(\d+) ', text)
                if revSearch:
                    revNumber = revSearch.group(1)
                    revValue = False

            # Optimizer search saving line number and its property
            optimaSwitch = re.search(findOptims, text)
            if optimaSwitch:
                optimCounter.append([n, optimaSwitch.group(3)])

            # Start counter for table acts
            insert = re.search(findInserts, text.lower())
            if insert:
                actionDictionary['insert'] += 1
            commit = re.search(findCommit, text.lower())
            if commit:
                actionDictionary['commit'] += 1
            truncate = re.search(findTruncate, text.lower())
            if truncate:
                actionDictionary['truncate'] += 1
            analyze = re.search(findAnalyze, text.lower())
            if analyze:
                actionDictionary['analyze'] += 1

            # Searching for tables
            tables = re.findall(findTables, text)
            for table in tables:
                # Saving to dictionary with schema as a key
                if table[2] not in data:
                    data[table[2]] = [table[3]]
                else:
                    data[table[2]].append(table[3])

    # Check if log file already exist
    # If it exists, copy its content to old file to write new logs at the begging and add old data
    if not os.path.isfile('etl_parser.log'):
        with open('etl_parser.log', 'w') as makeFile:
            makeFile.write('\n')
    copyfile('etl_parser.log', 'etl_parser_old.log')

    with open('etl_parser.log', 'w') as writeLog:
        # Setting time to write a log
        now = datetime.datetime.now()
        # Writing start log header
        writeLog.write('#####BEGIN PARSE JOB'
                       '\tFilename={}'
                       '\tSRC_CODE_BEGIN={}'
                       '\tSRC_CODE_END={}'
                       '\tPARSE_DATETIME={}#####\n'.format(filename,
                                                           startrange,
                                                           endrange,
                                                           now.strftime("%Y-%m-%d %H:%M")))

        # Writing tables within schemas to log file
        for top in data:
            writeLog.write('[{}]'.format(top.upper()) + '\n')
            for tableToWrite in set(data[top]):
                writeLog.write(tableToWrite.upper() + '\n')
            writeLog.write('\n')

        # Writing optimizer setters to log file
        writeLog.write('set optimezers: \n')
        for switch in optimCounter:
            writeLog.write('-'.join([str(switch[0]), switch[1]]) + '\n')
        writeLog.write('\n')

        # Writing rev-parameter to log file
        writeLog.write('rev parameter - ' + revNumber + '\n\n')

        # Writing table actions to log file
        for act in actionDictionary:
            writeLog.write(' - '.join([act.upper(), str(actionDictionary[act])]) + '\n')
        writeLog.write('\n')

        # Writing end log header
        writeLog.write('#####END PARSE JOB'
                       '\tFilename={}'
                       '\tSRC_CODE_BEGIN={}'
                       '\tSRC_CODE_END={}'
                       '\tPARSE_DATETIME={}#####\n'.format(filename,
                                                           startrange,
                                                           endrange,
                                                           now.strftime("%Y-%m-%d %H:%M")) + '\n')

        with open('etl_parser_old.log') as adFile:
            for line in adFile:
                writeLog.write(line)

    os.remove('etl_parser_old.log')
