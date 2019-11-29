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


logLines = []
PC = 0
quantum = 0
case = None

txtFile = open(sys.argv[1])
for line in txtFile:
    logLines.append(line)

case = str.strip(logLines[0])
quantum = int(logLines[1][7:])

for log in logLines:
    log = str.strip(log)
    print([int(s) for s in log.split() if s.isdigit()])
