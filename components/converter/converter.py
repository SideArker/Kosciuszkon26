from pathlib import Path
import csv
import time
import numpy as np
import pandas as pd

CONVERTER_DIR = Path(__file__).resolve().parent
DATA_DIR = CONVERTER_DIR / "data"

TUNI_FS = 50_000_000
ENDIAN = "<"
WINDOW_SECONDS = 0.0002
CHUNK_WINDOWS = 100

SCENARIOS = {
    "clear": {
        "input_bin": DATA_DIR / "Clearsky signal C-7.bin",
        "output_csv": DATA_DIR / "tuni2025_clear_C7_features.csv",
        "label": 0,
        "prn": "-1",
    },
    "spoof": {
        "input_bin": DATA_DIR / "SS-18_GPS_2Spoofer_Static_NoMP_TruePosition.bin",
        "output_csv": DATA_DIR / "tuni2025_spoof_SS18_features.csv",
        "label": 1,
        "prn": "1;2",
    },
}

def read_iq_block(path: str | Path, start_sample: int, n_samples: int, endian: str = ENDIAN, header_bytes: int = 0) -> np.ndarray:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    dtype = np.dtype(endian + "f4")
    bytes_per_iq_sample = 8
    offset_bytes = header_bytes + int(start_sample) * bytes_per_iq_sample
    count = int(n_samples) * 2
    raw = np.fromfile(path, dtype=dtype, count=count, offset=offset_bytes)
    if raw.size == 0:
        return np.array([], dtype=np.complex64)
    if raw.size % 2:
        raw = raw[:-1]
    iq = raw.reshape(-1, 2)
    i = iq[:, 0].astype(np.float32)
    q = iq[:, 1].astype(np.float32)
    x = i + 1j * q
    return x.astype(np.complex64)

def safe_skewness(values: np.ndarray) -> float:
    values = values.astype(np.float64)
    mean = np.mean(values)
    std = np.std(values)
    if std == 0 or not np.isfinite(std):
        return 0.0
    return float(np.mean(((values - mean) / std) ** 3))

def safe_kurtosis(values: np.ndarray) -> float:
    values = values.astype(np.float64)
    mean = np.mean(values)
    std = np.std(values)
    if std == 0 or not np.isfinite(std):
        return 0.0
    return float(np.mean(((values - mean) / std) ** 4) - 3.0)

def estimate_doppler_hz(x: np.ndarray, fs: int) -> float:
    if len(x) < 2:
        return 0.0
    phase_diff = np.angle(x[1:] * np.conj(x[:-1]))
    phase_diff = phase_diff[np.isfinite(phase_diff)]
    if phase_diff.size == 0:
        return 0.0
    return float(np.mean(phase_diff) * fs / (2.0 * np.pi))

def extract_window_features(x: np.ndarray, window_start_sample: int, fs: int, label: int, prn: str) -> dict | None:
    time_s = window_start_sample / fs
    i = np.real(x).astype(np.float64)
    q = np.imag(x).astype(np.float64)
    finite_mask = np.isfinite(i) & np.isfinite(q)
    if not np.any(finite_mask):
        return None
    i = i[finite_mask]
    q = q[finite_mask]
    x_valid = i + 1j * q
    power_values = i ** 2 + q ** 2
    magnitude = np.sqrt(power_values)
    phase = np.arctan2(q, i)
    return {
        "time_s": float(time_s),
        "label": int(label),
        "prn": prn,
        "doppler_hz": estimate_doppler_hz(x_valid, fs),
        "mean_I": float(np.mean(i)),
        "mean_Q": float(np.mean(q)),
        "power": float(np.mean(power_values)),
        "power_variance": float(np.var(power_values)),
        "mean_magnitude": float(np.mean(magnitude)),
        "std_magnitude": float(np.std(magnitude)),
        "mean_phase": float(np.mean(phase)),
        "skew_I": safe_skewness(i),
        "skew_Q": safe_skewness(q),
        "kurtosis_I": safe_kurtosis(i),
        "kurtosis_Q": safe_kurtosis(q),
        "min_I": float(np.min(i)),
        "max_I": float(np.max(i)),
        "min_Q": float(np.min(q)),
        "max_Q": float(np.max(q)),
    }

def convert_tuni2025_to_feature_csv(
    input_bin: str | Path,
    output_csv: str | Path,
    label: int,
    prn: str,
    fs: int = TUNI_FS,
    window_seconds: float = WINDOW_SECONDS,
    chunk_windows: int = CHUNK_WINDOWS,
    max_seconds: float | None = None,
    endian: str = ENDIAN,
    header_bytes: int = 0,
) -> pd.DataFrame:
    input_bin = Path(input_bin)
    output_csv = Path(output_csv)
    if not input_bin.exists():
        raise FileNotFoundError(f"File not found: {input_bin}")
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    bytes_per_iq_sample = 8
    file_size = input_bin.stat().st_size
    usable_bytes = file_size - header_bytes
    total_samples_in_file = usable_bytes // bytes_per_iq_sample
    total_seconds_in_file = total_samples_in_file / fs
    if max_seconds is not None:
        total_seconds = min(total_seconds_in_file, max_seconds)
        total_samples = int(total_seconds * fs)
    else:
        total_seconds = total_seconds_in_file
        total_samples = total_samples_in_file
    window_samples = int(window_seconds * fs)
    chunk_samples = window_samples * chunk_windows
    expected_rows = int(total_seconds / window_seconds)
    print(f"File: {input_bin}")
    print(f"Label: {label}")
    print(f"PRN: {prn}")
    print("Format: float32 interleaved I/Q")
    print(f"Sampling rate: {fs:,} Hz")
    print(f"Full recording duration: {total_seconds_in_file:.2f} s")
    print(f"Converted duration: {total_seconds:.2f} s")
    print(f"Window: {window_seconds} s = {window_samples:,} samples")
    print(f"Expected rows: ~{expected_rows:,}")
    print(f"Chunk: {chunk_windows} windows = {chunk_windows * window_seconds:.4f} s signal")
    print(f"Output CSV: {output_csv}")
    fieldnames = [
        "time_s",
        "label",
        "prn",
        "doppler_hz",
        "mean_I",
        "mean_Q",
        "power",
        "power_variance",
        "mean_magnitude",
        "std_magnitude",
        "mean_phase",
        "skew_I",
        "skew_Q",
        "kurtosis_I",
        "kurtosis_Q",
        "min_I",
        "max_I",
        "min_Q",
        "max_Q",
    ]
    all_rows_preview = []
    skipped_windows = 0
    written_rows = 0
    start_sample = 0
    program_start_time = time.time()
    last_log_time = program_start_time
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        while start_sample < total_samples:
            remaining = total_samples - start_sample
            n_samples = min(chunk_samples, remaining)
            x_chunk = read_iq_block(path=input_bin, start_sample=start_sample, n_samples=n_samples, endian=endian, header_bytes=header_bytes)
            if len(x_chunk) == 0:
                break
            rows = []
            full_windows_in_chunk = len(x_chunk) // window_samples
            for w in range(full_windows_in_chunk):
                a = w * window_samples
                b = a + window_samples
                window_start_sample = start_sample + a
                x_window = x_chunk[a:b]
                row = extract_window_features(x=x_window, window_start_sample=window_start_sample, fs=fs, label=label, prn=prn)
                if row is None:
                    skipped_windows += 1
                    continue
                rows.append(row)
            if rows:
                writer.writerows(rows)
                written_rows += len(rows)
                if len(all_rows_preview) < 5:
                    all_rows_preview.extend(rows[: 5 - len(all_rows_preview)])
            start_sample += n_samples
            now = time.time()
            if now - last_log_time >= 1.0:
                progress = 100.0 * start_sample / total_samples
                signal_time = start_sample / fs
                elapsed = now - program_start_time
                print(f"Progress: {progress:.2f}% | signal_t={signal_time:.2f}s / {total_seconds:.2f}s | elapsed={elapsed:.2f}s | rows={written_rows:,}")
                last_log_time = now
    elapsed_total = time.time() - program_start_time
    print(f"File saved: {output_csv}")
    print(f"Written rows: {written_rows:,}")
    print(f"Skipped empty/invalid windows: {skipped_windows}")
    print(f"Elapsed real time: {elapsed_total:.2f}s")
    return pd.DataFrame(all_rows_preview)

def convert_clear_sky(max_seconds: float | None = 30.0) -> pd.DataFrame:
    cfg = SCENARIOS["clear"]
    return convert_tuni2025_to_feature_csv(input_bin=cfg["input_bin"], output_csv=cfg["output_csv"], label=cfg["label"], prn=cfg["prn"], max_seconds=max_seconds)

def convert_spoof(max_seconds: float | None = 30.0) -> pd.DataFrame:
    cfg = SCENARIOS["spoof"]
    return convert_tuni2025_to_feature_csv(input_bin=cfg["input_bin"], output_csv=cfg["output_csv"], label=cfg["label"], prn=cfg["prn"], max_seconds=max_seconds)

def convert_both(max_seconds: float | None = 30.0) -> tuple[pd.DataFrame, pd.DataFrame]:
    clear_preview = convert_clear_sky(max_seconds=max_seconds)
    spoof_preview = convert_spoof(max_seconds=max_seconds)
    return clear_preview, spoof_preview

def run_default_converter() -> pd.DataFrame:
    return convert_clear_sky(max_seconds=10.0)

if __name__ == "__main__":
    run_default_converter()