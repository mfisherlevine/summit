import os
import shutil
HOMEDIR = os.environ['HOME']

KERNEL_JSON = """{
 "argv": [
  "/opt/lsst/software/stack/python/miniconda3-4.7.10/envs/lsst-scipipe-4d7b902/bin/python",
  "-m",
  "ipykernel_launcher",
  "-f",
  "{connection_file}"
 ],
 "display_name": "Python 3",
 "language": "python"
"""


def textToFile(filename, text):
    with open(filename, "w") as f:
        f.write(text)


def continuePrompt(message):
    print(message)
    cont = input("Press y to continue, anything else to quit:")
    if cont.lower()[0] != 'y':
        exit()


def makeKernel():
    kernelDir = os.path.join(HOMEDIR, ".local/share/jupyter/kernels/merlins_kernel")
    kernelFilename = os.path.join(HOMEDIR, ".local/share/jupyter/kernels/merlins_kernel/kernel.json")
    if not os.path.exists(kernelDir):
        os.makedirs(kernelDir)
    if os.path.exists(kernelFilename):
        continuePrompt(f"Trying to overwrite existing kernel file {kernelFilename}")
    textToFile(kernelFilename, KERNEL_JSON)


if __name__ == '__main__':
    makeKernel()
