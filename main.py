# from components.parser import parse_and_prepare
# #nasz cudowny Parser.py

# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import classification_report
# import pandas as pd



# print("1. Wczytywanie i parsowanie danych...")
# X_train, y_train = parse_and_prepare('data/train.csv')
# X_verify, y_verify = parse_and_prepare('data/verify.csv')


# print("\n--- ROZKŁAD KLAS W DANYCH ---")
# print("Zbiór treningowy (train.csv):")
# print(y_train.value_counts())

# print("\nZbiór weryfikacyjny (verify.csv):")
# print(y_verify.value_counts())



# print(f"\n2. Trenowanie algorytmu (Zbiór treningowy: {len(X_train)} rekordów)...")
# clf = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
# clf.fit(X_train, y_train)

# print(f"\n3. Testowanie modelu (Zbiór weryfikacyjny: {len(X_verify)} rekordów)...")
# y_pred = clf.predict(X_verify)

# print("\n--- RAPORT SKUTECZNOŚCI ---")
# print(classification_report(y_verify, y_pred))



# print("\n--- ANALIZA WAŻNOŚCI CECH (Feature Importances) ---")
# importances = clf.feature_importances_
# feature_names = X_train.columns

# feat_imp = pd.DataFrame({
#     'Cecha': feature_names, 
#     'Ważność': importances
# }).sort_values(by='Ważność', ascending=False)

# print(feat_imp.to_string(index=False))























from components.parser import parse_and_prepare
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import pandas as pd

# --- PARAMETRY ---
FILE_PATH = 'data/texbat_fixed.csv'
SPLIT_ROW = 20000  # Tutaj zaczyna się "zgadywanka"
# -----------------

print("1. Przygotowywanie danych...")
full_data = parse_and_prepare(FILE_PATH)

full_data = full_data.sort_values(by=['TOW', 'TOW_Frac']).reset_index(drop=True)

features = ['c_n0_diff', 'doppler_diff', 'c_n0_rolling_std']
X = full_data[features]
y = full_data['Label']

X_train = X.iloc[:SPLIT_ROW]
y_train = y.iloc[:SPLIT_ROW]

X_test = X.iloc[SPLIT_ROW:]
y_test = y.iloc[SPLIT_ROW:]

print(f"Trening do wiersza {SPLIT_ROW}. Test od wiersza {SPLIT_ROW} do {len(full_data)}.")

print("\nRozkład w treningu:")
print(y_train.value_counts())



print("\n2. Trenowanie modelu...")
clf = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
clf.fit(X_train, y_train)

print("\n3. Raport skuteczności (Zgadywanka):")
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))

print("\n--- ANALIZA WAŻNOŚCI CECH ---")
feat_imp = pd.DataFrame({
    'Cecha': features, 
    'Ważność': clf.feature_importances_
}).sort_values(by='Ważność', ascending=False)
print(feat_imp.to_string(index=False))












#wydruk modelu do pliku:

import joblib

# Nazwa pliku
model_filename = 'gps_spoofing_model.pkl'

# Tworzymy słownik z modelem i metadanymi
model_data = {
    'model': clf,
    'features': features,
    'description': 'Model RF trenowany na danych TEXBAT (balanced)'
}

# Zapis do pliku
joblib.dump(model_data, model_filename)

print(f"\nModel został pomyślnie zapisany w pliku: {model_filename}")




#do oczytu:
# import joblib
# import pandas as pd

# # Ładowanie całego pakietu
# saved_data = joblib.load('gps_spoofing_model.pkl')

# loaded_clf = saved_data['model']
# model_features = saved_data['features']

# print(f"Model załadowany. Cechy: {model_features}")

# # Przykład użycia na nowych danych (X_new musi mieć kolumny z model_features)
# # predictions = loaded_clf.predict(X_new[model_features])