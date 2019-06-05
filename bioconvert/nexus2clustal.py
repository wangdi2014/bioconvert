# -*- coding: utf-8 -*-
###########################################################################
# Bioconvert is a project to facilitate the interconversion               #
# of life science data from one format to another.                        #
#                                                                         #
# Authors: see CONTRIBUTORS.rst                                           #
# Copyright © 2018  Institut Pasteur, Paris and CNRS.                     #
# See the COPYRIGHT file for details                                      #
#                                                                         #
# bioconvert is free software: you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by    #
# the Free Software Foundation, either version 3 of the License, or       #
# (at your option) any later version.                                     #
#                                                                         #
# bioconvert is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of          #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
# GNU General Public License for more details.                            #
#                                                                         #
# You should have received a copy of the GNU General Public License       #
# along with this program (COPYING file).                                 #
# If not, see <http://www.gnu.org/licenses/>.                             #
###########################################################################
"""Converts :term:`NEXUS` file to :term:`CLUSTAL` file."""
import os
import colorlog
from Bio import SeqIO

from bioconvert import ConvBase
from bioconvert.core.decorators import requires

_log = colorlog.getLogger(__name__)


__all__ = ['NEXUS2CLUSTAL']


class NEXUS2CLUSTAL(ConvBase):
    """
    Converts a sequence alignment from :term:`NEXUS` format to :term:`CLUSTAL` format. ::

        converter = NEXUS2CLUSTAL(infile, outfile)
        converter(method='goalign')

    default method = goalign
    available methods = goalign
    """
    _default_method = 'goalign'

    def __init__(self, infile, outfile=None, alphabet=None, *args, **kwargs):
        """.. rubric:: constructor

        :param str infile: input :term:`NEXUS` file.
        :param str outfile: (optional) output :term:`CLUSTAL` file
        """
        super().__init__(infile, outfile)
        self.alphabet = alphabet

    @requires("go")
    def _method_goalign(self, threads=None, *args, **kwargs):
        """
        Convert :term:`NEXUS` file in  :term:`CLUSTAL` format using goalign tool.
        https://github.com/fredericlemoine/goalign

        :param threads: not used.
        """
        self.install_tool('goalign')
        cmd = 'goalign reformat clustal --nexus -i {infile} -o {outfile}'.format(
            infile=self.infile,
            outfile=self.outfile)
        self.execute(cmd)

    @requires(python_library="biopython")
    def _method_biopython(self, threads=None, *args, **kwargs):
         from Bio import AlignIO
         alignments = list(AlignIO.parse(self.infile, "nexus", alphabet=self.alphabet))
         AlignIO.write(alignments, self.outfile, "clustal")

    @requires("squizz")
    def _method_squizz(self, threads=None, *args, **kwargs):
        """
        Convert :term:`NEXUS` file in :term:`CLUSTAL` format using squizz tool.
        The CLUSTAL output file contains the consensus line

        for instance ::

            read3           -AT-
            read2           -AAG
            read4           -AGG
                             *

        :param threads: not used
        """
        cmd = 'squizz -c CLUSTAL {infile} > {outfile}'.format(
            infile=self.infile,
            outfile=self.outfile)
        self.execute(cmd)
