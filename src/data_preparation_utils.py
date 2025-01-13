import os
import pandas as pd


# Absoluter Pfad zum Skriptverzeichnis und Datenordner
script_dir = os.path.dirname(os.path.abspath(__file__))
root_raw = os.path.join(script_dir, '..', 'data', 'raw')
root_interim = os.path.join(script_dir, '..', 'data', 'interim')
root_processed = os.path.join(script_dir, '..', 'data', 'processed')

# Rohdaten
data_kfz = '46251-0021_de_2020_flat.csv' # Daten über Fahrzeugbestand
data_pop = '12211-Z-03_flat.csv' # Bevölkerungsdaten
data_vee = 'AI-S-01_flat.csv' # Daten über Einkommen der privaten Haushalte
data_svu = 'AI013-3_flat.csv' # Straßenverkehrsunfälle

# Relevante Spaltennamen, Beschreibungen und Umbenennungen in den Rohdatensätzen
relevant_cols = [
    # kfz
    {'name': '1_variable_attribute_code', 'description': 'Landkreis ID', 'rename': 'landkreis_id', 'dtype': 'str'},
    {'name': '1_variable_attribute_label', 'description': 'Landkreis Name', 'rename': 'landkreis', 'dtype': 'str'},
    {'name': '2_variable_attribute_code', 'description': 'Kraftstoffarten -> Antriebe', 'rename': 'antrieb', 'dtype': 'str'},
    {'name': '3_variable_attribute_code', 'description': 'Emissionsgruppen', 'rename': 'emissionsgruppen', 'dtype': 'str'},
    {'name': 'value', 'description': 'Anzahl der Fahrzeuge', 'rename': 'anzahl_fahrzeuge', 'dtype': 'Int64'},
    # Gemeinsam pop, vee, svu
    {'name': '1_Auspraegung_Code', 'description': 'Landkreis ID', 'rename': 'landkreis_id', 'dtype': 'str'},
    {'name': '1_Auspraegung_Label', 'description': 'Landkreis Name', 'rename': 'landkreis', 'dtype': 'str'},
    # pop
    {'name': '2_Auspraegung_Code', 'description': 'Alter ID', 'rename': 'alter_id', 'dtype': 'str'},
    {'name': '2_Auspraegung_Label', 'description': 'Altersklasse', 'rename': 'alter', 'dtype': 'str'},
    {'name': '3_Auspraegung_Code', 'description': 'Geschlecht ID', 'rename': 'geschlecht_id', 'dtype': 'str'},
    {'name': '3_Auspraegung_Label', 'description': 'Geschlecht', 'rename': 'geschlecht', 'dtype': 'str'},
    {'name': 'BEVMZ11__Bevoelkerung_am_Hauptwohnort__1000', 'description': 'Bevölkerungsanzahl in Tausend', 'rename': 'anzahl_personen', 'dtype': 'float64'},
    # vee
    {'name': 'ID0002__Verfuegbares_Einkommen_je_EW__EUR', 'description': 'Verfügbares Einkommen je Einwohner in EUR', 'rename': 'vee', 'dtype': 'float64'},
    # svu
    {'name': 'AI1303__Strassenverkehrsunfaelle_je_10.000_Kfz__Anzahl', 'description': 'Unfaelle je 10000 Kfz.', 'rename': 'unfaelle_je_10k_kfz', 'dtype': 'float64'}
]


def select_columns(df: pd.DataFrame, relevant_cols: list) -> pd.DataFrame:
    """
    Extrahiert die relevanten Spalten aus einem DataFrame gemäß der Festlegung in relevant_cols.
    
    Args:
        df: DataFrame mit allen Spalten
        relevant_cols: Liste mit Dictionaries, die die relevanten Spalten definieren
        
    Returns:
        DataFrame mit nur den relevanten Spalten
    """
    # Extrahiere Spaltennamen aus relevant_cols, die im DataFrame existieren
    selected_cols = [d['name'] for d in relevant_cols if d['name'] in df.columns]
    
    # Wähle nur die relevanten Spalten aus
    return df[selected_cols]


def rename_columns(df: pd.DataFrame, relevant_cols: list) -> pd.DataFrame:
    """
    Benennt die Spalten eines DataFrames um und setzt die Datentypen gemäß der Festlegung in relevant_cols.
    
    Args:
        df: DataFrame mit den ursprünglichen Spaltennamen
        relevant_cols: Liste mit Dictionaries, die die Umbenennung und Datentypen definieren
        
    Returns:
        DataFrame mit umbenannten Spalten und korrekten Datentypen
    """
    # Erstelle Dictionary für Umbenennung (alt -> neu)
    rename_dict = {d['name']: d['rename'] for d in relevant_cols if d['name'] in df.columns}
    
    # Benenne Spalten um
    df = df.rename(columns=rename_dict)
    
    # Erstelle Dictionary für Datentypen (neu -> dtype)
    dtype_dict = {d['rename']: d['dtype'] for d in relevant_cols if d['rename'] in df.columns}
    
    # Setze Datentypen für jede Spalte
    for col, dtype in dtype_dict.items():
        if dtype in ['float64', 'Float64', 'Int64']:
            # Behandle numerische Spalten
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(',', '.'),
                errors='coerce'
            ).astype(dtype)
        else:
            # Behandle nicht-numerische Spalten
            df[col] = df[col].astype(dtype)
    
    return df


def remove_leading_zeros(df: pd.DataFrame) -> pd.DataFrame:
    """
    Entfernt führende Nullen aus der Spalte 'landkreis_id'.
    
    Args:
        df: DataFrame mit der Spalte 'landkreis_id'
        
    Returns:
        DataFrame mit bereinigter landkreis_id Spalte
    """
    if 'landkreis_id' in df.columns:
        df['landkreis_id'] = df['landkreis_id'].astype(str).str.lstrip('0')
    return df


def standardize_kfz_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardisiert die Kategorien 'antrieb' und 'emissionsgruppen' im KFZ-DataFrame.
    
    Args:
        df: DataFrame mit den Spalten 'antrieb' und 'emissionsgruppen'
        
    Returns:
        DataFrame mit standardisierten Kategoriespalten
    """
    # Kopie des DataFrames erstellen
    df = df.copy()
    
    # Antriebe standardisieren
    df['antrieb'] = (
        df['antrieb']
        .str.lower()                                    # Konvertiere in Kleinbuchstaben
        .str.replace(r'^ks-', '', regex=True)           # Entferne vorangestelltes 'ks-'
        .str.replace('-', '', regex=False)              # Entferne alle '-' Zeichen
        .replace({'sonst': 'sonstigeantriebe'})         # Ersetze 'sonst' mit 'sonstigeantriebe'
    )
    
    # Emissionsgruppen standardisieren
    df['emissionsgruppen'] = (
        df['emissionsgruppen']
        .str.lower()                                    # Konvertiere in Kleinbuchstaben
        .str.replace(r'^pkw-', '', regex=True)          # Entferne vorangestelltes 'pkw-'
        .str.replace('-', '', regex=False)              # Entferne alle '-' Zeichen
        .replace({'euro6r': 'euro6'})                   # Ersetze 'euro6r' mit 'euro6'
        .replace({'sonst': 'sonstigeemissionsgruppen'}) # Ersetze 'sonst' mit 'sonstigeemissionsgruppen'
    )
    
    return df


def transform_kfz_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transformiert den KFZ-DataFrame durch Pivotierung und Summierung.
    
    Args:
        df: DataFrame mit den Spalten 'landkreis_id', 'landkreis', 'antrieb', 
            'emissionsgruppen' und 'anzahl_fahrzeuge'
        
    Returns:
        Transformierter DataFrame mit:
        - Pivotierten Spalten für Antrieb-Emissions-Kombinationen
        - Summen für einzelne Antriebsarten und Emissionsgruppen
        - Gesamtanzahl der Fahrzeuge
    """
    # Pivotieren des DataFrame
    df = df.pivot_table(
        index=['landkreis_id', 'landkreis'], 
        columns=['antrieb', 'emissionsgruppen'], 
        values='anzahl_fahrzeuge', 
        fill_value=0)
    
    # MultiIndex der Spalten flach machen
    df.columns = [f"{antrieb.lower()}_{emission.lower()}" for antrieb, emission in df.columns]
    
    # Konvertiere alle pivotierten Spalten zu int
    df = df.astype(int)
    
    # Gesamtanzahl der Fahrzeuge berechnen
    df['gesamt'] = df.sum(axis=1).astype(int)
    
    # Spaltennamen-Extraktion
    antriebe = df.columns.str.extract(r"^(\w+)_")[0].dropna().unique()
    emissionen = df.columns.str.extract(r"_(\w+)$")[0].dropna().unique()
    
    # Summen für Antriebsarten berechnen
    for antrieb in antriebe:
        antrieb_spalten = [col for col in df.columns if col.startswith(f"{antrieb}_")]
        df[antrieb] = df[antrieb_spalten].sum(axis=1).astype(int)
    
    # Summen für Emissionsgruppen berechnen
    for emission in emissionen:
        emission_spalten = [col for col in df.columns if col.endswith(f"_{emission}")]
        df[emission] = df[emission_spalten].sum(axis=1).astype(int)
    
    # MultiIndex in Spalten umwandeln
    df = df.reset_index()
    
    # Spalte 'gesamt' umbenennen
    df = df.rename(columns={'gesamt': 'anzahl_kfz'})
    
    return df

def fix_missing_values(df_combined: pd.DataFrame, df_reference: pd.DataFrame, column_name: str, verbose: bool = False) -> pd.DataFrame:
    """
    Korrigiert fehlende Werte in einem DataFrame durch Nachschlagen von Werten aus einem Referenz-DataFrame.
    
    Diese Funktion wird verwendet, um fehlende oder ungültige Werte (NaN oder <= 0) in einer bestimmten Spalte
    des kombinierten DataFrames zu korrigieren, indem entsprechende Werte aus einem Referenz-DataFrame nachgeschlagen werden.
    Die Zuordnung erfolgt über die landkreis_id.
    
    Args:
        df_combined (pd.DataFrame): DataFrame mit zu korrigierenden fehlenden Werten
        df_reference (pd.DataFrame): Referenz-DataFrame mit korrekten Werten
        column_name (str): Name der zu korrigierenden Spalte
        verbose (bool, optional): Wenn True, werden detaillierte Ausgaben gedruckt. Defaults to False.
    
    Returns:
        pd.DataFrame: DataFrame mit korrigierten Werten
    
    Hinweise:
        - Funktion prüft auf NaN-Werte und Werte <= 0
        - Führende Nullen in landkreis_id werden beim Matching entfernt
        - Das Korrekturergebnis wird protokolliert, wenn verbose=True
    """
    # Prüfe auf fehlende Werte
    missing_values = df_combined[df_combined[column_name].isna()]
    
    if not missing_values.empty:
        if verbose:
            print(f"Gefunden: {len(missing_values)} fehlende '{column_name}' Werte")
        
        # Iteriere durch Zeilen mit fehlenden Werten
        for index, row in missing_values.iterrows():
            # Entferne Nullen am Ende der landkreis_id für die Suche
            landkreis_id_trans = str(row['landkreis_id']).rstrip('0')
            
            # Suche nach passendem Eintrag im Referenz-DataFrame
            matching_row = df_reference[df_reference['landkreis_id'] == landkreis_id_trans]
            
            if not matching_row.empty:
                df_combined.loc[index, column_name] = matching_row[column_name].values[0]
                if verbose:
                    print(f"Fehlender Wert für '{row['landkreis']}' wurde ersetzt mit '{column_name}' Wert: {matching_row[column_name].values[0]}")
            else:
                if verbose:
                    print(f"Kein passender '{column_name}' Wert gefunden für '{row['landkreis']}'")
    elif verbose:
        print(f"Alle '{column_name}' Werte sind gültig und vorhanden.")

    # Abschließende Prüfung auf verbleibende fehlende Werte
    still_missing = df_combined[df_combined[column_name].isna()]
    if still_missing.empty:
        if verbose:
            print(f"Alle fehlenden '{column_name}' Werte wurden erfolgreich korrigiert.")
    elif verbose:
        print(f"Es gibt noch Landkreise mit fehlenden '{column_name}' Werten:")
        print(still_missing[['landkreis_id', 'landkreis']])
    
    return df_combined