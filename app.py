import pandas as pd
import streamlit as st
import plotly.express as px

from datetime import date, datetime
from dateutil import parser

st.set_page_config(page_title='Dashboard Version beta', layout="wide", )
st.header('Performance Overview Version beta - gdb')
st.sidebar.markdown("# Global Overview")

#########################################################
############## INSTALLED DCU STATUS #####################
#########################################################
excel_file = 'plc_to_st.xlsx'
sheet_name = 'Sheet1'

df = pd.read_excel(excel_file, sheet_name=sheet_name)
del df["Unnamed: 0"]
df.rename(columns={"Collector/DCU": "DCU", "Meter ID": "Nb Meter"}, inplace=True)

st.subheader(f'Installed DCU Status on {df.columns[-1]}')
st.dataframe(df.iloc[:, :-1].astype(str), width=1000)

#######################################################################
######### OFFICIAL PERF CALCULATION TABLE #############################
#######################################################################
df_rw_ww_t = pd.read_excel("df_rw_ww_transposed.xlsx", engine="openpyxl", parse_dates=True, dtype=str)
df_rw_ww_t.set_index("Unnamed: 0", inplace=True)
del df_rw_ww_t["Total Collectable"]

st.subheader('Official Performance Calculation')
st.dataframe(df_rw_ww_t, width=2000)
# st.line_chart(df_rw_ww_t["Performance"])

#######################################################################
######### KPI RW/WW CHART #############################################
#######################################################################
df_fig = df_rw_ww_t.reset_index().rename(columns={"Unnamed: 0": "Date"})
df_fig["Date"] = df_fig["Date"].astype(str).apply(lambda x: parser.parse(x).date()).apply(lambda x: x.strftime("%d %b"))
df_fig["Performance"] = df_fig["Performance"].astype(str).apply(lambda x: x[:-1]).astype(float)

fig = px.line(df_fig, x="Date", y="Performance", title='KPI', markers=True, text="Performance")
fig.update_xaxes(visible=True, fixedrange=False)
fig.update_layout(
    showlegend=True,
    plot_bgcolor="silver",
    font_family="Courier New",
    font_color="black",
    title_font_family="Times New Roman",
    title_font_color="blue",
    legend_title_font_color="green")
fig.update_traces(textposition="bottom center")
st.plotly_chart(fig)

############## DCU STATUS BASED ON SELECTION ##########
#######################################################
DCU = df['DCU'].unique().tolist()

dc_selection = st.multiselect('Select a DCU:', DCU)
mask = df["DCU"].isin(dc_selection)
number_of_result = df[mask].shape[0]
# st.markdown(f'*Available Results: {number_of_result}*')

# --- GROUP DATAFRAME AFTER SELECTION
df_grouped = df[mask].groupby("DCU").agg("sum")
df_grouped = df_grouped.reset_index()[["DCU", "Nb Meter"]]

df_selection = df[mask][["DCU", "Marker", "Nb Meter"]]
bar_chart = px.bar(df_selection,
                   x='DCU',
                   y='Nb Meter',
                   color="Marker",
                   text='Marker',
                   text_auto=True,
                   title=f"Selected DCU Status on {df.columns[-1]}")

st.plotly_chart(bar_chart)
fig_01 = st.dataframe(df_grouped, width=2000)

################## SELECTED DCU PERF #######################
############################################################
df_kpi_dc = pd.read_excel("st_df_kpi_dc.xlsx")

st.subheader("Selected DCU Performance :")
duration_selection = st.slider('Days', min_value=5, max_value=90)

df_kpi_dc_selected_col = ["DCU", "Info"] + [col for col in df_kpi_dc.columns[-duration_selection - 2:-2]]
df_kpi_dc_selected = df_kpi_dc[df_kpi_dc["DCU"].isin(dc_selection)][df_kpi_dc_selected_col].set_index("DCU")
st.dataframe(df_kpi_dc_selected.iloc[:, :-1])

df_chart_kpi_dc = df_kpi_dc_selected.drop("Info", axis=1).T.reset_index().rename(columns={"index": "Date"})

for col in df_chart_kpi_dc.columns[1:]:
    fig_kpi_dc = px.line(df_chart_kpi_dc, x="Date", y=f"{col}", title=f"{col}", markers=True, text=f"{col}")
    fig_kpi_dc.update_xaxes(visible=True, fixedrange=False)
    fig_kpi_dc.update_layout(
        showlegend=True,
        plot_bgcolor="silver",
        font_family="Courier New",
        font_color="black",
        title_font_family="Times New Roman",
        title_font_color="blue",
        legend_title_font_color="green")
    fig_kpi_dc.update_traces(textposition="bottom center")
    st.plotly_chart(fig_kpi_dc)
