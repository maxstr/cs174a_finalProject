#include <stdio.h>
#include "gmp.h"
#include "paillier.h"
#include <stdlib.h>
#include <string.h>
#include "WrappedCrypto.h"

const int keySize = 128;

keys generate_keys()
{
  keys retval;
  paillier_pubkey_t* publics;
  paillier_prvkey_t* privates;
  paillier_keygen(keySize,&publics,&privates,paillier_get_rand_devrandom);
  retval.public = paillier_pubkey_to_hex(publics);
  retval.private = paillier_prvkey_to_hex(privates);
  return retval;
}

void* encrypt_num(unsigned long int num, char *publkey, int* size)
{
  //make the pubkey from the string
  paillier_pubkey_t* publics = paillier_pubkey_from_hex(publkey);
  
  //make the plaintext variable
  paillier_plaintext_t* plain;
  plain = paillier_plaintext_from_ui(num);

  //make an empty ciphertext variable to be filled with ciphertext
  paillier_ciphertext_t* encrypted;
  encrypted = paillier_create_enc_zero();

  //Do the encryption!
  paillier_enc(encrypted,publics,plain,paillier_get_rand_devrandom);

  //return the result!

  void *result;
  *size = mpz_sizeinbase(encrypted->c, 2);
  result = paillier_ciphertext_to_bytes(mpz_sizeinbase(encrypted->c, 2),encrypted);
  
  return result;
}

unsigned int decrypt_num(void *to_unencrypt,char* pubkey,char*privkey, int size)
{
  //make a temp variable for encrypted
  //unsigned long int*uitemp = &to_unencrypt;
  //void *vtemp = (void *)uitemp;


  //make a ciphertext out of given encrypted text
  paillier_ciphertext_t* encrypted;
  encrypted = paillier_ciphertext_from_bytes(to_unencrypt, size);

  //make the public and private keys for doing the decryption
    paillier_pubkey_t* publics = paillier_pubkey_from_hex(pubkey);
    paillier_prvkey_t* privates = paillier_prvkey_from_hex(privkey,publics);

  //make a plaintext to store the result. 10 is just a stub, could be anything.

  paillier_plaintext_t* plainText = paillier_dec(NULL,publics,privates,encrypted);

  return mpz_get_ui(plainText->m);
}

void* homomorphic_add(void *num1,void* num2, char* publ,int size1, int size2, int* retsize)
{

  //make a public key from the string
  paillier_pubkey_t *publics = paillier_pubkey_from_hex(publ);
  
  //make ciphertexts out of given encrypted data
  paillier_ciphertext_t* encrypted1;
  encrypted1 = paillier_ciphertext_from_bytes(num1,size1);

  paillier_ciphertext_t* encrypted2;
  encrypted2 = paillier_ciphertext_from_bytes(num2,size2);

  
  //make a ciphertext for the result
  paillier_ciphertext_t* ct;
  ct = paillier_create_enc_zero();

  //do the addition
  paillier_mul(publics,ct,encrypted1,encrypted2);
  *retsize = mpz_sizeinbase(ct->c, 2);
  void* result;
 result = paillier_ciphertext_to_bytes(mpz_sizeinbase(ct->c, 2),ct); 

  //return result as iresult
 return result;
}
// Allocates and returns a pointer to an array of unsigned chars
unsigned char* toText (void* data, int size) {
    unsigned char* ret = (unsigned char*) malloc(sizeof(unsigned char) * size);
    for (int i = 0; i < size; i++) {
        ret[i] = *((unsigned char*) (data + i));
    }
    return ret;
}
void* toData (unsigned char* text) {
    return (void*) text;
}


int main()
{
    keys bothkeys = generate_keys();
    printf("Keys:\nPublic: %s\n\nPrivate: %s\n",bothkeys.public,bothkeys.private);
    int size,size1,size2;
    unsigned int result;
    void *enc = encrypt_num(1234, bothkeys.public, &size);
    void *enc2 = encrypt_num(1234,bothkeys.public,&size1); 
    void *enc3 = homomorphic_add(enc,enc2,bothkeys.public,size,size1,&size2);
    result = decrypt_num(enc3, bothkeys.public ,bothkeys.private, size2);
    printf("Decrypted Number:\n%d\n",result);
  
    return 0;

    
}

