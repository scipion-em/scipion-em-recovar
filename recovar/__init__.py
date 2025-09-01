# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors: Eugenio Pablo Murillo Solanas (ep.murillo@usp.ceu.es)
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
import pyworkflow.utils as pwutils
import pwem

from recovar.constants import *

__version__ = "0.1"  # plugin version
_logo = "icon.png"
_references = ['gilles2023bayesian']


class Plugin(pwem.Plugin):
    _url = "https://github.com/scipion-em/scipion-em-recovar"
    _supportedVersions = VERSIONS # binary version

    @classmethod
    def _defineVariables(cls):
        cls._defineVar(RECOVAR_ENV_ACTIVATION, DEFAULT_ACTIVATION_CMD)

    @classmethod
    def getEnviron(cls):
        """ Setup the environment variables needed to launch my program. """
        environ = pwutils.Environ(os.environ)

        return environ

    @classmethod
    def getDependencies(cls):
        """ Return a list of dependencies. """
        neededProgs = []
        return neededProgs

    @classmethod
    def defineBinaries(cls, env):
        for ver in cls._supportedVersions:
            cls.addRecovarPackage(env, ver, default = (ver == RECOVAR_DEFAULT_VERSION))
                       
    @classmethod
    def addRecovarPackage(cls, env, version, default = False):
        RECOVAR_INSTALLED = f'recovar_{version}_installed'
        
        condaEnvCmd = cls.getCondaActivationCmd()
        # Environment creation
        RECOVAR_ENV_NAME = f"{RECOVAR_ENV_BASE_NAME}-{version}"
        condaEnvCmd += f' conda create -y -n {RECOVAR_ENV_NAME} python=3.11 && '
        condaEnvCmd += f' conda activate {RECOVAR_ENV_NAME} && '
        # Actual packages installation
        condaEnvCmd += f' pip install git+https://github.com/scikit-fmm/scikit-fmm.git -f https://download.pytorch.org/whl/torch_stable.html torch==2.3.1+cpu "jax[cuda12]"==0.5.0 recovar=={version} && '
        condaEnvCmd += f' touch {RECOVAR_INSTALLED}'
        installationCmds = [(condaEnvCmd, RECOVAR_INSTALLED)]

        envPath = os.environ.get('PATH', "")  # keep path since conda likely in there
        installEnvVars = {'PATH': envPath} if envPath else None

        env.addPackage(RECOVAR,
                       version=version,
                       tar='void.tgz',
                       commands=installationCmds,
                       neededProgs=cls.getDependencies(),
                       vars=installEnvVars,
                       default=default)
        
    @classmethod
    def getRecovarEnvActivation(cls):
        return cls.getVar(RECOVAR_ENV_ACTIVATION)
        
    @classmethod
    def runRecovar(cls, protocol, program, args, cwd=None):
        fullProgram = '%s %s && %s' % (cls.getCondaActivationCmd(),
                                       cls.getRecovarEnvActivation(), program)
        protocol.runJob(fullProgram, args, env=cls.getEnviron(), cwd=cwd,
                        numberOfMpi=1)
                       
