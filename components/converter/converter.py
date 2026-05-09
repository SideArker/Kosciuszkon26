from pathlib import Path
import numpy as np
import pandas as pd
import csv

CONVERTER_DIR = Path(__file__).resolve().parent
DATA_DIR = CONVERTER_DIR / "data"

DS8_BIN = DATA_DIR / "ds8.bin"
OUTPUT_CSV = DATA_DIR / "ds8_features.csv"

FS = 25_000_000
WINDOW_SECONDS = 0.001
CHUNK_WINDOWS = 100
SPOOF_START_SECOND = 110.0

def read_iq_block(path: str | Path, start_sample: int, n_samples: int, endian: str = "<", normalize: bool = True) -> np.ndarray:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku: {path}")

    dtype = np.dtype(endian + "i2")
    offset_bytes = int(start_sample) * 2 * dtype.itemsize
    count = int(n_samples) * 2

    raw = np.fromfile(path, dtype=dtype, count=count, offset=offset_bytes)

    if raw.size == 0:
        return np.array([], dtype=np.complex64)

    if raw.size % 2:
        raw = raw[:-1]

    iq = raw.reshape(-1, 2)
    x = iq[:, 0].astype(np.float32) + 1j * iq[:, 1].astype(np.float32)

    if normalize:
        x /= 32768.0

    return x.astype(np.complex64)

def label_from_time(time_s: float) -> int:
    return 1 if time_s >= SPOOF_START_SECOND else 0

def extract_window_features(x: np.ndarray, window_start_sample: int, fs: float = FS) -> dict:
    time_s = window_start_sample / fs
    magnitude = np.abs(x)
    phase = np.angle(x)

    return {
        "time_s": time_s,
        "label": label_from_time(time_s),
        "mean_I": float(np.mean(np.real(x))),
        "mean_Q": float(np.mean(np.imag(x))),
        "power": float(np.mean(np.real(x) ** 2 + np.imag(x) ** 2)),
        "mean_magnitude": float(np.mean(magnitude)),
        "std_magnitude": float(np.std(magnitude)),
        "mean_phase": float(np.mean(phase)),
        "min_I": float(np.min(np.real(x))),
        "max_I": float(np.max(np.real(x))),
        "min_Q": float(np.min(np.imag(x))),
        "max_Q": float(np.max(np.imag(x))),
    }

def convert_ds8_to_feature_csv(input_bin: str | Path = DS8_BIN, output_csv: str | Path = OUTPUT_CSV,
                               fs: int = FS, window_seconds: float = WINDOW_SECONDS,
                               chunk_windows: int = CHUNK_WINDOWS, max_seconds: float | None = None) -> pd.DataFrame:
    input_bin = Path(input_bin)
    output_csv = Path(output_csv)

    if not input_bin.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku: {input_bin}")

    output_csv.parent.mkdir(parents=True, exist_ok=True)

    total_samples = input_bin.stat().st_size // 4
    total_seconds = total_samples / fs

    if max_seconds is not None:
        total_seconds = min(total_seconds, max_seconds)
        total_samples = int(total_seconds * fs)

    window_samples = int(window_seconds * fs)
    chunk_samples = window_samples * chunk_windows

    print(f"Plik: {input_bin}")
    print(f"Rozmiar próbek I/Q: {total_samples:,}")
    print(f"Czas nagrania: {total_seconds:.2f} s")
    print(f"Okno: {window_seconds} s = {window_samples:,} próbek")
    print(f"Wyjście CSV: {output_csv}")

    all_rows_preview = []
    start_sample = 0

    with open(output_csv, 'w', newline='') as f:
        fieldnames = ["time_s", "label", "mean_I", "mean_Q", "power", 
                      "mean_magnitude", "std_magnitude", "mean_phase", 
                      "min_I", "max_I", "min_Q", "max_Q"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        while start_sample < total_samples:
            remaining = total_samples - start_sample
            n_samples = min(chunk_samples, remaining)

            x_chunk = read_iq_block(path=input_bin, start_sample=start_sample, n_samples=n_samples)

            if len(x_chunk) == 0:
                break

            rows = []
            full_windows_in_chunk = len(x_chunk) // window_samples

            for w in range(full_windows_in_chunk):
                a = w * window_samples
                b = a + window_samples
                window_start_sample = start_sample + a
                x_window = x_chunk[a:b]

                row = extract_window_features(x=x_window, window_start_sample=window_start_sample, fs=fs)
                rows.append(row)
            
            if rows:
                writer.writerows(rows)
                
                if len(all_rows_preview) < 5:
                    all_rows_preview.extend(rows[:5])

            start_sample += n_samples

            current_time = start_sample / fs
            if (start_sample // chunk_samples) % 5 == 0:
                progress = 100.0 * start_sample / total_samples
                print(f"Postęp: {progress:.2f}% | t={current_time:.2f}s")

    print(f"Zapisano pomyślnie cały plik: {output_csv}")
    return pd.DataFrame(all_rows_preview)

def run_default_converter() -> pd.DataFrame:
    return convert_ds8_to_feature_csv(
        input_bin=DS8_BIN,
        output_csv=OUTPUT_CSV,
        max_seconds=None,
    )

if __name__ == "__main__":
    run_default_converter()