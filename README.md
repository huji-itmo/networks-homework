# Signal Plotter

Библиотека для отображения электрических сигналов в горизонтальном формате (для курса "Компьютерные сети").

## Установка

```bash
uv venv
uv sync
```

## Использование

### Python-скрипт

```python
from signal_plotter import SignalPlotter, plot_signal
import numpy as np

plotter = SignalPlotter()

# Синусоида
fig = plotter.plot_signal(
    signal_func=lambda t: np.sin(2 * np.pi * t),
    title="Синусоида",
    output_path="output/signal.png"
)

# Цифровой сигнал (0 и 1)
fig = plotter.plot_digital_signal(
    bits=[1, 0, 1, 1, 0],
    bit_time=1.0,
    transition_time=0.2,
    output_path="output/digital.png"
)

# Биполярный сигнал (-1, 0, 1)
fig = plotter.plot_bipolar_signal(
    levels=[1, -1, 1, 0],
    bit_time=1.0,
    transition_time=0.2,
    output_path="output/bipolar.png"
)
```

### Запуск примеров

```bash
source .venv/bin/activate
python -m signal_plotter.example
```

## Команды UV

```bash
uv venv           # создать виртуальное окружение
uv sync           # установить зависимости
uv run python ... # запустить Python без активации окружения
```
