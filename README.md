from ds_python_interpreter import ds_python_interpreter

# Tworzenie pliku README.md
ds_python_interpreter(code="""
readme_content = \"\"\"
# GPS Spoofing Detection Model (TEXBAT Based)

Projekt badawczy poświęcony wykrywaniu ataków typu **GPS Spoofing** przy użyciu uczenia maszynowego. Model analizuje parametry fizyczne sygnału GNSS, aby odróżnić sygnał autentyczny od symulowanego (spoofowanego).

## 🚀 O Projekcie
Głównym celem jest stworzenie odpornego klasyfikatora, który potrafi wykryć anomalia w sygnale GPS bez polegania na cechach podatnych na wyciek danych (data leakage), takich jak surowe wartości fazy czy bezwzględny czas.

### Kluczowe funkcjonalności:
* **Grupowanie po PRN:** Analiza różnicowa parametrów prowadzona jest wewnątrz grup konkretnych satelitów.
* **Inżynieria Cech (Feature Engineering):** * `doppler_diff`: Nagłe zmiany częstotliwości Dopplera.
    * `c_n0_diff`: Skoki mocy sygnału.
    * `c_n0_rolling_std`: Analiza stabilności sygnału w oknie czasowym (wykrywanie nienaturalnie \\\"czystego\\\" sygnału).
* **Time-Series Split:** Model trenowany na przeszłości, testowany na przyszłości, co symuluje rzeczywisty przebieg ataku.

## 🛠 Technologie
* **Język:** Python 3.x
* **Analiza danych:** Pandas, NumPy
* **Machine Learning:** Scikit-learn (Random Forest), LightGBM
* **Serializacja:** Joblib (zapisywanie wag modelu)

## 📂 Struktura Projektu
* `main.py` – Skrypt treningowy, ewaluacja modelu i eksport do `.pkl`.
* `components/parser.py` – Moduł przetwarzania danych i inżynierii cech.
* `data/` – Katalog na zbiory danych (np. TEXBAT).
* `gps_spoofing_model.pkl` – Gotowy do użycia, wyeksportowany model.

## 📈 Wyniki i Skuteczność
Obecna wersja modelu (Random Forest z balansem klas) osiąga:
* **Accuracy:** ~90%
* **Precision (Spoofing):** ~76%
* **Recall (Spoofing):** ~45% (W trakcie optymalizacji - priorytet na wykrywanie False Negatives).

## 🔮 Roadmapa (Streamlit App)
Kolejnym etapem projektu jest stworzenie interaktywnego dashboardu w **Streamlit**, który pozwoli na:
1. **Analizę plików CSV:** Przesyłanie własnych logów z odbiorników i natychmiastowa wizualizacja ryzyka ataku.
2. **Monitoring Live:** Symulacja wnioskowania w czasie rzeczywistym na podstawie napływających danych.
3. **Visual Debugger:** Podgląd ważności cech i wykresów anomalii dla poszczególnych satelitów.

## 📚 Bibliografia
Dane wykorzystane w projekcie pochodzą z zestawu **TEXBAT** (Texas Spoofing Test Battery), uznawanego za światowy standard w testowaniu systemów anty-spoofingowych.
