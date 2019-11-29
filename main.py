# ----------------------------------------------------------------------------------
# -- Tecnológico de Monterrey
# -- Sistemas operativos
# -- Ing. Jorge Luis Garza Murillo e Ing. Jose I. Icaza

# -- Proyecto final
# -- Noviembre 29, 2019

# -- Ernesto Cervantes Juarez
# -- A01196642
# -- Mauricio Nañez Pro
# -- A01194458
# -- Fernando Carrillo Mora
# -- A01194204
# -- Ernesto Cervantes Juarez
# -- A01196642
# ----------------------------------------------------------------------------------

# debe de dar el nombre de archivo al momento de correr el programa.

import sys
import math

waitQueue = []
blockedQueue = []
processStatus = {}
clk = 0
llega_length = 3
cpu = None

logLines = []
quantum = 0
case = 0 # 0 RR   1 prioNonPreemptive


def llega(words):
    global waitQueue
    numbers = validateLength(words, llega_length)
    pID = numbers[1]
    if pID in processStatus:
        error("Ya estaba el proceso")
    else:
        processStatus[pID] = 'waitQueue'
        waitQueue.append(pID)


def acaba(words):
    global processStatus, waitQueue, blockedQueue
    numbers = validateLength(words, 3)
    pID = numbers[1]
    if not pID in processStatus:
        error("No estaba el proceso")
    else:
        if processStatus[pID] == 'waitQueue':
            waitQueue.remove(pID)
            processStatus.pop(pID)
            print('clk', numbers[0], '   processStatus', processStatus)
        elif processStatus[pID] == 'blockedQueue':
            blockedQueue.remove(pID)
            processStatus.pop(pID)
            print('clk', numbers[0], '   processStatus', processStatus)
        else:
            processStatus.pop(pID)
            changePIDactual(False, numbers[0])


def startIO(words):
    global processStatus, waitQueue, blockedQueue
    numbers = validateLength(words, 3)
    pID = numbers[1]
    if not pID in processStatus:
        error("No estaba el proceso")
    else:
        if processStatus[pID] == 'waitQueue':
            waitQueue.remove(pID)
            blockedQueue.append(pID)
            processStatus[pID] = 'blockedQueue'
            print('clk', numbers[0], '   processStatus', processStatus)
        elif processStatus[pID] == 'blockedQueue':
            error("ya estaba en la lista")
        else:
            processStatus[pID] = 'blockedQueue'
            blockedQueue.append(pID)
            changePIDactual(False, numbers[0])


def endIO(words):
    global processStatus, waitQueue, blockedQueue
    numbers = validateLength(words, 3)
    pID = numbers[1]
    if not pID in processStatus:
        error("No estaba el proceso")
    else:
        if processStatus[pID] == 'blockedQueue':
            blockedQueue.remove(pID)
            waitQueue.append(pID)
            processStatus[pID] = 'waitQueue'
        else:
            error("no estaba en la lista")


def endSimulacion(words):
    error("clk " +words[0]+ "    fin")


def error(message):
    sys.exit(message)


def validateLength(words, length):
    if len(words) != length:
        error("Faltaron argumentos")
    return [int(s) for s in words if s.isdigit()]

def changePIDactual(goToWait, time):
    global cpu, clk
    clk = time
    if goToWait and (cpu is not None):
        waitQueue.append(cpu)
        processStatus[cpu] = 'waitQueue'
    if waitQueue:
        cpu = waitQueue.pop(0)
        processStatus[cpu] = 'running'
        print('clk', clk, '   processStatus', processStatus)
    else:
        cpu = None


txtFile = open("RR.log")  # sys.argv[1]
for line in txtFile:
    logLines.append(line)

#case = str.strip(logLines[0])
quantum = int(logLines[1][7:])

logLines.pop(0)
logLines.pop(0)

for log in logLines:
    log = str.strip(log)
    words = log.split()
    timestamp = int(words[0])

    if(timestamp - clk) > quantum and waitQueue:
        ciclos = math.floor((timestamp - clk) / quantum)
        for i in range(0, ciclos):
            changePIDactual(True, clk + quantum)

    if words[1] == "Llega":
        llega(words)
        print('clk', timestamp, '   processStatus', processStatus)
        if cpu is None:
            changePIDactual(False, timestamp)
    elif words[1] == "Acaba":
        acaba(words)
    elif words[1] == "startI/O":
        startIO(words)
    elif words[1] == "endI/O":
        endIO(words)
        print('clk', timestamp, '   processStatus', processStatus)
    elif words[1] == "endSimulacion":
        endSimulacion(words)
        print('clk', timestamp, '   processStatus', processStatus)
    else:
        error("error de cod")



