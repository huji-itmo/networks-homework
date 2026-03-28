"""
Генератор отчёта по лабораторной работе
"""

import os
from pathlib import Path

import numpy as np

from signal_plotter import SignalPlotter
from signal_plotter.encodings import (
    ami_encode,
    bytes_to_bits,
    encode_4b5b,
    manchester_encode,
    nrz_encode,
    rz_encode,
    scramble,
)
from signal_plotter.metrics import (
    EncodingMetrics,
    calculate_4b5b_nrz_metrics,
    calculate_ami_metrics,
    calculate_manchester_metrics,
    calculate_nrz_metrics,
    calculate_rz_metrics,
    calculate_scrambled_nrz_metrics,
    find_max_consecutive,
)


def hex_to_bytes(hex_str: str) -> bytes:
    """Конвертация hex-строки в байты."""
    hex_str = hex_str.replace(" ", "").replace("0x", "")
    return bytes.fromhex(hex_str)


def bits_to_hex_string(bits: list[int]) -> str:
    """Конвертация битов в hex-строку."""
    result = []
    for i in range(0, len(bits), 8):
        byte_bits = bits[i : i + 8]
        byte = 0
        for j, bit in enumerate(byte_bits):
            byte = (byte << 1) | bit
        result.append(f"{byte:02X}")
    return " ".join(result)


def bits_to_binary_string(bits: list[int]) -> str:
    """Конвертация битов в бинарную строку с пробелами по 8 бит."""
    result = []
    for i in range(0, len(bits), 8):
        result.append("".join(map(str, bits[i : i + 8])))
    return " ".join(result)


def format_bits(bits: list[int]) -> str:
    """Форматирование битов для отчёта."""
    return "".join(map(str, bits))


def generate_report(
    hex_data: str = "B2699C", bit_rate: float = 100.0, output_dir: str = "output"
) -> str:
    """
    Генерация полного отчёта по лабораторной работе.

    Args:
        hex_data: Hex-строка с данными (напр. "B2699C")
        bit_rate: Скорость передачи в Мбит/с
        output_dir: Директория для сохранения

    Returns:
        Путь к сгенерированному отчёту
    """
    os.makedirs(output_dir, exist_ok=True)

    data = hex_to_bytes(hex_data)
    bits = bytes_to_bits(data)

    report_lines = []

    report_lines.append("# Отчёт по лабораторной работе")
    report_lines.append("")
    report_lines.append("**Дисциплина:** Компьютерные сети")
    report_lines.append("**Тема:** Исследование методов кодирования в цифровых сетях")
    report_lines.append("")

    report_lines.append("## 1. Цель работы")
    report_lines.append("")
    report_lines.append(
        "Исследование методов физического и логического кодирования сигналов в цифровых сетях, "
    )
    report_lines.append("анализ их характеристик и сравнение эффективности.")
    report_lines.append("")

    report_lines.append("## 2. Этап 1: Формирование сообщения")
    report_lines.append("")
    report_lines.append("### Исходные данные")
    report_lines.append("")
    report_lines.append(f"- **Hex:** 0x{hex_data.upper()}")
    report_lines.append(f"- **Байты:** {bits_to_hex_string(bits)}")
    report_lines.append(f"- **Биты:** {bits_to_binary_string(bits)}")
    report_lines.append(f"- **Длина:** {len(bits)} бит ({len(bits) // 8} байт)")
    report_lines.append("")

    plotter = SignalPlotter(figsize=(16, 3), dpi=150)

    def make_plot(sig, duration):
        def wrapper(t_arr):
            indices = np.round(t_arr / duration * (len(sig) - 1)).astype(int)
            indices = np.clip(indices, 0, len(sig) - 1)
            return sig[indices]

        return wrapper

    report_lines.append("## 3. Этап 2: Физическое кодирование")
    report_lines.append("")

    metrics_list = []

    methods = [
        ("NRZ", nrz_encode, calculate_nrz_metrics),
        (
            "Manchester",
            lambda b: manchester_encode(b, "ieee"),
            calculate_manchester_metrics,
        ),
        ("RZ", rz_encode, calculate_rz_metrics),
        ("AMI", ami_encode, calculate_ami_metrics),
    ]

    for method_name, encode_func, metrics_func in methods:
        signal = encode_func(bits)

        fig = plotter.plot_signal(
            signal_func=make_plot(signal, len(signal)),
            num_samples=len(signal) * 10,
            title=f"{method_name}: {format_bits(bits)[:16]}...",
            y_range=(-1.3, 1.3),
            time_range=(0, len(signal)),
            output_path=f"{output_dir}/report_{method_name.lower()}.png",
        )

        m = metrics_func(bits, bit_rate)
        metrics_list.append(m)

        report_lines.append(f"### 3.{len(metrics_list)} {method_name}")
        report_lines.append("")

        if method_name == "NRZ":
            report_lines.append(
                "**Описание:** Метод NRZ (Non-Return-to-Zero) - уровень сигнала не меняется в течение бита."
            )
            report_lines.append("1 → высокий уровень, 0 → низкий уровень.")
        elif method_name == "Manchester":
            report_lines.append(
                "**Описание:** Манчестерское кодирование - переход в середине каждого бита."
            )
            report_lines.append("0 → переход LOW→HIGH, 1 → переход HIGH→LOW.")
        elif method_name == "RZ":
            report_lines.append(
                "**Описание:** Метод RZ (Return-to-Zero) - сигнал возвращается к нулю во второй половине бита."
            )
        elif method_name == "AMI":
            report_lines.append(
                "**Описание:** Биполярное кодирование с чередованием - единицы чередуют полярность, нули - нулевой уровень."
            )

        report_lines.append("")
        report_lines.append(
            f"![{method_name}](../output/report_{method_name.lower()}.png)"
        )
        report_lines.append("")

        report_lines.append("**Характеристики:**")
        report_lines.append("")

        if method_name == "NRZ":
            nmax = max(m.max_consecutive_zeros, m.max_consecutive_ones)
            report_lines.append("**Верхняя граница частоты:**")
            report_lines.append("")
            report_lines.append(
                f"$$f_{{в}} = \\frac{{C}}{{2}} = \\frac{{{bit_rate:.0f}}}{{2}} = {m.f_high:.1f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(
                "Деление на 2 связано с тем, что наихудший случай для NRZ — чередование 101010. "
                "При этом формируется меандр с периодом в 2 бита, то есть частота равна половине битовой скорости."
            )
            report_lines.append("")
            report_lines.append("**Нижняя граница частоты:**")
            report_lines.append("")
            report_lines.append(
                f"$$f_{{н}} = \\frac{{C}}{{2 \\cdot N_{{max}}}} = \\frac{{{bit_rate:.0f}}}{{2 \\cdot {nmax}}} = \\frac{{{bit_rate:.0f}}}{{2 * {nmax}}} = {m.f_low:.2f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(
                f"где $N_{{max}} = {nmax}$ — максимальная длина серии одинаковых бит "
                f"(нули: {m.max_consecutive_zeros}, единицы: {m.max_consecutive_ones})"
            )
            report_lines.append("")
            report_lines.append(
                "Чем длиннее серия одинаковых бит, тем медленнее меняется сигнал и тем ниже "
                "нижняя граница спектра. Длинная серия нулей или единиц эквивалентна низкочастотному "
                "составляющему, поэтому $N_{max}$ определяет минимальную частоту."
            )
            report_lines.append("")
            report_lines.append("**Полоса пропускания:**")
            report_lines.append("")
            report_lines.append(
                f"$$\\Delta f = f_{{в}} - f_{{н}} = {m.f_high:.1f} - {m.f_low:.2f} = {m.bandwidth:.2f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(f"- Уровней сигнала: {m.signal_levels}")
            report_lines.append(
                f"- Постоянная составляющая (DC): {'Да' if m.has_dc_component else 'Нет'}"
            )
            if m.has_dc_component:
                report_lines.append(
                    "  NRZ имеет постоянную составляющую, потому что средний уровень сигнала "
                    "зависит от соотношения нулей и единиц в данных. Если единиц больше, "
                    "среднее значение сигнала смещено вверх от нуля."
                )
            report_lines.append(f"- Макс. серия нулей: {m.max_consecutive_zeros}")
            report_lines.append(f"- Макс. серия единиц: {m.max_consecutive_ones}")

        elif method_name == "Manchester":
            report_lines.append("**Верхняя граница частоты:**")
            report_lines.append("")
            report_lines.append(f"$$f_{{в}} = C = {bit_rate:.0f} \\text{{ МГц}}$$")
            report_lines.append("")
            report_lines.append(
                "Манчестерское кодирование имеет гарантированный переход в середине "
                "каждого бита, поэтому максимальная частота равна скорости передачи. "
                "В отличие от NRZ (где $f_в = C/2$), здесь переход происходит вдвое чаще — "
                "при чередовании 1010 переходы совпадают и дают период в 1 бит."
            )
            report_lines.append("")
            report_lines.append("**Нижняя граница частоты:**")
            report_lines.append("")
            report_lines.append(
                f"$$f_{{н}} = \\frac{{C}}{{2}} = \\frac{{{bit_rate:.0f}}}{{2}} = {m.f_low:.1f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(
                "Даже в наихудшем случае (серия одинаковых бит, например 1111) в середине "
                "каждого бита происходит переход, поэтому минимальная частота не опускается ниже $C/2$."
            )
            report_lines.append("")
            report_lines.append("**Полоса пропускания:**")
            report_lines.append("")
            report_lines.append(
                f"$$\\Delta f = f_{{в}} - f_{{н}} = {bit_rate:.0f} - {m.f_low:.1f} = {m.bandwidth:.1f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(f"- Уровней сигнала: {m.signal_levels}")
            report_lines.append(
                f"- Постоянная составляющая (DC): {'Да' if m.has_dc_component else 'Нет'}"
            )
            if not m.has_dc_component:
                report_lines.append(
                    "  Постоянная составляющая отсутствует, так как каждый бит содержит "
                    "ровно половину периода на высоком и половину на низком уровне. "
                    "Среднее значение сигнала всегда равно нулю независимо от данных."
                )

        elif method_name == "RZ":
            report_lines.append("**Верхняя граница частоты:**")
            report_lines.append("")
            report_lines.append(f"$$f_{{в}} = C = {bit_rate:.0f} \\text{{ МГц}}$$")
            report_lines.append("")
            report_lines.append(
                "В методе RZ импульс занимает только половину битового интервала, "
                "затем сигнал возвращается к нулю. Это эквивалентно тому, что "
                "длительность импульса вдвое короче, чем у NRZ, поэтому "
                "спектр расширяется вдвое — максимальная частота равна $C$, а не $C/2$."
            )
            report_lines.append("")
            report_lines.append("**Нижняя граница частоты:**")
            report_lines.append("")
            report_lines.append(
                f"$$f_{{н}} = \\frac{{C}}{{4}} = \\frac{{{bit_rate:.0f}}}{{4}} = {m.f_low:.1f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(
                "Для чередующейся последовательности 101010: каждый импульс HIGH длится "
                "половину бита, затем ноль на оставшуюся половину бита, затем снова HIGH. "
                "Период такого сигнала равен 2 бита (1 бит HIGH-импульс + 1 бит пауза/следующий импульс), "
                "но с учётом возврата к нулю фундаментальная частота получается $C/4$."
            )
            report_lines.append("")
            report_lines.append("**Полоса пропускания:**")
            report_lines.append("")
            report_lines.append(
                f"$$\\Delta f = f_{{в}} - f_{{н}} = {bit_rate:.0f} - {m.f_low:.1f} = {m.bandwidth:.1f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(f"- Уровней сигнала: {m.signal_levels}")
            report_lines.append(
                "  (три уровня: $+V$, $0$, $-V$ — для единицы используется положительный или "
                "отрицательный импульс с возвратом к нулю)"
            )
            report_lines.append(
                f"- Постоянная составляющая (DC): {'Да' if m.has_dc_component else 'Нет'}"
            )

        elif method_name == "AMI":
            report_lines.append("**Верхняя граница частоты:**")
            report_lines.append("")
            report_lines.append(
                f"$$f_{{в}} = \\frac{{C}}{{2}} = \\frac{{{bit_rate:.0f}}}{{2}} = {m.f_high:.1f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(
                "Как и в NRZ, наихудший случай — чередование бит 101010, дающее меандр с частотой $C/2$."
            )
            report_lines.append("")
            report_lines.append("**Нижняя граница частоты:**")
            report_lines.append("")
            report_lines.append(
                f"$$f_{{н}} = \\frac{{C}}{{2 \\cdot (N_{{max}} + 1)}} = "
                f"\\frac{{{bit_rate:.0f}}}{{2 \\cdot ({m.max_consecutive_zeros} + 1)}} = "
                f"\\frac{{{bit_rate:.0f}}}{{2 \\cdot {m.max_consecutive_zeros + 1}}} = "
                f"\\frac{{{bit_rate:.0f}}}{{2 * {m.max_consecutive_zeros + 1}}} = "
                f"{m.f_low:.2f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(
                f"где $N_{{max}} = {m.max_consecutive_zeros}$ — максимальная серия нулей в исходном сообщении"
            )
            report_lines.append("")
            report_lines.append(
                "В AMI нули не несут информации о полярности — они просто означают отсутствие "
                "сигнала. Серия из $N_{max}$ нулей между двумя единицами создаёт паузу, "
                "длина которой определяет нижнюю границу спектра. "
                "Формула содержит $(N_{max} + 1)$, а не просто $N_{max}$, "
                "потому что нужно учитывать и саму единицу, ограничивающую серию нулей — "
                "переход от одной единицы к другой через $N_{max}$ нулей занимает $N_{max} + 1$ битовых интервала."
            )
            report_lines.append("")
            report_lines.append("**Полоса пропускания:**")
            report_lines.append("")
            report_lines.append(
                f"$$\\Delta f = f_{{в}} - f_{{н}} = {m.f_high:.1f} - {m.f_low:.2f} = {m.bandwidth:.2f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(f"- Уровней сигнала: {m.signal_levels}")
            report_lines.append(
                "  (три уровня: $+V$, $0$, $-V$ — единицы чередуют полярность, нули — нулевой уровень)"
            )
            report_lines.append(
                f"- Постоянная составляющая (DC): {'Да' if m.has_dc_component else 'Нет'}"
            )
            if not m.has_dc_component:
                report_lines.append(
                    "  Постоянная составляющая отсутствует, так как положительные и "
                    "отрицательные импульсы чередуются и компенсируют друг друга."
                )
            report_lines.append(f"- Макс. серия нулей: {m.max_consecutive_zeros}")

        report_lines.append("")

    encoded_bits = encode_4b5b(bits)
    m_4b5b = calculate_4b5b_nrz_metrics(bits, encoded_bits, bit_rate)
    metrics_list.append(m_4b5b)

    signal_4b5b = nrz_encode(encoded_bits)

    fig = plotter.plot_signal(
        signal_func=make_plot(signal_4b5b, len(signal_4b5b)),
        num_samples=len(signal_4b5b) * 10,
        title=f"4B/5B: {format_bits(encoded_bits)[:20]}...",
        y_range=(-1.3, 1.3),
        time_range=(0, len(signal_4b5b)),
        output_path=f"{output_dir}/report_4b5b.png",
    )

    report_lines.append("## 4. Этап 3: Логическое (избыточное) кодирование")
    report_lines.append("")
    report_lines.append("### 4B/5B")
    report_lines.append("")
    report_lines.append(
        "**Описание:** Метод 4B/5B заменяет каждые 4 бита на 5-битный символ."
    )
    report_lines.append(
        "Цель - устранить длинные последовательности нулей и обеспечить синхронизацию."
    )
    report_lines.append("")
    report_lines.append(
        f"**Исходное сообщение:** {format_bits(bits)} ({len(bits)} бит)"
    )
    report_lines.append(
        f"**Закодированное сообщение:** {format_bits(encoded_bits)} ({len(encoded_bits)} бит)"
    )
    report_lines.append("![4B/5B](../output/report_4b5b.png)")
    report_lines.append("")
    report_lines.append("**Характеристики:**")
    report_lines.append("")

    report_lines.append("**Коэффициент расширения:**")
    report_lines.append("")
    report_lines.append(
        f"$$k = \\frac{{L_{{код}}}}{{L_{{исх}}}} = "
        f"\\frac{{{m_4b5b.encoded_length}}}{{{m_4b5b.original_length}}} = "
        f"{m_4b5b.expansion_factor:.2f}$$"
    )
    report_lines.append("")
    report_lines.append(
        "Каждые 4 бита данных заменяются на 5-битный символ, поэтому закодированная "
        "последовательность на 25% длиннее исходной."
    )
    report_lines.append("")

    report_lines.append("**Избыточность:**")
    report_lines.append("")
    report_lines.append(
        f"$$R = \\frac{{L_{{код}} - L_{{исх}}}}{{L_{{код}}}} \\cdot 100\\% = "
        f"\\frac{{{m_4b5b.encoded_length} - {m_4b5b.original_length}}}{{{m_4b5b.encoded_length}}} \\cdot 100\\% = "
        f"\\frac{{{m_4b5b.encoded_length - m_4b5b.original_length}}}{{{m_4b5b.encoded_length}}} \\cdot 100\\% = "
        f"{m_4b5b.redundancy_percent:.1f}\\%$$"
    )
    report_lines.append("")
    report_lines.append(
        "Избыточность показывает, какая доля передаваемых бит не несёт полезной "
        "информации. Здесь 20% бит добавлены специально для обеспечения синхронизации."
    )
    report_lines.append("")

    report_lines.append("**Скорость в канале:**")
    report_lines.append("")
    report_lines.append(
        f"$$C_{{кан}} = C \\cdot k = {bit_rate:.0f} \\cdot {m_4b5b.expansion_factor:.2f} = {m_4b5b.channel_rate:.1f} \\text{{ Мбит/с}}$$"
    )
    report_lines.append("")
    report_lines.append(
        "Поскольку в канал передаётся больше бит, чем в исходных данных, "
        "скорость в канале выше номинальной. Все расчёты частот для 4B/5B "
        "используют именно $C_{кан}$, а не исходную скорость $C$."
    )
    report_lines.append("")

    report_lines.append("**Верхняя граница частоты:**")
    report_lines.append("")
    report_lines.append(
        f"$$f_{{в}} = \\frac{{C_{{кан}}}}{{2}} = "
        f"\\frac{{{m_4b5b.channel_rate:.1f}}}{{2}} = "
        f"{m_4b5b.f_high:.1f} \\text{{ МГц}}$$"
    )
    report_lines.append("")

    report_lines.append("**Нижняя граница частоты:**")
    report_lines.append("")
    report_lines.append(
        f"$$f_{{н}} = \\frac{{C_{{кан}}}}{{2 \\cdot N_{{max}}}} = "
        f"\\frac{{{m_4b5b.channel_rate:.1f}}}{{2 \\cdot 4}} = "
        f"\\frac{{{m_4b5b.channel_rate:.1f}}}{{8}} = "
        f"{m_4b5b.f_low:.2f} \\text{{ МГц}}$$"
    )
    report_lines.append("")
    report_lines.append(
        "где $N_{max} = 4$ — максимальное число нулей подряд после 4B/5B кодирования"
    )
    report_lines.append("")
    report_lines.append(
        "Таблица 4B/5B гарантирует не более 3 нулей подряд внутри одного 5-битного символа. "
        "Однако нули могут оказаться на стыке двух соседних символов: "
        "если символ заканчивается нулями, а следующий начинается нулями, "
        "серия может достигнуть 4 бит. Именно поэтому в формуле используется $N_{max} = 4$, а не 3."
    )
    report_lines.append("")

    report_lines.append("**Полоса пропускания:**")
    report_lines.append("")
    report_lines.append(
        f"$$\\Delta f = f_{{в}} - f_{{н}} = {m_4b5b.f_high:.1f} - {m_4b5b.f_low:.2f} = {m_4b5b.bandwidth:.2f} \\text{{ МГц}}$$"
    )
    report_lines.append("")

    report_lines.append(f"- Уровней сигнала: {m_4b5b.signal_levels}")
    report_lines.append(f"- Макс. серия нулей: {m_4b5b.max_consecutive_zeros}")
    report_lines.append("")

    scrambled_bits = scramble(bits)
    m_scrambled = calculate_scrambled_nrz_metrics(bits, scrambled_bits, bit_rate)
    metrics_list.append(m_scrambled)

    signal_scrambled = nrz_encode(scrambled_bits)

    fig = plotter.plot_signal(
        signal_func=make_plot(signal_scrambled, len(signal_scrambled)),
        num_samples=len(signal_scrambled) * 10,
        title=f"Scrambled NRZ: {format_bits(scrambled_bits)[:20]}...",
        y_range=(-1.3, 1.3),
        time_range=(0, len(signal_scrambled)),
        output_path=f"{output_dir}/report_scrambled.png",
    )

    report_lines.append("## 5. Этап 4: Скремблирование")
    report_lines.append("")
    report_lines.append("### Скремблирование (полином 7-го порядка)")
    report_lines.append("")
    report_lines.append(
        "**Описание:** Скремблирование с полиномом B_i = A_i ⊕ B_{i-5} ⊕ B_{i-7}."
    )
    report_lines.append(
        "Цель - устранение постоянной составляющей и длинных последовательностей нулей."
    )
    report_lines.append("")
    report_lines.append(
        f"**Исходное сообщение:** {format_bits(bits)} ({len(bits)} бит)"
    )
    report_lines.append(
        f"**Скремблированное сообщение:** {format_bits(scrambled_bits)} ({len(scrambled_bits)} бит)"
    )
    report_lines.append(
        f"**Макс. серия нулей до скремблирования:** {find_max_consecutive(bits, 0)}"
    )
    report_lines.append(
        f"**Макс. серия нулей после скремблирования:** {find_max_consecutive(scrambled_bits, 0)}"
    )
    report_lines.append("")
    report_lines.append("![Scrambled NRZ](../output/report_scrambled.png)")
    report_lines.append("")
    report_lines.append("**Характеристики:**")
    report_lines.append("")

    max_zeros_before = find_max_consecutive(bits, 0)
    max_zeros_after = m_scrambled.max_consecutive_zeros

    report_lines.append("**Верхняя граница частоты:**")
    report_lines.append("")
    report_lines.append(
        f"$$f_{{в}} = \\frac{{C}}{{2}} = \\frac{{{bit_rate:.0f}}}{{2}} = {m_scrambled.f_high:.1f} \\text{{ МГц}}$$"
    )
    report_lines.append("")
    report_lines.append(
        "Скремблирование не меняет битовую скорость и не добавляет избыточности, "
        "поэтому верхняя граница частоты такая же, как у обычного NRZ."
    )
    report_lines.append("")

    report_lines.append("**Нижняя граница частоты:**")
    report_lines.append("")
    nmax_scrambled = max(max_zeros_after, 1)
    report_lines.append(
        f"$$f_{{н}} = \\frac{{C}}{{2 \\cdot N_{{max}}}} = "
        f"\\frac{{{bit_rate:.0f}}}{{2 \\cdot {nmax_scrambled}}} = "
        f"\\frac{{{bit_rate:.0f}}}{{2 * {nmax_scrambled}}} = "
        f"{m_scrambled.f_low:.2f} \\text{{ МГц}}$$"
    )
    report_lines.append("")
    report_lines.append(
        f"где $N_{{max}} = {nmax_scrambled}$ — максимальная серия нулей после скремблирования "
        f"(до: {max_zeros_before}, после: {max_zeros_after})"
    )
    report_lines.append("")
    report_lines.append(
        "Скремблирование разбивает длинные последовательности нулей путём XOR с "
        "псевдослучайной последовательностью, заданной полиномом. "
        "В результате $N_{max}$ уменьшается, что поднимает нижнюю границу частоты "
        "и сужает требуемую полосу пропускания."
    )
    report_lines.append("")

    report_lines.append("**Полоса пропускания:**")
    report_lines.append("")
    report_lines.append(
        f"$$\\Delta f = f_{{в}} - f_{{н}} = {m_scrambled.f_high:.1f} - {m_scrambled.f_low:.2f} = {m_scrambled.bandwidth:.2f} \\text{{ МГц}}$$"
    )
    report_lines.append("")

    report_lines.append(f"- Уровней сигнала: {m_scrambled.signal_levels}")
    report_lines.append(
        f"- Постоянная составляющая (DC): {'Да' if m_scrambled.has_dc_component else 'Нет'}"
    )
    report_lines.append(f"- Макс. серия нулей: {max_zeros_after}")
    report_lines.append("")

    report_lines.append("## 6. Сводная таблица характеристик")
    report_lines.append("")
    report_lines.append(
        "| Метод | Полоса (МГц) | f_в (МГц) | f_н (МГц) | Уровни | DC |"
    )
    report_lines.append(
        "|-------|-------------|-----------|-----------|--------|-----|"
    )

    for m in metrics_list:
        dc = "Да" if m.has_dc_component else "Нет"
        bw = f"{m.bandwidth:.1f}"
        f_high = f"{m.f_high:.1f}"
        f_low = f"{m.f_low:.1f}"
        levels = str(m.signal_levels)
        report_lines.append(
            f"| {m.encoding_name} | {bw} | {f_high} | {f_low} | {levels} | {dc} |"
        )

    report_lines.append("")

    report_lines.append("## 7. Формулы для расчёта частот")
    report_lines.append("")
    report_lines.append("### Общие определения")
    report_lines.append("")
    report_lines.append("- $C$ — скорость передачи данных (бит/с)")
    report_lines.append("- $N_{max}$ — максимальная длина серии одинаковых бит подряд")
    report_lines.append(
        "- $f_{в}$ — верхняя граница частоты (максимальная частота спектра)"
    )
    report_lines.append(
        "- $f_{н}$ — нижняя граница частоты (минимальная существенная частота)"
    )
    report_lines.append("- $\\Delta f$ — требуемая полоса пропускания")
    report_lines.append("")
    report_lines.append(
        "Верхняя граница $f_{в}$ определяется минимальной длительностью элемента сигнала: "
        "чем короче импульс, тем выше частоты в его спектре. "
        "Нижняя граница $f_{н}$ зависит от максимальной повторяющейся структуры в данных — "
        "длинная серия одинаковых бит создаёт низкочастотный сигнал."
    )
    report_lines.append("")
    report_lines.append("### Формулы по методам")
    report_lines.append("")

    report_lines.append(
        "| Метод | Формула $f_{в}$ | Формула $f_{н}$ | Формула $\\Delta f$ |"
    )
    report_lines.append(
        "|-------|-----------------|-----------------|---------------------|"
    )
    report_lines.append("| NRZ | $C/2$ | $C/(2 \\cdot N_{max})$ | $f_{в} - f_{н}$ |")
    report_lines.append("| Manchester | $C$ | $C/2$ | $f_{в} - f_{н}$ |")
    report_lines.append("| RZ | $C$ | $C/4$ | $f_{в} - f_{н}$ |")
    report_lines.append(
        "| AMI | $C/2$ | $C/(2 \\cdot (N_{max}+1))$ | $f_{в} - f_{н}$ |"
    )
    report_lines.append(
        "| 4B/5B+NRZ | $C_{кан}/2$ | $C_{кан}/(2 \\cdot 4)$ | $f_{в} - f_{н}$ |"
    )
    report_lines.append(
        "| Scrambled NRZ | $C/2$ | $C/(2 \\cdot N_{max})$ | $f_{в} - f_{н}$ |"
    )
    report_lines.append("")

    report_lines.append("### Расчёт для каждого метода")
    report_lines.append("")

    for m in metrics_list:
        report_lines.append(f"#### {m.encoding_name}")
        report_lines.append("")

        if m.encoding_name == "NRZ":
            nmax = max(m.max_consecutive_zeros, m.max_consecutive_ones)
            report_lines.append(
                f"$$f_{{в}} = \\frac{{C}}{{2}} = \\frac{{{m.bit_rate:.0f}}}{{2}} = {m.f_high:.1f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(
                f"$$f_{{н}} = \\frac{{C}}{{2 \\cdot N_{{max}}}} = "
                f"\\frac{{{m.bit_rate:.0f}}}{{2 \\cdot {nmax}}} = {m.f_low:.2f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(
                f"$$\\Delta f = f_{{в}} - f_{{н}} = {m.f_high:.1f} - {m.f_low:.2f} = {m.bandwidth:.2f} \\text{{ МГц}}$$"
            )

        elif "Manchester" in m.encoding_name:
            report_lines.append(f"$$f_{{в}} = C = {m.bit_rate:.0f} \\text{{ МГц}}$$")
            report_lines.append("")
            report_lines.append(
                f"$$f_{{н}} = \\frac{{C}}{{2}} = \\frac{{{m.bit_rate:.0f}}}{{2}} = {m.f_low:.1f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(
                f"$$\\Delta f = f_{{в}} - f_{{н}} = {m.f_high:.0f} - {m.f_low:.1f} = {m.bandwidth:.1f} \\text{{ МГц}}$$"
            )

        elif m.encoding_name == "RZ":
            report_lines.append(f"$$f_{{в}} = C = {m.bit_rate:.0f} \\text{{ МГц}}$$")
            report_lines.append("")
            report_lines.append(
                f"$$f_{{н}} = \\frac{{C}}{{4}} = \\frac{{{m.bit_rate:.0f}}}{{4}} = {m.f_low:.1f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(
                f"$$\\Delta f = f_{{в}} - f_{{н}} = {m.f_high:.0f} - {m.f_low:.1f} = {m.bandwidth:.1f} \\text{{ МГц}}$$"
            )

        elif m.encoding_name == "AMI":
            report_lines.append(
                f"$$f_{{в}} = \\frac{{C}}{{2}} = \\frac{{{m.bit_rate:.0f}}}{{2}} = {m.f_high:.1f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(
                f"$$f_{{н}} = \\frac{{C}}{{2 \\cdot (N_{{max}} + 1)}} = "
                f"\\frac{{{m.bit_rate:.0f}}}{{2 \\cdot ({m.max_consecutive_zeros} + 1)}} = "
                f"\\frac{{{m.bit_rate:.0f}}}{{2 \\cdot {m.max_consecutive_zeros + 1}}} = "
                f"{m.f_low:.2f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(
                f"$$\\Delta f = f_{{в}} - f_{{н}} = {m.f_high:.1f} - {m.f_low:.2f} = {m.bandwidth:.2f} \\text{{ МГц}}$$"
            )

        elif m.encoding_name == "4B/5B+NRZ":
            report_lines.append(
                f"$$C_{{кан}} = C \\cdot k = {m.bit_rate:.0f} \\cdot {m.expansion_factor:.2f} = {m.channel_rate:.1f} \\text{{ Мбит/с}}$$"
            )
            report_lines.append("")
            report_lines.append(
                f"$$f_{{в}} = \\frac{{C_{{кан}}}}{{2}} = \\frac{{{m.channel_rate:.1f}}}{{2}} = {m.f_high:.1f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(
                f"$$f_{{н}} = \\frac{{C_{{кан}}}}{{2 \\cdot 4}} = \\frac{{{m.channel_rate:.1f}}}{{8}} = {m.f_low:.2f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(
                f"$$\\Delta f = f_{{в}} - f_{{н}} = {m.f_high:.1f} - {m.f_low:.2f} = {m.bandwidth:.2f} \\text{{ МГц}}$$"
            )

        elif "Scrambled" in m.encoding_name:
            nmax = max(m.max_consecutive_zeros, 1)
            report_lines.append(
                f"$$f_{{в}} = \\frac{{C}}{{2}} = \\frac{{{m.bit_rate:.0f}}}{{2}} = {m.f_high:.1f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(
                f"$$f_{{н}} = \\frac{{C}}{{2 \\cdot N_{{max}}}} = "
                f"\\frac{{{m.bit_rate:.0f}}}{{2 \\cdot {nmax}}} = {m.f_low:.2f} \\text{{ МГц}}$$"
            )
            report_lines.append("")
            report_lines.append(
                f"$$\\Delta f = f_{{в}} - f_{{н}} = {m.f_high:.1f} - {m.f_low:.2f} = {m.bandwidth:.2f} \\text{{ МГц}}$$"
            )

        report_lines.append("")
    report_lines.append("## 8. Выводы")
    report_lines.append("")
    report_lines.append("### Анализ результатов")
    report_lines.append("")

    min_bandwidth = min(m.bandwidth for m in metrics_list)
    best_methods = [m for m in metrics_list if m.bandwidth == min_bandwidth]
    best_names = ", ".join(m.encoding_name for m in best_methods)

    report_lines.append(
        f"1. **Минимальную полосу пропускания** требует метод {best_names}: **{min_bandwidth:.1f} МГц**. "
    )
    report_lines.append(
        f"   Это достигается благодаря уменьшению $N_{{max}}$ скремблированием, "
        f"что поднимает нижнюю границу частоты $f_{{н}}$ и сужает полосу."
    )
    report_lines.append("")

    no_dc_methods = [m for m in metrics_list if not m.has_dc_component]
    report_lines.append(
        f"2. **Отсутствие постоянной составляющей (DC)** имеют {len(no_dc_methods)} методов: "
    )
    report_lines.append(", ".join([m.encoding_name for m in no_dc_methods]) + ". ")
    report_lines.append(
        "Это важно для систем с трансформаторной развязкой, где постоянная "
        "составляющая не может проходить через трансформатор."
    )
    report_lines.append("")

    nrz_metrics = next(m for m in metrics_list if m.encoding_name == "NRZ")
    manchester_metrics = next(
        m for m in metrics_list if "Manchester" in m.encoding_name
    )

    report_lines.append("3. **Сравнение NRZ и Manchester:**")
    report_lines.append(
        f"   - Manchester требует полосу в {manchester_metrics.bandwidth / nrz_metrics.bandwidth:.1f} раза больше "
        f"({manchester_metrics.bandwidth:.1f} vs {nrz_metrics.bandwidth:.1f} МГц)"
    )
    report_lines.append(
        "   - Но Manchester обеспечивает гарантированную синхронизацию благодаря переходу в середине каждого бита"
    )
    report_lines.append(
        "   - У Manchester нет зависимости от данных: полоса всегда одна и та же, "
        "в отличие от NRZ, где $f_{н}$ зависит от $N_{max}$ в конкретном сообщении"
    )
    report_lines.append("")

    report_lines.append("4. **Логическое кодирование (4B/5B):**")
    report_lines.append(
        f"   - Увеличивает скорость до {m_4b5b.channel_rate:.0f} Мбит/с (избыточность {m_4b5b.redundancy_percent:.0f}%)"
    )
    report_lines.append(
        f"   - Гарантирует не более {m_4b5b.max_consecutive_zeros} нулей подряд"
    )
    report_lines.append(
        f"   - Полоса увеличивается пропорционально: {m_4b5b.bandwidth:.1f} МГц"
    )
    report_lines.append("")

    report_lines.append("5. **Скремблирование:**")
    report_lines.append("   - Не увеличивает скорость (избыточность 0%)")
    report_lines.append(
        f"   - Сокращает максимальную серию нулей с {find_max_consecutive(bits, 0)} до {find_max_consecutive(scrambled_bits, 0)}"
    )
    report_lines.append(
        f"   - Полоса сужается с {nrz_metrics.bandwidth:.1f} до {m_scrambled.bandwidth:.1f} МГц благодаря уменьшению $N_{{max}}$"
    )
    report_lines.append("")

    report_lines.append("### Рекомендации")
    report_lines.append("")
    report_lines.append(
        "- **Для высокоскоростных линий** (ограниченная полоса): NRZ, AMI или Scrambled NRZ"
    )
    report_lines.append(
        "- **Для критически важной синхронизации**: Manchester (гарантированный переход)"
    )
    report_lines.append("- **Для баланса скорости и синхронизации**: 4B/5B + NRZ")
    report_lines.append("")

    report = "\n".join(report_lines)

    report_path = f"{output_dir}/report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Отчёт сгенерирован: {report_path}")

    return report_path


def main():
    """Точка входа."""
    generate_report(hex_data="C3C4C2", bit_rate=100.0)


if __name__ == "__main__":
    main()
