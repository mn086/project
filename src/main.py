import os
import pandas as pd

from data_preparation_utils import *


def main():
    """
    Hauptfunktion, die als Einstiegspunkt für das Programm dient.
    """
    try:
        # Dataframes der Rohdaten
        df_kfz = pd.read_csv(os.path.join(root_raw, data_kfz), sep=";", decimal='.') # Fahrzeugbestand
        df_pop = pd.read_csv(os.path.join(root_raw, data_pop), sep=";", decimal='.', encoding='ISO-8859-1') # Bevölkerungsdaten
        df_vee = pd.read_csv(os.path.join(root_raw, data_vee), sep=";", decimal='.', encoding='ISO-8859-1') # Einkommen
        df_svu = pd.read_csv(os.path.join(root_raw, data_svu), sep=";", decimal='.', encoding='ISO-8859-1') # Straßenverkehrsunfälle

        # Daten vorverarbeiten
        df_kfz = select_columns(df_kfz, relevant_cols)
        #df_kfz = rename_columns(df_kfz, relevant_cols)
        df_kfz.rename(columns= {
            '1_variable_attribute_code' : 'landkreis_id',
            '1_variable_attribute_label': 'landkreis',
            '2_variable_attribute_code': 'antrieb',
            '3_variable_attribute_code': 'emissionsgruppen',
            'value': 'anzahl_fahrzeuge'
            }, inplace=True)
        df_kfz['anzahl_fahrzeuge']= pd.to_numeric(df_kfz['anzahl_fahrzeuge'], errors='coerce').astype('Int64')
        #
        df_kfz = standardize_kfz_categories(df_kfz)
        df_kfz = remove_leading_zeros(df_kfz)

        df_pop = select_columns(df_pop, relevant_cols)
        #df_pop = rename_columns(df_pop, relevant_cols)
        df_pop.rename(columns= {
            '1_Auspraegung_Code' : 'landkreis_id',
            '1_Auspraegung_Label': 'landkreis',
            '2_Auspraegung_Code': 'alter_id',
            '2_Auspraegung_Label': 'alter',
            '3_Auspraegung_Code': 'geschlecht_id',
            '3_Auspraegung_Label': 'geschlecht',
            'BEVMZ11__Bevoelkerung_am_Hauptwohnort__1000': 'anzahl_personen_1000'
            }, inplace=True)
        df_pop['anzahl_personen_1000'] = pd.to_numeric(df_pop['anzahl_personen_1000'], errors='coerce').astype('float64')
        #
        df_pop = remove_leading_zeros(df_pop)

        df_vee = select_columns(df_vee, relevant_cols)
        df_vee = rename_columns(df_vee, relevant_cols)
        df_vee = remove_leading_zeros(df_vee)

        df_svu = select_columns(df_svu, relevant_cols)
        df_svu = rename_columns(df_svu, relevant_cols)
        df_svu = remove_leading_zeros(df_svu)

        # Daten auschließen
        df_kfz = df_kfz.dropna() # aggregierte Zeilen haben NaN in den Spalten 'antriebe' und 'emissionsgruppen'
        df_kfz = df_kfz[~df_kfz['landkreis'].str.contains(r'\)\s*$', na=False)] # Ausschluss von Landkreisen mit Gebietsreform, diese enden beispielsweise mit "(bis 03.09.2011)"

        df_pop = df_pop[df_pop['alter_id'].isna()] # Nur aggregierte Zeilen behalten (alter_id ist NaN)
        df_pop = df_pop[df_pop['geschlecht_id'].isna()] # Nur aggregierte Zeilen behalten (geschlecht_id ist NaN), übrig bleiben Zeilen der Gesamteinwohnerzahl

        # Pivotierung und Summierung des KFZ-DataFrame
        df_kfz = transform_kfz_data(df_kfz)

        # Transformierte Daten zwischenspeichern
        df_kfz.to_csv(os.path.join(root_interim, 'kfz.csv'))
        df_vee.to_csv(os.path.join(root_interim, 'vee.csv'))
        df_pop.to_csv(os.path.join(root_interim, 'pop.csv'))
        df_svu.to_csv(os.path.join(root_interim, 'svu.csv'))

        # Zusammenführen der Dataframes mit Hilfe der landkreis_id
        df_merged = df_kfz.merge(df_vee[['landkreis_id', 'vee']], on='landkreis_id', how='left')
        df_merged = df_merged.merge(df_pop[['landkreis_id', 'anzahl_personen_1000']], on='landkreis_id', how='left')
        df_merged = df_merged.merge(df_svu[['landkreis_id', 'unfaelle_je_10k_kfz']], on='landkreis_id', how='left')
        
        # Suche nach Daten, die aufgrund inkonsistenter `landkreis_id` nicht gemerged werden konnten
        # (es verbleiben Landkreise, zu denen keine Daten in df_pop gefunden werden können -> Ausgabe mit verbose=True )
        df_merged = fix_missing_values(df_merged, df_vee, 'vee')
        df_merged = fix_missing_values(df_merged, df_pop, 'anzahl_personen_1000')
        df_merged = fix_missing_values(df_merged, df_svu, 'unfaelle_je_10k_kfz')

        # Feature Engineering: Neue Spalte 'anzahl_kfz_je_person' erstellen
        df_merged['anzahl_kfz_je_person'] = df_merged['anzahl_kfz'] / (df_merged['anzahl_personen_1000'] * 1000)

        # Zusammengesetzen aufbereiteten Datensatz speichern
        df_merged.to_csv(os.path.join(root_processed, 'kfz_kombiniert.csv'), index=False, encoding='utf-8')

        # Gliederung der Daten zur explorativen Analyse, Normierung und Modellerstellung
        list_kfz_aggr_antriebe = ["benzin", "diesel", "elektro", "gas", "hybrid", "pih", "sonstigeantriebe"]
        list_kfz_aggr_eg = ["euro1", "euro2", "euro3", "euro4", "euro5", "euro6", "euro6dt", "euro6d", "sonstigeemissionsgruppen"]

        df_antriebe = df_merged[['landkreis'] + list_kfz_aggr_antriebe]
        df_eg = df_merged[['landkreis'] + list_kfz_aggr_eg]

        df_antriebe_prozent = df_antriebe.copy()
        df_antriebe_prozent[list_kfz_aggr_antriebe] = df_antriebe[list_kfz_aggr_antriebe].apply(lambda x: x / x.sum() * 100, axis=1)
        df_eg_prozent = df_eg.copy()
        df_eg_prozent[list_kfz_aggr_eg] = df_eg[list_kfz_aggr_eg].apply(lambda x: x / x.sum() * 100, axis=1)

        # Dataframe für die Korrelation erstellen
        df_corr = pd.DataFrame(pd.concat([df_merged[['anzahl_personen_1000', 'vee', 'anzahl_kfz', 'anzahl_kfz_je_person', 'unfaelle_je_10k_kfz']],
                                          df_antriebe_prozent[list_kfz_aggr_antriebe],
                                          df_eg_prozent[list_kfz_aggr_eg]], axis=1))
        df_corr = df_corr[['anzahl_personen_1000', 'vee', 'anzahl_kfz_je_person', 'unfaelle_je_10k_kfz',
                                    'elektro', 'pih',
                                    'euro2', 'euro3', 'euro4', 'euro6', 'euro6dt']]
        
        # Datensätze speichern
        df_antriebe.to_csv(os.path.join(root_interim, 'antriebe.csv'), index=False, encoding='utf-8')
        df_antriebe_prozent.to_csv(os.path.join(root_interim, 'antriebe_prozent.csv'), index=False, encoding='utf-8')
        df_eg.to_csv(os.path.join(root_interim, 'emissionsgruppen.csv'), index=False, encoding='utf-8')
        df_eg_prozent.to_csv(os.path.join(root_interim, 'emissionsgruppen_prozent.csv'), index=False, encoding='utf-8')
        df_corr.to_csv(os.path.join(root_processed, 'regression_data.csv'), index=False, encoding='utf-8')

        print(df_corr.info())
        print("Programm erfolgreich beendet!")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

if __name__ == "__main__":
    main()