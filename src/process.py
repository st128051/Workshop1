import math
import matplotlib.pyplot as plt
import csv
import os

#input

data_rough = [
    0.350, 0.349, 0.350, 0.352, 0.351,
    0.352, 0.350, 0.351, 0.351, 0.349
]
omega_rough = 0.0026  # погрешность прибора на грубой шкале, В

data_precise = [
    0.3529, 0.3526, 0.3525, 0.3527, 0.3531,
    0.3533, 0.3502, 0.3501, 0.3500, 0.3500,
    0.3504, 0.3506, 0.3501, 0.3499, 0.3498,
    0.3501, 0.3500, 0.3501, 0.3498, 0.3503,
    0.3498, 0.3499, 0.3502, 0.3506, 0.3503,
    0.3505, 0.3500, 0.3499, 0.3500, 0.3494,
    0.3499, 0.3496, 0.3498, 0.3500, 0.3498,
    0.3495, 0.3503, 0.3500, 0.3502, 0.3504,
    0.3499, 0.3501, 0.3503, 0.3505, 0.3506,
    0.3505, 0.3512, 0.3509, 0.3513, 0.3506
]
omega_precise = 0.000337  # погрешность прибора на точной шкале, В
unit = "В"                # единица измерения
quantity_name = "U"       # обозначение величины

#Статистико

def mean(data):
    return sum(data) / len(data)

def variance(data, unbiased=True):
    m = mean(data)
    n = len(data)
    sq_diff = 0
    for x in data:
        sq_diff += (x - m) ** 2
    if unbiased and n > 1:
        return sq_diff / (n - 1)
    else:
        return sq_diff / n

def std_dev(data, unbiased=True):
    return math.sqrt(variance(data, unbiased))

def std_error(data):
    return std_dev(data, unbiased=True) / math.sqrt(len(data))

def student_t_coeff(n, p=0.95):
    table = {
        2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571, 7: 2.447,
        8: 2.365, 9: 2.306, 10: 2.262, 11: 2.228, 12: 2.201, 13: 2.179,
        14: 2.160, 15: 2.145, 16: 2.131, 17: 2.120, 18: 2.110, 19: 2.101,
        20: 2.093, 21: 2.086, 22: 2.080, 23: 2.074, 24: 2.069, 25: 2.064,
        26: 2.060, 27: 2.056, 28: 2.052, 29: 2.048, 30: 2.045, 31: 2.042,
        32: 2.040, 33: 2.037, 34: 2.035, 35: 2.032, 36: 2.030, 37: 2.028,
        38: 2.026, 39: 2.024, 40: 2.022, 41: 2.020, 42: 2.018, 43: 2.017,
        44: 2.015, 45: 2.014, 46: 2.013, 47: 2.012, 48: 2.011, 49: 2.010,
        50: 2.009, 51: 2.008, 52: 2.007, 53: 2.006, 54: 2.005, 55: 2.004,
        56: 2.003, 57: 2.002, 58: 2.002, 59: 2.001, 60: 2.000
    }
    if n in table:
        return table[n]
    elif n > 60:
        return 1.96
    else:
        return 1.96

def confidence_interval(data, p=0.95):
    n = len(data)
    if n < 2:
        return 0.0
    t = student_t_coeff(n, p)
    se = std_error(data)
    return t * se

def histogram_data(data, bins=10):
    """Возвращает границы интервалов и частоты для гистограммы"""
    xmin = min(data)
    xmax = max(data)
    width = (xmax - xmin) / bins
    boundaries = [xmin + i * width for i in range(bins+1)]
    counts = [0] * bins
    for x in data:
        for i in range(bins):
            if boundaries[i] <= x < boundaries[i+1]:
                counts[i] += 1
                break
        # Если x равно правой границе, относим к последнему интервалу
        if x == boundaries[-1]:
            counts[-1] += 1
    return boundaries, counts

#точные измер

n = len(data_precise)
x_mean = mean(data_precise)
var_unbiased = variance(data_precise, unbiased=True)
std = std_dev(data_precise, unbiased=True)
std_err = std_error(data_precise)
ci = confidence_interval(data_precise)

print("===== РЕЗУЛЬТАТЫ ОБРАБОТКИ ТОЧНЫХ ИЗМЕРЕНИЙ =====")
print(f"Число наблюдений n = {n}")
print(f"Среднее арифметическое x̄ = {x_mean:.6f} {unit}")
print(f"Несмещённая дисперсия σ² = {var_unbiased:.8f} {unit}²")
print(f"Стандартное отклонение σ = {std:.6f} {unit}")
print(f"Стандартная ошибка среднего σ_x̄ = {std_err:.6f} {unit}")
print(f"Полуширина доверительного интервала Δx (P=0.95) = {ci:.6f} {unit}")
print(f"Погрешность прибора ω = {omega_precise} {unit}")

# Сравнение с погрешностью прибора
if ci > omega_precise:
    final_error = ci
    print("Доверительный интервал больше приборной погрешности -> итоговая погрешность = Δx")
elif ci < omega_precise:
    final_error = omega_precise
    print("Приборная погрешность больше -> итоговая погрешность = ω")
else:
    final_error = math.sqrt(ci**2 + omega_precise**2)
    print("Погрешности одного порядка -> суммируем квадратично")

print(f"\nОкончательный результат: {quantity_name} = ({x_mean:.6f} ± {final_error:.6f}) {unit}, P=0.95")

##uhfabrt

os.makedirs("output", exist_ok=True)
os.makedirs("figures", exist_ok=True)  # для сохранения картинок отчёта

# 4.1 График дрейфа
plt.figure(figsize=(10, 5))
plt.plot(range(1, n+1), data_precise, 'bo-', markersize=3, linewidth=0.5)
plt.xlabel('Номер наблюдения')
plt.ylabel(f'{quantity_name}, {unit}')
plt.title('Зависимость результатов наблюдений от времени (порядка)')
plt.grid(True)
plt.savefig('figures/drift.png', dpi=300)
plt.show()

# 4.2 Гистограмма
bins = 10  
boundaries, counts = histogram_data(data_precise, bins=bins)
centers = [(boundaries[i] + boundaries[i+1])/2 for i in range(bins)]

plt.figure(figsize=(8, 5))
plt.bar(centers, counts, width=(boundaries[1]-boundaries[0]), edgecolor='black', alpha=0.7)
plt.xlabel(f'{quantity_name}, {unit}')
plt.ylabel('Частота')
plt.title('Гистограмма распределения результатов наблюдений')
plt.grid(axis='y')
plt.savefig('figures/histogram.png', dpi=300)
plt.show()

with open('output/histogram_data.txt', 'w') as f:
    f.write("# center  count\n")
    for c, cnt in zip(centers, counts):
        f.write(f"{c:.6f} {cnt}\n")

# 4.3График плотности
total = n
density = [c/total for c in counts]
plt.figure(figsize=(8, 5))
plt.plot(centers, density, 'ro-', markersize=4)
plt.xlabel(f'{quantity_name}, {unit}')
plt.ylabel('δn = Δn/n')
plt.title('График доли попаданий в интервалы')
plt.grid(True)
plt.savefig('figures/density.png', dpi=300)
plt.show()

# tabliza

with open('output/table_precise.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['№', f'{quantity_name}_i', 'd_i', 'd_i^2'])
    for i, x in enumerate(data_precise, start=1):
        d = x - x_mean
        writer.writerow([i, f"{x:.6f}", f"{d:.6f}", f"{d*d:.8f}"])

with open('output/table_precise.tex', 'w', encoding='utf-8') as f:
    f.write("\\begin{tabular}{|c|c|c|c|}\n")
    f.write("\\hline\n")
    f.write("№ & $U_i$, В & $d_i = U_i - \\overline{U}$ & $d_i^2$ \\\\\n")
    f.write("\\hline\n")
    for i, x in enumerate(data_precise, start=1):
        d = x - x_mean
        f.write(f"{i} & {x:.6f} & {d:.6f} & {d*d:.8f} \\\\\n")
    f.write("\\hline\n")
    f.write("\\end{tabular}\n")

print("\nТаблицы и графики сохранены в папках output/ и figures/")

# grubie izm

# таблица 2 для отчёта
with open('output/table_rough.tex', 'w', encoding='utf-8') as f:
    f.write("\\begin{tabular}{|c|c|c|c|}\n")
    f.write("\\hline\n")
    f.write("№ п/п & Диапазон шкалы, В & $U_i$, В & $\\Delta U_{\\text{приб}}$, В \\\\\n")
    f.write("\\hline\n")
    for i, x in enumerate(data_rough, start=1):
        f.write(f"{i} & 0-10 & {x:.3f} & {omega_rough} \\\\\n")
    f.write("\\hline\n")
    f.write("\\end{tabular}\n")

print("Таблица грубых измерений сохранена в output/table_rough.tex")