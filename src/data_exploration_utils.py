import pandas as pd
import matplotlib.pyplot as plt


def create_table_figure_matplotlib(df: pd.DataFrame, description: str = '') -> None:
    """Erstellt eine Tabellenabbildung mit matplotlib
    
    Args:
        df: Der zu visualisierende DataFrame
        description: Die Beschreibung unter der Abbildung
    """
    # Berechne maximale Textlänge für jede Spalte (Header + Inhalt)
    max_lengths = {}
    for col in df.columns:
        # Berücksichtige Kopfzeile und Inhalt
        header_length = len(str(col))
        content_length = df[col].astype(str).map(len).max()
        max_lengths[col] = max(header_length, content_length)
    
    # Berechne relative Breiten (Total = 1.0)
    total_length = sum(max_lengths.values())
    col_widths = {col: length/total_length for col, length in max_lengths.items()}
    
    # Erstelle Figure mit dynamischer Höhe
    fig_height = len(df) * 0.25
    fig, ax = plt.subplots(figsize=(15, fig_height))
    ax.axis('tight')
    ax.axis('off')
    
    # Erstelle Tabelle
    table = ax.table(cellText=df.values,
                    colLabels=df.columns,
                    loc='center',
                    cellLoc='left')
    
    # Formatiere Tabelle
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    
    # Wende berechnete Spaltenbreiten an
    for (row, col), cell in table.get_celld().items():
        cell.set_width(col_widths[df.columns[col]])
        cell.PAD = 0.01
        cell.set_text_props(wrap=True)
        if row == 0:  # Kopfzeile
            cell.set_height(0.06)
    
    plt.tight_layout()
    if description:
        plt.figtext(0.5, 0.02, description, wrap=True, horizontalalignment='center', fontsize=10)
    plt.show()

def create_table_figure_pandas(df: pd.DataFrame, description: str = '') -> None:
    """
    Erstellt eine formatierte Tabellenansicht mit Pandas Styler.
    
    Args:
        df: Der zu visualisierende DataFrame
        description: Die Beschreibung unter der Tabelle
    """
    # Erstelle einen Styler mit angepasstem Format und verstecktem Index
    styled_df = df.style\
        .hide(axis='index')\
        .set_properties(**{
            'text-align': 'left',
            'font-size': '10pt',
            'padding': '2px',
            'white-space': 'pre-wrap',
            'border': '1px solid black'
        })\
        .set_caption(description)\
        .set_table_styles([
            {'selector': 'caption', 
             'props': [
                 ('caption-side', 'bottom'),
                 ('font-size', '10pt'),
                 ('text-align', 'center')
             ]},
            {'selector': 'th',
             'props': [
                 ('text-align', 'center'),
                 ('font-weight', 'bold'),
                 ('border', '1px solid black'),
                 ('background-color', '#f2f2f2')
             ]},
            {'selector': 'table',
             'props': [
                 ('border-collapse', 'collapse'),
                 ('border', '1px solid black')
             ]}
        ])
    
    # Zeige die formatierte Tabelle
    display(styled_df)

def create_table_figure(df: pd.DataFrame, description: str = '', use_pandas: bool = False) -> None:
    """
    Erstellt eine Tabellenabbildung aus einem DataFrame.
    
    Args:
        df: Der zu visualisierende DataFrame
        description: Die Beschreibung unter der Abbildung
        use_pandas: Wenn True, wird Pandas Styler verwendet, sonst matplotlib (Standard: False)
    """
    if use_pandas:
        create_table_figure_pandas(df, description)
    else:
        create_table_figure_matplotlib(df, description)