# ----------------------------------------------------------------------------------
# -- Tecnológico de Monterrey
# -- Sistemas operativos
# -- Ing. Jorge Luis Garza Murillo e Ing. Jose I. Icaza

# -- Proyecto final
# -- Diciembre 3, 2019

# -- Ernesto Cervantes Juarez   Mauricio Nañez Pro
# -- A01196642                  A01194458
# -- Fernando Carrillo Mora     Marco Ortiz
# -- A01194204                  A00823250
# ----------------------------------------------------------------------------------

# IMPORTANTE: se debe de dar el nombre de archivo al momento de correr el programa.
# $ python main.py RR.log

import sys
import math
from tabulate import tabulate

processStatus = {}      # 0 status  # 1 llegada  # 2 priority   # 3 cpu  # 4 io     # 5 temp
processFinished = {}    # 0 name    # 1 llegada  # 2 salida     # 3 cpu  # 4 espera # 5 turnaround # 6 io
blockedQueue = []
waitQueue = []
completed = []
eventTable = []

clk = 0
cpu = None
case = 2
llega_length = 3
quantum = None


def main():
    global quantum
    logLines = []
    logFile = open(sys.argv[1])  # "FCFS.log") #sys.argv[1])

    for line in logFile:
        logLines.append(line)

    checkCase(logLines[0])
    quantum = int(logLines[1][7:]) if int(logLines[1][7:]) != 0 else None

    logLines.pop(0)
    logLines.pop(0)

    for line, log in enumerate(logLines, start=3):
        words = str.split(log, "//", 1)
        words = str.strip(words[0]).split()
        timestamp, instruction = words[0:2]
        if not timestamp.isdigit():
            error(line, "No se puede leer timestamp.")
            continue
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
            continue


def checkCase(name):
    global case, llega_length, waitQueue
    case = str.strip(str.split(name, "//", 1)[0])
    if case == "FCFS":
        case = 1
    elif case == "RR":
        case = 2
        llega_length = 3
    elif case == "prioNonPreemptive":
        case = 3
        llega_length = 5
        waitQueue = [[], [], [], [], [], [], []]
    elif case == "prioPreemptive":
        case = 4
        waitQueue = [[], [], [], [], [], [], []]
    else:
        error(1, "Nombre incorrecto de política. Se tomará como RR.")


def llega(words, line):
    global waitQueue
    timestamp, processID, priority  = validateLengthAndReturnNumbers(words, llega_length, line, ((case == 1) or (case == 2)))
    if timestamp == -1:
        return
    if processID in processStatus:
        error(line, "El proceso " + str(processID) + " ya estaba dentro en " + processStatus[processID][0])
        return
    else:
        processStatus[processID] = ['waitQueue', timestamp, priority, 0, 0, 0]
        if priority is None:
            waitQueue.append(processID)
        else:
            waitQueue[priority].append(processID)
    if cpu is None:
        endCurrentProcess(False, timestamp, "Llega " + str(processID))
    else:
        addSnapshot(timestamp, "Llega", str(processID))


def acaba(words, line):
    global processStatus, waitQueue, blockedQueue, processFinished
    timestamp, processID  = validateLengthAndReturnNumbers(words, 3, line)
    if timestamp == -1:
        return
    if not processID in processStatus:
        error(line, "El proceso " + str(processID) + " no estaba registrado.")
        return
    else:
        status = processStatus[processID]
        if status[0] == 'running':
            processStatus[processID][0] = "finished"
            endCurrentProcess(False, timestamp, "Acaba " + str(processID))
        elif status[0] == 'waitQueue':
            if status[2] is None:
                waitQueue.remove(processID)
            else:
                waitQueue[status[2]].remove(processID)
            addSnapshot(timestamp, "Acaba", str(processID))
        elif status[0] == 'blockedQueue':
            blockedQueue.remove(processID)
            addSnapshot(timestamp, "Acaba", str(processID))
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
        completed.append(processID)
        if not processStatus:
            addSnapshot(timestamp, "Acaba", str(processID))
        


def startIO(words, line):
    global processStatus, waitQueue, blockedQueue
    timestamp, processID = validateLengthAndReturnNumbers(words, 3, line)
    if timestamp == -1:
        return
    if not processID in processStatus:
        error(line, "El proceso " + str(processID) + " no estaba registrado.")
        return
    else:
        status = processStatus[processID]
        if status == 'blockedQueue':
            error(line, "El proceso " + str(processID) + " ya estaba bloqueado.")
            return
        if status[0] == 'waitQueue':
            error(line, "El proceso " + str(processID) + " no estaba corriendo.")
            return
        else:
            processStatus[processID][0] = 'blockedQueue'
            blockedQueue.append(processID)
            endCurrentProcess(False, timestamp, "startI/O " + str(processID))
            processStatus[processID][5] = timestamp


def endIO(words, line):
    global processStatus, waitQueue, blockedQueue
    timestamp, processID = validateLengthAndReturnNumbers(words, 3, line)
    if timestamp == -1:
        return
    if not processID in processStatus:
        error(line, "El proceso " + str(processID) + " no estaba registrado.")
        return
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
            addSnapshot(timestamp, "endI/O", str(processID))
        else:
            error(line, "El proceso " + str(processID) + " no estaba bloqueado.")
            return


def endSimulacion(words, line):
    if processStatus:
        error(line, "Todavía hay procesos corriendo.")
        return
    addSnapshot(words[0], "Fin", "")

    print("\n")
    printTable()
    print("\n")
    printStats()
    sys.exit()
    

def printTable():
    headers = ["Evento", "Cola de listos", "CPU", "Bloqueados", "Terminados"]
    print(tabulate(eventTable, headers=headers,tablefmt="orgtbl"))
    

def addSnapshot(timestamp, eventName, process):
    global processStatus, waitQueue, blockedQueue
    eventString = str(timestamp) + " -  " + eventName + " " + process
    event = [eventString, [], '-', [], []] # evento, listos, cpu, bloquados, terminados

    for pid, value in processStatus.items():
        if(value[0] == "running"): event[2] = pid
    

    event[1] = ', '.join([str(elem) for elem in waitQueue])
    event[3] = ', '.join([str(elem) for elem in blockedQueue])
    event[4] = ', '.join([str(elem) for elem in completed])

    
    eventTable.append(event)
    

def printStats():
    headers = ["Proceso", "T. Llegada", "T. Salida", "T. CPU", "T. espera", "Turnaround", "T. I/O"]
    table = sorted(processFinished.values())
    print(tabulate(table, headers=headers,tablefmt="orgtbl"))
    tEspPromedio = sum([table[i][4] for i in range(len(table))]) / len(table)
    print("\nTiempo de espera promedio: ", '%.2f' % tEspPromedio, "s")
    turnaroundPromedio = sum([table[i][5] for i in range(len(table))]) / len(table)
    print("Turnaround promedio: ", '%.2f' % turnaroundPromedio, "s", "\n")


def error(line, message):
    print("ERROR en línea " + str(line) + ": " + message)


def validateLengthAndReturnNumbers(words, length, line, append=False):
    temp = [int(s) for s in words if s.isdigit()]
    if len(words) != length:
        error(line, "Faltaron argumentos. Había " + str(len(words)) + " y se esperaban " + str(length) + ".")
        temp[0] = -1
    if append:
        temp.append(None)
    return temp


def endCurrentProcess(goToWaitQueue, timestamp, string="Quantum", goToBlockedQueue=False):
    global cpu, clk
    if cpu is not None:
        cpuTime = timestamp - clk
        processStatus[cpu][3] = processStatus[cpu][3] + cpuTime
    
    if goToWaitQueue:
        waitQueue.append(cpu)
        processStatus[cpu][0] = 'waitQueue'
    if quantum is not None:
        if waitQueue:
            cpu = waitQueue.pop(0)
            processStatus[cpu][0] = 'running'
            processStatus[cpu][5] = timestamp
            addSnapshot(timestamp, string, "")
        else:
            cpu = None
    else:
        if waitQueue[0]:
            cpu = waitQueue[0].pop(0)
            processStatus[cpu][0] = 'running'
            processStatus[cpu][5] = timestamp
            addSnapshot(timestamp, string, "")
        elif waitQueue[1]:
            cpu = waitQueue[1].pop(0)
            processStatus[cpu][0] = 'running'
            processStatus[cpu][5] = timestamp
            addSnapshot(timestamp, string, "")
        elif waitQueue[2]:
            cpu = waitQueue[2].pop(0)
            processStatus[cpu][0] = 'running'
            processStatus[cpu][5] = timestamp
            addSnapshot(timestamp, string, "")
        elif waitQueue[3]:
            cpu = waitQueue[3].pop(0)
            processStatus[cpu][0] = 'running'
            processStatus[cpu][5] = timestamp
            addSnapshot(timestamp, string, "")
        elif waitQueue[4]:
            cpu = waitQueue[4].pop(0)
            processStatus[cpu][0] = 'running'
            processStatus[cpu][5] = timestamp
            addSnapshot(timestamp, string, "")
        elif waitQueue[5]:
            cpu = waitQueue[5].pop(0)
            processStatus[cpu][0] = 'running'
            processStatus[cpu][5] = timestamp
            addSnapshot(timestamp, string, "")
        elif waitQueue[6]:
            cpu = waitQueue[6].pop(0)
            processStatus[cpu][0] = 'running'
            processStatus[cpu][5] = timestamp
            addSnapshot(timestamp, string, "")
        else:
            cpu = None

    clk = timestamp

if __name__ == '__main__':
    main()
