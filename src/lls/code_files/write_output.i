%module write_output

%{
/* the resulting C file should be built as a python extension */
#define SWIG_FILE_WITH_INIT
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include "write_output.h"
%}

/*  include the numpy typemaps */
%include "numpy.i"
/*  need this for correct module initialization */
%init %{
    import_array();
%}

/* typemap for array */
%apply (int* IN_ARRAY1, int DIM1) {(int *arr, int size)}

void write_data_test(int *arr, int size);
int interrupts(int flag);
int setup(void);