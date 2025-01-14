import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath('..'))
from src.data_preparation_utils import root_raw, root_interim, root_processed, data_kfz, data_pop, data_vee, data_svu, relevant_cols
from src.data_exploration_utils import create_table_figure, create_stacked_bar_chart, create_distribution_plot, create_density_plot, create_scatterplot_grid


# Dataframes der Rohdaten
df_kfz = pd.read_csv(os.path.join(root_raw, data_kfz), sep=";", decimal='.') # Fahrzeugbestand
df_pop = pd.read_csv(os.path.join(root_raw, data_pop), sep=";", decimal='.', encoding='ISO-8859-1') # Bevölkerungsdaten
df_vee = pd.read_csv(os.path.join(root_raw, data_vee), sep=";", decimal='.', encoding='ISO-8859-1') # Einkommen
df_svu = pd.read_csv(os.path.join(root_raw, data_svu), sep=";", decimal='.', encoding='ISO-8859-1') # Straßenverkehrsunfälle

# Dataframe der zusammengesetzen aufbereiteten Daten
df_merged = pd.read_csv(os.path.join(root_processed, 'kfz_kombiniert.csv'))

# gruppierte und normierte Dataframes (abgeleitet aus df_merged)
df_antriebe = pd.read_csv(os.path.join(root_interim, 'antriebe.csv'))
df_antriebe_prozent = pd.read_csv(os.path.join(root_interim, 'antriebe_prozent.csv'))
df_eg = pd.read_csv(os.path.join(root_interim, 'emissionsgruppen.csv'))
df_eg_prozent = pd.read_csv(os.path.join(root_interim, 'emissionsgruppen_prozent.csv'))
df_regr = pd.read_csv(os.path.join(root_processed, 'regression_data.csv'))

# Datenwörterbuch
data_dict = {
    "landkreis_id": {
        "Beschreibung": "Landkreis ID",
        "Rolle": "ID",
        "Typ": "",
        "Format": "String"
    },
    "anzahl_personen_1000": {
        "Beschreibung": "Bevölkerungsanzahl in Tausend",
        "Rolle": "Prädiktor",
        "Typ": "numerisch",
        "Format": "Float"
    },
    "vee": {
        "Beschreibung": "Verfügbares Einkommen je Einwohner in EUR",
        "Rolle": "Prädiktor",
        "Typ": "numerisch",
        "Format": "Float"
    },
    "anzahl_kfz_je_person": {
        "Beschreibung": "Anzahl der Kraftfahrzeuge pro Person",
        "Rolle": "Prädiktor",
        "Typ": "numerisch",
        "Format": "Float"
    },
    "unfaelle_je_10k_kfz": {
        "Beschreibung": "Unfaelle je 10000 Kfz",
        "Rolle": "Prädiktor",
        "Typ": "numerisch",
        "Format": "Float"
    },
    "elektro": {
        "Beschreibung": "Anteil der Elektrofahrzeuge",
        "Rolle": "Prädiktor",
        "Typ": "numerisch",
        "Format": "Float"
    },
    "pih": {
        "Beschreibung": "Anteil der Plug-in-Hybridfahrzeuge",
        "Rolle": "Prädiktor",
        "Typ": "numerisch",
        "Format": "Float"
    },
    "euro2": {
        "Beschreibung": "Anteil der Fahrzeuge mit EURO 2 Norm",
        "Rolle": "Prädiktor",
        "Typ": "numerisch",
        "Format": "Float"
    },
    "euro3": {
        "Beschreibung": "Anteil der Fahrzeuge mit EURO 3 Norm",
        "Rolle": "Prädiktor",
        "Typ": "numerisch",
        "Format": "Float"
    },
    "euro4": {
        "Beschreibung": "Anteil der Fahrzeuge mit EURO 4 Norm",
        "Rolle": "Antwort",
        "Typ": "numerisch",
        "Format": "Float"
    },
    "euro6": {
        "Beschreibung": "Anteil der Fahrzeuge mit EURO 6 Norm",
        "Rolle": "Prädiktor",
        "Typ": "numerisch",
        "Format": "Float"
    },
    "euro6dt": {
        "Beschreibung": "Anteil der Fahrzeuge mit EURO 6d-TEMP Norm",
        "Rolle": "Prädiktor",
        "Typ": "numerisch",
        "Format": "Float"
    }
}
df_data_dictionary = pd.DataFrame.from_dict(data_dict, orient='index').reset_index()
df_data_dictionary.columns = ["Name", "Beschreibung", "Rolle", "Typ", "Format"]

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

# Fahrzeugbestand nach Antriebsart und Landkreis
chart_antriebe = create_stacked_bar_chart(
    df=df_antriebe,
    id_vars=['landkreis'],
    var_name='antriebsart',
    value_name='Anzahl',
    x_axis_title='Landkreis',
    chart_title='Fahrzeugbestand nach Antriebsart und Landkreis'
)

# Fahrzeugbestand nach Antriebsart und Landkreis (normiert)
chart_antriebe_prozent = create_stacked_bar_chart(
    df=df_antriebe_prozent,
    id_vars=['landkreis'],
    var_name='antriebsart',
    value_name='Anteil %',
    x_axis_title='Landkreis',
    chart_title='Fahrzeugbestand nach Antriebsart und Landkreis'
)

# Fahrzeugbestand nach Emissionsgruppe und Landkreis (normiert)
chart_eg_prozent = create_stacked_bar_chart(
    df=df_eg_prozent,
    id_vars=['landkreis'],
    var_name='Emissiongruppe',
    value_name='Anteil %',
    x_axis_title='Landkreis',
    chart_title='Fahrzeugbestand nach Emissionsgruppe und Landkreis'
)