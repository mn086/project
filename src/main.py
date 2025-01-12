import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath('..'))
from src.data_preparation_utils import select_columns, rename_columns, remove_leading_zeros, standardize_kfz_categories
#from src.data_exploration_utils import *


def main():
    """
    Hauptfunktion, die als Einstiegspunkt für das Programm dient.
    """
    try:
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
        
        
        print("Programm erfolgreich beendet!")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

if __name__ == "__main__":
    main()