#include <assert.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>  // For read()
#include <string.h>  // For memcpy()

// Input buffer.
static const size_t MaxInputSize = 1 << 20;
static uint8_t InputBuf[MaxInputSize];

extern int LLVMFuzzerTestOneInput(const unsigned char *data, size_t size);
__attribute__((weak)) extern int LLVMFuzzerInitialize(int *argc, char ***argv);
int main(int argc, char **argv)
{
  fprintf(stderr, "StandaloneFuzzTargetMain: running %d inputs\n", argc - 1);
  ssize_t n_read = read(0, InputBuf, MaxInputSize);
  if (n_read > 0)
  {
    uint8_t *copy = (uint8_t *)malloc(n_read);
    memcpy(copy, InputBuf, n_read);
    LLVMFuzzerTestOneInput(copy, n_read);
    free(copy);
    fprintf(stderr, "Done: (%zd bytes)\n", n_read);
  }
}
