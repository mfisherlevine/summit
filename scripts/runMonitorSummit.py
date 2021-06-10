# This file is part of rapid_analysis.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
from time import sleep
from pathlib import Path
from google.cloud import storage

import lsst.daf.persistence as dafPersist
from lsst.pex.exceptions import NotFoundError
from lsst.rapid.analysis.bestEffort import BestEffortIsr
from lsst.rapid.analysis.imageExaminer import ImageExaminer
from lsst.rapid.analysis.summarizeImage import SummarizeImage
from lsst.atmospec.utils import isDispersedExp

# TODO: maybe add option to create display and return URL?


# all things used by the pool workers live outside the class
def _dataIdToFilename(prefix, dataId, outputRoot):
    filename = f"{prefix}_dayObs_{dataId['dayObs']}_seqNum_{dataId['seqNum']}.png"
    return os.path.join(outputRoot, filename)


def _imExamine(exp, dataId, outputRoot):
    filename = _dataIdToFilename('imExam', dataId, outputRoot)
    if os.path.exists(filename):
        print(f"Skipping {filename}")
        return
    imexam = ImageExaminer(exp, savePlots=filename, doTweakCentroid=True)
    imexam.plot()
    return filename


def runImExam(exp, dataId, outputRoot):
    try:
        writtenFile = _imExamine(exp, dataId, outputRoot)
        return writtenFile
    except Exception as e:
        print(f"Skipped imExam on {dataId} because {e}")
        return None


def _spectrumSummarize(exp, dataId, outputRoot):
    filename = _dataIdToFilename('spectrumSummary', dataId, outputRoot)
    if os.path.exists(filename):
        print(f"Skipping {filename}")
        return
    summary = SummarizeImage(exp, savePlotAs=filename)
    summary.run()
    return filename


def runSpectrumSummary(exp, dataId, outputRoot):
    try:
        writtenFile = _spectrumSummarize(exp, dataId, outputRoot)
        return writtenFile
    except Exception as e:
        print(f"Skipped imExam on {dataId} because {e}")
        return None


class Monitor():
    cadence = 1  # in seconds
    runIsr = True
    client = storage.Client()
    bucket = client.get_bucket('rubintv_data')

    def __init__(self, repoDir, doWriteImExams=False,
                 imExamOutputPath='',
                 **kwargs):
        """"""
        self.repoDir = repoDir
        self.bestEffort = BestEffortIsr(repoDir, **kwargs)
        outpath = os.path.join(repoDir, 'rerun/quickLook')
        self.butler = dafPersist.Butler(outpath)
        self.doWriteImExams = doWriteImExams
        if self.doWriteImExams:
            assert imExamOutputPath != '', "Must provide output path when writing imExams"
        self.imExamOutputPath = imExamOutputPath

    def googleUpload(self, filename, prefix):
        prefixes = ["summit_imexam", "summit_specexam"]
        if prefix not in prefixes:
            print(f"Error: {prefix} not in {prefixes}")
            return

        path = Path(filename)
        blob = self.bucket.blob("/".join([prefix, path.name]))
        blob.upload_from_filename(filename)

    def _getLatestExpId(self):
        return sorted(self.butler.queryMetadata('raw', 'expId'))[-1]

    def _getDayObsSeqNumFromExpId(self, expId):
        return self.butler.queryMetadata('raw', ['dayObs', 'seqNum'], expId=expId)[0]

    def _getLatestImageDataIdAndExpId(self):
        expId = self._getLatestExpId()
        dayObs, seqNum = self._getDayObsSeqNumFromExpId(expId)
        dataId = {'dayObs': dayObs, 'seqNum': seqNum}
        return dataId, expId

    def run(self, durationInSeconds=-1):

        if durationInSeconds == -1:
            nLoops = int(1e9)
        else:
            nLoops = int(durationInSeconds//self.cadence)

        lastDisplayed = -1
        for i in range(nLoops):
            try:
                dataId, expId = self._getLatestImageDataIdAndExpId()

                if lastDisplayed == expId:
                    sleep(self.cadence)
                    continue

                if self.runIsr:
                    exp = self.bestEffort.getExposure(dataId)
                else:
                    exp = self.butler.get('raw', **dataId)

                lastDisplayed = expId

                # run imexam here
                if self.imExamOutputPath:
                    print('Running imexam...')
                    filename = runImExam(exp, dataId, self.imExamOutputPath)
                    if filename:
                        print("Uploading imExam to storage bucket")
                        self.googleUpload(filename, 'summit_imexam')
                        print('Upload complete')

                    if isDispersedExp(exp):
                        print('Running spectrum summary...')
                        filename = runSpectrumSummary(exp, dataId, self.imExamOutputPath)
                        if filename:
                            print("Uploading specExam to storage bucket")
                            self.googleUpload(filename, 'summit_specexam')
                            print('Upload complete')

                    print('Finished generating plots, waiting for next image...')

            except NotFoundError as e:  # NotFoundError when filters aren't defined
                print(f'Skipped displaying {dataId} due to {e}')
        return


if __name__ == '__main__':
    repoDir = '/project/shared/auxTel/'
    imExamOutputPath = '/home/mfisherlevine/autoPlotting/'

    monitor = Monitor(repoDir,
                      doWriteImExams=True,
                      imExamOutputPath=imExamOutputPath)
    monitor.run()
