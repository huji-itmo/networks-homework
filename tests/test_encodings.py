"""
Тесты для физического кодирования сигналов
"""

import pytest
import numpy as np
from signal_plotter.encodings import (
    nrz_encode,
    manchester_encode,
    rz_encode,
    ami_encode,
    bytes_to_bits,
)


class TestBytesToBits:
    def test_single_byte(self):
        assert bytes_to_bits(bytes([0b10110010])) == [1, 0, 1, 1, 0, 0, 1, 0]

    def test_multiple_bytes(self):
        result = bytes_to_bits(bytes([0b10110010, 0b00000001]))
        assert result == [1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1]

    def test_all_zeros(self):
        assert bytes_to_bits(bytes([0b00000000])) == [0] * 8

    def test_all_ones(self):
        assert bytes_to_bits(bytes([0b11111111])) == [1] * 8


class TestNRZ:
    def test_single_bit_one(self):
        result = nrz_encode([1])
        np.testing.assert_array_equal(result, [1])

    def test_single_bit_zero(self):
        result = nrz_encode([0])
        np.testing.assert_array_equal(result, [-1])

    def test_multiple_bits(self):
        result = nrz_encode([1, 0, 1, 1, 0])
        np.testing.assert_array_equal(result, [1, -1, 1, 1, -1])

    def test_custom_levels(self):
        result = nrz_encode([1, 0], levels=(0, 1))
        np.testing.assert_array_equal(result, [1, 0])


class TestManchester:
    def test_bit_one_ieee(self):
        result = manchester_encode([1], variant="ieee")
        np.testing.assert_array_equal(result, [1, -1])

    def test_bit_zero_ieee(self):
        result = manchester_encode([0], variant="ieee")
        np.testing.assert_array_equal(result, [-1, 1])

    def test_multiple_bits_ieee(self):
        result = manchester_encode([1, 0, 1], variant="ieee")
        np.testing.assert_array_equal(result, [1, -1, -1, 1, 1, -1])

    def test_bit_one_thomas(self):
        result = manchester_encode([1], variant="thomas")
        np.testing.assert_array_equal(result, [-1, 1])

    def test_bit_zero_thomas(self):
        result = manchester_encode([0], variant="thomas")
        np.testing.assert_array_equal(result, [1, -1])


class TestRZ:
    def test_bit_one(self):
        result = rz_encode([1])
        np.testing.assert_array_equal(result, [1, 0])

    def test_bit_zero(self):
        result = rz_encode([0])
        np.testing.assert_array_equal(result, [-1, 0])

    def test_multiple_bits(self):
        result = rz_encode([1, 0, 1])
        np.testing.assert_array_equal(result, [1, 0, -1, 0, 1, 0])

    def test_custom_levels(self):
        result = rz_encode([1, 0], levels=(-2, 0, 2))
        np.testing.assert_array_equal(result, [2, 0, -2, 0])


class TestAMI:
    def test_all_zeros(self):
        result = ami_encode([0, 0, 0, 0])
        np.testing.assert_array_equal(result, [0, 0, 0, 0])

    def test_all_ones(self):
        result = ami_encode([1, 1, 1, 1])
        np.testing.assert_array_equal(result, [1, -1, 1, -1])

    def test_alternating(self):
        result = ami_encode([1, 0, 1, 0])
        np.testing.assert_array_equal(result, [1, 0, -1, 0])

    def test_complex_sequence(self):
        result = ami_encode([1, 0, 0, 1, 1, 0, 1])
        np.testing.assert_array_equal(result, [1, 0, 0, -1, 1, 0, -1])

    def test_custom_levels(self):
        result = ami_encode([1, 0, 1], levels=(-5, 0, 5))
        np.testing.assert_array_equal(result, [5, 0, -5])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
