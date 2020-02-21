# eups distrib install -t w_2020_04 lsst_distrib
# setup lsst_distrib -t w_2020_04
eups distrib install -t d_2020_02_17 lsst_distrib
setup lsst_distrib -t d_2020_02_17

cd $HOME/repos

### NetCDF
wget -L https://github.com/Unidata/netcdf-c/archive/v4.6.1.tar.gz
gzip -d v4.6.1.tar.gz
tar -xf v4.6.1.tar
cd netcdf-c-4.6.1
./configure  --prefix=$HOME/repos/BUILD_DIR/NETCDF --disable-netcdf-4
make
make install

cd ..
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/repos/BUILD_DIR/NETCDF/lib/

wget -L http://www.libradtran.org/download/history/libRadtran-2.0.2.tar.gz
gzip -d libRadtran-2.0.2.tar.gz
tar -xf libRadtran-2.0.2.tar
cd libRadtran-2.0.2

export LIBS="-lgslcblas -lgsl"
export LDFLAGS=-L$GSL_DIR/lib
export CPPFLAGS=-I$GSL_DIR/include
./configure  --prefix=$HOME/repos/BUILD_DIR/LIBRADTRAN --with-libnetcdf=$HOME/repos/BUILD_DIR/NETCDF
sed -i "s/PYTHON.*/PYTHON = \/usr\/bin\/python2.7/" Makeconf
make uvspec
cd ..


export LIBRADTRANDIR=$HOME/repos/libRadtran-2.0.2/
export LIBRADTRAN_DIR=$HOME/repos/libRadtran-2.0.2/


cd $HOME/repos
git clone https://github.com/lsst/astro_metadata_translator.git
cd astro_metadata_translator
setup -j -r .
scons


cd $HOME/repos
git clone https://github.com/lsst-sitcom/rapid_analysis.git
cd rapid_analysis
setup -j -r .
scons
git checkout tickets/DM-21412


cd $HOME/repos
git clone https://github.com/lsst-dm/atmospec.git
cd atmospec
setup -j -r .
scons
git checkout tickets/DM-20823


cd $HOME/repos
git clone https://github.com/lsst-dm/Spectractor.git
cd Spectractor
git checkout tickets/DM-23284
pip install -r requirements.txt
pip install -e .


cd $HOME/repos
git clone https://github.com/lsst/obs_base.git
cd obs_base
setup -j -r .
scons


cd $HOME/repos
git clone https://github.com/lsst/obs_lsst.git
cd obs_lsst
git checkout u/mfl/feb2020_observing
setup -j -r .
scons


cd $HOME/repos
git clone https://github.com/lsst/cp_pipe.git
cd cp_pipe
setup -j -r .
scons

cd $HOME/repos
cd summit
python mySetup.py
