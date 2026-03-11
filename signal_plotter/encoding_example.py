"""
Демонстрация физического кодирования сигналов
"""

import numpy as np
from signal_plotter import SignalPlotter
from signal_plotter.encodings import encode_data, bytes_to_bits


def main():
    """Демонстрация всех методов кодирования."""

    plotter = SignalPlotter(figsize=(16, 3), dpi=150)

    test_data = bytes([0b10110010, 0b01101001, 0b10011100])
    bits_str = "".join(map(str, bytes_to_bits(test_data)))
    print(
        f"Тестовые данные: {test_data.hex()} ({len(test_data)} байта, {len(bits_str)} бит)"
    )
    print(f"Биты: {bits_str}")
    print()

    encodings = [
        ("nrz", "NRZ (Non-Return-to-Zero)"),
        ("manchester", "Манчестерское кодирование"),
        ("rz", "RZ (Return-to-Zero)"),
        ("ami", "AMI (Alternate Mark Inversion)"),
    ]

    for enc_id, enc_name in encodings:
        signal = encode_data(test_data, enc_id)

        if enc_id == "nrz":
            y_range = (-1.2, 1.2)
            title = f"{enc_name}: {bits_str}"
        elif enc_id == "manchester":
            y_range = (-1.2, 1.2)
            title = f"{enc_name} (IEEE 802.3): {bits_str}"
        elif enc_id == "rz":
            y_range = (-1.2, 1.2)
            title = f"{enc_name}: {bits_str}"
        elif enc_id == "ami":
            y_range = (-1.2, 1.2)
            title = f"{enc_name}: {bits_str}"
        else:
            y_range = (-1.2, 1.2)
            title = f"{enc_name}: {bits_str}"

        def make_signal(t_arr, sig=signal):
            indices = t_arr.astype(int)
            indices = np.clip(indices, 0, len(sig) - 1)
            return sig[indices]

        fig = plotter.plot_signal(
            signal_func=make_signal,
            num_samples=len(signal) * 10,
            title=title,
            y_range=y_range,
            time_range=(0, len(signal)),
            output_path=f"output/encoding_{enc_id}.png",
        )
        plt.close(fig)
        print(f"Сохранено: output/encoding_{enc_id}.png")


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    main()
