# Signal Plotter

Библиотека для отображения электрических сигналов в горизонтальном формате (для курса "Компьютерные сети").

## Установка

```bash
uv venv
uv sync
```

## Использование

### Построение графиков сигналов

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

### Физическое кодирование (NRZ, Manchester, RZ, AMI)

```python
from signal_plotter.encodings import encode_data, bytes_to_bits
from signal_plotter.metrics import (
    calculate_nrz_metrics,
    calculate_manchester_metrics,
    calculate_rz_metrics,
    calculate_ami_metrics,
    generate_report
)

# Кодирование данных
data = bytes([0xB2, 0x69, 0x9C])
signal = encode_data(data, "nrz")

# Расчет метрик
bits = bytes_to_bits(data)
m = calculate_nrz_metrics(bits, bit_rate=100)
print(f"Полоса: {m.bandwidth} МГц")

# Генерация отчета
metrics_list = [
    calculate_nrz_metrics(bits, 100),
    calculate_manchester_metrics(bits, 100),
    calculate_rz_metrics(bits, 100),
    calculate_ami_metrics(bits, 100),
]
report = generate_report(metrics_list, bit_rate=100)
print(report)
```

### Запуск примеров

```bash
python -m signal_plotter.example      # примеры графиков
python -m signal_plotter.encoding_example  # кодирование сигналов
python -m signal_plotter.metrics_example   # расчет метрик
```

## Тесты

```bash
pytest tests/ -v
```

## Команды UV

```bash
uv venv           # создать виртуальное окружение
uv sync           # установить зависимости
uv run python ... # запустить Python без активации окружения
```
