#include <mysql.h>
struct sum_data
{
  void*	currentSum;
  int	currentLength;
};
char *SUM_HE(UDF_INIT *initid, UDF_ARGS *args,
          char *result, unsigned long *length,
          char *is_null, char *error);

my_bool SUM_HE_init(UDF_INIT *initid, UDF_ARGS *args, char *message);

void SUM_HE_clear(UDF_INIT *initid,
               char *is_null, char *error);
void SUM_HE_add(UDF_INIT *initid, UDF_ARGS *args,
             char *is_null, char *error);

