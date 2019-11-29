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

waitQueue = []
blockedQueue = []
processStatus = {}
clk = 0
llega_length = 3
PID_actual

logLines = []
quantum = 0
case = 0 # 0 RR   1 prioNonPreemptive

txtFile = open(sys.argv[1])
for line in txtFile:
    logLines.append(line)

#case = str.strip(logLines[0])
quantum = int(logLines[1][7:])

for log in logLines:
    log = str.strip(log)
    words = log.split()
    if words[1] == "Llega":
        llega(words)
    elif words[1] == "Acaba":
        acaba(words)
    elif words[1] == "startIO":
        startIO(words)
    elif words[1] == "endIO":
        endIO(words)
    elif words[1] == "endSimulacion":
        endSimulacion(words)
    else:
        error("")
    
    print(words)


def llega(words):
    global waitQueue
    numbers = validateLength(words, llega_length)
    pID = numbers[2]
    if pID in processStatus:
        error("Ya estaba el proceso")
    else:
        processStatus[pID] = 'waitQueue'
        waitQueue.append(pID)

def acaba(words):
    global processStatus, waitQueue, blockedQueue
    numbers = validateLength(words, 3)
    pID = numbers[2]
    if not pID in processStatus:
        error("No estaba el proceso")
    else:
        if processStatus[pID] == 'waitQueue':
            waitQueue.remove(pID)
        elif processStatus[pID] == 'blockedQueue':
            blockedQueue.remove(pID)
        else:
            changePIDactual(False)
        processStatus.pop(pID)

def startIO(words):
    global processStatus, waitQueue, blockedQueue
    numbers = validateLength(words, 3)
    pID = numbers[2]
    if not pID in processStatus:
        error("No estaba el proceso")
    else:
        if processStatus[pID] == 'waitQueue':
            waitQueue.remove(pID)
            blockedQueue.append(pID)
        elif processStatus[pID] == 'blockedQueue':
            error("ya estaba en la lista")
        else:
            changePIDactual(False)
            blockedQueue.append(pID)
        processStatus[pID] = 'blockedQueue'

def endIO(words):
    global processStatus, waitQueue, blockedQueue
    numbers = validateLength(words, 3)
    pID = numbers[2]
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
    pass

def error(message):
    sys.exit(message)

def validateLength(words, length):
    if len(words) != length:
        error("Faltaron argumentos")
    return [int(s) for s in words if s.isdigit()]

def changePIDactual(goToWait):
    global PID_actual
    
