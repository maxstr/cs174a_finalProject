#include <mysql.h>
struct sum_data
{
  void*	currentSum;
  int	currentLength;
};
char *homoSum(UDF_INIT *initid, UDF_ARGS *args,
          char *result, unsigned long *length,
          char *is_null, char *error);

my_bool homoSum_init(UDF_INIT *initid, UDF_ARGS *args, char *message);

void homoSum_clear(UDF_INIT *initid,
               char *is_null, char *error);
void homoSum_add(UDF_INIT *initid, UDF_ARGS *args,
             char *is_null, char *error);

