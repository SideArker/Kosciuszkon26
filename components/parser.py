import pandas as pd
import numpy as np

def parse_and_prepare(file_path: str):
    print(f"-> Wczytywanie i parsowanie pliku: {file_path}")
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {file_path}")
        return None

    # Zabezpieczenie przed błędami typów (np. litery w liczbach float)
    numeric_cols = [
        'time_s', 'label', 'prn', 'doppler_hz', 'power', 'power_variance', 
        'mean_magnitude', 'std_magnitude', 'mean_phase', 
        'skew_I', 'skew_Q', 'kurtosis_I', 'kurtosis_Q'
    ]
    
    # Wymuszamy konwersję. Błędy (np. tekst) zamienią się na NaN
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Usuwamy wiersze z zepsutymi wartościami bazowymi
    df = df.dropna(subset=['time_s', 'label', 'prn'])

    # Filtracja satelitów
    valid_prns = [-1, 1, 2]
    df = df[df['prn'].isin(valid_prns)].copy()
    
    if df.empty:
        print("Ostrzeżenie: DataFrame jest pusty po czyszczeniu i filtracji PRN!")
        return df

    # Logarytmowanie (Konwersja na dB)
    power_cols = ['power', 'power_variance', 'mean_magnitude', 'std_magnitude']
    for col in power_cols:
        if col in df.columns:
            df[f'{col}_dB'] = 10 * np.log10(df[col].replace(0, np.nan)) 
            df[f'{col}_dB'] = df[f'{col}_dB'].fillna(df[f'{col}_dB'].min())

    # Sortowanie chronologiczne
    df = df.sort_values(by=['time_s']).reset_index(drop=True)

    # Feature Engineering
    df['doppler_delta'] = df.groupby('prn')['doppler_hz'].diff().fillna(0)

    # Usunięcie resztek NaN powstałych np. przez funkcję diff()
    df = df.dropna()
    
    return df