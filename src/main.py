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

        # Spalten auswählen und umbenennen
        df_kfz = select_columns(df_kfz, relevant_cols)
        df_kfz = rename_columns(df_kfz, relevant_cols)
        df_kfz = standardize_kfz_categories(df_kfz)
        df_kfz = remove_leading_zeros(df_kfz)

        df_pop = select_columns(df_pop, relevant_cols)
        df_pop = rename_columns(df_pop, relevant_cols)
        df_pop = remove_leading_zeros(df_pop)

        df_vee = select_columns(df_vee, relevant_cols)
        df_vee = rename_columns(df_vee, relevant_cols)
        df_vee = remove_leading_zeros(df_vee)

        df_svu = select_columns(df_svu, relevant_cols)
        df_svu = rename_columns(df_svu, relevant_cols)
        df_svu = remove_leading_zeros(df_svu)

        print(df_kfz)
        print("Programm erfolgreich beendet!")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

if __name__ == "__main__":
    main()