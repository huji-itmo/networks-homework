"""
Генератор отчёта по лабораторной работе
"""

import os
from pathlib import Path

from signal_plotter.encodings import (
    bytes_to_bits,
    nrz_encode,
    manchester_encode,
    rz_encode,
    ami_encode,
    encode_4b5b,
    scramble,
)
from signal_plotter.metrics import (
    calculate_nrz_metrics,
    calculate_manchester_metrics,
    calculate_rz_metrics,
    calculate_ami_metrics,
    calculate_4b5b_nrz_metrics,
    calculate_scrambled_nrz_metrics,
    find_max_consecutive,
    EncodingMetrics,
)
from signal_plotter import SignalPlotter


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

    def make_plot(signal_array):
        def wrapper(t_arr):
            indices = (t_arr * (len(signal_array) - 1)).astype(int)
            indices = indices.clip(0, len(signal_array) - 1)
            return signal_array[indices]

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

        signal_arr = signal

        def make_plot(sig):
            def plot_func(t):
                indices = (t * (len(sig) - 1)).astype(int)
                indices = indices.clip(0, len(sig) - 1)
                return sig[indices]

            return plot_func

        fig = plotter.plot_signal(
            signal_func=make_plot(signal),
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
        report_lines.append(f"- Верхняя граница частоты: **{m.f_high:.2f} МГц**")
        report_lines.append(f"- Нижняя граница частоты: **{m.f_low:.2f} МГц**")
        report_lines.append(
            f"- Требуемая полоса пропускания: **{m.bandwidth:.2f} МГц**"
        )
        report_lines.append(f"- Уровней сигнала: {m.signal_levels}")
        report_lines.append(
            f"- Постоянная составляющая (DC): {'Да' if m.has_dc_component else 'Нет'}"
        )
        if m.max_consecutive_zeros:
            report_lines.append(f"- Макс. серия нулей: {m.max_consecutive_zeros}")
        report_lines.append("")

    encoded_bits = encode_4b5b(bits)
    m_4b5b = calculate_4b5b_nrz_metrics(bits, encoded_bits, bit_rate)
    metrics_list.append(m_4b5b)

    signal_4b5b = nrz_encode(encoded_bits)

    fig = plotter.plot_signal(
        signal_func=make_plot(signal_4b5b),
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
    report_lines.append(f"**Избыточность:** {m_4b5b.redundancy_percent:.1f}%")
    report_lines.append("")
    report_lines.append("![4B/5B](../output/report_4b5b.png)")
    report_lines.append("")
    report_lines.append("**Характеристики:**")
    report_lines.append(f"- Скорость в канале: **{m_4b5b.channel_rate:.1f} Мбит/с**")
    report_lines.append(f"- Верхняя граница частоты: **{m_4b5b.f_high:.2f} МГц**")
    report_lines.append(f"- Нижняя граница частоты: **{m_4b5b.f_low:.2f} МГц**")
    report_lines.append(
        f"- Требуемая полоса пропускания: **{m_4b5b.bandwidth:.2f} МГц**"
    )
    report_lines.append(f"- Уровней сигнала: {m_4b5b.signal_levels}")
    report_lines.append(f"- Макс. серия нулей: {m_4b5b.max_consecutive_zeros}")
    report_lines.append("")

    scrambled_bits = scramble(bits)
    m_scrambled = calculate_scrambled_nrz_metrics(bits, scrambled_bits, bit_rate)
    metrics_list.append(m_scrambled)

    signal_scrambled = nrz_encode(scrambled_bits)

    fig = plotter.plot_signal(
        signal_func=make_plot(signal_scrambled),
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
    report_lines.append(f"- Верхняя граница частоты: **{m_scrambled.f_high:.2f} МГц**")
    report_lines.append(f"- Нижняя граница частоты: **{m_scrambled.f_low:.2f} МГц**")
    report_lines.append(
        f"- Требуемая полоса пропускания: **{m_scrambled.bandwidth:.2f} МГц**"
    )
    report_lines.append(f"- Уровней сигнала: {m_scrambled.signal_levels}")
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

    report_lines.append("## 7. Выводы")
    report_lines.append("")
    report_lines.append("### Анализ результатов")
    report_lines.append("")

    min_bandwidth = min(m.bandwidth for m in metrics_list)
    best_methods = [m for m in metrics_list if m.bandwidth == min_bandwidth]

    report_lines.append(
        f"1. **Минимальную полосу пропускания** требуют методы NRZ, AMI и Scrambled NRZ: **{min_bandwidth:.1f} МГц**. "
    )
    report_lines.append(f"   Это связано с тем, что их максимальная частота равна C/2.")
    report_lines.append("")

    no_dc_methods = [m for m in metrics_list if not m.has_dc_component]
    report_lines.append(
        f"2. **Отсутствие постоянной составляющей (DC)** имеют {len(no_dc_methods)} методов: "
    )
    report_lines.append(", ".join([m.encoding_name for m in no_dc_methods]) + ". ")
    report_lines.append("Это важно для систем с трансформаторной развязкой.")
    report_lines.append("")

    nrz_metrics = next(m for m in metrics_list if m.encoding_name == "NRZ")
    manchester_metrics = next(
        m for m in metrics_list if "Manchester" in m.encoding_name
    )

    report_lines.append("3. **Сравнение NRZ и Manchester:**")
    report_lines.append(
        f"   - Manchester требует полосу в 2 раза больше ({manchester_metrics.bandwidth:.1f} vs {nrz_metrics.bandwidth:.1f} МГц)"
    )
    report_lines.append(
        f"   - Но Manchester обеспечивает гарантированную синхронизацию благодаря переходу в середине каждого бита"
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
    report_lines.append(f"   - Не увеличивает скорость (избыточность 0%)")
    report_lines.append(
        f"   - Сокращает максимальную серию нулей с {find_max_consecutive(bits, 0)} до {find_max_consecutive(scrambled_bits, 0)}"
    )
    report_lines.append(
        f"   - Полоса остаётся как у NRZ: {m_scrambled.bandwidth:.1f} МГц"
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
    generate_report(hex_data="B2699C", bit_rate=100.0)


if __name__ == "__main__":
    main()
