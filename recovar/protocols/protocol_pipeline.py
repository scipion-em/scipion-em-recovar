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
from pyworkflow.utils.path import createLink, makePath

from pwem.objects import SetOfParticles, SetOfParticlesFlex, VolumeMask
from pwem.protocols import EMProtocol

from recovar.convert import writeMetadata, readEmbedding, convertZsToNumpy
from recovar import Plugin
from recovar.constants import RECOVAR

class RecovarPipeline(EMProtocol):
    _label = 'pipeline'
    _devStatus = BETA
    
    def _defineParams(self, form: params.Form):
        """ Define the input parameters that will be used.
        Params:
            
        """
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

        form.addParam('inputParticles', params.PointerParam,
                      pointerClass = SetOfParticles,
                      pointerCondition = 'hasAlignmentProj', # TODO: Add validation for CTF in the validation section because aca no se puede
                      important = True,
                      label = 'Input particles',
                      allowsNull = False,
                      help = ''
                      )
        
        form.addParam('solventMask', params.PointerParam,
                      pointerClass = VolumeMask,
                      label = 'Solvent mask',
                      allowsNull = False,
                      help = ''
                      )
        
        form.addParam('focusMask', params.PointerParam,
                      pointerClass = VolumeMask,
                      label = 'Focus mask',
                      allowsNull = True,
                      help = ''
                      )
        
        form.addParam('zComponents', params.IntParam,
                      label = 'Number of Z components',
                      default = 20 )

    # --------------------------- STEPS functions ------------------------------

    def _insertAllSteps(self):
        self._insertFunctionStep(self.convertInputStep)
        self._insertFunctionStep(self.runRecovarStep)
        self._insertFunctionStep(self.createOutputStep)

    def convertInputStep(self):
        makePath(self._getImagesDatadir())

        writeMetadata(self.inputParticles.get(),
                      self._getPosesFilename(),
                      self._getCTFFilename(),
                      self._getImagesFilename())
        
        files = self.inputParticles.get().getFiles()
        for file in files:
            basename = os.path.basename(file)
            createLink(
                file, 
                self._getImagesDatadir(basename)
            )
        
    def runRecovarStep(self):
        program = 'recovar'

        args = []
        args.append('pipeline')
        args.append(self._getImagesFilename())
        args += ['--datadir', self._getImagesDatadir()]
        args += ['-o', self._getOutputDir()]
        args += ['--poses', self._getPosesFilename()]
        args += ['--ctf', self._getCTFFilename()]
        args += ['--zdim', self.zComponents.get()]
        args += ['--mask', self.solventMask.get().getFileName()]

        if self.focusMask.get() is not None:
            args += ['--focus-mask', self.focusMask.get().getFileName()]

        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        Plugin.runRecovar(self, program, args)
        
    def createOutputStep(self):
        fields = self._getOutputFields()
        for field in fields:
            outputParticles: SetOfParticlesFlex = SetOfParticlesFlex.create(
                self._getPath(),
                suffix=field,
                progName=RECOVAR
            )
            outputParticles.copyInfo(self.inputParticles.get())

            convertZsToNumpy(
                self, 
                self._getEmbeddingsFilename(), 
                self._getTemporaryNumpyEmbeddingsFilename(), 
                field
            )
            
            readEmbedding(
                outputParticles, 
                self.inputParticles.get(), 
                self._getTemporaryNumpyEmbeddingsFilename()
            )
            
            self._defineOutputs(**{field: outputParticles})
            self._defineSourceRelation(self.inputParticles, outputParticles)

    # --------------------------- INFO functions ---------------------------------
    # --------------------------- UTILS functions --------------------------------
    def _getImagesDatadir(self, *args) -> str:
        return self._getExtraPath('images', *args)

    def _getImagesFilename(self) -> str:
        return self._getImagesDatadir('images.star')

    def _getPosesFilename(self) -> str:
        return self._getExtraPath('poses.pkl')
    
    def _getCTFFilename(self) -> str:
        return self._getExtraPath('ctf.pkl')
    
    def _getOutputDir(self, *paths) -> str:
        return self._getExtraPath('output', *paths)
    
    def _getEmbeddingsFilename(self) -> str:
        return self._getOutputDir('model', 'embeddings.pkl')
    
    def _getEigenVolumeFilename(self, index: int) -> str:
        return self._getOutputDir('output', 'volumes', f'eigen_pos{index:04d}.mrc')
    
    def _getConsensusVolumeFilename(self) -> str:
        return self._getOutputDir('output', 'volumes', 'mean.mrc')
    
    def _getTemporaryNumpyEmbeddingsFilename(self) -> str:
        return self._getTmpPath('embedding.npy')
    
    def _getOutputFields(self) -> list:
        nz: int = self.zComponents.get()
        return [
            f'{nz}',
            f'{nz}_noreg'
        ]
