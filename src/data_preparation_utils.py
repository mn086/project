import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath('..'))
from src.data_exploration_utils import create_table_figure

# absoluter Pfad zum Skriptverzeichnis und Datenordner
script_dir = os.path.dirname(os.path.abspath(__file__))
root_raw = os.path.join(script_dir, '..', 'data', 'raw')

# Rohdaten
data_kfz = '46251-0021_de_2020_flat.csv' # Daten über Fahrzeugbestand
data_pop = '12211-Z-03_flat.csv' # Bevölkerungsdaten
data_vee = 'AI-S-01_flat.csv' # Daten über Einkommen der privaten Haushalte
data_svu = 'AI013-3_flat.csv' # Straßenverkehrsunfälle

# Dataframes der Rohdaten
df_kfz = pd.read_csv(os.path.join(root_raw, data_kfz), sep=";", decimal='.') # Fahrzeugbestand
df_pop = pd.read_csv(os.path.join(root_raw, data_pop), sep=";", decimal='.', encoding='ISO-8859-1') # Bevölkerungsdaten
df_vee = pd.read_csv(os.path.join(root_raw, data_vee), sep=";", decimal='.', encoding='ISO-8859-1') # Einkommen
df_svu = pd.read_csv(os.path.join(root_raw, data_svu), sep=";", decimal='.', encoding='ISO-8859-1') # Straßenverkehrsunfälle

# Relevante Spaltennamen, Beschreibungen und Umbenennungen in den Rohdatensätzen
relevant_cols = [
    # kfz
    {'name': '1_variable_attribute_code', 'description': 'Landkreis ID', 'rename': 'landkreis_id'},
    {'name': '1_variable_attribute_label', 'description': 'Landkreis Name', 'rename': 'landkreis'},
    {'name': '2_variable_attribute_code', 'description': 'Kraftstoffarten -> Antriebe', 'rename': 'antrieb'},
    {'name': '3_variable_attribute_code', 'description': 'Emissionsgruppen', 'rename': 'emissionsgruppen'},
    {'name': 'value', 'description': 'Anzahl der Fahrzeuge', 'rename': 'anzahl_fahrzeuge'},
    # Gemeinsam pop, vee, svu
    {'name': '1_Auspraegung_Code', 'description': 'Landkreis ID', 'rename': 'landkreis_id'},
    {'name': '1_Auspraegung_Label', 'description': 'Landkreis Name', 'rename': 'landkreis'},
    # pop
    {'name': '2_Auspraegung_Code', 'description': 'Alter ID', 'rename': 'alter_id'},
    {'name': '2_Auspraegung_Label', 'description': 'Altersklasse', 'rename': 'alter'},
    {'name': '3_Auspraegung_Code', 'description': 'Geschlecht ID', 'rename': 'geschlecht_id'},
    {'name': '3_Auspraegung_Label', 'description': 'Geschlecht', 'rename': 'geschlecht'},
    {'name': 'BEVMZ11__Bevoelkerung_am_Hauptwohnort__1000', 'description': 'Bevölkerungsanzahl in Tausend', 'rename': 'anzahl_personen'},
    # vee
    {'name': 'ID0002__Verfuegbares_Einkommen_je_EW__EUR', 'description': 'Verfügbares Einkommen je Einwohner in EUR', 'rename': 'vee'},
    # svu
    {'name': 'AI1303__Strassenverkehrsunfaelle_je_10.000_Kfz__Anzahl', 'description': 'Unfaelle je 10000 Kfz.', 'rename': 'unfaelle_je_10k_kfz'}
]


def create_info_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Erstellt eine Übersichtstabelle mit Informationen zu allen Spalten eines DataFrames.
    
    Args:
        df: Der zu analysierende DataFrame
        
    Returns:
        pd.DataFrame: Tabelle mit Spalteninformationen (Datentyp, Anzahl Werte, Anzahl NULL-Werte, Anzahl Ausprägungen)
    """
    df_info = []
    for column in df.columns:
        dtype = str(df[column].dtype)
        non_null = df[column].count()
        null_count = df[column].isnull().sum()
        unique_count = df[column].nunique()
        df_info.append({
            'Spalte': column,
            'Datentyp': dtype,
            'Anzahl_Werte': non_null,
            'Anzahl_NULL': null_count,
            'Anzahl_Ausprägungen': unique_count
        })
    
    return pd.DataFrame(df_info)


def add_description_column(info_df: pd.DataFrame, relevant_cols: list) -> pd.DataFrame:
    """
    Fügt eine Spalte 'Beschreibung' zu einem DataFrame hinzu, basierend auf den relevanten Spaltennamen.
    
    Args:
        info_df: DataFrame, der von create_info_table zurückgegeben wurde
        relevant_cols: Liste von Dictionaries mit relevanten Spalteninformationen
        
    Returns:
        pd.DataFrame: Der erweiterte DataFrame mit einer zusätzlichen Spalte 'Beschreibung'
    """
    # Erstelle ein Dictionary für schnellen Zugriff auf Beschreibungen
    description_dict = {col['name']: col['description'] for col in relevant_cols}
    
    # Füge die Spalte 'Beschreibung' hinzu
    info_df['Beschreibung'] = info_df['Spalte'].apply(lambda x: description_dict.get(x, 'nicht relevant'))
    
    return info_df


def create_info_figure(df: pd.DataFrame, description: str = 'Beschreibung der Datenspalten') -> None:
    """
    Erstellt eine Übersichtstabelle mit Informationen zu allen Spalten eines DataFrames.
    
    Args:
        df: Der zu visualisierende DataFrame
        description: Die Beschreibung unter der Abbildung (Standard: 'Beschreibung der Datenspalten')
    """
    info_df = create_info_table(df)
    info_df = add_description_column(info_df, relevant_cols)
    create_table_figure(info_df, description)