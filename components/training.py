from parser import parse_and_prepare
from lightgbm import LGBMClassifier, early_stopping
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd
import joblib
import os

<<<<<<< Updated upstream
# -----------------

def create_model(model_name: str, file_path: str, clf: LGBMClassifier, features: list):
    model_filename = f'{model_name}.pkl'

# Tworzymy słownik z modelem i metadanymi
=======
def create_model(model_name: str, save_dir: str, clf: LGBMClassifier, features: list, scaler: StandardScaler) -> str:
    model_filename = os.path.join(save_dir, f'{model_name}.pkl') if save_dir else f'{model_name}.pkl'

    # Zapisujemy zarówno model jak i skaler, żeby run_model miał jak przeskalować nowe dane
>>>>>>> Stashed changes
    model_data = {
        'model': clf,
        'scaler': scaler,
        'features': features,
        'description': 'LGBM Detector'
    }

    joblib.dump(model_data, model_filename)
<<<<<<< Updated upstream

    print(f"\nModel został pomyślnie zapisany w pliku: {model_filename}")
=======
    print(f"\nModel i skaler zostały pomyślnie zapisane w pliku: {model_filename}")
    return model_filename
>>>>>>> Stashed changes

def analyze_data(file_path: str, split_ratio: float = 0.8, output_model: bool = True):
    print("1. Przygotowywanie danych...")
    full_data = parse_and_prepare(file_path)
    
    if full_data is None or full_data.empty:
        return None, None, None

    features = [
        'doppler_hz', 'doppler_delta', 'power_dB', 'power_variance_dB', 
        'mean_magnitude_dB', 'std_magnitude_dB', 'mean_phase', 
        'skew_I', 'skew_Q', 'kurtosis_I', 'kurtosis_Q'
    ]
    
    X = full_data[features]
    y = full_data['label']

    # Podział chronologiczny (split_row)
    split_row = int(len(full_data) * split_ratio)
    x_train_full = X.iloc[:split_row]
    y_train_full = y.iloc[:split_row]
    x_test = X.iloc[split_row:]
    y_test = y.iloc[split_row:]

    print(f"Trening do wiersza {split_row}. Test od wiersza {split_row} do {len(full_data)}.")

    x_train, x_val, y_train, y_val = train_test_split(x_train_full, y_train_full, test_size=0.2, random_state=42)

    # Skalowanie (Uczymy tylko na treningu, aplikujemy na resztę)
    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train)
    x_val = scaler.transform(x_val)
    x_test = scaler.transform(x_test)

    print("\nRozkład w treningu:")
    print(y_train_full.value_counts())

    print("\n2. Trenowanie modelu...")
    clf = LGBMClassifier(n_estimators=100, learning_rate=0.05, num_leaves=31, class_weight='balanced', random_state=42)
    clf.fit(x_train, y_train, eval_set=[(x_val, y_val)], callbacks=[early_stopping(stopping_rounds=20)])

    print("\n3. Raport skuteczności:")
    y_pred = clf.predict(x_test)
    class_report = classification_report(y_test, y_pred, output_dict=True)
    print(classification_report(y_test, y_pred))

    print("\n--- ANALIZA WAŻNOŚCI CECH ---")
    feat_imp = pd.DataFrame({
        'Cecha': features, 
        'Ważność': clf.feature_importances_
    }).sort_values(by='Ważność', ascending=False)
    print(feat_imp.to_string(index=False))
    
<<<<<<< Updated upstream
    
    if output_model:
        model_path = os.path.dirname(file_path)
        create_model('lgbm_gps_spoof_detector', model_path, clf, features)
    return class_report, feat_imp
=======
    saved_model_path = None
    if output_model:
        save_dir = os.path.dirname(file_path)
        saved_model_path = create_model('gps_spoof_detector', save_dir, clf, features, scaler)
        
    return class_report, feat_imp, saved_model_path

def run_model(file_path: str, model_path: str):
    print("1. Ładowanie modelu...")
    model_data = joblib.load(model_path)
    clf: LGBMClassifier = model_data['model']
    scaler: StandardScaler = model_data['scaler']
    features: list = model_data['features']

    print("2. Przygotowywanie danych...")
    full_data = parse_and_prepare(file_path)
    
    if full_data is None or full_data.empty:
        return None, None, None

    X = full_data[features]
    X_scaled = scaler.transform(X)
    full_data['prediction'] = clf.predict(X_scaled)

    class_report = None
    if 'label' in full_data.columns:
        y_true = full_data['label']
        y_pred = full_data['prediction']
        class_report = classification_report(y_true, y_pred, output_dict=True)
        print("\nRaport skuteczności:")
        print(classification_report(y_true, y_pred))

    feat_imp = pd.DataFrame({
        'Cecha': features,
        'Ważność': clf.feature_importances_,
    }).sort_values(by='Ważność', ascending=False)

    print(f"\nGotowe. Przewidziano {len(full_data)} wierszy.")
    return full_data, class_report, feat_imp
>>>>>>> Stashed changes

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(base_path, '../data', 'tuniClear.csv')
    
    analyze_data(data_file, split_ratio=0.8, output_model=True)