import pandas as pd

def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    # Sortowanie chronologiczne wewnątrz każdego satelity
    df = df.sort_values(by=['PRN', 'TOW', 'TOW_Frac'])
    
    # Grupowanie po satelicie (PRN), aby różnice miały sens fizyczny
    grouped = df.groupby('PRN')
    
    df_feat = df.copy()
    
    # Różnica mocy sygnału (C/N0) dla konkretnego satelity
    df_feat['c_n0_diff'] = grouped['C_N0'].diff()
    
    # Różnica częstotliwości Dopplera
    df_feat['doppler_diff'] = grouped['Doppler'].diff()
    
    # Opcjonalnie: Wariancja C/N0 w oknie kroczącym (wykrywanie nienaturalnych skoków)
    df_feat['c_n0_rolling_std'] = grouped['C_N0'].shift(1).rolling(window=5).std()

    # Usuwamy pierwsze rekordy dla każdego PRN (bo mają NaN w polach .diff())
    df_feat = df_feat.dropna()
    
    return df_feat

def parse_and_prepare(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    
    # Konwersja na typy numeryczne
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()

    # Inżynieria cech
    df = _engineer_features(df)
    
    return df









