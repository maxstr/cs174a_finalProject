typedef struct
{
  char* public;
  char* private;
}keys;


keys generate_keys();
void* encrypt_num(unsigned long int num,char* publkey, int*);
unsigned int decrypt_num(void* encrypted, char* pubkey, char*privkey, int);
void* homomorphic_add(void* val1, void* val2,char* publ, int, int, int*);
