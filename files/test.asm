section .data
limite dd 5
contador dd 0

section .text
global _start

_start:
    mov ecx, 0          ; Inicializa contador en registro

bucle:
    inc ecx             ; Incrementa
    mov [contador], ecx ; Guarda en memoria
    
    cmp ecx, [limite]   ; Compara con 5
    jne bucle           ; Si no es igual, repite
    
    ; Terminar
    mov eax, 1          ; Syscall exit
    int 0x80