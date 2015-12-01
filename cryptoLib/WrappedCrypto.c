#include <stdio.h>
#include "gmp.h"
#include "paillier.h"
#include <stdlib.h>
#include <string.h>

int key_pair_length = 128;
typedef struct
{
  char* public;
  char* private;
}keys;


keys generate_keys();
void* encrypt_num(unsigned long int num,char* publkey);
char* decrypt_num(void* encrypted, char* pubkey, char*privkey);
void* homomorphic_add(void* val1, void* val2,char* publ);

keys generate_keys()
{
  keys retval;
  paillier_pubkey_t* publics;
  paillier_prvkey_t* privates;
  paillier_keygen(key_pair_length,&publics,&privates,paillier_get_rand_devrandom);
  retval.public = paillier_pubkey_to_hex(publics);
  retval.private = paillier_prvkey_to_hex(privates);
  paillier_freepubkey(publics);
  paillier_freeprvkey(privates);
  return retval;
}

void* encrypt_num(unsigned long int num,char *publkey)
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
  result = (char*)paillier_ciphertext_to_bytes(key_pair_length,encrypted);
  
  paillier_freepubkey(publics);
  paillier_freeplaintext(plain);
  paillier_freeciphertext(encrypted);
  return result;
}

char* decrypt_num(void *to_unencrypt,char* pubkey,char*privkey)
{
  //make a temp variable for encrypted
  //unsigned long int*uitemp = &to_unencrypt;
  //void *vtemp = (void *)uitemp;

  //make a ciphertext out of given encrypted text
  paillier_ciphertext_t* encrypted;
  encrypted = paillier_ciphertext_from_bytes(to_unencrypt,key_pair_length);

  //make the public and private keys for doing the decryption
    paillier_pubkey_t* publics = paillier_pubkey_from_hex(pubkey);
    paillier_prvkey_t* privates = paillier_prvkey_from_hex(privkey,publics);

  //make a plaintext to store the result. 10 is just a stub, could be anything.
  paillier_plaintext_t* plain;
  plain = paillier_plaintext_from_ui(10);

  paillier_dec(plain,publics,privates,encrypted);
  char* result;
  result = paillier_plaintext_to_str(plain);
  paillier_freepubkey(publics);
  paillier_freeprvkey(privates);
  paillier_freeplaintext(plain);
  paillier_freeciphertext(encrypted);
  return result;
}

void* homomorphic_add(void *num1,void* num2, char* publ)
{

  //make a public key from the string
  paillier_pubkey_t *publics = paillier_pubkey_from_hex(publ);
  
  //make ciphertexts out of given encrypted data
  paillier_ciphertext_t* encrypted1;
  encrypted1 = paillier_ciphertext_from_bytes(num1,key_pair_length);

  paillier_ciphertext_t* encrypted2;
  encrypted2 = paillier_ciphertext_from_bytes(num2,key_pair_length);

  
  //make a ciphertext for the result
  paillier_ciphertext_t* result;
  result = paillier_create_enc_zero();

  
  //do the addition
  paillier_mul(publics,result,encrypted1,encrypted2);


  //return result as iresult
  return paillier_ciphertext_to_bytes(key_pair_length,result);
}



int main()
{
  keys bothkeys = generate_keys();
  printf("%s,%s\n",bothkeys.public,bothkeys.private);
  int done = 0;
  char *result;
      result = decrypt_num(encrypt_num(1234,bothkeys.public),bothkeys.public,bothkeys.private);
      printf("%s\n",result);

  
  return 0;
}

