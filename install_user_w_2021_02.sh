source /opt/lsst/software/stack/loadLSST.bash
setup lsst_distrib -t w_2021_02

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
git checkout e9a044d8157728fd960c9d36e609540fc30973a4
setup -j -r .
scons opt=3 -j 4


cd $HOME/repos
git clone https://github.com/lsst/pipe_tasks.git
cd pipe_tasks
git checkout u/mfl/DM-27652-w_02_rebase
setup -j -r .
scons opt=3 -j 4
