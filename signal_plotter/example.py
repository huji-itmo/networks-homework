"""
Пример использования библиотеки Signal Plotter
Демонстрация построения графиков сигналов для курса компьютерных сетей
"""

import numpy as np
import matplotlib.pyplot as plt
from signal_plotter import SignalPlotter, plot_signal


def sine_wave(t: np.ndarray) -> np.ndarray:
    """Синусоидальный сигнал [-1, 1]"""
    return np.sin(2 * np.pi * t)


def cosine_wave(t: np.ndarray) -> np.ndarray:
    """Косинусоидальный сигнал [-1, 1]"""
    return np.cos(2 * np.pi * t)


def square_wave(t: np.ndarray) -> np.ndarray:
    """Меандр (прямоугольный сигнал) [0, 1]"""
    return (np.sin(2 * np.pi * t) > 0).astype(float)


def sawtooth_wave(t: np.ndarray) -> np.ndarray:
    """Пилообразный сигнал [0, 1]"""
    return 2 * (t - np.floor(t + 0.5))


def main():
    """Основная функция - демонстрация всех возможностей"""

    plotter = SignalPlotter(figsize=(16, 3), dpi=150)

    print("=" * 50)
    print("Signal Plotter - Демонстрация")
    print("=" * 50)

    print("\n1. Синусоида (диапазон [-1, 1]):")
    fig = plotter.plot_signal(
        signal_func=sine_wave,
        num_samples=1000,
        title="Синусоидальный сигнал",
        ylabel="Амплитуда",
        color="blue",
        output_path="output/sine_wave.png",
        format="png",
        y_range=(-1.2, 1.2),
    )
    plt.close(fig)

    print("\n2. Косинусоида (диапазон [-1, 1]):")
    fig = plotter.plot_signal(
        signal_func=cosine_wave,
        num_samples=1000,
        title="Косинусоидальный сигнал",
        color="green",
        output_path="output/cosine_wave.png",
        y_range=(-1.2, 1.2),
    )
    plt.close(fig)

    print("\n3. Меандр (цифровой сигнал, диапазон [0, 1]):")
    fig = plotter.plot_signal(
        signal_func=square_wave,
        num_samples=1000,
        title="Меандр (прямоугольный сигнал)",
        color="red",
        output_path="output/square_wave.png",
        y_range=(-0.1, 1.1),
    )
    plt.close(fig)

    print("\n4. Пилообразный сигнал (диапазон [0, 1]):")
    fig = plotter.plot_signal(
        signal_func=sawtooth_wave,
        num_samples=1000,
        title="Пилообразный сигнал",
        color="purple",
        output_path="output/sawtooth_wave.png",
        y_range=(-0.1, 1.1),
    )
    plt.close(fig)

    print("\n5. Цифровой сигнал из битов (bit_time=1.0, мгновенный переход):")
    bits = [1, 0, 1, 1, 0]
    fig = plotter.plot_digital_signal(
        bits=bits,
        bit_time=1.0,
        transition_time=0.0,
        samples_per_bit=100,
        title="Цифровой сигнал: " + "".join(map(str, bits)) + " (5 битов, t=0..5)",
        output_path="output/digital_signal.png",
        amplitude=1.0,
    )
    plt.close(fig)

    print("\n6. Цифровой сигнал с transition_time (плавный переход):")
    bits = [1, 0, 1, 0, 1]
    fig = plotter.plot_digital_signal(
        bits=bits,
        bit_time=1.0,
        transition_time=0.3,
        samples_per_bit=100,
        title="Цифровой сигнал с плавным переходом",
        output_path="output/digital_signal_transition.png",
        amplitude=1.0,
    )
    plt.close(fig)

    print("\n7. Цифровой сигнал с разным bit_time:")
    bits = [1, 0, 1]
    fig = plotter.plot_digital_signal(
        bits=bits,
        bit_time=2.0,
        transition_time=0.0,
        samples_per_bit=100,
        title="Цифровой сигнал: bit_time=2.0 (3 бита, t=0..6)",
        output_path="output/digital_signal_bit_time.png",
        amplitude=1.0,
    )
    plt.close(fig)

    print("\n8. Быстрый вызов с помощью функции plot_signal():")
    fig = plot_signal(
        signal_func=lambda t: np.sin(4 * np.pi * t),
        num_samples=500,
        title="Быстрый вызов: синус 2 Гц",
        color="orange",
        output_path="output/quick_plot.png",
    )
    plt.close(fig)

    print("\n" + "=" * 50)
    print("Все графики сохранены в папку 'output/'")
    print("=" * 50)


if __name__ == "__main__":
    main()
