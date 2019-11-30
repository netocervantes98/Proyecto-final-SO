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
import pprint

logLines = []
quantum = 0
case = 0 # 0 RR   1 prioNonPreemptive
llega_length = 3

processStatus = {} # 0 status  # 1 llegada  # 2 priority  # 3 cpu  # 4 io  # 5 temp
processFinished = {} # 0 name  # 1 llegada  # 2 salida  # 3 cpu  # 4 espera  # 5 turnaround # 6 io
waitQueue = []
blockedQueue = []

clk = 0
cpu = None

def llega(words, line):
    global waitQueue
    timestamp, processID, priority  = validateLengthAndReturnNumbers(words, llega_length, line, (case == 1 or (case == 2)))
    if processID in processStatus:
        error(line, "El proceso " + str(processID) + " ya estaba dentro en " + processStatus[processID][0])
    else:
        processStatus[processID] = ['waitQueue', timestamp, priority, 0, 0, 0]
        if priority is None:
            waitQueue.append(processID)
        else:
            waitQueue[priority].append(processID)
    if cpu is None:
        endCurrentProcess(False, timestamp)
    else:
        print('clk', timestamp, '   processStatus', processStatus)



def acaba(words, line):
    global processStatus, waitQueue, blockedQueue, processFinished
    timestamp, processID  = validateLengthAndReturnNumbers(words, 3, line)
    if not processID in processStatus:
        error(line, "El proceso " + str(processID) + " no estaba registrado.")
    else:
        status = processStatus[processID]
        if status[0] == 'running':
            endCurrentProcess(False, timestamp)
        elif status[0] == 'waitQueue':
            if status[2] is None:
                waitQueue.remove(processID)
            else:
                waitQueue[status[2]].remove(processID)
        elif status[0] == 'blockedQueue':
            blockedQueue.remove(processID)
        processFinished[processID] = [
            processID,
            processStatus[processID][1],
            timestamp, 
            processStatus[processID][3],
            timestamp - processStatus[processID][1] - processStatus[processID][3] - processStatus[processID][4],
            timestamp - processStatus[processID][1],
            processStatus[processID][4],
        ]
        processStatus.pop(processID)
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
        if status[0] == 'waitQueue':
            error(line, "El proceso " + str(processID) + " no estaba corriendo.")
        else:
            endCurrentProcess(False, timestamp)
            processStatus[processID][0] = 'blockedQueue'
            blockedQueue.append(processID)
            processStatus[processID][5] = timestamp


def endIO(words, line):
    global processStatus, waitQueue, blockedQueue
    processID  = validateLengthAndReturnNumbers(words, 3, line)[1]
    if not processID in processStatus:
        error(line, "El proceso " + str(processID) + " no estaba registrado.")
    else:
        if processStatus[processID][0] == 'blockedQueue':
            blockedQueue.remove(processID)
            processStatus[processID][0] = 'waitQueue'
            IOtime = timestamp - processStatus[processID][5]
            processStatus[processID][4] = processStatus[processID][4] + IOtime
            if processStatus[processID][2] is None:
                waitQueue.append(processID)
            else:
                waitQueue[processStatus[processID][2]].append(processID)
        else:
            error(line, "El proceso " + str(processID) + " no estaba bloqueado.")


def endSimulacion(words, line):
    if processStatus:
        error(line, "Todavía hay procesos corriendo.")
    print("name, llegada, salida, cpu, espera, turnaround, io")
    pprint.pprint(processFinished)
    sys.exit("clk "+ words[0] + "    fin")


def error(line, message):
    sys.exit("ERROR en línea " + str(line) + ": "+ message)


def validateLengthAndReturnNumbers(words, length, line, append=False):
    if len(words) != length:
        error(line, "Faltaron argumentos. Había " + str(len(words)) + " y se esperaban " + str(length) + ".")
    temp = [int(s) for s in words if s.isdigit()]
    if append:
        temp.append(None)
    return temp

def endCurrentProcess(goToBlockedQueue, timestamp):
    global cpu, clk
    if cpu is not None:
        cpuTime = timestamp - clk
        processStatus[cpu][3] = processStatus[cpu][3] + cpuTime

    if goToBlockedQueue:
        waitQueue.append(cpu)
        processStatus[cpu][0] = 'waitQueue'
    if waitQueue:
        cpu = waitQueue.pop(0)
        processStatus[cpu][0] = 'running'
        processStatus[cpu][5] = timestamp
        print('clk', clk, '   processStatus', processStatus)
    else:
        cpu = None
    clk = timestamp


logFile = open(sys.argv[1])  # sys.argv[1]
for line in logFile:
    logLines.append(line)

case = str.strip(str.split(logLines[0], "//", 1)[0])
if case == "FCFS":
    case = 1
elif case == "RR":
    case = 2
elif case == "prioNonPreemptive":
    case = 3
    waitQueue = [[], [], [], [], [], [], []]
elif case == "prioPreemptive":
    case = 4
    waitQueue = [[], [], [], [], [], [], []]
else:
    error(1, "Nombre incorrecto de política.")
quantum = int(logLines[1][7:]) if int(logLines[1][7:]) != 0 else None

logLines.pop(0)
logLines.pop(0)

for line, log in enumerate(logLines, start=3):
    words = str.strip(log).split()
    timestamp, instruction = words[0:2]
    if not timestamp.isdigit():
        error(line, "No se puede leer timestamp.")
    timestamp = int(timestamp)

    if quantum is not None:
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
        endSimulacion(words, line)
    else:
        error(line, "No se puede leer log : \'" + log + "\'")

    if instruction == "endI/O" or instruction == "endSimulacion":
        print('clk', timestamp, '   processStatus', processStatus)
