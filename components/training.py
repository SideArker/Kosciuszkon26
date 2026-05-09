from components.parser import parse_and_prepare
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
import pandas as pd
from lightgbm import LGBMClassifier, early_stopping
import joblib
import os

# -----------------

def create_model(model_name: str, file_path: str, clf: LGBMClassifier, features: list):
    model_filename = f'{model_name}.pkl'

# Tworzymy słownik z modelem i metadanymi
    model_data = {
        'model': clf,
        'features': features,
        'description': 'Model RF trenowany na danych TEXBAT (balanced)'
    }

    # Zapis do pliku
    joblib.dump(model_data, model_filename)

    print(f"\nModel został pomyślnie zapisany w pliku: {model_filename}")



def analyze_data(file_path: str, split_row: int, output_model: bool = True):
    print("1. Przygotowywanie danych...")

    full_data = parse_and_prepare(file_path)
    full_data = full_data.sort_values(by=['TOW', 'TOW_Frac']).reset_index(drop=True)

    features = ['c_n0_diff', 'doppler_diff', 'c_n0_rolling_std']
    X = full_data[features]
    y = full_data['Label']

    x_train_full = X.iloc[:split_row]
    y_train_full = y.iloc[:split_row]

    x_test = X.iloc[split_row:]
    y_test = y.iloc[split_row:]

    print(f"Trening do wiersza {split_row}. Test od wiersza {split_row} do {len(full_data)}.")

    x_train, x_val, y_train, y_val = train_test_split(x_train_full, y_train_full, test_size=0.2, random_state=42)

    print("\nRozkład w treningu:")
    print(y_train_full.value_counts())



    print("\n2. Trenowanie modelu...")
    clf = LGBMClassifier(n_estimators=100,
                         learning_rate=0.05,
                         num_leaves=31,
                         class_weight='balanced',
                         random_state=42)
    clf.fit(x_train, y_train,
            eval_set=[(x_val, y_val)],
            callbacks=[early_stopping(stopping_rounds=50)])

    print("\n3. Raport skuteczności (Zgadywanka):")
    y_pred = clf.predict(x_test)
    class_report = classification_report(y_test, y_pred, output_dict=True)
    print(classification_report(y_test, y_pred))

    print(class_report)
    print("\n--- ANALIZA WAŻNOŚCI CECH ---")
    feat_imp = pd.DataFrame({
        'Cecha': features, 
        'Ważność': clf.feature_importances_
    }).sort_values(by='Ważność', ascending=False)
    print(feat_imp.to_string(index=False))
    
    
    if output_model:
        model_path = os.path.dirname(file_path)
        create_model('lgbm_gps_spoof_detector', model_path, clf, features)
    return class_report, feat_imp


