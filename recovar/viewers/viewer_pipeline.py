# **************************************************************************
# *
# * Authors:     Oier Lauzirika Zarrabeitia (oierlauzi@bizkaia.eu)
# * Authors: Mikel Iceta Tena (miceta@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
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

from pyworkflow.viewer import ProtocolViewer, DESKTOP_TKINTER, WEB_DJANGO
from pyworkflow.protocol.params import LabelParam, BooleanParam, FloatParam

from pwem.viewers import ChimeraView

from recovar.protocols import RecovarPipeline

class RecovarViewerPipeline(ProtocolViewer):
    _label = 'viewer pipeline'
    _targets = [RecovarPipeline]
    _environments = [DESKTOP_TKINTER, WEB_DJANGO]
    
    def __init__(self, **kwargs):
        ProtocolViewer.__init__(self, **kwargs)

    # --------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        form.addSection(label='Analysis')
        form.addParam('showConsensus', BooleanParam, default=True, label='Show consensus volume')
        form.addParam('eigenVolumeThreshold', FloatParam, default=8, label='Eigen-volume threshold')
        form.addParam('displayEigenVolume', LabelParam, label='Eigen-volumes')

    #--------------------------- INFO functions ----------------------------------------------------

    # --------------------------- DEFINE display functions ----------------------
    def _getVisualizeDict(self):
        return {
            'displayEigenVolume': self._displayEigenVolume,
        }

    def _displayEigenVolume(self, e):
        command = self._writeChimeraScript()
        return [ChimeraView(command)]
        
    # --------------------------- UTILS functions -----------------------------
    def _getEigenVolumeFilename(self, index: int) -> str:
        return self.protocol._getEigenVolumeFilename(index)
    
    def _getConsensusVolumeFilename(self) -> str:
        return self.protocol._getConsensusVolumeFilename()
    
    def _writeChimeraScript(self) -> str:
        scriptFile = self.protocol._getExtraPath('fusion_chimera.cxc')
        consensusVolumeFilename = os.path.abspath(self._getConsensusVolumeFilename())
        n = self.protocol.zComponents.get()
        
        with open(scriptFile, 'w') as f:
            for i in range(n):
                id = i+1
                eigenVolumeFilename = os.path.abspath(self._getEigenVolumeFilename(i))
                if self.showConsensus.get():
                    f.write('open %s id %d.1\n' % (consensusVolumeFilename, id))
                    f.write('color #%d.1 #9a9a9a80\n' % id)

                f.write('open %s id %d.2\n' % (eigenVolumeFilename, id))
                f.write('open %s id %d.3\n' % (eigenVolumeFilename, id))
                f.write('volume multiply #%d.2 #%d.3 modelId %d.4\n' % ((id, )*3))
                f.write('volume #%d.4 rmsLevel %f\n' % (i+1, self.eigenVolumeThreshold.get()))
                f.write('color sample #%d.4 map #%d.2 range -1e-12,1e-12\n' % ((id,)*2))
                f.write('close #%d.3\n' % id)
            f.write("tile\n")
            
        return scriptFile