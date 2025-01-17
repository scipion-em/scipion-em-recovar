# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors: Eugenio Pablo Murillo Solanas (ep.murillo@usp.ceu.es)
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

# Referenced merging RECOVAR's GitHub repository & bioRxiv's citation tools
"""
@article{gilles2023bayesian,
title = "A Bayesian Framework for Cryo-EM Heterogeneity Analysis using Regularized Covariance Estimation",
journal = "bioRxiv",
pages = "32",
year = "2024",
publisher = "Cold Spring Harbor Laboratory",
abstract = {Proteins and the complexes they form are central to nearly all cellular processes. Their flexibility, expressed through a continuum of states, provides a window into their biological functions. Cryogenic electron microscopy (cryo-EM) is an ideal tool to study these dynamic states as it captures specimens in non-crystalline conditions and enables high-resolution reconstructions. However, analyzing the heterogeneous distributions of conformations from cryo-EM data is challenging. We present RECOVAR, a method for analyzing these distributions based on principal component analysis (PCA) computed using a REgularized COVARiance estimator. RECOVAR is fast, robust, interpretable, expressive, and competitive with the state-of-art neural network methods on heterogeneous cryo-EM datasets. The regularized covariance method efficiently computes a large number of high-resolution principal components that can encode rich heterogeneous distributions of conformations and does so robustly thanks to an automatic regularization scheme. The novel reconstruction method based on adaptive kernel regression resolves conformational states to a higher resolution than all other tested methods on extensive independent benchmarks while remaining highly interpretable. Additionally, we exploit favorable properties of the PCA embedding to estimate the conformational density accurately. This density allows for better interpretability of the latent space by identifying stable states and low free-energy motions. Finally, we present a scheme to navigate the high-dimensional latent space by automatically identifying these low free-energy trajectories. We make the code freely available at https://github.com/ma-gilles/recovar. Competing Interest StatementThe authors have declared no competing interest.},
elocation-id = "2023.10.28.564422",
doi = "https://doi.org/10.1101/2023.10.28.564422",
url = "https://www.biorxiv.org/content/10.1101/2023.10.28.564422v4",
eprint = "https://www.biorxiv.org/content/early/2024/09/06/2023.10.28.564422.full.pdf",
author = "Gilles, Marc Aurèle T and Singer, Amit",
keywords = "RECOVAR Single Particle Analysis",
}
"""