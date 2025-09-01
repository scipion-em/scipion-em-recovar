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

RECOVAR = 'recovar'

# Supported versions
V0_4_5 = "0.4.5"  # Released March 17, 2025
VERSIONS = [V0_4_5]
RECOVAR_DEFAULT_VERSION = V0_4_5

RECOVAR_ENV_BASE_NAME = "recovar"
RECOVAR_ENV_ACTIVATION = "RECOVAR_ENV_ACTIVATION"

DEFAULT_ENV_NAME = f"{RECOVAR}-{RECOVAR_DEFAULT_VERSION}"
DEFAULT_ACTIVATION_CMD = 'conda activate ' + DEFAULT_ENV_NAME
