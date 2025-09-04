# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors: Oier Lauzirika Zarrabeitia (olauzirika@cnb.csic.es)
# * Authors: Mikel Iceta Tena (miceta@cnb.csic.es)
# *
# * Spanish National Center for Biotechnology (CNB)
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import os

from pyworkflow.constants import BETA
from pyworkflow.protocol.constants import LEVEL_ADVANCED
import pyworkflow.protocol.params as params
from pyworkflow.utils import Message

from pwem.protocols import EMProtocol
from pwem.objects import SetOfVolumes, Volume

from recovar import Plugin
from recovar.protocols import RecovarPipeline

class RecovarAnalyze(EMProtocol):
    _label = 'analyze'
    _devStatus = BETA
    
    def _defineParams(self, form: params.Form):
        form.addSection(label=Message.LABEL_INPUT)

        form.addHidden(params.USE_GPU, params.BooleanParam, default=True,
                           expertLevel=LEVEL_ADVANCED,
                           label="Use GPU?",
                           help="Set to True if you want to use GPU implementation."
                           )
        
        form.addHidden(params.GPU_LIST, params.StringParam, default='0',
                       expertLevel=LEVEL_ADVANCED,
                       label="Choose GPU IDs",
                       help="GPU may have several cores. Set it to zero"
                            " if you do not know what we are talking about."
                            " First core index is 0, second 1 and so on."
                            " Recovar can use multiple GPUs - in that case"
                            " set to i.e. *0 1 2*."
                            )

        form.addParam('pipelineProtocol', params.PointerParam,
                      pointerClass = RecovarPipeline,
                      important = True,
                      label = 'Pipeline protocol',
                      allowsNull = False,
                      help = ''
                      )
        
        form.addParam('numberOfClusters', params.IntParam, default=40, 
                      label='Number of clusters')

    # --------------------------- STEPS functions ------------------------------

    def _insertAllSteps(self):
        self._insertFunctionStep(self.runRecovarStep)
        self._insertFunctionStep(self.createOutputStep)

    def runRecovarStep(self):
        pipeline = self._getPipelineProtocol()

        program = 'recovar'

        args = []
        args.append('analyze')
        args.append(pipeline._getOutputDir())
        args += ['-o', self._getOutputDirectory()]
        args += ['--zdim', pipeline.zComponents.get()]
        args += ['--n-clusters', self.numberOfClusters.get()]

        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        Plugin.runRecovar(self, program, args)
        
    def createOutputStep(self):
        n = self.numberOfClusters.get()
        
        outputVolumes = SetOfVolumes.create(self._getPath())
        outputVolumes.setSamplingRate(
            self._getPipelineProtocol().inputParticles.get().getSamplingRate()
        )
        
        for i in range(n):
            vol = Volume(location=self._getOutputVolumeFile(i))
            outputVolumes.append(vol)
        
        self._defineOutputs(volumes=outputVolumes)

    # --------------------------- INFO functions ---------------------------------
    def _validate(self):
        errors = []
        
        pipeline = self._getPipelineProtocol()
        if not pipeline.isFinished():
            errors.append('The selected pipeline protocol must be finished.')
            
        return errors
        
    # --------------------------- UTILS functions --------------------------------
    def _getPipelineProtocol(self) -> RecovarPipeline:
        return self.pipelineProtocol.get()

    def _getOutputDirectory(self, *paths) -> str:
        return self._getExtraPath('analysis', *paths)
    
    def _getOutputVolumeFile(self, index: int) -> str:
        return self._getOutputDirectory(
            'kmeans_center_volumes', 
            'all_volumes', 
            'vol%04d.mrc' % index
        )