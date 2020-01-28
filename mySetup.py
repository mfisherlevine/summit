import os
HOMEDIR = os.environ['HOME']

KERNEL_JSON = """{
 "argv": [
  "/home/saluser/.local/share/jupyter/kernels/new_kernel/launch.sh",
  "{connection_file}"
 ],
 "display_name": "Local setup",
 "language": "python"
}
"""

KERNEL_SCRIPT = """#!/bin/bash
set -x
CONFIG_FILE=$1

source /opt/lsst/software/stack/loadLSST.bash
# conda activate lsst-scipipe-4d7b902

if [ -e ${HOME}/notebooks/.user_setups ]; then
    source ${HOME}/notebooks/.user_setups
fi

exec /opt/lsst/software/stack/python/miniconda3-4.7.10/envs/lsst-scipipe-4d7b902/bin/python -m ipykernel -f ${CONFIG_FILE}

"""

USER_CONFIG = """
setup lsst_distrib -t w_2020_03

setup -j atmospec -r $HOME/repos/atmospec
setup -j rapid_analysis -r $HOME/repos/rapid_analysis
setup -j obs_base -r $HOME/repos/obs_base
setup -j obs_lsst -r $HOME/repos/obs_lsst

"""


def textToFile(filename, text):
    if os.path.exists(filename):
        continuePrompt(f"Trying to overwrite existing file {filename}")
    with open(filename, "w") as f:
        f.write(text)


def continuePrompt(message):
    print(message)
    cont = input("Press y to continue, anything else to quit:")
    if cont.lower()[0] != 'y':
        exit()


def makeKernel():
    kernelDir = os.path.join(HOMEDIR, ".local/share/jupyter/kernels/new_kernel")
    kernelFilename = os.path.join(kernelDir, "kernel.json")
    launchScriptFilename = os.path.join(kernelDir, "launch.sh")
    if not os.path.exists(kernelDir):
        os.makedirs(kernelDir)

    textToFile(kernelFilename, KERNEL_JSON)
    print(f"Wrote kernel file to {kernelFilename}")

    textToFile(launchScriptFilename, KERNEL_SCRIPT)
    print(f"Wrote launch script to {launchScriptFilename}")

    os.chmod(launchScriptFilename, 0o755)

    userConfigFileDir = os.path.join(HOMEDIR, 'notebooks')  # to mimic the LSP
    if not os.path.exists(userConfigFileDir):
        os.makedirs(userConfigFileDir)
    userConfigFilename = os.path.join(userConfigFileDir, ".user_setups")
    textToFile(userConfigFilename, USER_CONFIG)
    print(f"Wrote user config to {userConfigFilename}")


if __name__ == '__main__':
    makeKernel()
