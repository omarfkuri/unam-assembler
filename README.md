# Ensamblador en Python

## Integrantes

# Garcia Nava Diego 
# Ramírez Rodríguez Oscar Gael 
# Freaner Kuri Omar Ariel

## Correr el programa
```bash
./scripts/run.sh
```

## Funcionamiento

### 1 Pasada (Módulo `one_pass`)

El proceso de ensamblado consiste de
leer tokens y generar código de
inmediato, línea por línea.

### 2 Pasadas (Módulo `two_pass`)

El proceso de ensamblado consiste
de dos partes: lectura de tokens y
generación de código. 

El proceso de lectura es realizado por el
sistema `Parser`. Su trabajo es leer un
archivo y construir un arreglo de instrucciones
y una tabla de símbolos.

El sistema `CodeGenerator` se encarga de procesar
las instrucciones leídas. Construye una tabla de
referencias y código de máquina.