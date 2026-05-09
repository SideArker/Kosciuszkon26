# import pandas as pd

# def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
#     df_feat = df.copy()
#     if 'C_N0' in df_feat.columns:
#         df_feat['c_n0_diff'] = df_feat['C_N0'].diff().fillna(0)
#     if 'Carrier_Phase' in df_feat.columns and 'Code_Phase' in df_feat.columns:
#         df_feat['phase_divergence'] = abs(df_feat['Carrier_Phase'] - df_feat['Code_Phase'])
#     return df_feat


# def parse_and_prepare(filepath: str) -> tuple[pd.DataFrame, pd.Series]:
#     try:
#         df = pd.read_csv(filepath)
#     except FileNotFoundError:
#         raise FileNotFoundError(f"Nie znaleziono pliku: {filepath}")

#     for col in df.columns:
#         df[col] = pd.to_numeric(df[col], errors='coerce')
#     df = df.dropna()
#     df = _engineer_features(df)
#     if 'Label' not in df.columns:
#         raise ValueError(f"Plik {filepath} nie zawiera kolumny 'Label'!")
#     y = df['Label']
#     cols_to_drop = ['TOW','TOW_Frac','PRN','C_N0','Carrier_Phase','Code_Phase','Tracking_State','Doppler','Label', 'phase_divergence']
#     if 'S_id' in df.columns:
#         cols_to_drop.append('S_id')
#     X = df.drop(columns=cols_to_drop, errors='ignore')
    
#     return X, y











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









