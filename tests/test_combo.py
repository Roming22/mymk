from collections import OrderedDict
from unittest.mock import MagicMock, call

import pytest

import mymk.feature.keys.combo as combo

expand = combo.expand_combo


class TestTokenizeFunctions:
    # @staticmethod
    # def test_group():
    #     definition = "A|B"
    #     result = combo._tokenize_or(definition)
    #     assert result == [["A"],["B"]]

    @staticmethod
    def test_or():
        definition = "A|B"
        result = combo._tokenize_or(definition)
        assert result == ["A", "B"]

    @staticmethod
    def test_and():
        definition = "A+B"
        result = combo._tokenize_and(definition)
        assert result == ["A+B"]

    @staticmethod
    def test_star():
        definition = "A*B"
        result = combo._tokenize_star(definition)
        assert result == ["A+B", "B+A"]


# class TestParsing:
#     @staticmethod
#     def test_star_and():
#         definition = "A*B+C"
#         result = expand(definition)
#         assert result == ["A+B+C","B+C+A"]

#     @staticmethod
#     def test_and_star():
#         definition = "A+B*C"
#         result = expand(definition)
#         assert result == ["A+B+C","C+A+B"]
