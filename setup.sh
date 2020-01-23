export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/repos/BUILD_DIR/NETCDF/lib/
export PYSYN_CDBS=$HOME/repos/Spectractor/tests/data
export LIBRADTRANDIR=$HOME/repos/libRadtran-2.0.2/
# export DISPLAY=

setup -j atmospec -r ~/repos/atmospec
setup -j rapid_analysis -r ~/repos/rapid_analysis
