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