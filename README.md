# compilador
# Como compilar e executar em ambiente Linux (WSL/Ubuntu)

1. Instale o GCC (caso não tenha):
```bash
sudo apt update
sudo apt install build-essential
```

2. Compile o arquivo principal:
```bash
gcc main.c -o main
```

3. Execute o programa:
```bash
./main
```

4. (Opcional) Para testar com um arquivo de entrada:
```bash
./main < test.txt
```

---
Este projeto foi desenvolvido para fins de estudo de compiladores.