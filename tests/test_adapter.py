# -*- coding: utf-8 -*-
from mmdemultiplex.adapters import Adapter, WHERE_START, WHERE_END, AdapterMatch

__author__ = "MarcoMernberger"
__copyright__ = "MarcoMernberger"
__license__ = "mit"


def test_adapter_init():
    adapter = Adapter("")
    assert adapter.locate.__name__ == "locate_null"
    assert not hasattr(adapter, "adapter")
    "TCA_CTGGCA_TGCCCAGGGTCCGGAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    adapter_sequence = "CTGGCA"
    adapter = Adapter(adapter_sequence)
    assert adapter.maximal_number_of_errors == 0
    assert adapter.adapter_sequence == adapter_sequence
    assert adapter.adapter_sequence_length == 6
    assert adapter.minimal_overlap == 6
    assert adapter.index_adapter_end
    assert adapter.where == WHERE_START
    assert adapter.correct_for_adapter_location(5) == 11
    assert adapter.get_position_from_adaptermatch(AdapterMatch(*[-1, -1, -1, 1, -1, -1])) == 1
    assert not adapter.find_right_most
    assert adapter.locate.__name__ == adapter.exact_locate.__name__
    adapter_sequence = "CTACACG"
    adapter = Adapter(
        adapter_sequence, 1, False, minimal_overlap=2, find_right_most_occurence=True,
    )
    assert adapter.maximal_number_of_errors == 1
    assert adapter.adapter_sequence == "GCACATC"
    assert adapter.adapter_sequence_length == 7
    assert adapter.minimal_overlap == 2
    assert adapter.index_adapter_end
    assert adapter.where == WHERE_START
    assert adapter.correct_for_adapter_location(5) == 12
    assert adapter.get_position_from_adaptermatch(AdapterMatch(*[-1, -1, -1, 1, -1, -1])) == 1
    assert adapter.find_right_most
    assert adapter.locate.__name__ == adapter.cutadapt_locate.__name__
    adapter = Adapter(adapter_sequence, 1, True, minimal_overlap=2, find_right_most_occurence=True,)
    assert adapter.maximal_number_of_errors == 1
    assert adapter.adapter_sequence == "GCACATC"
    assert adapter.adapter_sequence_length == 7
    assert adapter.minimal_overlap == 2
    assert not adapter.index_adapter_end
    assert adapter.where == WHERE_START
    assert adapter.correct_for_adapter_location(5) == 5
    assert adapter.get_position_from_adaptermatch(AdapterMatch(*[-1, -1, 2, 1, -1, -1])) == 2
    assert adapter.find_right_most
    assert adapter.locate.__name__ == adapter.cutadapt_locate.__name__
    adapter = Adapter(adapter_sequence, index_adapter_end=False)
    assert adapter.correct_for_adapter_location(5) == 5
    assert adapter.get_position_from_adaptermatch(AdapterMatch(*[-1, -1, 2, 1, -1, -1])) == 2
    assert not adapter.find_right_most


def test_adapter_not_present():
    adapter_sequence = "ADAPTER"
    adapter = Adapter(adapter_sequence, index_adapter_end=False, find_right_most_occurence=True)
    test = "TCA_TGCCCAGGGTCCGGAGGC_TTTCCC"
    index = adapter.locate(test)
    assert not index
    adapter = Adapter(adapter_sequence)
    index = adapter.locate(test)
    assert not index


def test_find_last_adapter_start_index():
    adapter_sequence = "ADAPTER"
    adapter = Adapter(adapter_sequence, index_adapter_end=False, find_right_most_occurence=True)
    test = "TCA_ADAPTER_TGCCCAGGGTCCGGAGGC_TTTCCC"
    index = adapter.locate(test)
    assert index == -33
    assert test[:index] == "TCA_"
    test = "TCA_ADAPTER_TGCCCAGGGTCCGGAGGC_ADAPTER"
    index = adapter.locate(test)
    assert index == -7
    assert test[:index] == "TCA_ADAPTER_TGCCCAGGGTCCGGAGGC_"


def test_find_last_adapter_end_index():
    adapter_sequence = "ADAPTER"
    adapter = Adapter(adapter_sequence, index_adapter_end=True, find_right_most_occurence=True)
    test = "TCA_ADAPTER_TGCCCAGGGTCCGGAGGC_TTTCCC"
    index = adapter.locate(test)
    assert index == -26
    assert test[index:] == "_TGCCCAGGGTCCGGAGGC_TTTCCC"
    test = "TCA_ADAPTER_TGCCCAGGGTCCGGAGGC_ADAPTER_TTT"
    index = adapter.locate(test)
    assert index == -4
    assert test[index:] == "_TTT"


def test_find_first_adapter_end_index():
    adapter_sequence = "ADAPTER"
    adapter = Adapter(adapter_sequence, index_adapter_end=True)
    test = "TCA_ADAPTER_TGCCCAGGGTCCGGAGGC_TTTCCC"
    index = adapter.locate(test)
    assert index == 11
    assert test[index:] == "_TGCCCAGGGTCCGGAGGC_TTTCCC"
    test = "TCA_ADAPTER_TGCCCAGGGTCCGGAGGC_ADAPTER_TTT"
    index = adapter.locate(test)
    assert index == 11
    assert test[index:] == "_TGCCCAGGGTCCGGAGGC_ADAPTER_TTT"


def test_find_first_adapter_start_index():
    adapter_sequence = "ADAPTER"
    adapter = Adapter(adapter_sequence, index_adapter_end=False)
    test = "TCA_ADAPTER_TGCCCAGGGTCCGGAGGC_TTTCCC"
    index = adapter.locate(test)
    assert index == 4
    assert test[:index] == "TCA_"
    test = "TCA_ADAPTER_TGCCCAGGGTCCGGAGGC_ADAPTER_TTT"
    index = adapter.locate(test)
    assert index == 4


def test_locate_find_first_adapter():
    # exact
    adapter_sequence = "ADAPTER"
    # find first adapter
    adapter = Adapter(adapter_sequence, index_adapter_end=True)
    test = "TCA_ADAPTER_TGCCCAGGGTCCGGAGGC_TTTCCC"
    index = adapter.locate(test)
    assert test[index:] == "_TGCCCAGGGTCCGGAGGC_TTTCCC"
    test = "TCA_ADAPTER_TGCCCAGGGTCCGGAGGC_ADAPTER"
    assert test[index:] == "_TGCCCAGGGTCCGGAGGC_ADAPTER"
    # with error
    adapter = Adapter(adapter_sequence, index_adapter_end=True, maximal_number_of_errors=1)
    test = "TCA_ADDPTER_TGCCCAGGGTCCGGAGGC_TTTCCC"
    index = adapter.locate(test)
    test[index:] == "_TGCCCAGGGTCCGGAGGC_TTTCCC"
    # a full correct adapter is always preferred
    test = "TCA_ADDPTER_TGCCCAGGGTCCGGAGGC_ADAPTER"
    index = adapter.locate(test)
    assert test[:index] == "TCA_ADDPTER_TGCCCAGGGTCCGGAGGC_ADAPTER"
    # if both adapter have the same amount of errors, accept the first
    test = "TCA_ADDPTER_TGCCCAGGGTCCGGAGGC_ADAPTTR"
    index = adapter.locate(test)
    assert test[:index] == "TCA_ADDPTER"
    adapter = Adapter(adapter_sequence, index_adapter_end=True, maximal_number_of_errors=2)
    # if both adapter have errors, accept the better one
    test = "TCA_ADDPTTR_TGCCCAGGGTCCGGAGGC_ADAPTTR"
    index = adapter.locate(test)
    assert test[:index] == "TCA_ADDPTTR_TGCCCAGGGTCCGGAGGC_ADAPTTR"
    test = "TCA_ADDPTTR_TGCCCAGGGTCCGGAGGC_"
    index = adapter.locate(test)
    assert test[:index] == "TCA_ADDPTTR"
    adapter = Adapter(adapter_sequence, index_adapter_end=False, maximal_number_of_errors=1)
    test = "TCA_ADDPTER_TGCCCAGGGTCCGGAGGC_TTTCCC"
    index = adapter.locate(test)
    assert test[:index] == "TCA_"
    test = "TCA_ADDPTER_TGCCCAGGGTCCGGAGGC_ADAPTER"
    index = adapter.locate(test)
    assert test[:index] == "TCA_ADDPTER_TGCCCAGGGTCCGGAGGC_"


def test_find_last_adapter():
    # find last adapter
    adapter_sequence = "ADAPTER"
    adapter = Adapter(adapter_sequence, index_adapter_end=False, find_right_most_occurence=True)
    test = "TCA_ADAPTER_TGCCCAGGGTCCGGAGGC_TTTCCC"
    index = adapter.locate(test)
    assert test[:index] == "TCA_"
    test = "TCA_ADAPTER_TGCCCAGGGTCCGGAGGC_ADAPTER"
    index = adapter.locate(test)
    assert test[:index] == "TCA_ADAPTER_TGCCCAGGGTCCGGAGGC_"
    # with error
    adapter = Adapter(
        adapter_sequence,
        index_adapter_end=True,
        find_right_most_occurence=True,
        maximal_number_of_errors=1,
    )
    test = "TCA_ADDPTER_TGCCCAGGGTCCGGAGGC_TTTCCC"
    index = adapter.locate(test)
    test[index:] == "_TGCCCAGGGTCCGGAGGC_TTTCCC"
    test = "TCA_ADDPTER_TGCCCAGGGTCCGGAGGC_ADDPTER_TTT"
    index = adapter.locate(test)
    assert test[index:] == "_TTT"
    adapter = Adapter(
        adapter_sequence,
        index_adapter_end=False,
        find_right_most_occurence=True,
        maximal_number_of_errors=1,
    )
    test = "TCA_ADDPTER_TGCCCAGGGTCCGGAGGC_TTTCCC"
    index = adapter.locate(test)
    assert test[:index] == "TCA_"
    test = "TCA_ADDPTER_TGCCCAGGGTCCGGAGGC_ADAPTRR"
    index = adapter.locate(test)
    assert test[:index] == "TCA_ADDPTER_TGCCCAGGGTCCGGAGGC_"


def test_partial_adapter():
    adapter_sequence = "ADAPTER"
    adapter = Adapter(adapter_sequence, minimal_overlap=5)
    test = "APTER_REMAIN"
    assert adapter.locate(test) == 5
    test = "PTER_REMAIN"
    assert adapter.locate(test) is None
    test = "ADAPTE_REMAIN"
    assert adapter.locate(test) is None
    adapter = Adapter(adapter_sequence, minimal_overlap=5, index_adapter_end=False)
    assert adapter.where == WHERE_START
    test = "REMAIN_ADAPT"
    assert adapter.locate(test) is None
    test = "REMAIN_DAPTER"
    assert adapter.locate(test) is None
    adapter = Adapter(
        adapter_sequence, minimal_overlap=5, index_adapter_end=False, find_right_most_occurence=True
    )
    assert adapter.where == WHERE_START
    test = "REMAIN_ADAPT"
    assert adapter.locate(test) == -5
    test = "REMAIN_ADAP"
    assert adapter.locate(test) is None
    test = "REMAIN_DAPTER"
    assert adapter.locate(test) is None


def test_locate_front_partial_adapter():
    adapter_sequence = "ADAPTER"
    adapter = Adapter(adapter_sequence)
    # exact match
    test = "GGCA_TGCCC_ADAPTER_GAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    assert adapter.locate(test) == 18
    # no match
    test = "GGCA_TGCCC_ADAPTTR_GAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    assert adapter.locate(test) is None
    # partial back
    adapter = Adapter(adapter_sequence, minimal_overlap=4)

    test = "DAPTER_TGCCCAGGGTCCGGAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    assert adapter.locate(test) == 6
    adapter = Adapter(adapter_sequence, minimal_overlap=4)
    test = "PTER_TGCCCAGGGTCCGGAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    assert adapter.locate(test) == 4
    test = "APTER_TGCCCAGGGTCCGGAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    assert adapter.locate(test) == 5
    test = "TER_TGCCCAGGGTCCGGAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    assert adapter.locate(test) is None
    test = "TTTPTER_TGCCCAGGGTCCGGAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    assert adapter.locate(test) is None  # we don't want errors, just missing parts
    # partial front
    adapter = Adapter(adapter_sequence, minimal_overlap=4)
    test = "ADAPTE_TGCCCAGGGTCCGGAGGC_TTTCCC"
    assert adapter.locate(test) is None
    # still no errors
    test = (
        "TC_ADAPTET_TGCCCAGGGTCCGGAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    )
    assert adapter.locate(test) is None
    test = "APTET_TGCCCAGGGTCCGGAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    assert adapter.locate(test) is None
    # with errors
    adapter = Adapter(adapter_sequence, maximal_number_of_errors=2)
    test = (
        "TCA_ADAPTRR_TGCCCAGGGTCCGGAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    )
    assert adapter.locate(test) == 11
    test = (
        "TCA_ADAPRRR_TGCCCAGGGTCCGGAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    )
    assert adapter.locate(test) == 11
    test = (
        "TCA_ADARRRR_TGCCCAGGGTCCGGAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    )
    assert adapter.locate(test) is None
    # with errors and partial
    adapter = Adapter(adapter_sequence, maximal_number_of_errors=1, minimal_overlap=5)
    test = (
        "TCA_ADAPTRR_TGCCCAGGGTCCGGAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    )
    assert adapter.locate(test) == 11
    test = "DAPTRR_TGCCCAGGGTCCGGAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    assert adapter.locate(test) == 6
    test = "APTRR_TGCCCAGGGTCCGGAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    assert adapter.locate(test) == 5
    test = "DAPRRR_TGCCCAGGGTCCGGAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    assert adapter.locate(test) is None
    test = "APRRR_TGCCCAGGGTCCGGAGGC_TTTCCC_ATCGATCG_GGGCCC_GGGTGGTTGTCAGTGGCCCTCC_CTTTTG_CAGCTA"
    assert adapter.locate(test) is None


def test_locate_end_partial_adapter():
    adapter_sequence = "ADAPTER"
    adapter = Adapter(
        adapter_sequence, index_adapter_end=False, find_right_most_occurence=True, minimal_overlap=4
    )
    assert adapter.where == WHERE_START
    # last occurence, start pos
    test = "TCA_ADAPTER_CTTTTG_ADAPTER_CAGCTA"
    index = adapter.locate(test)
    assert index == -14
    assert test[:index] == "TCA_ADAPTER_CTTTTG_"
    # only exact matches
    test = "GGCA_TGCCC_ADAPTTR_GAGGC"
    assert adapter.locate(test) is None
    # a partial match (front) is better than nothing
    test = "TCA_DDDDDD_CTTTTG_ADAPTE"
    index = adapter.locate(test)
    assert test[:index] == "TCA_DDDDDD_CTTTTG_"
    # partial match (back) should not be recognized
    test = "TCA_CTTTTG_DAPTER"
    assert adapter.locate(test) is None
    test = "TCA_ADAPTER_CTTTTG_DAPTER"
    assert adapter.locate(test) == -21
    # partial match front, if a full adapter is present, this is reported
    test = "TCA_ADAPTER_CTTTTG_ADAP"
    index = adapter.locate(test)
    assert test[:index] == "TCA_"
    # no match, as overlap is too short
    test = "TCA_TCGA_CTTTTG_ADA"
    assert adapter.locate(test) is None
    # now with error tolerance
    adapter = Adapter(
        adapter_sequence,
        index_adapter_end=False,
        find_right_most_occurence=True,
        minimal_overlap=4,
        maximal_number_of_errors=1,
    )
    # accept 1 error
    test = "TCA_ADDPTER_CTTTTG_ADAP"
    assert adapter.locate(test) == -19
    # if the full adapter has more than one error, accept partial
    test = "TCA_ADDDTER_CTTTTG_ADAP"
    assert adapter.locate(test) == -4
    # no match
    test = "TCA_ADDDTER_CTTTTG_ADA"
    assert adapter.locate(test) is None
    # 1 error at the end is ok
    test = "TC_ADAPTET"
    assert adapter.locate(test) == -7
    # since we allow 1 error, this is now a full match
    test = "TGCC_DAPTER"
    assert adapter.locate(test) == -7
    # but this is not
    test = "TGCC_APTER"
    assert adapter.locate(test) is None


def test_locate():
    adapter_sequence = "ADAPTER"
    adapter = Adapter(adapter_sequence, index_adapter_end=False, maximal_number_of_errors=1)
    test = "ADAPTER_TTT"
    assert adapter.locate(test) == 0
    test = "TTT_ADAPTRR_TTT"
    assert adapter.locate(test) == 4
    test = "TTT_ADAPRRR_TTT"
    assert adapter.locate(test) is None
    adapter = Adapter(adapter_sequence, index_adapter_end=True, maximal_number_of_errors=1)
    assert hasattr(adapter, "adapter")
    test = "ADAPTER_TTT"
    assert adapter.locate(test) == 7
    test = "TTT_ADAPTRR_TTT"
    assert adapter.locate(test) == 11
    test = "TTT_ADAPRRR_TTT"
    assert adapter.locate(test) is None


def test_locate_0():
    adapter_sequence = ""
    adapter = Adapter(adapter_sequence)
    test = "ADAPTER_TTT"
    assert adapter.locate(test) == 0
    assert adapter.locate.__name__ == "locate_null"
