source /opt/lsst/software/stack/loadLSST.bash

# eups distrib install -t w_2021_02 lsst_distrib
setup lsst_distrib -t w_2021_02

cd $HOME/repos
git clone https://github.com/lsst-dm/Spectractor.git
cd Spectractor
pip install -r requirements.txt
pip install -e .


cd $HOME/repos
git clone https://github.com/lsst-dm/atmospec.git
cd atmospec
setup -j -r .
scons


cd $HOME/repos
git clone https://github.com/lsst-sitcom/rapid_analysis.git
cd rapid_analysis
setup -j -r .
scons
git checkout tickets/DM-21412


cd $HOME/repos
git clone https://github.com/lsst/obs_base.git
cd obs_base
git checkout e9a044d8157728fd960c9d36e609540fc30973a4
setup -j -r .
scons


cd $HOME/repos
git clone https://github.com/lsst/pipe_tasks.git
cd obs_base
git checkout u/mfl/DM-27652-w_02_rebase
setup -j -r .
scons
