import streamlit as st

import pandas as pd
import numpy as np
import altair as alt

st.title("Análisis Tweets de aerolíneas de USA")
st.header("Fuente de información")
st.write(
    """
    Un trabajo de análisis de sentimientos sobre los problemas de cada una de las principales aerolíneas estadounidenses. 
    Los datos de Twitter se extrajeron de febrero de 2015 y se les pidió a los contribuyentes que primero clasificaran los
     tweets positivos, negativos y neutrales, y luego clasificaran las razones negativas (como "vuelo tardío" o "servicio 
     grosero"). 
    
    """
)

st.write("https://www.kaggle.com/crowdflower/twitter-airline-sentiment")


df = pd.read_csv("datos/Tweets.csv", sep=",", encoding="latin1")

st.dataframe(df.iloc[:20])


st.header("Análisis de datos")

#-----------------------------------------------------------------------------------------------------------------------

st.subheader("Cantidad de tweets por sentimientos")

source = pd.DataFrame({
    'clases':['negative', 'neutral', 'positive'],
    'tweets': list(df["airline_sentiment"].value_counts())
})
plot1 = alt.Chart(source).mark_bar().encode(

    x=alt.X('clases',axis=alt.Axis(
                                    labelAngle=0,
                                    )),
    y='tweets',
    tooltip=[
        alt.Tooltip('tweets:Q', title="Total tweets"),
    ]
).properties(
    width=400,
    height=300
)

st.altair_chart(plot1)

#-----------------------------------------------------------------------------------------------------------------------
st.subheader("Cantidad total de tweets por aerolíneas")

aerolineas = df["airline"].value_counts()
source = pd.DataFrame({
    'aerolineas':aerolineas.index,
    'tweets': aerolineas.values
})
plot2 = alt.Chart(source).mark_bar().encode(

    x=alt.X('aerolineas',axis=alt.Axis(
                                    labelAngle=-45,
                                    )),
    y='tweets',
    tooltip=[
        alt.Tooltip('tweets:Q', title="Total tweets"),
    ]
).properties(
    width=400,
    height=300
)

st.altair_chart(plot2)

#-----------------------------------------------------------------------------------------------------------------------
st.subheader("Tweets de sentimiento por aerolíneas")

df_filter = df[["airline_sentiment", "airline"]]
# agrupacion de sentiment por aerolineas
serie = df_filter.groupby(["airline","airline_sentiment"])["airline"].count()
df_airline_sent = pd.DataFrame(columns=["airline", "sentiment", "cantidad"])
for air, atr in serie.index:
    df_airline_sent.loc[df_airline_sent.shape[0]] = {
        "airline": air,
        "sentiment": atr,
        "cantidad": serie[air][atr],
    }

gp_chart = alt.Chart(df_airline_sent).mark_bar().encode(
  alt.Column('airline'),
  alt.X('sentiment', axis=alt.Axis(
                                    labelAngle=-45,
                                    )),
  alt.Y('cantidad', axis=alt.Axis(grid=False)),
  alt.Color('airline'),
    tooltip=[
      alt.Tooltip('cantidad:Q', title="Total tweets"),
  ]
)

st.altair_chart(gp_chart)

#-----------------------------------------------------------------------------------------------------------------------
st.subheader("Cantidad de incidencias en total")

st.write("los tweets negativos están categorizados en diferentes incidencias.")

incidencias = df["negativereason"].value_counts()
source = pd.DataFrame({
    'incidencias':incidencias.index,
    'tweets': incidencias.values
})
plot4 = alt.Chart(source).mark_bar().encode(

    x=alt.X('incidencias',axis=alt.Axis(
                                    labelAngle=-45,
                                    )),
    y='tweets',
    tooltip=[
        alt.Tooltip('tweets:Q', title="Total tweets"),
    ]
).properties(
    width=400,
    height=300
)

st.altair_chart(plot4)

#-----------------------------------------------------------------------------------------------------------------------
st.subheader("Porcentaje de Incidencias por empresa")

st.write("""
Todas las empresas parecen tener la misma proporción de incidencias excepto Delta y United que tiene más incidencias con
 vuelos atrasados que las otra aerolíneas.
""")

df_filter = df[["negativereason", "airline"]]
serie = df_filter.groupby(["airline","negativereason"])["airline"].count()
df_airline_reason = pd.DataFrame(columns=["airline", "negativereason", "cantidad"])
for air, atr in serie.index:
    valor = np.round((serie[air][atr]/serie[air].sum())*100,1)
    df_airline_reason.loc[df_airline_reason.shape[0]] = {
        "airline": air,
        "negativereason": atr,
        "cantidad": valor,
    }

plo5 = alt.Chart(df_airline_reason).mark_rect().encode(
    x='airline:O',
    y='negativereason:O',
    tooltip=[
        alt.Tooltip('cantidad:Q', title="% issue"),
    ],
    color='cantidad:Q'
).properties(
    width=500,
    height=400
)

st.altair_chart(plo5)


#-----------------------------------------------------------------------------------------------------------------------
st.subheader("Linea de tiempo de los tweets durante los 7 dias")
st.write("""
Buscando por Google con este simple comando de fechas “delayed flights after:2015-02-22 before:2015-02-24” encontré 
artículos que mencionan tormentas que obligaron a cancelar vuelos.
""")
st.write("[noticia vuelos cancelados](https://www.usatoday.com/story/todayinthesky/2015/02/23/airlines-cancel-1250-flights-as-yet-another-storm-hits-dfw-dallas-texas/23873767/)")
df["tweet_created"] = df["tweet_created"].astype("datetime64[ns]")
#crear un dataframe para poder crear un grupo
df_fecha = pd.DataFrame()
df_fecha["year"] = df["tweet_created"].dt.year
df_fecha["month"] = df["tweet_created"].dt.month
df_fecha["day"] = df["tweet_created"].dt.day
df_fecha["hour"] = df["tweet_created"].dt.hour

#agrupando por hora los tweets
#airline after:2015-02-24 before:2015-02-17
grupo_hora = df_fecha.groupby(["year", "month", "day", "hour"])

# contar los tweets por hora
serie_tiempo = grupo_hora["hour"].count()

df_x_time = serie_tiempo.index.to_frame(index=None)
df_fecha_tweets = pd.DataFrame()
df_fecha_tweets["fecha"] = pd.to_datetime(df_x_time)
df_fecha_tweets["cantidad"] = serie_tiempo.values

plot6 = alt.Chart(df_fecha_tweets).mark_line().encode(
    x='fecha:T',
    y='cantidad:Q'
).properties(
    width=600,
    height=300
)

st.altair_chart(plot6)


#-----------------------------------------------------------------------------------------------------------------------

st.subheader("Linea de tiempo de todos los tweets de un dia")

df_fecha1=df_fecha[["year", "month", "day"]]
df_fecha1 = df_fecha1.drop_duplicates()
df_fecha1=df_fecha1.sort_values(by='day')
df_fecha1=pd.to_datetime(df_fecha1)


option = st.selectbox(
     'Selecciona una fecha',
     df_fecha1)

st.write('Fecha 1:', option)

dia_despues = pd.to_datetime(option) + pd.DateOffset(days=1)
st.write('Fecha 2:', dia_despues)


dia = df_fecha_tweets[(df_fecha_tweets["fecha"] > option) &
                      (df_fecha_tweets["fecha"] < dia_despues) ]
plot7=alt.Chart(dia).mark_line().encode(
    x='fecha:T',
    y='cantidad:Q'
).properties(
    width=600,
    height=300
)

st.altair_chart(plot7)

#-----------------------------------------------------------------------------------------------------------------------
st.subheader("Línea de tiempo de todos los tweets agrupados por sentimiento")

df_fecha_sent = df_fecha
df_fecha_sent["sentiment"] = df["airline_sentiment"]
grupo_hora_sent = df_fecha_sent.groupby(["year", "month", "day", "hour", "sentiment"])
serie_tiempo = grupo_hora_sent["sentiment"].count()

df_x_time = serie_tiempo.index.to_frame(index=None)

df_fecha_tweets_sent = pd.DataFrame()
df_fecha_tweets_sent["sentiment"] = df_x_time["sentiment"]
df_fecha_tweets_sent["fecha"] = pd.to_datetime(df_x_time[["year","month","day", "hour"]])
df_fecha_tweets_sent["cantidad"] = serie_tiempo.values

plot8 = alt.Chart(df_fecha_tweets_sent).mark_line().encode(
    x='fecha:T',
    y='cantidad:Q',
    color='sentiment:N'
).properties(
    width=800,
    height=300
)
st.altair_chart(plot8)
#-----------------------------------------------------------------------------------------------------------------------
st.subheader("Línea de tiempo de todos los tweets agrupados por sentimiento de un dia")

option1 = st.selectbox(
     'Selecciona una fecha',
     df_fecha1, key="dia_agrupado")

st.write('Fecha 1:', option1)

dia_despues1 = pd.to_datetime(option1) + pd.DateOffset(days=1)
st.write('Fecha 2:', dia_despues1)


dia1 = df_fecha_tweets_sent[(df_fecha_tweets_sent["fecha"] > option1) &
                      (df_fecha_tweets_sent["fecha"] < dia_despues1) ]
plot9=alt.Chart(dia1).mark_line().encode(
    x='fecha:T',
    y='cantidad:Q',
    color='sentiment:N'
).properties(
    width=800,
    height=300
)

st.altair_chart(plot9)

#-----------------------------------------------------------------------------------------------------------------------
st.subheader("Promedio las incidencias de los 7 días en una franja de 24 horas.")
st.write("""
El propósito de la gráfica es mostrar si alguna incidencia aumentaba en un horario distinto a otra, pero al parecer todas
 aumentan y decaen en el mismo horario.
""")

df_hora_reason = df_fecha[["hour"]]
df_hora_reason["negativereason"] = df["negativereason"]
df_hora_reason = df_hora_reason[df["airline_sentiment"] == "negative"]

grupo_hora_reason = df_hora_reason.groupby(["hour", "negativereason"])
serie_tiempo = grupo_hora_reason["hour"].count()
serie_tiempo= serie_tiempo/7 # 7 dias de muestreo

df_x_time = serie_tiempo.index.to_frame(index=None)

df_fecha_tweets_reason = pd.DataFrame()
df_fecha_tweets_reason["negativereason"] = df_x_time["negativereason"]
df_fecha_tweets_reason["hora"] = df_x_time["hour"]
df_fecha_tweets_reason["cantidad"] = serie_tiempo.values

plot10 = alt.Chart(df_fecha_tweets_reason).mark_line().encode(
    x='hora',
    y='cantidad:Q',
    color='negativereason:N',
    tooltip=[
        alt.Tooltip('cantidad:Q', title="issue"),
    ]
).properties(
    width=800,
    height=300
)

st.altair_chart(plot10)

#-----------------------------------------------------------------------------------------------------------------------
st.subheader("Mapa de calor")
st.write("Cantidad de tweets por cada estado")

from vega_datasets import data as vega_data

pop = vega_data.population_engineers_hurricanes()
pop = pop.drop(['population', 'engineers', 'hurricanes'], axis=1)
#Dataset de ciudades y estados
bp_data = pd.read_csv("datos/us_cities_states_counties.csv", sep="|")
#eliminando columnas innecesarias
bp_data = bp_data.drop(['County', 'City alias'], axis=1)
#eliminando filas repetidas
bp_data = bp_data.drop_duplicates()
#eliminando filas en nulos
bp_data=bp_data[bp_data["City"].notna()]

ruta_csv = "datos/extraccion_estados.csv"
df_cities = pd.read_csv(ruta_csv)

#agrupacion por estado
states_issue = df_cities.groupby("state").aggregate(
    cantidad = ("cantidad", sum)
)
states_issue = states_issue.reset_index()

#Join entre el dataset de huracanes y el dataset creado con las cantidad de tweet
states_issue_merge = pd.merge(states_issue,pop,on='state')
states_issue_merge=states_issue_merge.sort_values(by='cantidad', ascending=False)
states = alt.topo_feature(vega_data.us_10m.url, 'states')

plot_map = alt.Chart(states).mark_geoshape().encode(
    color='cantidad:Q',
    tooltip=[
        alt.Tooltip('state:O'),
        alt.Tooltip('cantidad:Q', title="tweets"),
    ],
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(states_issue_merge, 'id',
                         ["state","cantidad"])
).properties(
    width=500,
    height=300
).project(
    type='albersUsa'
)


st.altair_chart(plot_map)

st.dataframe(states_issue_merge[["state", "cantidad"]])
#-----------------------------------------------------------------------------------------------------------------------
st.subheader("Cantidad de incidencias por estado")
st.write("""
Primero se elige un tipo de incidencia e inmediatamente se agrupan los datos  por aerolínea y finalmente se cuenta las 
incidencias por cada estado.
""")
incidencias = df["negativereason"].unique()[1:]
option5 = st.selectbox(
     'Selecciona una incidencia',
     incidencias)

#seleccionando las columnas relevantes
df_localidad = df[["negativereason", "airline", "tweet_location"]]
#renombrando la columna para hacer el join por el mismo nombre
df_localidad=df_localidad.rename(columns={'tweet_location': 'localidad'})
#join de los dataframe
df_state_reason = pd.merge(df_localidad,df_cities[["localidad","state"]],on='localidad')
#eliminando la columna que solo servia de puente
df_state_reason=df_state_reason.drop(['localidad'], axis=1)
#eliminando los tweets que no son negativos
df_state_reason.dropna(subset = ["negativereason"], inplace=True)
df_state_reason= pd.merge(df_state_reason,pop,on='state')

#filtrando el dataframe por la incidencia a graficar
group_issue_state = df_state_reason[df_state_reason["negativereason"] == option5]
#quitando la columna negativereason
group_issue_state = group_issue_state[["airline", "state", "id"]]
#agrupando por aerolinea y contado los tweets
serie = group_issue_state.groupby(["airline", "state", "id"]).size()
df_aux = serie.index.to_frame(index=None)
df_aux["cantidad"] = serie.values

lista_aerolineas = df_aux["airline"].unique()
df_sta_aero = pd.DataFrame(columns=["airline", "state", "id"])
for aero in lista_aerolineas:
    for i_state in range(pop.shape[0]):
        state = pop.iloc[i_state]["state"]
        id_ = pop.iloc[i_state]["id"]
        df_sta_aero.loc[df_sta_aero.shape[0]] = {"airline": aero,
                                                 "state": state,
                                                 "id": id_}

df_all_state_air = pd.merge(df_aux, df_sta_aero, on=['airline', 'state', 'id'], how='outer')
df_all_state_air["id"] = df_all_state_air["id"].astype(int)
df_all_state_air["cantidad"] = df_all_state_air["cantidad"].fillna(value=0)

plot22 = alt.Chart(df_all_state_air).mark_geoshape().encode(
    shape='geo:G',
    color='cantidad:Q',
    tooltip=['state:N', 'cantidad:Q'],
    facet=alt.Facet('airline:N', columns=2),
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(data=states, key='id'),
    as_='geo'
).properties(
    width=300,
    height=175,
).project(
    type='albersUsa'
)


st.altair_chart(plot22)

#-----------------------------------------------------------------------------------------------------------------------
st.subheader("Cantidad de tweets por sentimientos")

st.altair_chart(plot1)