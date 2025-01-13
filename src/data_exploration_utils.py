import pandas as pd
import matplotlib.pyplot as plt
import altair as alt


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

def create_stacked_bar_chart(df, id_vars, var_name, value_name, x_axis_title, chart_title):
    """
    Erstellt ein gestapeltes Balkendiagramm aus einem DataFrame.

    Parameter:
    df (pd.DataFrame): Der DataFrame, der die Daten enthält
    id_vars (list): Liste der Spalten, die als Identifikatoren verwendet werden
    var_name (str): Name der Spalte, die die Kategorien enthält
    value_name (str): Name der Spalte, die die Werte enthält
    x_axis_title (str): Titel der x-Achse
    chart_title (str): Titel des Diagramms

    Rückgabewert:
    alt.Chart: Das erstellte gestapelte Balkendiagramm
    """
    
    # Den DataFrame schmelzen, um Motortypen in eine einzelne Spalte zu konvertieren
    df_melted = df.melt(
        id_vars=id_vars, 
        var_name=var_name, 
        value_name=value_name
    )

    # Gestapeltes Balkendiagramm erstellen
    chart = alt.Chart(df_melted).mark_bar().encode(
        x=alt.X(f'{id_vars[0]}:N', axis=alt.Axis(labels=False, title=x_axis_title)),  # Labels aufgrund der großen Anzahl ausblenden
        y=alt.Y(f'{value_name}:Q', stack='zero'),
        color=f'{var_name}:N',
        tooltip=[id_vars[0], var_name, value_name]
    ).properties(
        width=800,
        height=400,
        title=chart_title
    )
    
    return chart