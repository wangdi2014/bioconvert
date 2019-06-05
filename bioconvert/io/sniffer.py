###########################################################################
# Bioconvert is a project to facilitate the interconversion               #
# of life science data from one format to another.                        #
#                                                                         #
# Authors: see CONTRIBUTORS.rst                                           #
# Copyright © 2018-2019  Institut Pasteur, Paris and CNRS.                #
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
"""Sniffer for all formats included in Bioconvert"""
from bioconvert.core.extensions import extensions

import colorlog
_log = colorlog.getLogger(__name__)


class Sniffer(object):
    """Sniffer for formats included in Bioconvert

    :attr:`bioconvert.core.extensions.extensions`

    ::

        >>> from bioconvert import Sniffer
        >>> s =  Sniffer()
        >>> s.sniff("test.clustal")
        "clustal"

    TSV and CSV matchess many formats. For example a BED file is compatible with
    the TSV format.

    If a file matches several 2 formats and includes a TSV/CSV, we ignore the
    TSV/CSV.


    """
    #formats = sorted(extensions.keys())

    def __init__(self):

        self.methods = [x for x in dir(self) if x.startswith("is")]

        # let us just check whether a format is missing
        self.formats = [x.replace("is_", "") for x in self.methods]
        for frmt in extensions.keys():
            if frmt not in self.formats:
                print('warning please add the is_{} method in the sniffer'.format(frmt))

    def sniff(self, filename):
        """Return first frmt found to be compatible with the input file"""

        candidates = []

        # If a fmrt is ods, it will be compatible with xls, xlxs etc leading
        # to an ambiguity. If there are several candidates found and the frmt
        # is found in the candidates, most probably this is the good one.
        # So we could first try the method is_frmt and if the answer is True, we
        # can stop there.
        try:
            extension = filename.split(".")[-1]
            func = getattr(self, "is_{}".format(extension))
            ret = func(filename)
            if ret is True:
                _log.debug("Confirm the format based on extension and is_{} function".format(
                    extension))
                candidates.append(extension)
            else:
                raise Error
        except:
            # otherwise, we should try all formats and methods available
            # 
            for frmt in self.formats:
                _log.debug("Trying {}".format(frmt))
                func = getattr(self, "is_{}".format(frmt))
                try:
                    ret = func(filename)
                    if ret is True:
                        candidates.append(frmt)
                except NotImplementedError:
                    pass

        if "tsv" in candidates or "csv" in candidates:
            _log.warning("Ignore TSV/CSV: {}".format(candidates))
            candidates = [x for x in candidates if x not in ["tsv", "csv"]]

        # bcf is known to also be gz
        for frmt in ['bam', 'bcf']:
            if frmt in candidates and "gz" in candidates:
                candidates = [x for x in candidates if x not in ["gz"]]

        if len(candidates) == 0:
            return None
        elif len(candidates) == 1:
            return candidates[0]
        else:
            _log.warning("Sniffer found several candidates: {}".format(candidates))
            return candidates

    def _is_blank_line(self, line):
        line = line.strip()
        if len(line) == 0:
            return True
        else:
            return False

    def _is_magic(self, filename, magic):
        """Figure out whether magic number of the file fits the argument."""

        data = open(filename, "rb")
        buff = data.read(56)
        L = len(magic)

        # we need at least L + 1 values
        if len(buff)<=L:
            return False

        # then, each magic number should fit the first bytes
        ret = [buff[i] == magic[i] for i in range(0, L)]

        if False in ret:
            return False
        else:
            return True

    def is_abi(self, filename):
        try:
            data = open(filename, "rb")
            buff = data.read(4)
            if buff[0:4].decode() == "ABIF":
                return True
        except:
            return False

    def is_bam(self, filename):
        try:
            import pysam
            d = pysam.AlignmentFile(filename)
            return d.is_bam
        except:
            return False

    def is_bcf(self, filename):
        try:
            import pysam
            d = pysam.VariantFile(filename)
            return d.is_bcf
        except:
            return False

    def is_binary_bed(self, filename):
        # This could be a BED binary file from plink or BEDGrapg
        # https://www.cog-genomics.org/plink2/formats#bed
        try:
            return self._is_magic(filename, [0x6c, 0x1b, 0x1])
        except:
            return False

    def is_bed(self, filename):
        try:
            data = open(filename, "r")
            line = data.readline()
            if len(line.split())<4:
                return False
            else:
                return True
        except:
            return False

    def is_bedgraph(self, filename):
        return self.is_bed(filename)

    def is_bigwig(self, filename):
        raise NotImplementedError

    def is_bigbed(self, filename):
        raise NotImplementedError

    def is_bplink(self, filename):
        raise NotImplementedError

    def is_bz2(self, filename):
        try:
            return self._is_magic(filename, [0x42, 0x5A, 0x68])
        except:
            return False

    def is_cdao(self, filename):
        raise NotImplementedError

    def is_csv(self, filename):

        try:
            import pandas as pd
            df = pd.read_csv(filename, sep=",")
            if len(df.columns) > 1:
                return True
        except:
            pass

    def is_cram(self, filename):
        try:
            import pysam
            d = pysam.AlignmentFile(filename)
            return d.is_cram
        except:
            return False

    def is_clustal(self, filename):
        with open(filename, "r") as fin:
            try:
                line = fin.readline().strip()
                if self._is_blank_line(line):
                    pass
                elif line.startswith("CLUSTAL"):
                    return True
            except:
                return False

    def is_dsrc(self, filename):
        try:
            # FIXME not sure whether we need more characters ?
            return self._is_magic(filename, [0xaa, 0x2])
        except:
            return False

    def is_embl(self, filename):
        raise NotImplementedError

    def is_ena(self, filename):
        try:

            data = open(filename, "r")
            L1 = data.readline()     
            if L1.startswith("ID"):
                return True
            else:
                return False
        except:
            return False


    def is_fasta(self, filename):
        # FIXME this is valid for FASTA 
        try:
            data = open(filename, "r")
            line1 = data.readline()
            line2 = data.readline()
            if line1.startswith(">") and line2[0] in "ABCDEFGHIKLMNPQRSTUVWYZX*-":
                return True
            else:
                return False
        except:
            return False

    def is_fastq(self, filename):
        try:
            data = open(filename, "r")
            line1 = data.readline()
            line2 = data.readline()
            line3 = data.readline()
            line4 = data.readline()
            if line1.startswith("@") and line3.startswith("+"):
                return True
            else:
                return False
        except:
            return False

    def is_genbank(self, filename):

        with open(filename, "r") as fin:
            try:
                line = fh.readline().strip()
                if self._is_blank_line(line):
                    pass
                else:
                    data = line.split()
                    data[0] in ['LOCUS']
                return True
            except:
                return False

    def is_gfa(self, filename):
        raise NotImplementedError

    def is_gff2(self, filename):
        try:
            with open(filename, "r") as fin:
                data = fin.readline()
                if "gff-version 2" in data.strip():
                    return True
                else:
                    return False
        except:
            return False

    def is_gff3(self, filename):
        try:
            with open(filename, "r") as fin:
                data = fin.readline()
                if "gff-version 3" in data.strip():
                    return True
                else:
                    return False
        except:
            return False


    def is_gz(self, filename):
        try:
            return self._is_magic(filename, [0x1f, 0x8b])
        except:
            return False

    def is_json(self, filename):
        try:
            import json
            with open(filename) as fin:
                data = fin.read()
                json.loads(data)
                return True
        except:
            return False

    def is_maf(self, filename):
        with open(filename, "r") as fin:
            try:
                # read at most 50 lines and figure out whether
                # some lines starts with a or s
                # we get rid of the comments.
                # Read 5000 characters at most.
                data = fin.readlines(5000)
                comments = [line for line in data if line.startswith('#')]
                data = [line.strip() for line in data if line.startswith('#') is False]

                # get rid of blank lines
                data = [line for line in data if len(line.strip())!=0]
                starts = [line[0:2] for line in data]

                if len(starts) == 0: 
                    return False

                # line must start with one of i, e, q, a, s letter
                for x in starts:
                    assert x in ['a ', 's ', 'e ', 'q ', 'i ']
                return True
            except Exception as err:
                _log.debug(err)
                return False

    def is_newick(self, filename):
        try:
            with open(filename, "r") as fin:
                data = fin.readlines()
                if data[0].strip()[0] == "(" and data[-1].strip()[-1] == ';':
                    return True
                else:
                    return False
        except:
            return False
        raise NotImplementedError

    def is_nexus(self, filename):
        try:
            with open(filename, "r") as fin:
                line = fin.readline()
                if line.startswith("#NEXUS"):
                    return True
                else:
                    return False
        except:
            return False

    def is_ods(self, filename):
        try:
            return self._is_magic(filename, [0x50, 0x4b, 0x03, 0x04])
        except:
            return False

    def is_paf(self, filename):
        raise NotImplementedError

    def is_phylip(self, filename):

        with open(filename, "r") as fin:
            # First, we figure out the dimensions of the alignemnt.
            # we should find 2 integers
            # blank lines are forbidden in  principle between header an
            # alignment
            try:
                header = fin.readline().strip()
                first = fin.readline().strip()
                m, n = header.split()
                m = int(m)
                n = int(n)
                name, seq = first.split(" ", 1)
                seq = seq.replace(" ", "")
                # we identify each alignement and check that the length are
                # identical and equal to n
                for this in range(1, m-1): # -1 since we already read 1 line
                    nextline = fin.readline().strip()
                    name, seq2 = nextline.split(" ", 1)
                    seq2= seq2.replace(" ","")
                    assert len(seq) == len(seq2), "not same length"
                return True
            except Exception as err:
                #print(err)
                return False

    def is_phyloxml(self, filename):
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(filename)
            tree.getroot()
            root = tree.getroot()
            if "phyloxml" in root.tag:
                return True
            else:
                return False
        except:
            return False

    def is_plink(self, filename):
        raise NotImplementedError

    def is_qual(self, filename):
        # if line1.startswith(">") and line2[0] in "ABCDEFGHIKLMNPQRSTUVWYZX*-":
        try:
            data = open(filename, "r")
            line1 = data.readline()
            line2 = data.readline()

            # we check the first line identifier. 
            # then, we scan the entire line searching of encoding qualities
            # hoping that values between 33 and 126 will be enough to
            # differentiate them from the standard nucleotides and protein
            # characters. 
            scores = [x for x in line2 if x not in "ABCDEFGHIKLMNPQRSTUVWYZX*-"]
            # if we find a character (e.g !, #ietc) it means is a quality file
            # however, if we do not find such a value, it does not mean it is
            # not a quality.

            # For instance, there is no way to say that ::
            #    >ID
            #    AACCTTGG
            # is a qual or fasta file
        

            if line1.startswith(">") and len(scores)>1:
                return True
            else:
                return False
        except:
            return False

    def is_sam(self, filename):
        try:
            import pysam
            d = pysam.AlignmentFile(filename)
            return d.is_sam
        except:
            return False

    def is_scf(self, filename):
        try:
            data = open(filename, "rb")
            buff = data.read(56)
            if buff[0:4].decode() == ".scf":
                return True
        except:
            return False

    def is_sra(self, filename):
        # not need. This is not a format.
        raise NotImplementedError

    def is_stockholm(self, filename):
        with open(filename, "r") as fin:
            try:
                header = fin.readline().strip()
                assert "STOCKHOLM" in header

                return True
            except:
                return False

    def is_rar(self, filename):
        try:
            c1 = self._is_magic(filename, [0x52, 0x61, 0x72, 0x21, 0x1A , 0x7, 0x0])
            c2 = self._is_magic(filename, [0x52, 0x61, 0x72, 0x21, 0x1A , 0x7, 0x0])
            if c1 or c2:
                return True
            else:
                return False
        except:
            return False

    def is_tar(self, filename):
        try:
            # length must be > 260
            return self._is_magic(filename, [0x75, 0x73, 0x74, 0x61, 0x72])
        except:
            return False

    def is_twobit(self, filename):
        try:
            data = open(filename, "rb")
            buff = data.read(16)
            if 0x43 in buff and 0x27 in buff:
               return True
            else:
                return False
        except:
            return False

    def is_tsv(self, filename):
        try:
            import pandas as pd
            df = pd.read_csv(filename, sep="\s+")
            if len(df.columns) > 1:
                return True
        except:
            pass

    def is_vcf(self, filename):
        try:
            import pysam
            d = pysam.VariantFile(filename)
            return d.is_vcf
        except:
            return False

    def is_wiggle(self, filename):
        raise NotImplementedError

    def is_wig(self, filename):
        raise NotImplementedError

    def is_xls(self, filename):
        try:
            return self._is_magic(filename, [0xd0, 0xcf, 0x11])
        except:
            return False

    def is_xlsx(self, filename):
        try:
            return self._is_magic(filename, [0xd0, 0xcf, 0x11])
        except:
            return False

    def is_xmfa(self, filename):
        try:
            with open(filename, "r") as fin:
                line = fin.readline()
                if "FormatVersion" in line and "Mauve" in line:
                    return True
                else:
                    return False
        except:
            return False

    def is_yaml(self, filename):
        raise NotImplementedError

    def is_zip(self, filename):
        try:
            c1 = self._is_magic(filename, [0x50,  0x4B, 0x3, 0x4])
            c2 = self._is_magic(filename, [0x50,  0x4B, 0x3, 0x4])
            c3 = self._is_magic(filename, [0x50,  0x4B, 0x3, 0x4])
            if c1 or c2 or c3:
                return True
            else:
                return False
        except:
            return False


    def is_7zip(self, filename):
        try:
            return self._is_magic(filename, [0x37, 0x7A, 0xbc, 0xaf,0x27, 0x1C])
        except:
            return False

    def is_xz(self, filename):
        try:
            return self._is_magic(filename, [0xFD, 0x37, 0x7A, 0x58, 0x5A, 0x00])
        except:
            return False
