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


class Test4B5B:
    def test_0000(self):
        from signal_plotter.encodings import encode_4b5b, decode_4b5b

        result = encode_4b5b([0, 0, 0, 0])
        assert result == [1, 1, 1, 1, 0]

    def test_0001(self):
        from signal_plotter.encodings import encode_4b5b

        result = encode_4b5b([0, 0, 0, 1])
        assert result == [0, 1, 0, 0, 1]

    def test_1111(self):
        from signal_plotter.encodings import encode_4b5b

        result = encode_4b5b([1, 1, 1, 1])
        assert result == [1, 1, 1, 0, 1]

    def test_multiple_nibbles(self):
        from signal_plotter.encodings import encode_4b5b

        result = encode_4b5b([1, 1, 0, 0, 0, 0, 1, 0])
        assert len(result) == 10

    def test_padding(self):
        from signal_plotter.encodings import encode_4b5b

        result = encode_4b5b([1, 0, 1])
        assert len(result) == 5

    def test_decode(self):
        from signal_plotter.encodings import encode_4b5b, decode_4b5b

        original = [1, 1, 0, 0, 0, 0, 1, 0]
        encoded = encode_4b5b(original)
        decoded = decode_4b5b(encoded)
        assert decoded == original

    def test_max_consecutive_zeros(self):
        from signal_plotter.encodings import encode_4b5b
        from signal_plotter.metrics import find_max_consecutive

        bits = [0, 0, 0, 0, 0, 0]
        encoded = encode_4b5b(bits)
        max_zeros = find_max_consecutive(encoded, 0)
        assert max_zeros <= 3


class TestScrambling:
    def test_scramble_basic(self):
        from signal_plotter.encodings import scramble

        bits = [1, 1, 0, 0, 0, 0, 1, 0]
        result = scramble(bits)
        assert len(result) == len(bits)

    def test_scramble_all_zeros(self):
        from signal_plotter.encodings import scramble

        bits = [0] * 10
        result = scramble(bits)
        assert len(result) == 10

    def test_scramble_all_ones(self):
        from signal_plotter.encodings import scramble

        bits = [1] * 10
        result = scramble(bits)
        assert len(result) == 10

    def test_scramble_decode(self):
        from signal_plotter.encodings import scramble, unscramble

        bits = [1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0]
        scrambled = scramble(bits)
        unscrambled = unscramble(scrambled)
        assert unscrambled == bits

    def test_scramble_max_consecutive_zeros(self):
        from signal_plotter.encodings import scramble
        from signal_plotter.metrics import find_max_consecutive

        bits = [1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0]
        scrambled = scramble(bits)
        max_zeros = find_max_consecutive(scrambled, 0)
        assert max_zeros <= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
