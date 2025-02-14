#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""util.py: Contains utility functions for the demultiplexer package."""

from pathlib import Path
from typing import Optional, Callable, List, Dict, Tuple, Any, Union
from pandas import DataFrame
from dataclasses import dataclass, replace
import pandas as pd
import tempfile
import shutil
import pypipegraph as ppg
import collections
import mbf_align
import re

try:
    import string

    maketrans = string.maketrans
except (ImportError, NameError, AttributeError):
    maketrans = bytes.maketrans


__author__ = "Marco Mernberger"
__copyright__ = "Copyright (c) 2020 Marco Mernberger"
__license__ = "mit"


rev_comp_table = maketrans(b"ACBDGHKMNSRUTWVYacbdghkmnsrutwvy", b"TGVHCDMKNSYAAWBRTGVHCDMKNSYAAWBR")


AdapterMatch = collections.namedtuple(
    "AdapterMatch", ["astart", "astop", "rstart", "rstop", "matches", "errors"]
)


@dataclass
class Read:
    """Data class for sequencing reads"""

    Name: str
    Sequence: str
    Quality: str


class Fragment:
    """Data class for single-end and paired-end Reads/Fragments."""

    def __init__(self, *reads: Read):
        self.reads = reads
        self.Read1 = self.reads[0]
        if len(reads) == 2:
            self.Read2 = self.reads[1]

    def __iter__(self):
        for read in self.reads:
            yield read

    def copy(self):
        return Fragment(replace(self.Read1), replace(self.Read2))


class TemporaryToPermanent:
    def __init__(self, permanent_file: Path):
        self.permanent_file = permanent_file

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        if exception_type is None:
            self.close()
        else:
            self.file_handle.close()
            self.tmp_directory.cleanup()

    def open(self, *args, **kwargs):
        self.tmp_directory = tempfile.TemporaryDirectory(dir=self.permanent_file.parent)
        self.tmp_path = Path(self.tmp_directory.name)
        self.temp_file = self.tmp_path / self.permanent_file.relative_to(self.permanent_file.root)
        self.temp_file.parent.mkdir(exist_ok=True, parents=True)
        self.file_handle = self.temp_file.open(*args, **kwargs)
        return self

    def close(self):
        self.file_handle.close()
        shutil.move(self.temp_file, self.permanent_file)
        delattr(self, "file_handle")
        self.tmp_directory.cleanup()
        delattr(self, "tmp_path")
        # delattr(self, "file_handle")

    def write(self, *args, **kwargs):
        self.file_handle.write(*args, **kwargs)

    @property
    def closed(self) -> bool:
        if hasattr(self, "file_handle"):
            return self.file_handle.closed
        return True


def reverse_complement(sequence: str) -> str:
    """
    reverse_complement retuzrns the reverse complement of given sequence.

    Parameters
    ----------
    sequence : str
        Input sequence.

    Returns
    -------
    str
        Reverse complement of input sequence.
    """
    return sequence[::-1].translate(rev_comp_table)


def get_df_callable_for_demultiplexer(
    df_in: DataFrame,
    fw_col_name: str,
    rv_col_name: str,
    sample_col_name: str,
    trim_start_col_name: Optional[str] = None,
    trim_end_col_name: Optional[str] = None,
) -> DataFrame:
    def call():
        df = df_in.copy()
        df[fw_col_name].fillna("", inplace=True)
        df[rv_col_name].fillna("", inplace=True)
        whitespace = re.compile(r"\s+")
        assert len(df[fw_col_name].unique()) == len(df)  # check if the barcodes are unique
        df["key"] = df[sample_col_name].str.replace(whitespace, "_")
        df = df.set_index("key")

        if trim_start_col_name is None and trim_end_col_name is None:
            df = df.rename(
                columns={
                    fw_col_name: "start_barcode",
                    rv_col_name: "end_barcode",
                }
            )
            return df[["start_barcode", "end_barcode"]]

        else:
            df = df.rename(
                columns={
                    fw_col_name: "start_barcode",
                    rv_col_name: "end_barcode",
                    trim_start_col_name: "trim_after_start",
                    trim_end_col_name: "trim_before_end",
                }
            )
            return df[["start_barcode", "end_barcode", "trim_after_start", "trim_before_end"]]

    return call


def iterate_fastq(filename: str, reverse_reads: bool) -> Read:
    op = mbf_align._common.BlockedFileAdaptor(filename)
    while True:
        try:
            name = op.readline()[1:-1].decode()
            seq = op.readline()[:-1].decode()
            op.readline()
            qual = op.readline()[:-1].decode()
            if reverse_reads:
                seq = seq[::-1].translate(rev_comp_table)
                qual = qual[::-1]
            yield Read(name, seq, qual)
        except StopIteration:
            break


def get_fastq_iterator(paired) -> Callable:
    fastq_iterator = iterate_fastq

    def _iterreads_paired_end(tuple_of_files: Tuple[Path]) -> Fragment:
        for reads in zip(
            fastq_iterator(str(tuple_of_files[0]), reverse_reads=False),
            fastq_iterator(str(tuple_of_files[1]), reverse_reads=False),
        ):
            yield Fragment(*reads)

    def _iterreads_single_end(filetuple) -> Fragment:
        for read in fastq_iterator(str(filetuple[0]), reverse_reads=False):
            yield Fragment(read)

    if paired:
        return _iterreads_paired_end
    else:
        return _iterreads_single_end
