"""
Модуль расчета метрик кодирования сигналов
Для курса "Компьютерные сети"
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class EncodingMetrics:
    """Единый контейнер метрик для любой кодировки"""

    encoding_name: str
    bit_rate: float
    channel_rate: Optional[float] = None

    f_high: Optional[float] = None
    f_low: Optional[float] = None
    f_mid: Optional[float] = None
    f_avg: Optional[float] = None
    spectrum_width: Optional[float] = None
    bandwidth: Optional[float] = None

    has_dc_component: Optional[bool] = None
    signal_levels: Optional[int] = None

    max_consecutive_zeros: Optional[int] = None
    max_consecutive_ones: Optional[int] = None
    ones_count: Optional[int] = None
    total_bits: Optional[int] = None

    original_length: Optional[int] = None
    encoded_length: Optional[int] = None
    redundancy_percent: Optional[float] = None
    expansion_factor: Optional[float] = None

    notes: List[str] = field(default_factory=list)

    def calculate_derived(self):
        """Авто-расчет производных метрик после заполнения основных"""
        if self.f_high is not None and self.f_low is not None:
            self.f_mid = (self.f_high + self.f_low) / 2
            self.spectrum_width = self.f_high - self.f_low
            if self.bandwidth is None:
                self.bandwidth = self.f_high - self.f_low
        if self.channel_rate is None:
            self.channel_rate = self.bit_rate


def find_max_consecutive(bits: List[int], value: int) -> int:
    """Найти максимальную длину последовательности одинаковых бит"""
    max_len = current = 0
    for bit in bits:
        if bit == value:
            current += 1
            max_len = max(max_len, current)
        else:
            current = 0
    return max_len


def calculate_weighted_avg_frequency(
    bits: List[int], bit_rate: float, method: str
) -> float:
    """Расчет средней частоты на основе анализа паттернов"""
    if len(bits) < 2:
        return bit_rate / 2

    transitions = sum(1 for i in range(1, len(bits)) if bits[i] != bits[i - 1])
    transition_density = transitions / (len(bits) - 1) if len(bits) > 1 else 0

    if method == "nrz":
        return bit_rate / 2 * transition_density + bit_rate / (2 * len(bits)) * (
            1 - transition_density
        )
    elif method == "manchester":
        return bit_rate * 0.75
    elif method == "rz":
        return bit_rate
    elif method == "ami":
        ones_ratio = sum(bits) / len(bits) if len(bits) > 0 else 0
        return ones_ratio * bit_rate / 2
    return bit_rate / 2


def calculate_nrz_metrics(bits: List[int], bit_rate: float) -> EncodingMetrics:
    """Расчет метрик для NRZ"""
    m = EncodingMetrics(
        encoding_name="NRZ",
        bit_rate=bit_rate,
        total_bits=len(bits),
        ones_count=sum(bits),
        signal_levels=2,
        has_dc_component=True,
    )

    m.max_consecutive_zeros = find_max_consecutive(bits, 0)
    m.max_consecutive_ones = find_max_consecutive(bits, 1)
    nmax = max(m.max_consecutive_zeros, m.max_consecutive_ones)

    m.f_high = bit_rate / 2
    m.f_low = bit_rate / (2 * nmax) if nmax > 0 else bit_rate / 2
    m.f_avg = calculate_weighted_avg_frequency(bits, bit_rate, "nrz")

    m.notes.append(f"nmax={nmax} влияет на нижнюю границу частот")
    m.calculate_derived()
    return m


def calculate_manchester_metrics(
    bits: List[int], bit_rate: float, variant: str = "ieee"
) -> EncodingMetrics:
    """Расчет метрик для Manchester"""
    m = EncodingMetrics(
        encoding_name=f"Manchester ({variant.upper()})",
        bit_rate=bit_rate,
        total_bits=len(bits),
        signal_levels=2,
        has_dc_component=False,
    )

    m.f_high = bit_rate
    m.f_low = bit_rate / 2
    m.f_avg = (m.f_high + m.f_low) / 2

    m.notes.append("Гарантированный переход в середине каждого бита")
    m.calculate_derived()
    return m


def calculate_rz_metrics(bits: List[int], bit_rate: float) -> EncodingMetrics:
    """Расчет метрик для RZ"""
    m = EncodingMetrics(
        encoding_name="RZ",
        bit_rate=bit_rate,
        total_bits=len(bits),
        signal_levels=3,
        has_dc_component=False,
    )

    m.f_high = bit_rate
    m.f_low = bit_rate / 4
    m.f_avg = bit_rate

    m.notes.append("Импульс длится половину такта, затем возврат к нулю")
    m.calculate_derived()
    return m


def calculate_ami_metrics(bits: List[int], bit_rate: float) -> EncodingMetrics:
    """Расчет метрик для AMI"""
    m = EncodingMetrics(
        encoding_name="AMI",
        bit_rate=bit_rate,
        total_bits=len(bits),
        signal_levels=3,
        has_dc_component=False,
    )

    m.max_consecutive_zeros = find_max_consecutive(bits, 0)
    m.ones_count = sum(bits)
    m.total_bits = len(bits)

    m.f_high = bit_rate / 2
    m.f_low = bit_rate / (2 * (m.max_consecutive_zeros + 1))
    m.f_avg = (m.ones_count / m.total_bits) * (bit_rate / 2) if m.total_bits > 0 else 0

    m.notes.append(
        f"Нижняя граница зависит от серии нулей: nmax={m.max_consecutive_zeros}"
    )
    m.calculate_derived()
    return m


def calculate_4b5b_nrz_metrics(
    original_bits: List[int], encoded_bits: List[int], bit_rate: float
) -> EncodingMetrics:
    """Расчет метрик для 4B/5B + NRZ"""
    m = EncodingMetrics(
        encoding_name="4B/5B+NRZ",
        bit_rate=bit_rate,
        original_length=len(original_bits),
        encoded_length=len(encoded_bits),
        total_bits=len(encoded_bits),
        ones_count=sum(encoded_bits),
        signal_levels=2,
        has_dc_component=False,
    )

    m.expansion_factor = len(encoded_bits) / len(original_bits)
    m.redundancy_percent = (
        (len(encoded_bits) - len(original_bits)) / len(encoded_bits) * 100
    )
    m.channel_rate = bit_rate * m.expansion_factor

    m.max_consecutive_zeros = 3

    m.f_high = m.channel_rate / 2
    m.f_low = m.channel_rate / (2 * 4)
    m.f_avg = calculate_weighted_avg_frequency(encoded_bits, m.channel_rate, "nrz")

    m.notes.append(
        f"4B/5B гарантирует ≤3 нулей подряд; избыточность {m.redundancy_percent:.1f}%"
    )
    m.calculate_derived()
    return m


def calculate_scrambled_nrz_metrics(
    original_bits: List[int],
    scrambled_bits: List[int],
    bit_rate: float,
    poly_order: int = 7,
) -> EncodingMetrics:
    """Расчет метрик для скремблированного NRZ"""
    m = EncodingMetrics(
        encoding_name=f"Scrambled NRZ (polynomial order {poly_order})",
        bit_rate=bit_rate,
        total_bits=len(scrambled_bits),
        ones_count=sum(scrambled_bits),
        signal_levels=2,
        has_dc_component=False,
    )

    m.max_consecutive_zeros = find_max_consecutive(scrambled_bits, 0)

    m.f_high = bit_rate / 2
    m.f_low = bit_rate / (2 * max(m.max_consecutive_zeros, 1))
    m.f_avg = bit_rate / 4

    m.notes.append(
        f"Скремблирование полиномом {poly_order}-го порядка; макс. нулей подряд: {m.max_consecutive_zeros}"
    )
    m.calculate_derived()
    return m


def generate_report(metrics_list: List[EncodingMetrics], bit_rate: float) -> str:
    """Генерация Markdown отчета из списка метрик"""
    report = ["# Отчет по методам кодирования", ""]
    report.append(f"**Исходная скорость передачи:** {bit_rate} Мбит/с")
    report.append("")

    report.append("## Сводная таблица характеристик")
    report.append("")
    report.append("| Метод | Полоса (МГц) | Уровни сигнала | DC |")
    report.append("|-------|-------------|---------------|-----|")

    for m in metrics_list:
        dc = "Да" if m.has_dc_component else "Нет"
        bw = f"{m.bandwidth:.1f}" if m.bandwidth else "-"
        levels = m.signal_levels if m.signal_levels else "-"
        report.append(f"| {m.encoding_name} | {bw} | {levels} | {dc} |")

    report.append("")

    for m in metrics_list:
        report.append(f"### {m.encoding_name}")
        report.append("")

        if m.bandwidth:
            report.append(f"- **Требуемая полоса пропускания:** {m.bandwidth:.1f} МГц")

        if m.f_low and m.f_high:
            report.append(f"- **Спектр:** {m.f_low:.2f} – {m.f_high:.2f} МГц")

        if m.spectrum_width:
            report.append(f"- **Ширина спектра:** {m.spectrum_width:.2f} МГц")

        if m.f_avg:
            report.append(f"- **Средняя частота:** {m.f_avg:.2f} МГц")

        if m.channel_rate and m.channel_rate != m.bit_rate:
            report.append(f"- **Скорость в канале:** {m.channel_rate:.1f} Мбит/с")

        if m.redundancy_percent:
            report.append(f"- **Избыточность:** {m.redundancy_percent:.1f}%")

        if m.max_consecutive_zeros:
            report.append(f"- **Макс. серия нулей:** {m.max_consecutive_zeros}")

        if m.notes:
            report.append(f"- **Примечания:** {'; '.join(m.notes)}")

        report.append("")

    return "\n".join(report)
