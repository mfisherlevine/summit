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
import numpy as np
from multiprocessing import Pool

import lsst.daf.persistence as dafPersist
import lsst.afw.cameraGeom.utils as cgUtils
from lsst.pex.exceptions import NotFoundError
from lsst.rapid.analysis.bestEffort import BestEffortIsr
from lsst.rapid.analysis.imageExaminer import ImageExaminer
from lsst.rapid.analysis.summarizeImage import SummarizeImage
from lsst.rapid.analysis.utils import isExpDispersed

import lsst.geom as geom
from time import sleep

# TODO: maybe add option to create display and return URL?

# all things used by the pool workers live outside the class
def _dataIdToFilename(prefix, dataId, outputRoot):
    filename = f"{prefix}_dayObs_{dataId['dayObs']}_seqNum_{dataId['seqNum']}.png"
    return os.path.join(outputRoot, filename)

def _buildArgs(exp, dataId, outputRoot, rsyncDestination):
    return [(exp, dataId, outputRoot, rsyncDestination)]

def _imExamine(exp, dataId, outputRoot):
    filename = _dataIdToFilename('imExam', dataId, outputRoot)
    if os.path.exists(filename):
        print(f"Skipping {filename}")
        return
    imexam = ImageExaminer(exp, savePlots=filename, doTweakCentroid=True)
    imexam.plot()
    return filename

def _sendFile(filename, rsyncDestination):
    args = f'rsync {filename} {rsyncDestination}'
    os.system(args)

def runImExam(exp, dataId, outputRoot, rsyncDestination):
    try:
        writtenFile = _imExamine(exp, dataId, outputRoot)
        fullRsyncDest = f"{rsyncDestination}/imExam/"
        _sendFile(writtenFile, fullRsyncDest)
    except Exception as e:
        print(f"Skipped imExam on {dataId} because {e}")
        
def _spectrumSummarize(exp, dataId, outputRoot):
    filename = _dataIdToFilename('spectrumSummary', dataId, outputRoot)
    if os.path.exists(filename):
        print(f"Skipping {filename}")
        return
    summary = SummarizeImage(exp, savePlotAs=filename)
    summary.run()
    return filename

def runSpectrumSummary(exp, dataId, outputRoot, rsyncDestination):
    try:
        writtenFile = _spectrumSummarize(exp, dataId, outputRoot)
        fullRsyncDest = f"{rsyncDestination}/spectrumSummaries/"
        _sendFile(writtenFile, fullRsyncDest)
    except Exception as e:
        print(f"Skipped imExam on {dataId} because {e}")

class Monitor():
    cadence = 1  # in seconds
    runIsr = True

    def __init__(self, repoDir, fireflyDisplay, doWriteImExams=False,
                 imExamOutputPath='',
                 rsyncDestination='',
                 **kwargs):
        """"""
        self.repoDir = repoDir
        self.display = fireflyDisplay
        self.bestEffort = BestEffortIsr(repoDir, **kwargs)
        self.writeQuickLookImages = None
        outpath = os.path.join(repoDir, 'rerun/quickLook')
        self.butler = dafPersist.Butler(outpath)
        self.overlayAmps = False  # do the overlay?
        self.doWriteImExams = doWriteImExams
        if self.doWriteImExams:
            assert imExamOutputPath != '', "Must provide output path when writing imExams"
        self.imExamOutputPath = imExamOutputPath
        self.rsyncDestination = rsyncDestination
        

    def _getLatestExpId(self):
        return sorted(self.butler.queryMetadata('raw', 'expId'))[-1]

    def _getDayObsSeqNumFromExpId(self, expId):
        return self.butler.queryMetadata('raw', ['dayObs', 'seqNum'], expId=expId)[0]

    def _getLatestImageDataIdAndExpId(self):
        expId = self._getLatestExpId()
        dayObs, seqNum = self._getDayObsSeqNumFromExpId(expId)
        dataId = {'dayObs': dayObs, 'seqNum': seqNum}
        return dataId, expId

    def _calcImageStats(self, exp):
        elements = []
        median = np.median(exp.image.array)
        elements.append(f"Median={median:.2f}")
        mean = np.mean(exp.image.array)
        # elements.append(f"Median={median:.2f}")
        elements.append(f"Mean={mean:.2f}")

        return elements

    def _makeImageInfoText(self, dataId, exp, asList=False):
        # TODO: add the following to the display:
        # az, el, zenith angle
        # main source centroid
        # PSF
        # num saturated pixels (or maybe just an isSaturated bool)
        # main star max ADU (post isr)

        elements = []

        imageType = self.butler.queryMetadata('raw', 'imageType', dataId)[0]
        obj = None
        if imageType.upper() not in ['BIAS', 'DARK', 'FLAT']:
            try:
                obj = self.butler.queryMetadata('raw', 'OBJECT', dataId)[0]
                obj = obj.replace(' ', '')
            except Exception:
                pass

        for k, v in dataId.items():  # dataId done per line for vertical display
            elements.append(f"{k}:{v}")

        if obj:
            elements.append(f"{obj}")
        else:
            elements.append(f"{imageType}")

        expTime = exp.getInfo().getVisitInfo().getExposureTime()
        filt = exp.getFilter().getName()

        elements.append(f"{expTime}s exp")
        elements.append(f"{filt}")

        elements.extend(self._calcImageStats(exp))

        if asList:
            return elements
        return " ".join([e for e in elements])

    def _printImageInfo(self, elements):
        size = 3
        top = 3850  # just under title for size=3
        xnom = -600  # 0 is the left edge of the image
        vSpacing = 100  # about right for size=3, can make f(size) if needed

        # TODO: add a with buffering and a .flush()
        # Also maybe a sleep as it seems buggy
        for i, item in enumerate(elements):
            y = top - (i*vSpacing)
            x = xnom + (size * 18.5 * len(item)//2)
            self.display.dot(str(item), x, y, size, ctype='red', fontFamily="courier")
            

    def run(self, durationInSeconds=-1):

        if durationInSeconds == -1:
            nLoops = int(1e9)
        else:
            nLoops = int(durationInSeconds//self.cadence)
            
        pool = Pool(4)

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

                print(f"Displaying {dataId}...")
                imageInfoText = self._makeImageInfoText(dataId, exp, asList=True)
                # too long of a title breaks Java FITS i/o
                fireflyTitle = " ".join([s for s in imageInfoText])[:67]
                self.display.scale('asinh', 'zscale')
                self.display.mtv(exp, title=fireflyTitle)
                if self.overlayAmps:
                    cgUtils.overlayCcdBoxes(exp.getDetector(), display=self.display, isTrimmed=True)

                self._printImageInfo(imageInfoText)
                lastDisplayed = expId
                
                # run imexam here
                if self.imExamOutputPath:
                    print('Running imexam...')
                    args = _buildArgs(exp, dataId, self.imExamOutputPath, self.rsyncDestination)
                    pool.starmap(runImExam, args)

                    if isExpDispersed(exp):
                        print('Running spectrum summary...')
                        args = _buildArgs(exp, dataId, self.imExamOutputPath, self.rsyncDestination)
                        pool.starmap(runSpectrumSummary, args)    
                        
                    print('Finished spawning sub-plotting')
                
                if self.writeQuickLookImages:
                    print(f"Writing quickLookExp for {dataId}")
                    self.butler.put(exp, "quickLookExp", dataId)

            except NotFoundError as e:  # NotFoundError when filters aren't defined
                print(f'Skipped displaying {dataId} due to {e}')
        return

if __name__ == '__main__':
    repoDir = '/project/shared/auxTel/'
    rsyncDestination = 'merlin@162.245.221.96:/data'
    imExamOutputPath = '/home/mfisherlevine/autoPlotting/'

    import os
    import lsst.afw.display as afwDisplay
    afwDisplay.setDefaultBackend('lsst.display.firefly')
    display1 = afwDisplay.getDisplay(frame=1, name='LATISS_monitor_background',
                                     url=os.environ['FIREFLY_URL'])	

    monitor = Monitor(repoDir, display1,
                      doWriteImExams=True,
                      imExamOutputPath=imExamOutputPath,
                      rsyncDestination=rsyncDestination)
    monitor.writeQuickLookImages = False
    monitor.run()
