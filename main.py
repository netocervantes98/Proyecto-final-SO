# ----------------------------------------------------------------------------------
# -- Tecnológico de Monterrey
# -- Sistemas operativos
# -- Ing. Jorge Luis Garza Murillo e Ing. Jose I. Icaza

# -- Proyecto final
# -- Noviembre 29, 2019

# -- Ernesto Cervantes Juarez   Mauricio Nañez Pro
# -- A01196642                  A01194458
# -- Fernando Carrillo Mora     Marco Ortiz
# -- A01194204                  A01196642
# ----------------------------------------------------------------------------------

# IMPORTANTE: se debe de dar el nombre de archivo al momento de correr el programa.

import sys
import math

logLines = []
quantum = 0
case = 0 # 0 RR   1 prioNonPreemptive
llega_length = 3

processStatus = {}
waitQueue = []
blockedQueue = []

clk = 0
cpu = None

def llega(words, line):
    global waitQueue
    timestamp, processID  = validateLengthAndReturnNumbers(words, llega_length, line)[0:1]
    if processID in processStatus:
        error(line, "El proceso " + str(processID) + " ya estaba dentro en " + processStatus[processID])
    else:
        processStatus[processID] = 'waitQueue'
        waitQueue.append(processID)
    if cpu is None:
            endCurrentProcess(False, timestamp)


def acaba(words, line):
    global processStatus, waitQueue, blockedQueue
    timestamp, processID  = validateLengthAndReturnNumbers(words, 3, line)
    if not processID in processStatus:
        error(line, "El proceso " + str(processID) + " no estaba registrado.")
    else:
        status = processStatus[processID]
        processStatus.pop(processID)
        if status == 'running':
            endCurrentProcess(False, timestamp)
            return
        if status == 'waitQueue':
            waitQueue.remove(processID)
        elif status == 'blockedQueue':
            blockedQueue.remove(processID)
        print('clk', timestamp, '   processStatus', processStatus)


def startIO(words, line):
    global processStatus, waitQueue, blockedQueue
    timestamp, processID = validateLengthAndReturnNumbers(words, 3, line)
    if not processID in processStatus:
        error(line, "El proceso " + str(processID) + " no estaba registrado.")
    else:
        status = processStatus[processID]
        if status == 'blockedQueue':
            error(line, "El proceso " + str(processID) + " ya estaba bloqueado.")
        processStatus[processID] = 'blockedQueue'
        blockedQueue.append(processID)
        if status == 'waitQueue':
            waitQueue.remove(processID)
            print('clk', timestamp, '   processStatus', processStatus)
        else:
            endCurrentProcess(False, timestamp)


def endIO(words, line):
    global processStatus, waitQueue, blockedQueue
    processID  = validateLengthAndReturnNumbers(words, 3, line)[1]
    if not processID in processStatus:
        error(line, "El proceso " + str(processID) + " no estaba registrado.")
    else:
        if processStatus[processID] == 'blockedQueue':
            blockedQueue.remove(processID)
            processStatus[processID] = 'waitQueue'
            waitQueue.append(processID)
        else:
            error(line, "El proceso " + str(processID) + " no estaba bloqueado.")


def endSimulacion(words):
    sys.exit("clk "+ words[0] + "    fin")


def error(line, message):
    sys.exit("ERROR en línea " + str(line) + ": "+ message)


def validateLengthAndReturnNumbers(words, length, line):
    if len(words) != length:
        error(line, "Faltaron argumentos. Había " + str(len(words)) + " y se esperaban " + str(length) + ".")
    return [int(s) for s in words if s.isdigit()]

def endCurrentProcess(goToBlockedQueue, timestamp):
    global cpu, clk
    clk = timestamp
    if goToBlockedQueue and (cpu is not None):
        waitQueue.append(cpu)
        processStatus[cpu] = 'waitQueue'
    if waitQueue:
        cpu = waitQueue.pop(0)
        processStatus[cpu] = 'running'
        print('clk', clk, '   processStatus', processStatus)
    else:
        cpu = None


logFile = open(sys.argv[1])
for line in logFile:
    logLines.append(line)

#case = str.strip(logLines[0])
quantum = int(logLines[1][7:])
logLines.pop(0)
logLines.pop(0)

for line, log in enumerate(logLines, start=3):
    words = str.strip(log).split()
    timestamp, instruction = words[0:2]
    if not timestamp.isdigit():
        error(line, "No se puede leer timestamp.")
    timestamp = int(timestamp)

    if(timestamp - clk) > quantum and waitQueue:
        ciclos = math.floor((timestamp - clk) / quantum)
        for i in range(0, ciclos):
            endCurrentProcess(True, clk + quantum)

    if instruction == "Llega":
        llega(words, line)
    elif instruction == "Acaba":
        acaba(words, line)
    elif instruction == "startI/O":
        startIO(words, line)
    elif instruction == "endI/O":
        endIO(words, line)
    elif instruction == "endSimulacion":
        endSimulacion(words)
    else:
        error(line, "No se puede leer log : \'" + log + "\'")
    if instruction == "Llega" or instruction == "endI/O" or instruction == "endSimulacion":
        print('clk', timestamp, '   processStatus', processStatus)