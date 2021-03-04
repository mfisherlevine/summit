source /opt/lsst/software/stack/loadLSST.bash
setup lsst_distrib -t w_2021_10

mkdir -p $HOME/repos

cd $HOME/repos
git clone https://github.com/lsst-dm/Spectractor.git
cd Spectractor
git checkout tickets/DM-28773
git pull
pip install -r requirements.txt
pip install -e .


cd $HOME/repos
git clone https://github.com/lsst-dm/atmospec.git
cd atmospec
setup -j -r .
git checkout tickets/DM-26719
scons opt=3 -j 4


cd $HOME/repos
git clone https://github.com/lsst-sitcom/rapid_analysis.git
cd rapid_analysis
setup -j -r .
scons opt=3 -j 4
git checkout tickets/DM-21412
