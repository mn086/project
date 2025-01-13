import sys
import os
import pandas as pd


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