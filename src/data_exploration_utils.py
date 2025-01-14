import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
from typing import List, Optional


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

def create_distribution_plot(df: pd.DataFrame, column_name: str, observation_label: str, 
                           xmin: float = None, xmax: float = None, width: int = 400) -> alt.VConcatChart:
    """
    Erstellt eine kombinierte Visualisierung aus Histogramm und Boxplot.
    
    Args:
    df (pd.DataFrame): DataFrame mit den zu visualisierenden Daten
    column_name (str): Name der zu visualisierenden Spalte
    observation_label (str): Bezeichnung der beobachteten Einheiten (z.B. "Landkreise", "Städte")
    xmin (float, optional): Minimumwert der x-Achse. Bei None wird Auto-Skalierung verwendet
    xmax (float, optional): Maximumwert der x-Achse. Bei None wird Auto-Skalierung verwendet
    width (int): Breite der Diagramme in Pixeln
    
    Returns:
        alt.VConcatChart: Kombiniertes Diagramm aus Histogramm und Boxplot
    """
    if column_name not in df.columns:
        raise ValueError(f"Spalte {column_name} nicht im DataFrame gefunden")
    
    if xmin is None:
        xmin = df[column_name].min()
    if xmax is None:
        xmax = df[column_name].max()
    
    histogram = alt.Chart(df).mark_bar().encode(
        x=alt.X(f'{column_name}:Q',
                bin=alt.Bin(maxbins=30),
                title='',
                axis=alt.Axis(grid=True),
                scale=alt.Scale(domain=[xmin, xmax])),
        y=alt.Y('count():Q',
                title=f'Anzahl {observation_label}')
    ).properties(
        width=width,
        height=200
    )

    boxplot = alt.Chart(df).mark_boxplot(
        median={'color': 'white'},
        color='#57A44C'
    ).encode(
        x=alt.X(f'{column_name}:Q',
                title=f'{column_name} (%)',
                axis=alt.Axis(grid=True),
                scale=alt.Scale(domain=[xmin, xmax]))
    ).properties(
        width=width,
        height=50
    )

    combined_chart = alt.vconcat(histogram, boxplot).properties(
        title={
            'text': f'Verteilung der {column_name} nach {observation_label}',
            'anchor': 'middle',
            'fontSize': 16
        }
    )
    
    return combined_chart

def create_density_plot(df: pd.DataFrame, column_name: str, observation_label: str, 
                       xmin: float = None, xmax: float = None, width: int = 400) -> alt.Chart:
    """
    Erstellt eine Visualisierung der Dichteverteilung (KDE-Plot).
    
    Args:
        df: DataFrame mit den zu visualisierenden Daten
        column_name: Name der zu visualisierenden Spalte
        observation_label: Bezeichnung der beobachteten Einheiten (z.B. "Landkreise", "Städte")
        xmin: Minimumwert der x-Achse. Bei None wird Auto-Skalierung verwendet
        xmax: Maximumwert der x-Achse. Bei None wird Auto-Skalierung verwendet
        width: Breite des Diagramms in Pixeln
    
    Returns:
        alt.Chart: Dichteverteilungsdiagramm
    """
    if column_name not in df.columns:
        raise ValueError(f"Spalte {column_name} nicht im DataFrame gefunden")
    
    if xmin is None:
        xmin = df[column_name].min()
    if xmax is None:
        xmax = df[column_name].max()
    
    density_plot = alt.Chart(df).transform_density(
        column_name,
        as_=[column_name, 'density']
    ).mark_area(
        opacity=0.7,
        color='#57A44C'
    ).encode(
        x=alt.X(f'{column_name}:Q',
                title=f'{observation_label}',
                scale=alt.Scale(domain=[xmin, xmax])),
        y=alt.Y('density:Q',
                title='Wahrscheinlichkeitsdichte'),
        tooltip=[
            alt.Tooltip(f'{column_name}:Q', title=observation_label, format='.1f'),
            alt.Tooltip('density:Q', title='Dichte', format='.4f')
        ]
    ).properties(
        width=width,
        height=300,
        title=f'Dichteverteilung der {observation_label}'
    )
    
    return density_plot

def create_scatterplot_grid(df: pd.DataFrame, 
                          list_row: Optional[List[str]] = None, 
                          list_col: Optional[List[str]] = None, 
                          width: int = 150, 
                          height: int = 150) -> alt.Chart:
    """
    Erstellt ein Raster von Streudiagrammen für die angegebenen Spalten eines DataFrames.
    Diese Funktion generiert ein Grid von Streudiagrammen unter Verwendung von Altair, 
    wobei jedes Diagramm die Beziehung zwischen zwei Variablen darstellt.

    Args:
        df: Der DataFrame, der die zu plottenden Daten enthält
        list_row: Liste der Spaltennamen für die Y-Achsen. 
                 Wenn None, werden alle Spalten des DataFrames verwendet
        list_col: Liste der Spaltennamen für die X-Achsen.
                 Wenn None, werden alle Spalten des DataFrames verwendet
        width: Breite jedes einzelnen Plots in Pixeln (Standard: 150)
        height: Höhe jedes einzelnen Plots in Pixeln (Standard: 150)

    Returns:
        Ein Altair-Chart-Objekt, das das Raster von Streudiagrammen darstellt

    Beispiel:
        >>> df = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
        >>> chart = create_scatterplot_grid(df)
        >>> chart.save('scatterplot_grid.html')
    """
    # Standardmäßig alle Spaltennamen verwenden, wenn keine Listen angegeben sind
    if list_row is None:
        list_row = df.columns.tolist()
    if list_col is None:
        list_col = df.columns.tolist()
    
    chart = alt.Chart(df).mark_circle().encode(
        x=alt.X(alt.repeat("column"),
                type='quantitative',
                scale=alt.Scale(zero=False)
                ),
        y=alt.Y(alt.repeat("row"),
                type='quantitative',
                scale=alt.Scale(zero=False)
                )
    ).properties(
        width=width,
        height=height
    ).repeat(
        row=list_row,
        column=list_col
    )
    return chart

def plot_regression_and_residuals(X, y):
    plots = []
    for feature in X.columns:
        # Berechne Steigung und Achsenabschnitt für einfache lineare Regression
        X_feature = X[[feature]]
        slope = np.cov(X_feature[feature], y)[0,1] / np.var(X_feature[feature])
        intercept = y.mean() - slope * X_feature[feature].mean()
        y_pred = intercept + slope * X_feature[feature]
        
        # Erstelle DataFrame für beide Plots
        df_plot = pd.DataFrame({
            feature: X_feature[feature],
            'y': y,
            'y_pred': y_pred,
            'residuals': y - y_pred
        })
        
        # Scatterplot mit Regressionsgerade
        base_scatter = alt.Chart(df_plot).encode(
            x=alt.X(feature, title=None)
        )
        
        scatter = base_scatter.mark_point().encode(
            y=alt.Y('y', title='y')
        ) + base_scatter.mark_line(color='red').encode(
            y=alt.Y('y_pred', title='y_pred')
        ).properties(
            height=200
        )
        
        # Geradengleichung als Text - mit verbesserter Darstellung für negative Steigung
        equation_text = f'y = {intercept:.2f} {"+" if slope >= 0 else "-"} {abs(slope):.2f} * x'
        text = alt.Chart(pd.DataFrame({
            feature: [X_feature[feature].min() + (X_feature[feature].max() - X_feature[feature].min()) * 0.1],
            'y': [y.max() - (y.max() - y.min()) * 0.1],
            'text': [equation_text]
        })).mark_text(align='left', baseline='top').encode(
            x=feature,
            y='y',
            text='text'
        )
        
        scatter = scatter + text
        
        # Residuenplot
        base_residual = alt.Chart(df_plot).encode(
            x=alt.X(feature, title=feature)
        )
        
        residual_plot = base_residual.mark_point().encode(
            y=alt.Y('residuals', title='Residuen')
        ).properties(
            height=75
        )
        
        # Kombiniere Plots vertikal mit gemeinsamer x-Achse
        combined_plot = alt.vconcat(scatter, residual_plot).resolve_scale(
            x='shared'
        )
        plots.append(combined_plot)
    
    # Anordnung der Plots in einem Raster mit 3 Spalten
    rows = []
    for i in range(0, len(plots), 3):
        row = alt.hconcat(*plots[i:i+3])
        rows.append(row)
    
    return alt.vconcat(*rows)