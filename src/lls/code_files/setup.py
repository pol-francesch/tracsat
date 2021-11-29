# Run the following command line prompt to recompile wrapper
# python3 setup.py build_ext -i
# make sure to delete .so file when updating wrapper

from distutils.core import setup, Extension
import numpy

setup(ext_modules=[Extension("_write_output",
      sources=["write_output.c", "write_output.i"],
      include_dirs=[numpy.get_include()])])