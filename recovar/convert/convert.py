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

import numpy as np
import pickle as pkl
import os.path

from pwem.objects import (SetOfParticles, Particle, SetOfParticlesFlex, ParticleFlex, 
                          Transform, CTFModel, Acquisition)
from pwem.emlib.image import ImageHandler
from emtable import Table
from recovar import Plugin

def writeMetadata(inputParticles: SetOfParticles, 
                  poseFilename: str, 
                  ctfFilename: str, 
                  imagesFilename: str ):

    rotations = np.empty((len(inputParticles), 3, 3))
    shifts = np.empty((len(inputParticles), 2))
    ctfParams = np.empty((len(inputParticles), 9))
    images : Table = Table(columns=['rlnImageName'])
    ih = ImageHandler()

    particle : Particle
    ctf : CTFModel = CTFModel()
    for i, particle in enumerate(inputParticles):
        # Poses
        transform : Transform = particle.getTransform()
        matrix = transform.getMatrix()
        matrix = np.linalg.inv(matrix)

        rotations[i] = matrix[0:3, 0:3]
        shifts[i] = -matrix[0:2, 3]

        # CTFs
        ctf = particle.getCTF()
        ctfParams[i, 2:5] = [ctf.getDefocusU(), ctf.getDefocusV(), ctf.getDefocusAngle()]

        # Image location
        images.addRow(ih.locationToXmipp(particle.getLocation()))

    acquisition : Acquisition = inputParticles.getAcquisition()
    ctfParams[:, 0] = inputParticles.getDimensions()[0]
    ctfParams[:, 1] = inputParticles.getSamplingRate()
    ctfParams[:, 5] = acquisition.getVoltage()
    ctfParams[:, 6] = acquisition.getSphericalAberration()
    ctfParams[:, 7] = acquisition.getAmplitudeContrast()
    ps = ctf.getPhaseShift()
    if ps is None:
        print("WARNING: Phase shift not defined, setting to 0.0")
        ctfParams[:, 8] = 0.0
    else:
        ctfParams[:, 8] = ctf.getPhaseShift()

    shifts /= inputParticles.getDimensions()[0:2]

    images.write(imagesFilename, "particles")

    # Write poses
    with open(poseFilename, 'wb') as f:
        pkl.dump((rotations, shifts), f)   

    # Write CTFs
    with open(ctfFilename, 'wb') as f:
        pkl.dump(ctfParams, f)

def readEmbedding(setOfParticlesFlex: SetOfParticlesFlex, 
                  inputParticles: SetOfParticles,
                  embeddingsFilename: str):
    embeddings = np.load(embeddingsFilename)
    
    particle: Particle
    embedding: np.ndarray
    for particle, embedding in zip(inputParticles, embeddings):
        flexParticle = ParticleFlex('recovar')
        flexParticle.copyInfo(particle)
        flexParticle.setZFlex(embedding)
        setOfParticlesFlex.append(flexParticle)

def convertZsToNumpy(protocol, zsFilename: str, numpyFilename: str, field: str):
    PYTHON = 'python'
    script = os.path.join(os.path.dirname(__file__), 'convert_zs.py')

    program = f'{PYTHON} {script}'
    args = []
    args += ['-i', zsFilename]
    args += ['-o', numpyFilename]
    args += ['-f', field]
    
    Plugin.runRecovar(protocol, program, args)
