section .data
numero  dd 5          ; Calcularemos 5! (120)
resultado dd 1        ; Aquí guardaremos el resultado

section .text
global _start

_start:
    mov eax, 1        ; El resultado empieza en 1
    mov ecx, [numero] ; Cargamos el 5 en ECX

ciclo:
    cmp ecx, 1        ; ¿Llegamos a 1?
    jle fin           ; Si es menor o igual a 1, terminamos

    mul ecx           ; EAX = EAX * ECX
    dec ecx           ; Restamos 1 al contador
    jmp ciclo         ; Repetimos

fin:
    mov [resultado], eax ; Guardamos el 120 (0x78) en memoria
    int 0x80