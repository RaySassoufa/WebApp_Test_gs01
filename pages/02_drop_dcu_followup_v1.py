import pandas as pd
import streamlit as st

from dateutil import parser
from pathlib import Path

from google.oauth2 import service_account

from app import DCU


###########################################
#### ---- Drop DC FollowUP ---- ###########
###########################################
st.header("Drop DC Followup")
st.sidebar.markdown("# Drop DCU FollowUp")

spreadsheet_id = "1aSTIe5g76mqwh6MhrXW_Mqef7vzIPLLwOTeqpqXwaOU"
sheet_name = "drop_table"
gsheet_url = "https://docs.google.com/spreadsheets/d/1aSTIe5g76mqwh6MhrXW_Mqef7vzIPLLwOTeqpqXwaOU/edit#gid=0"
# gsheet_url_for_read_as_csv = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
service_account_credential = st.secrets["gcp_service_account"]  # return a dict

credentials = service_account.Credentials.from_service_account_info(
    service_account_credential, scopes=["https://www.googleapis.com/auth/spreadsheets"])

df_dc_drop_info = pd.read_excel("pages/drop_dc.xlsx").astype(str)
df_dc_drop_info["DCU"] = df_dc_drop_info["DCU"].apply(lambda x: "SAG099000000" + x[0:4])
df_dc_drop_info["Identification_Date"] = df_dc_drop_info["Identification_Date"].apply(lambda x: "not defined" if x == 'nan' else parser.parse(x).date())

btn_import_excel_into_gs_db = 999
import pygsheets
gc_pygsheets = pygsheets.authorize(custom_credentials=credentials)
sh_pygsheets = gc_pygsheets.open_by_key(spreadsheet_id)

def write_to_gsheet(sheet_name, data_df):
    try:
        sh_pygsheets.add_worksheet(sheet_name)
    except:
        pass
    wks = sh_pygsheets.worksheet_by_title(sheet_name)
    wks.clear(start='A1', end=None, fields='*')
    wks.set_dataframe(data_df, (1, 1))
    wks.frozen_rows = 1
    wks.frozen_cols = 2

    return len(wks.get_col(1, include_tailing_empty=False))

##### !!! Populate df_dc_drop_info dans drop_table du google sheet DB !!!!!!
if btn_import_excel_into_gs_db == 0:
    NB_ROWS = write_to_gsheet(sheet_name, df_dc_drop_info)
    st.markdown("The drop_dc is populated in DB/drop_table")
else:
    st.markdown("Existing drop_table in the Data Base")

# df_pygsheets = sh_pygsheets.worksheet_by_title("new_test_pygsheet").get_as_df(has_header=True, index_column=None, numerize=True, empty_value='')
###########################################
####### Section for gsheet ###########
###########################################

import gspread as gs
from gspread_dataframe import get_as_dataframe, set_with_dataframe

gc = gs.service_account_from_dict(service_account_credential)
sh = gc.open_by_url(gsheet_url)
ws = sh.worksheet(sheet_name)

st.markdown("drop_table")

fig_02 = st.empty()

# @st.cache(ttl=600)
def vue_drop_table():
    df_drop_table = get_as_dataframe(ws)
    fig_02.dataframe(df_drop_table.astype(str))

    return df_drop_table


df_drop_table = vue_drop_table()

#################################################
######### DCU INFO FORM #########################
#################################################
st.write("_" * 100)
st.subheader("\n" + "Insert DCU Info & Analysis in the Drop DCU Table :")
dc = st.selectbox('Select the concerned DCU:', DCU[1:])

def add_data(list_to_insert):
    ws.insert_row(values=list_to_insert, index=2, value_input_option="USER_ENTERED")
    st.success("Successfully Submitted")
    df_drop_table = vue_drop_table()

def update_data(dc, list_to_update):
    cell_dc = ws.find(dc)
    for i in range(0, len(list_to_update)):
        ws.update_cell(cell_dc.row, i+1, list_to_update[i])

    st.success("Successfully Submitted")
    df_drop_table = vue_drop_table()

def dcu_info_form():
    with st.form(key="Information form"):
        # with col1:
        date_info = st.date_input("Date of Update :")
        if dc in df_drop_table['DCU'].tolist():
            injection = st.text_input("Phase Injection :", value=f"{df_drop_table[df_drop_table['DCU'] == dc]['Injection'].item()}")
            discovered = st.text_input("Nb Discovered meters :", f"{df_drop_table[df_drop_table['DCU'] == dc]['Discovered_Meters'].item()}")
            dropped = st.text_input("Nb Dropped meters :", f"{df_drop_table[df_drop_table['DCU'] == dc]['Dropped_Meters'].item()}")
        else:
            injection = st.text_input("Phase Injection :")
            discovered = st.text_input("Nb Discovered meters :")
            dropped = st.text_input("Nb Dropped meters :")

        # with col2:
        if dc in df_drop_table['DCU'].tolist():
            meter_status = st.text_area("Meters Status WebGui :", f"{df_drop_table[df_drop_table['DCU'] == dc]['Meter_Status_WebGui'].item()}")
            cause = st.text_area("Cause of Drop :", f"{df_drop_table[df_drop_table['DCU'] == dc]['Cause'].item()}")
            action = st.text_area("Historique des Actions effectuée :", f"{df_drop_table[df_drop_table['DCU'] == dc]['Action'].item()}")
        else:
            meter_status = st.text_area("Meters Status WebGui :")
            cause = st.text_area("Cause of Drop :")
            action = st.text_area("Historique des Actions effectuée :")

        # with col3:
        if dc in df_drop_table['DCU'].tolist():
            replacement = st.text_input("if DCU replaced, indicate the new :", f"{df_drop_table[df_drop_table['DCU'] == dc]['DCU_Replacement'].item()}")
            sdcu = st.text_input("Related SDCU in the site :", f"{df_drop_table[df_drop_table['DCU'] == dc]['Related_SDCU'].item()}")
            status = st.text_input("Solved/Monitoring/To escalate :", f"{df_drop_table[df_drop_table['DCU'] == dc]['Status'].item()}")
            effectiveness = st.text_input("Effectiveness of Actions :", f"{df_drop_table[df_drop_table['DCU'] == dc]['Effectiveness_of_Remote_Actions'].item()}")
        else:
            replacement = st.text_input("if DCU replaced, indicate the new :")
            sdcu = st.text_input("Related SDCU in the site :")
            status = st.text_input("Solved/Monitoring/To escalate :")
            effectiveness = st.text_input("Effectiveness of Actions :")

        submission = st.form_submit_button("Submit your Changes !")

        if submission:
            if dc not in df_drop_table["DCU"].tolist():
                st.write("DC not in the drop_table and will be added to the database !")
                list_to_insert = [str(date_info), dc, injection, discovered, dropped, meter_status, cause, action, replacement, sdcu, status, effectiveness]
                add_data(list_to_insert)

            else:
                st.write("DC already in the drop_table and will be updated in the database !")
                list_to_update = [str(date_info), dc, injection, discovered, dropped, meter_status, cause, action, replacement, sdcu, status, effectiveness]
                update_data(dc, list_to_update)


dcu_info_form()