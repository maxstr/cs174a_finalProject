#include <mysql.h>
#include <gmp.h>
#include "WrappedCrypto.h"
#include <string.h>
#include "homoSum.h"
#include <stdio.h>

my_bool homoSum_init(UDF_INIT *initid, UDF_ARGS *args, char *message) {
    if (args->arg_count != 2) {
       strcpy(message, "wrong number of arguments: homoadd() requires two arguments");
        return 1;
    }
    initid->maybe_null = 0;
    initid->max_length = 65000;
    struct sum_data* data = malloc(sizeof(struct sum_data));
    int sumSize = 0;
    data->currentSum = zeroed(&sumSize);
    data->currentLength = sumSize;
    initid->ptr = (char*) data;
    return 0;
}

void homoSum_deinit( UDF_INIT* initid) {
    struct sum_data* data = (struct sum_data*) initid->ptr;
    free(data->currentSum);
    free(data);
}

void homoSum_clear(UDF_INIT* initid, char* is_null, char* message) {
    struct sum_data* data = (struct sum_data*) initid->ptr;
    int sumSize = 0;
    data->currentSum = zeroed(&sumSize);
    data->currentLength = sumSize;
}

void homoSum_add(UDF_INIT* initd, UDF_ARGS* args, char* is_null, char* message) {
    if (args->args[0] && args->args[1]) {
        struct sum_data* data = (struct sum_data*) initd->ptr;
        int newSize;
        void* oldSum = data->currentSum;
        data->currentSum = homomorphic_add(oldSum, (void *) args->args[0], args->args[1], data->currentLength, args->lengths[0], &newSize); 
        data->currentLength = newSize;
        free(oldSum);
    }
    else
        printf("An error occurred!");
}

char *homoSum(UDF_INIT *initid, UDF_ARGS *args,
          char *result, unsigned long *length,
          char *is_null, char *error) {
    struct sum_data* data = (struct sum_data*) initid->ptr;
    char* ourResult = calloc((data->currentLength*2 + 1), sizeof(char));
    for(int i = 0;i < data->currentLength;i++) {
        sprintf(&ourResult[i*2], "%02X", ((unsigned char*)(data->currentSum))[i]);
    } 
    ourResult[data->currentLength*2 + 1] = '\0';
    *length = data->currentLength*2 + 1;
    return ourResult;
}


