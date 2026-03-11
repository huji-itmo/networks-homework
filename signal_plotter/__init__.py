"""
Signal Plotter - мини библиотека для отображения сигналов
Используется в курсе компьютерных сетей для визуализации электрических сигналов
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Callable, Optional, Literal
from pathlib import Path

matplotlib.use("Agg")


class SignalPlotter:
    """
    Класс для отображения сигналов в горизонтальном формате.

    Поддерживает сигналы со значениями в диапазонах [0, 1] или [-1, 1].
    """

    def __init__(
        self, figsize: tuple = (16, 3), dpi: int = 150, style: str = "default"
    ):
        """
        Инициализация построителя графиков.

        Args:
            figsize: Размер фигуры (ширина, высота) в дюймах
            dpi: Разрешение изображения
            style: Стиль matplotlib
        """
        self.figsize = figsize
        self.dpi = dpi
        self.style = style

        if style != "default":
            try:
                plt.style.use(style)
            except:
                pass

    def plot_signal(
        self,
        signal_func: Callable[[np.ndarray], np.ndarray],
        num_samples: int = 1000,
        title: str = "",
        ylabel: str = "Амплитуда",
        xlabel: str = "Время",
        output_path: Optional[str] = None,
        format: Literal["png", "pdf", "svg"] = "png",
        show_grid: bool = True,
        color: str = "blue",
        linewidth: float = 1.5,
        y_range: Optional[tuple] = None,
        time_range: tuple = (0, 1),
    ) -> Figure:
        """
        Построение графика сигнала.

        Args:
            signal_func: Функция, принимающая массив numpy и возвращающая массив значений сигнала
            num_samples: Количество точек для отображения
            title: Заголовок графика
            ylabel: Метка оси Y
            xlabel: Метка оси X
            output_path: Путь для сохранения файла (если None, не сохраняется)
            format: Формат вывода (png, pdf, svg)
            show_grid: Показывать сетку
            color: Цвет линии сигнала
            linewidth: Толщина линии
            y_range: Диапазон оси Y (например, (-1, 1) или (0, 1))
            time_range: Диапазон времени (по умолчанию (0, 1))

        Returns:
            Объект Figure matplotlib
        """
        t = np.linspace(time_range[0], time_range[1], num_samples)
        y = signal_func(t)

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        ax.plot(t, y, color=color, linewidth=linewidth)

        if y_range is not None:
            y_min, y_max = y_range
            margin = (y_max - y_min) * 0.05
            if y.min() <= y_min + margin * 0.1:
                y_min -= margin
            if y.max() >= y_max - margin * 0.1:
                y_max += margin
            ax.set_ylim(y_min, y_max)
        else:
            y_min, y_max = y.min(), y.max()
            margin = (y_max - y_min) * 0.1
            ax.set_ylim(y_min - margin, y_max + margin)

        if title:
            ax.set_title(title, fontsize=14, pad=10)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)

        if show_grid:
            ax.grid(True, alpha=0.3, linestyle="--")

        ax.set_xlim(time_range[0], time_range[1])

        plt.tight_layout()

        if output_path:
            fig.savefig(output_path, format=format, bbox_inches="tight")
            print(f"Сохранено: {output_path}")

        return fig

    def plot_digital_signal(
        self,
        bits: list[int],
        bit_time: float = 1.0,
        transition_time: float = 0.0,
        samples_per_bit: int = 100,
        title: str = "Цифровой сигнал",
        output_path: Optional[str] = None,
        format: Literal["png", "pdf", "svg"] = "png",
        amplitude: float = 1.0,
    ) -> Figure:
        """
        Построение цифрового сигнала по битам.

        Args:
            bits: Список битов (0 или 1)
            bit_time: Время на один бит (если 5 битов и bit_time=1.0, график от 0 до 5)
            transition_time: Время перехода между состояниями (0 = мгновенный переход)
            samples_per_bit: Количество точек на каждый бит
            title: Заголовок графика
            output_path: Путь для сохранения
            format: Формат вывода
            amplitude: Амплитуда сигнала (1.0 для [0,1], может быть 2.0 для [-1,1])

        Returns:
            Объект Figure
        """
        total_time = len(bits) * bit_time
        num_samples = len(bits) * samples_per_bit
        t = np.linspace(0, total_time, num_samples)

        def signal_func(t_arr: np.ndarray) -> np.ndarray:
            result = np.zeros_like(t_arr)

            for i, bit in enumerate(bits):
                bit_start = i * bit_time
                bit_end = (i + 1) * bit_time

                prev_bit = bits[i - 1] if i > 0 else bit

                if transition_time > 0:
                    in_transition_in = (t_arr >= bit_start - transition_time / 2) & (
                        t_arr < bit_start + transition_time / 2
                    )
                    transition_progress = (
                        t_arr[in_transition_in] - (bit_start - transition_time / 2)
                    ) / transition_time
                    result[in_transition_in] = (
                        prev_bit + (bit - prev_bit) * transition_progress
                    ) * amplitude

                    in_steady = (t_arr >= bit_start + transition_time / 2) & (
                        t_arr < bit_end
                    )
                    result[in_steady] = bit * amplitude
                else:
                    mask = (t_arr >= bit_start) & (t_arr < bit_end)
                    result[mask] = bit * amplitude

            return result

        y_range = (0, amplitude) if amplitude > 0 else (-amplitude, amplitude)

        return self.plot_signal(
            signal_func=signal_func,
            num_samples=num_samples,
            title=title,
            y_range=y_range,
            output_path=output_path,
            format=format,
            time_range=(0, total_time),
        )

    def plot_bipolar_signal(
        self,
        levels: list[int],
        bit_time: float = 1.0,
        transition_time: float = 0.0,
        samples_per_bit: int = 100,
        title: str = "Биполярный сигнал",
        output_path: Optional[str] = None,
        format: Literal["png", "pdf", "svg"] = "png",
    ) -> Figure:
        """
        Построение биполярного сигнала (значения: -1, 0, 1).

        Args:
            levels: Список уровней сигнала (-1, 0 или 1)
            bit_time: Время на один уровень
            transition_time: Время перехода между состояниями (0 = мгновенный)
            samples_per_bit: Количество точек на каждый уровень
            title: Заголовок графика
            output_path: Путь для сохранения
            format: Формат вывода

        Returns:
            Объект Figure
        """
        total_time = len(levels) * bit_time
        num_samples = len(levels) * samples_per_bit
        t = np.linspace(0, total_time, num_samples)

        def signal_func(t_arr: np.ndarray) -> np.ndarray:
            result = np.zeros_like(t_arr)

            for i, level in enumerate(levels):
                level_start = i * bit_time
                level_end = (i + 1) * bit_time

                prev_level = levels[i - 1] if i > 0 else level

                if transition_time > 0:
                    in_transition = (t_arr >= level_start - transition_time / 2) & (
                        t_arr < level_start + transition_time / 2
                    )
                    transition_progress = (
                        t_arr[in_transition] - (level_start - transition_time / 2)
                    ) / transition_time
                    result[in_transition] = (
                        prev_level + (level - prev_level) * transition_progress
                    )

                    in_steady = (t_arr >= level_start + transition_time / 2) & (
                        t_arr < level_end
                    )
                    result[in_steady] = level
                else:
                    mask = (t_arr >= level_start) & (t_arr < level_end)
                    result[mask] = level

            return result

        return self.plot_signal(
            signal_func=signal_func,
            num_samples=num_samples,
            title=title,
            y_range=(-1.1, 1.1),
            output_path=output_path,
            format=format,
            time_range=(0, total_time),
        )


def plot_signal(
    signal_func: Callable[[np.ndarray], np.ndarray],
    num_samples: int = 1000,
    title: str = "",
    output_path: Optional[str] = None,
    format: Literal["png", "pdf", "svg"] = "png",
    figsize: tuple = (16, 3),
    dpi: int = 150,
    **plot_kwargs,
) -> Figure:
    """
    Удобная функция для быстрого построения графика сигнала.

    Args:
        signal_func: Функция сигнала
        num_samples: Количество точек
        title: Заголовок
        output_path: Путь для сохранения
        format: Формат
        figsize: Размер фигуры
        dpi: Разрешение
        **plot_kwargs: Дополнительные аргументы для SignalPlotter.plot_signal

    Returns:
        Объект Figure
    """
    plotter = SignalPlotter(figsize=figsize, dpi=dpi)
    return plotter.plot_signal(
        signal_func=signal_func,
        num_samples=num_samples,
        title=title,
        output_path=output_path,
        format=format,
        **plot_kwargs,
    )
