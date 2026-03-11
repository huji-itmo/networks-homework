"""
Демонстрация расчета метрик кодирования и генерации отчета
"""

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
    generate_report,
    EncodingMetrics,
)


def main():
    """Демонстрация расчета метрик"""

    test_data = bytes([0b10110010, 0b01101001, 0b10011100])
    bits = bytes_to_bits(test_data)
    bit_rate = 100.0

    print(f"Тестовые данные: {test_data.hex()} ({len(bits)} бит)")
    print(f"Биты: {''.join(map(str, bits))}")
    print(f"Скорость: {bit_rate} Мбит/с")
    print()

    metrics_list = []

    m = calculate_nrz_metrics(bits, bit_rate)
    metrics_list.append(m)
    print(f"NRZ: f_high={m.f_high}, f_low={m.f_low}, bandwidth={m.bandwidth}")

    m = calculate_manchester_metrics(bits, bit_rate)
    metrics_list.append(m)
    print(f"Manchester: f_high={m.f_high}, f_low={m.f_low}, bandwidth={m.bandwidth}")

    m = calculate_rz_metrics(bits, bit_rate)
    metrics_list.append(m)
    print(f"RZ: f_high={m.f_high}, f_low={m.f_low}, bandwidth={m.bandwidth}")

    m = calculate_ami_metrics(bits, bit_rate)
    metrics_list.append(m)
    print(f"AMI: f_high={m.f_high}, f_low={m.f_low}, bandwidth={m.bandwidth}")

    encoded_bits = encode_4b5b(bits)
    m = calculate_4b5b_nrz_metrics(bits, encoded_bits, bit_rate)
    metrics_list.append(m)
    print(
        f"4B/5B+NRZ: f_high={m.f_high}, f_low={m.f_low}, bandwidth={m.bandwidth}, channel_rate={m.channel_rate}"
    )

    scrambled_bits = scramble(bits)
    m = calculate_scrambled_nrz_metrics(bits, scrambled_bits, bit_rate)
    metrics_list.append(m)
    print(f"Scrambled NRZ: f_high={m.f_high}, f_low={m.f_low}, bandwidth={m.bandwidth}")

    report = generate_report(metrics_list, bit_rate)

    with open("output/metrics_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print()
    print("Отчет сохранен в: output/metrics_report.md")
    print()
    print("=" * 50)
    print(report)


if __name__ == "__main__":
    main()
