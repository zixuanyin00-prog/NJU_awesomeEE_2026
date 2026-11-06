"""Plot a USART1 capture and report DC or AC measurements."""

import argparse
import csv
from pathlib import Path
from statistics import fmean

SAMPLE_RATE_HZ = 200
INDEX_MASK = (1 << 32) - 1


def load_capture(path):
    voltages = []
    previous = None
    with path.open(encoding="utf-8-sig", newline="") as capture:
        for line, row in enumerate(csv.reader(capture), 1):
            if not row:
                continue
            try:
                index, raw, millivolts = map(int, row)
            except ValueError as error:
                raise ValueError(f"Line {line}: expected index,raw,mV.") from error
            if not 0 <= index <= INDEX_MASK or not 0 <= raw <= 4095:
                raise ValueError(f"Line {line}: sample index or ADC code out of range.")
            if millivolts != (raw * 3300 + 2047) // 4095:
                raise ValueError(f"Line {line}: millivolts do not match the ADC code.")
            if previous is not None and index != ((previous + 1) & INDEX_MASK):
                raise ValueError(f"Line {line}: sample index jumps from {previous} to {index}.")
            voltages.append(millivolts / 1000)
            previous = index
    if len(voltages) < 2:
        raise ValueError("At least two consecutive samples are required.")
    return voltages


def rising_crossings(voltages, low, high):
    midpoint = (low + high) / 2
    arm_level = midpoint - 0.1 * (high - low)
    crossings = []
    armed = False
    for index, (before, after) in enumerate(zip(voltages, voltages[1:])):
        if before < arm_level:
            armed = True
        if armed and before < midpoint <= after:
            crossing = index + (midpoint - before) / (after - before)
            crossings.append(crossing / SAMPLE_RATE_HZ)
            armed = False
    return crossings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path, help="Plain-text USART1 capture (index,raw,mV).")
    parser.add_argument("--mode", choices=("dc", "ac"), required=True)
    args = parser.parse_args()

    try:
        voltages = load_capture(args.capture)
    except (OSError, ValueError) as error:
        parser.exit(2, f"{error}\n")

    times = [index / SAMPLE_RATE_HZ for index in range(len(voltages))]
    low, high = min(voltages), max(voltages)
    report = [
        f"Source: {args.capture.name}",
        f"Mode: {args.mode.upper()}",
        f"Samples: {len(voltages)}; duration: {times[-1]:.3f} s at nominal {SAMPLE_RATE_HZ} Hz",
        f"Min: {low:.3f} V; max: {high:.3f} V; peak-to-peak: {high - low:.3f} V",
        f"Mean: {fmean(voltages):.3f} V",
    ]

    crossings = []
    if args.mode == "ac":
        crossings = rising_crossings(voltages, low, high)
        cycles = max(0, len(crossings) - 1)
        report.append(f"Complete rising-to-rising cycles: {cycles}")
        if cycles < 2:
            report.append("AC acceptance requires at least two complete cycles.")
        else:
            period = (crossings[-1] - crossings[0]) / cycles
            report.append(f"Mean period: {period:.4f} s; frequency: {1 / period:.3f} Hz")
            report.append(f"Midpoint (offset estimate for symmetric signals): {(low + high) / 2:.3f} V")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure, axis = plt.subplots(figsize=(9, 4.5), layout="constrained")
    axis.plot(times, voltages, label="ADC1 voltage")
    if len(crossings) >= 3:
        axis.axvspan(crossings[0], crossings[2], alpha=0.16, color="tab:green", label="Two complete cycles")
    axis.set(title=f"STM32F429 ADC1 ({args.mode.upper()})", xlabel="Time (s)", ylabel="Voltage (V)")
    axis.grid(alpha=0.3)
    axis.legend()
    figure.savefig(args.capture.with_suffix(".png"), dpi=150)
    plt.close(figure)

    summary = "\n".join(report) + "\n"
    args.capture.with_suffix(".analysis.txt").write_text(summary, encoding="utf-8")
    print(summary, end="")
    return int(args.mode == "ac" and len(crossings) < 3)


if __name__ == "__main__":
    raise SystemExit(main())
