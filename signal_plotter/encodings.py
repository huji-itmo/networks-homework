"""
Физическое кодирование сигналов: NRZ, Manchester, RZ, AMI
Для курса "Компьютерные сети"
"""

from typing import Literal

import numpy as np


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


_4B5B_TABLE = {
    (0, 0, 0, 0): (1, 1, 1, 1, 0),
    (0, 0, 0, 1): (0, 1, 0, 0, 1),
    (0, 0, 1, 0): (1, 0, 1, 0, 0),
    (0, 0, 1, 1): (1, 0, 1, 0, 1),
    (0, 1, 0, 0): (0, 1, 0, 1, 0),
    (0, 1, 0, 1): (0, 1, 0, 1, 1),
    (0, 1, 1, 0): (0, 1, 1, 1, 0),
    (0, 1, 1, 1): (0, 1, 1, 1, 1),
    (1, 0, 0, 0): (1, 0, 0, 1, 0),
    (1, 0, 0, 1): (1, 0, 0, 1, 1),
    (1, 0, 1, 0): (1, 0, 1, 1, 0),
    (1, 0, 1, 1): (1, 0, 1, 1, 1),
    (1, 1, 0, 0): (1, 1, 0, 1, 0),
    (1, 1, 0, 1): (1, 1, 0, 1, 1),
    (1, 1, 1, 0): (1, 1, 1, 0, 0),
    (1, 1, 1, 1): (1, 1, 1, 0, 1),
}

_INVERTED_4B5B_TABLE = {v: k for k, v in _4B5B_TABLE.items()}


def encode_4b5b(bits: list[int]) -> list[int]:
    """
    4B/5B кодирование.

    Каждые 4 бита заменяются на 5 бит по таблице.
    Гарантирует не более 3 нулей подряд.

    Args:
        bits: Список битов (длина должна быть кратна 4)

    Returns:
        Закодированный список битов (длина = len(bits) * 5 / 4)
    """
    if len(bits) % 4 != 0:
        padding = 4 - (len(bits) % 4)
        bits = bits + [0] * padding

    result = []
    for i in range(0, len(bits), 4):
        nibble = tuple(bits[i : i + 4])
        if nibble not in _4B5B_TABLE:
            raise ValueError(f"Некорректный ниббл: {nibble}")
        result.extend(_4B5B_TABLE[nibble])  # pyright: ignore[reportArgumentType]

    return result


def decode_4b5b(bits: list[int]) -> list[int]:
    """
    4B/5B декодирование.

    Args:
        bits: Список битов (длина должна быть кратна 5)

    Returns:
        Декодированный список битов
    """
    if len(bits) % 5 != 0:
        raise ValueError("Длина битов должна быть кратна 5")

    result = []
    for i in range(0, len(bits), 5):
        symbol = tuple(bits[i : i + 5])
        if symbol not in _INVERTED_4B5B_TABLE:
            raise ValueError(f"Некорректный 5-битный символ: {symbol}")
        result.extend(_INVERTED_4B5B_TABLE[symbol])  # pyright: ignore[reportArgumentType]

    return result


def scramble(bits: list[int], poly_order: int = 7) -> list[int]:
    """
    Скремблирование битов с использованием полинома.

    Формула: B_i = A_i XOR B_{i-5} XOR B_{i-7} (для полинома 7-го порядка)

    Args:
        bits: Список битов для скремблирования
        poly_order: Порядок полинома (по умолчанию 7)

    Returns:
        Скремблированный список битов
    """
    output = []

    for i, a in enumerate(bits):
        b_minus_5 = output[i - 5] if i >= 5 else 0
        b_minus_7 = output[i - 7] if i >= 7 else 0

        b = a ^ b_minus_5 ^ b_minus_7

        output.append(b)

    return output


def unscramble(bits: list[int], poly_order: int = 7) -> list[int]:
    """
    Дескремблирование битов.

    Так как B_i = A_i XOR B_{i-5} XOR B_{i-7},
    то A_i = B_i XOR B_{i-5} XOR B_{i-7}

    Args:
        bits: Список скремблированных битов
        poly_order: Порядок полинома (по умолчанию 7)

    Returns:
        Дескремблированный список битов
    """
    output = []

    for i, b in enumerate(bits):
        b_minus_5 = bits[i - 5] if i >= 5 else 0
        b_minus_7 = bits[i - 7] if i >= 7 else 0

        a = b ^ b_minus_5 ^ b_minus_7

        output.append(a)

    return output


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
