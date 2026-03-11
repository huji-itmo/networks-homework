"""
Физическое кодирование сигналов: NRZ, Manchester, RZ, AMI
Для курса "Компьютерные сети"
"""

import numpy as np
from typing import Literal


def bytes_to_bits(data: bytes) -> list[int]:
    """Конвертация байтов в список битов (8 бит на байт, старший бит первый)."""
    bits = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def nrz_encode(bits: list[int], levels: tuple = (-1, 1)) -> np.ndarray:
    """
    NRZ (Non-Return-to-Zero) - без возврата к нулю.

    Args:
        bits: Список битов (0 или 1)
        levels: Уровни для 0 и 1 (по умолчанию (-1, 1))

    Returns:
        Массив NumPy с закодированным сигналом
    """
    low, high = levels
    result = np.array([], dtype=float)

    for bit in bits:
        level = high if bit == 1 else low
        result = np.append(result, level)

    return result


def manchester_encode(
    bits: list[int], variant: Literal["ieee", "thomas"] = "ieee"
) -> np.ndarray:
    """
    Манчестерское кодирование.

    Args:
        bits: Список битов (0 или 1)
        variant: "ieee" - 0=низкий->высокий, 1=высокий->низкий (IEEE 802.3)
                "thomas" - инвертировано

    Returns:
        Массив NumPy с закодированным сигналом
    """
    result = np.array([], dtype=float)

    for bit in bits:
        if variant == "ieee":
            if bit == 1:
                result = np.append(result, [1, -1])
            else:
                result = np.append(result, [-1, 1])
        else:
            if bit == 1:
                result = np.append(result, [-1, 1])
            else:
                result = np.append(result, [1, -1])

    return result


def rz_encode(bits: list[int], levels: tuple = (-1, 0, 1)) -> np.ndarray:
    """
    RZ (Return-to-Zero) - с возвратом к нулю.

    Args:
        bits: Список битов (0 или 1)
        levels: Уровни (низкий, ноль, высокий). По умолчанию (-1, 0, 1)

    Returns:
        Массив NumPy с закодированным сигналом
    """
    low, zero, high = levels
    result = np.array([], dtype=float)

    for bit in bits:
        level = high if bit == 1 else low
        result = np.append(result, [level, zero])

    return result


def ami_encode(bits: list[int], levels: tuple = (-1, 0, 1)) -> np.ndarray:
    """
    AMI (Alternate Mark Inversion) - биполярное кодирование с чередованием.

    Args:
        bits: Список битов (0 или 1)
        levels: Уровни (отрицательный, ноль, положительный). По умолчанию (-1, 0, 1)

    Returns:
        Массив NumPy с закодированным сигналом
    """
    neg, zero, pos = levels
    result = np.array([], dtype=float)
    last_polarity = pos

    for bit in bits:
        if bit == 0:
            level = zero
        else:
            level = last_polarity
            last_polarity = -last_polarity

        result = np.append(result, level)

    return result


def encode_data(
    data: bytes,
    encoding: Literal["nrz", "manchester", "rz", "ami"],
    manchester_variant: Literal["ieee", "thomas"] = "ieee",
    nrz_levels: tuple = (-1, 1),
    rz_levels: tuple = (-1, 0, 1),
    ami_levels: tuple = (-1, 0, 1),
) -> np.ndarray:
    """
    Кодирование байтов в сигнал указанным методом.

    Args:
        data: Входные байты
        encoding: Метод кодирования ("nrz", "manchester", "rz", "ami")
        manchester_variant: Вариант манчестерского кодирования
        nrz_levels: Уровни для NRZ (для 0 и 1)
        rz_levels: Уровни для RZ
        ami_levels: Уровни для AMI

    Returns:
        Массив NumPy с закодированным сигналом
    """
    bits = bytes_to_bits(data)

    if encoding == "nrz":
        return nrz_encode(bits, nrz_levels)
    elif encoding == "manchester":
        return manchester_encode(bits, manchester_variant)
    elif encoding == "rz":
        return rz_encode(bits, rz_levels)
    elif encoding == "ami":
        return ami_encode(bits, ami_levels)
    else:
        raise ValueError(f"Unknown encoding: {encoding}")
