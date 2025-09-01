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

from pwem.objects import SetOfParticles, Particle, Transform, CTFModel, Acquisition
from pwem.emlib.image import ImageHandler
from emtable import Table
import numpy as np
import pickle as pkl
from os.path import abspath

def writeMetadata(inputParticles: SetOfParticles, poseFilename: str, ctfFilename: str, imagesFilename: str):

    # Variables
    rotations = np.empty((len(inputParticles), 3, 3))
    shifts = np.empty((len(inputParticles), 2))
    ctfParams = np.empty((len(inputParticles), 9))
    images : Table = Table(columns=['rlnImageName'])
    ih = ImageHandler()

    particle : Particle
    ctf : CTFModel = CTFModel()
    for i, particle in enumerate(inputParticles):
        # Pose parameters
        transform : Transform = particle.getTransform()

        mat = transform.getRotationMatrix()
        shiftX, shiftY, _ = transform.getShifts()

        rotations[i] = mat
        shifts[i] = [shiftX, shiftY]

        # CTF parameters, ONLY the variable ones
        ctf = particle.getCTF()
        ctfParams[i, 2:5] = [ctf.getDefocusU(), ctf.getDefocusV(), ctf.getDefocusAngle()]

        # Add image name to the table
        #position, filename = particle.getLocation()
        #filename = abspath(filename)
        images.addRow(ih.locationToXmipp(particle.getLocation()))

    # Write the consolidated Rln-formatted image stack
    images.write(imagesFilename, "particles")
    
    # Assign constant CTF parameters
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

    # Convert pose information into new format: fraction of box size
    shifts /= inputParticles.getDimensions()[0:2]

    # Write poses
    with open(poseFilename, 'wb') as f:
        pkl.dump((rotations, shifts), f)   

    # Write CTFs
    with open(ctfFilename, 'wb') as f:
        pkl.dump(ctfParams, f)


