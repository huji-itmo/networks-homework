"""
Тесты для модуля метрик кодирования
"""

import pytest
from signal_plotter.metrics import (
    find_max_consecutive,
    calculate_weighted_avg_frequency,
    calculate_nrz_metrics,
    calculate_manchester_metrics,
    calculate_rz_metrics,
    calculate_ami_metrics,
)


class TestFindMaxConsecutive:
    def test_all_zeros(self):
        assert find_max_consecutive([0, 0, 0, 0], 0) == 4

    def test_all_ones(self):
        assert find_max_consecutive([1, 1, 1, 1], 1) == 4

    def test_alternating(self):
        assert find_max_consecutive([1, 0, 1, 0], 0) == 1
        assert find_max_consecutive([1, 0, 1, 0], 1) == 1

    def test_mixed(self):
        assert find_max_consecutive([1, 1, 0, 0, 0, 1], 0) == 3
        assert find_max_consecutive([1, 1, 0, 0, 0, 1], 1) == 2

    def test_single(self):
        assert find_max_consecutive([1], 1) == 1
        assert find_max_consecutive([0], 0) == 1

    def test_empty(self):
        assert find_max_consecutive([], 0) == 0


class TestNRZMetrics:
    def test_manchester_pattern(self):
        bits = [1, 0, 1, 0, 1, 0]
        m = calculate_nrz_metrics(bits, 100)

        assert m.encoding_name == "NRZ"
        assert m.bit_rate == 100
        assert m.f_high == 50.0
        assert m.signal_levels == 2
        assert m.has_dc_component == True

    def test_long_zeros(self):
        bits = [1, 0, 0, 0, 0, 0, 1]
        m = calculate_nrz_metrics(bits, 100)

        assert m.max_consecutive_zeros == 5
        assert m.f_low == pytest.approx(10.0)

    def test_all_ones(self):
        bits = [1, 1, 1, 1]
        m = calculate_nrz_metrics(bits, 100)

        # nmax = 4, f_low = 100 / (2 * 4) = 12.5
        assert m.f_low == pytest.approx(12.5)


class TestManchesterMetrics:
    def test_basic(self):
        bits = [1, 0, 1, 1, 0]
        m = calculate_manchester_metrics(bits, 100)

        assert m.encoding_name == "Manchester (IEEE)"
        assert m.f_high == 100.0
        assert m.f_low == 50.0
        assert m.bandwidth == 100.0
        assert m.signal_levels == 2
        assert m.has_dc_component == False


class TestRZMetrics:
    def test_basic(self):
        bits = [1, 0, 1, 1, 0]
        m = calculate_rz_metrics(bits, 100)

        assert m.encoding_name == "RZ"
        assert m.f_high == 100.0
        assert m.f_low == 25.0
        assert m.bandwidth == 100.0
        assert m.signal_levels == 3
        assert m.has_dc_component == False


class TestAMIMetrics:
    def test_all_zeros(self):
        bits = [0, 0, 0, 0, 0]
        m = calculate_ami_metrics(bits, 100)

        # max_consecutive_zeros = 5, f_low = 100 / (2 * (5+1)) = 8.33
        assert m.encoding_name == "AMI"
        assert m.f_high == 50.0
        assert m.f_low == pytest.approx(8.33, abs=0.1)
        assert m.signal_levels == 3
        assert m.has_dc_component == False

    def test_all_ones(self):
        bits = [1, 1, 1, 1]
        m = calculate_ami_metrics(bits, 100)

        # max_consecutive_zeros = 0, f_low = 100 / (2 * (0+1)) = 50
        assert m.f_low == pytest.approx(50.0)
        assert m.f_avg == pytest.approx(50.0)

    def test_alternating(self):
        bits = [1, 0, 1, 0]
        m = calculate_ami_metrics(bits, 100)

        assert m.max_consecutive_zeros == 1


class TestCalculateDerived:
    def test_derived_values(self):
        m = calculate_nrz_metrics([1, 0, 1, 0], 100)

        # bits = [1, 0, 1, 0], nmax = 1, f_low = 100 / (2 * 1) = 50
        assert m.f_low == 50.0
        assert m.f_mid == pytest.approx((50.0 + 50.0) / 2)
        assert m.spectrum_width == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
