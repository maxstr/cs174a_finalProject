#include "WrappedCrypto.h"
#include <gmp.h>
#include <stdlib.h>
int main() {
    keys bothkeys = generate_keys();
    
    printf("Keys:\nPublic: %s\n\nPrivate: %s\n",bothkeys.public,bothkeys.private);
    int size,size1,size2;
    unsigned int result;
    void *enc = encrypt_num(1234, bothkeys.public, &size);
    void *enc2 = encrypt_num(1234,bothkeys.public,&size1); 
    void *enc3 = homomorphic_add(enc,enc2,bothkeys.public,size,size1,&size2);
    result = decrypt_num(enc3, bothkeys.public ,bothkeys.private, size2);
    printf("Decrypted Number:\n%d\n",result);
    free(enc);
    free(enc2);
    free(enc3);
    free(bothkeys.private);
    free(bothkeys.public);
    return 0;
}

