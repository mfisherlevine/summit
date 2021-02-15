source /opt/lsst/software/stack/loadLSST.bash
setup lsst_distrib -t w_2021_07

mkdir -p $HOME/repos

cd $HOME/repos
git clone https://github.com/lsst-dm/Spectractor.git
cd Spectractor
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


cd $HOME/repos
git clone https://github.com/lsst/obs_base.git
cd obs_base
setup -j -r .
scons opt=3 -j 4


cd $HOME/repos
git clone https://github.com/lsst/pipe_tasks.git
cd pipe_tasks
git checkout tickets/DM-27652
setup -j -r .
scons opt=3 -j 4
