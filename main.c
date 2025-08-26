#include <stdio.h>
#include <stdlib.h>

// void handleAtrr(){
//     fgets( ){
//         if ( == 61 ){
//             /// Trata a atribuição
//             /// TK.lexama <- ":="
//             /// TK.simb <- satrib
//             ///ler(carac)
//         }
//         else{
//             /// TK.lexical <- ":"
//             /// TK.simb <- sdoispontos
//             ///FIM
//         }
//     }
// }

int main()
{
    FILE *fp;
    char line[100];

    /// Abre arquivo
    fp = fopen("/home/victor/compilador/compilador/test.txt", "r");

    if( fp == NULL ){
        perror("Error to open the file");
        exit(EXIT_FAILURE);
    }

    while ( fgets(line, sizeof(line), fp) != NULL ){
        printf("%s", line);
    }

    fclose(fp);

    return 0;
}