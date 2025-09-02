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

import pickle as pkl
import numpy as np
import argparse

def __convert_embedding_keys(embeddings):
    result = {}
    
    for key, value in embeddings.items():
        result[str(key)] = value
        
    return result

def __read_embeddings(inputFilename: str):
    with open(inputFilename, 'rb') as f:
        embeddings = pkl.load(f)
        
    return __convert_embedding_keys(embeddings['zs'])

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description="Convert recovar embeddings to a numpy file"
    )
    
    argparser.add_argument('-i', '--input', type=str, help="Recovar's embaedding file")
    argparser.add_argument('-o', '--output', type=str, help="Converted numpy file")
    argparser.add_argument('-f', '--field', type=str, help="Embedding field to extract")

    args = argparser.parse_args()
    inputFilename = args.input
    outputFilename = args.output
    field = args.field
    
    embeddings = __read_embeddings(inputFilename)
    print(embeddings.keys())
    zs = embeddings[field]
    
    np.save(outputFilename, zs)
    