import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
df = pd.read_csv(url)

print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx Początek programu")
# print("Kraje:")
# print(df["location"].unique())

# print()
# print("Kolumny:")
# print(df.columns)

# nazwa __name__ to zmienna środowiskowa
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# potrzebne do heroku
server = app.server

countries_names = {'Germany': "Niemcy",
                   'Italy': "Włochy",
                   'Poland': "Polska",
                   'United Kingdom': "Wielka Brytania",
                  }

print("Klucze słownika countries_names")
labels = list(countries_names.keys())
print(labels)

print()
print("Wartości słownika countries_names")
values = list(countries_names.values())
print(values)

app.layout = html.Div([

    html.H3('Wybierz kraj, aby zobaczyć 3 wykresy dotyczące COVID-19.'),
    html.H5("Po najechaniu myszką wyświetlane są wyniki dla danej daty."),
    html.H5("Aby przybliżyć zaznacz wybrany obszar (powrót to symbol 'domek')."),
    dcc.Tabs(
        id='tabs-countries',
        children=[
            dcc.Tab(label='Polska', value='Poland'),
            dcc.Tab(label='Niemcy', value='Germany'),
            dcc.Tab(label='Włochy', value='Italy'),
            dcc.Tab(label='Wielka Brytania', value='United Kingdom'),
        ],
        value='Poland',
    ),
    # sekcja wynikowa pokazująca wykresy dla wybanego karaju
    html.Div(id='div-result-1'),

    # html.Div([
    #         dcc.Dropdown(
    #             id='dropdown-countries',
    #             options=[{'label': i, 'value': j} for i, j in zip(labels, values)],
    #             value="Poland"
    #         )
    #     ]
    # ),

    # sekcja wynikowa
    # html.Div([
    #     html.Hr(),
    #     html.H4('Wybrany kraj:'),
    #     # tu wyswietli podane parametry
    #     html.Div(id='div-1'),
    #     ], style={'margin': '0 auto', 'textAlign': 'center'}),

    ],   style={
            "color": "darkblue",  # kolor czcionki
            # "fontSize": 18,
            "background-color": "grey",
            "text-align": "center",
            "border": "4px solid Grey",
            # "border-style": "dashed"  # linia przerywana
        }
)

@app.callback(
    Output('div-result-1', 'children'),
    # do funkcji render_content wchodzi angielska nazwa kraju.
    # W domyśle Poland
    [Input('tabs-countries', 'value')]
)
# w zaleznosci od zakladki bedzie inna zawartosc w id='div-result-1"
def render_content(tab):

    print()
    print("---------------------------------------------------------- Funkcja render_content")
    # pokazuje w konsoli ktora zakladke wybralismy
    print("Wybrany kraj jako tab:", tab)

    country_name = tab

    important_columns = ['date',
                         'new_cases',
                         'total_cases',
                         'new_deaths',
                         'total_deaths',
                         'new_vaccinations',
                         'total_vaccinations']

    if tab == country_name:

        # df dla wybranego kraju dla wybranych kolumn
        df_country = df[df["location"] == country_name][important_columns]
        # chcę mieć indeksy od 0
        df_country.reset_index(drop=True, inplace=True)

        print()
        print("Suma braków: " + countries_names[country_name])
        print(df_country.isnull().sum())

        # Zastępuję braki nan w kolumnach new_deaths i total_deaths przez liczbę 0,
        # bo na początku epidemii nikt nie umierał przez 8 dni.
        df_country = df_country.replace(to_replace=np.nan, value=0)

        print()
        print("Już nie ma braków: " + countries_names[country_name])
        print(df_country.isnull().sum())

        # print()
        # print("Przed zamianą typów float na int")
        # print(df_country.info())

        # Zamieniam float64 na int64, żeby na przykład zmiast wartości 4345.0 była 4345"
        columns_to_change_type = ['new_cases',
                                  'total_cases',
                                  'new_deaths',
                                  'total_deaths',
                                  'new_vaccinations',
                                  'total_vaccinations']

        for column in columns_to_change_type:
            df_country[column] = df_country[column].astype("int64")

        # print()
        # print("Po zamianie typów float na int")
        # print(df_country.info())

        print()
        # kolumny z danymi (oprócz daty)
        columns_with_data = ['new_cases', 'total_cases', 'new_deaths', 'total_deaths',
                             'new_vaccinations', 'total_vaccinations']

        first_not_null_dates = []

        for column in columns_with_data:
            not_null_column_dates = df_country[df_country[column] > 0][["date", column]]
            # print(not_null_column_dates)
            first_column_date = not_null_column_dates.iloc[0]["date"]
            # print(first_column_date)
            first_not_null_dates.append(first_column_date)

        first_not_null_dictionary = {columns_with_data[i]: first_not_null_dates[i]
                                     for i in range(len(columns_with_data))}

        first_not_null_df = pd.DataFrame(data=first_not_null_dictionary,
                                         index=["first date with not null value"])

        print()
        print(first_not_null_df)

        print()
        # zamiana Series na ndarray
        first_not_null_case = first_not_null_df["new_cases"].values[0]
        # print(type(first_not_null_case))
        print(countries_names[country_name] + " pierwszy przypadek zachorowania: " + first_not_null_case)

        print()
        first_not_null_death = first_not_null_df["new_deaths"].values[0]
        # print(type(first_not_null_case))
        print(countries_names[country_name] + " pierwszy przypadek śmierci: " + first_not_null_death)

        print()
        first_not_null_vaccination = first_not_null_df["total_vaccinations"].values[0]
        # print(type(first_not_null_case))
        print(countries_names[country_name] + " pierwsza szczepionka: " + first_not_null_vaccination)

        print()
        print("Tyle dziś zachorowało")
        print(df_country.tail(1))
        print()
        print(df_country.tail(1)["new_cases"])
        print()
        print(df_country.tail(1)["new_cases"].values[0])

        print()
        print("Daty dla szczepień")
        dates_vaccinations = df_country.loc[df_country["date"] > "2020-12-19"]["date"].values
        print(dates_vaccinations)

        return html.Div([
            html.H3('Wybrano: ' + countries_names[country_name]),

            # nowe zachorowania i zgony
            dcc.Graph(
                figure={
                    "data": [
                        {
                            "x": df_country["date"],
                            "y": df_country["new_cases"],
                            "type": "line",
                            "marker": {
                                "color": "red"
                            },
                            "name": "Nowe zachorowania"
                        },
                        {
                            "x": df_country["date"],
                            "y": df_country["new_deaths"],
                            "type": "line",
                            "marker": {
                                "color": "black"
                            },
                            "name": "Nowe zgony"
                        }
                    ],
                    'layout': {
                        "title": "Zachorowania i zgony od " + first_not_null_case + "<br>" +
                        "Ostatnia ilość zachorowań: " + str(df_country.tail(1)["new_cases"].values[0]) + "<br>" +
                        "Ostatnia ilość zgonów: " + str(df_country.tail(1)["new_deaths"].values[0]),
                        # po najechaniu jest pionowa przerywana linia
                        "hovermode": "x unified"
                    }
                },
                style={
                    "color": "darkblue",  # kolor czcionki
                    # "fontSize": 18,
                    "background-color": "grey",
                    "text-align": "center",
                    "border": "4px solid Black",
                    # "border-style": "dashed"  # linia przerywana
                }
                # stara wersja, ale nie było widać wszystkich danych po najechaniu myszką
                # figure=go.Figure(
                #     data=[
                #         # pierwszy ślad
                #         go.Bar(
                #             x=df_country["date"],
                #             y=df_country["new_cases"],
                #             name="Nowe zachorowania",  # nazwa z legendy
                #             marker=go.bar.Marker(
                #                 # color="rgb(204, 64, 57)"  # jasny czerwony
                #                 color="red"
                #             )
                #         ),
                #         # drugi ślad
                #         go.Bar(
                #             x=df_country["date"],
                #             y=df_country["new_deaths"],
                #             name="Nowe zgony",  # nazwa z legendy
                #             marker=go.bar.Marker(
                #                 color="black"
                #             )
                #         )
                #     ],
                #     layout=go.Layout(
                #         title="Zachorowania i zgony od " + first_not_null_case + "<br>" +
                #         "Ostatnia ilość zachorowań: " + str(df_country.tail(1)["new_cases"].values[0]) + "<br>" +
                #         "Ostatnia ilość zgonów: " + str(df_country.tail(1)["new_deaths"].values[0]),
                #         showlegend=True
                #     )
                # )
            ),

            # suma zachorowań i zgonów
            dcc.Graph(
                figure={
                    "data": [
                        {
                            "x": df_country["date"],
                            "y": df_country["total_cases"],
                            "type": "bar",
                            "marker": {
                                "color": "rgb(204, 64, 57)"  # jasny czerwony
                            },
                            "name": "Suma zachorowań"
                        },
                        {
                            "x": df_country["date"],
                            "y": df_country["total_deaths"],
                            "type": "bar",
                            "marker": {
                                "color": "black"
                            },
                            "name": "Suma zgonów"
                        }
                    ],
                    'layout': {
                        "title": "Suma zachorowań i zgonów od " + first_not_null_case + "<br>" +
                        "Suma zachorowań: " + str(df_country.tail(1)["total_cases"].values[0]) + "<br>" +
                        "Suma zgonów: " + str(df_country.tail(1)["total_deaths"].values[0]),
                        # po najechaniu jest pionowa przerywana linia
                        "hovermode": "x unified"
                    }
                },
                style={
                    "color": "darkblue",  # kolor czcionki
                    # "fontSize": 18,
                    "background-color": "grey",
                    "text-align": "center",
                    "border": "4px solid Black",
                    # "border-style": "dashed"  # linia przerywana
                }
            ),

            # nowe zaszczepienia i suma zaszczepień
            dcc.Graph(
                figure={
                    "data": [
                        {
                            # "x": df_country["date"],
                            "x": dates_vaccinations,
                            # "y": df_country["new_vaccinations"],
                            "y": df_country.loc[df_country["date"] > "2020-12-19"]["new_vaccinations"].values,
                            "type": "line",
                            "marker":{
                                "color": "green"
                            },
                            "name": "Nowe zaszczepienia"
                        },
                        {
                            # "x": df_country["date"],
                            "x": dates_vaccinations,
                            # "y": df_country["total_vaccinations"],
                            "y": df_country.loc[df_country["date"] > "2020-12-19"]["total_vaccinations"].values,
                            "type": "bar",
                            "name": "Suma zaszczepień"
                        }
                    ],
                    'layout': {
                        "title": "Zaszczepienia od " + first_not_null_vaccination,
                        # po najechaniu jest pionowa przerywana linia
                        "hovermode": "x unified"
                    }
                },
                style={
                    "color": "darkblue",  # kolor czcionki
                    # "fontSize": 18,
                    "background-color": "grey",
                    "text-align": "center",
                    "border": "4px solid Black",
                    # "border-style": "dashed"  # linia przerywana
                }
            ),
        ])

# to do localhost
# if __name__ == "__main__":
#     app.run_server(debug=True)