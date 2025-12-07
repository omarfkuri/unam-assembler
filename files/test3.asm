section .data
numero  dd 5          ; Sumaremos 1+2+3+4+5
resultado dd 0        ; Aquí guardaremos el resultado

section .text
global _start

_start:
    mov eax, 0        ; Inicializamos el acumulador en 0
    mov ecx, 1        ; Contador empieza en 1

ciclo:
    cmp ecx, [numero] ; ¿Llegamos al número objetivo?
    jg fin            ; Si ecx > numero, terminamos

    add eax, ecx      ; EAX = EAX + ECX
    inc ecx           ; Sumamos 1 al contador
    jmp ciclo         ; Repetimos el ciclo

fin:
    mov [resultado], eax ; Guardamos el resultado en memoria
    int 0x80
