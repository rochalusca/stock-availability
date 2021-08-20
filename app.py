import streamlit as st
import pandas as pd
import re

st.title('Stock Availability')
st.markdown('Version 0.1, questions or suggestions: <a href="mailto:lucas.rocha@murrelektronik.co.uk">@lucas.rocha</a>', unsafe_allow_html=True)
DATA_PATH = st.file_uploader("Upload the file", type=["txt"],accept_multiple_files=False,)

@st.cache
def get_data():
    columns = {
        'Material': 'artNo',
        'Materialtext': 'description',
        'Conditionvalue': 'listPrice',
        'Storage(Plant1)': 'ukStock',
        'Storage(Plant2)': 'oppStock'
    }
    df = pd.read_csv(DATA_PATH, sep='\t', keep_default_na=False,
                     error_bad_lines=False, encoding='unicode-escape', skipinitialspace=True)
    df.drop(df.columns[df.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
    df.drop(df.columns[df.columns.str.contains('Currency', case=False)], axis=1, inplace=True)
    df.drop(df.columns[df.columns.str.contains('Materialgroup', case=False)], axis=1, inplace=True)
    df.columns = df.columns.str.replace(' ', '')
    df = df.replace({"^\s*|\s*$": ""}, regex=True)
    df = df.replace({"Call for delivery": '0'})
    df = df.replace({"": '0'})
    df = df.rename(columns=columns)
    df['artNo'] = df['artNo'].str.lstrip('0')
    df = df[df['ukStock'].str.isnumeric()]
    df = df[df['oppStock'].str.isnumeric()]
    df[['ukStock']] = df[['ukStock']].astype(int)
    df[['oppStock']] = df[['oppStock']].astype(int)
    return df

def get_eStock(user_qry,df):
  wordlist = df['artNo']
  result = pd.DataFrame({'artNo': [],'description': [],'listPrice': [], 'ukStock': [],'oppStock': []})
  if user_qry:
    for word in wordlist:
        if re.fullmatch(user_qry, word):
            result = df[df['artNo'] == word]

  return result

def get_aStock(user_qry,df):
    wordlist = df['artNo']
    res2 = pd.DataFrame({'artNo': [], 'description': [], 'listPrice': [],'ukStock': [], 'oppStock': []})
    if user_qry:
        user_qry = user_qry.replace('*', ".*")
        for word in wordlist:
            if re.search(user_qry, word):
                res = df[df['artNo'] == word]
                res2 = res2.append(res, ignore_index=True)

        res2[['ukStock']] = res2[['ukStock']].astype(int)
        res2[['oppStock']] = res2[['oppStock']].astype(int)
        res2 = (res2[(res2['oppStock'] > 0) | (res2['ukStock'] > 0) & (res2['artNo'] == user_qry)])
    return res2

if __name__ == '__main__':

    if DATA_PATH == None:
        st.write('No files on cache, please upload the file.')
    else:
        df = get_data()
        user_qry = st.text_input('', 'Insert the part number',max_chars=20)
        if user_qry is not None:
            result = get_eStock(user_qry,df)
            st.dataframe(result.assign(hack='').set_index('hack'))

        if st.checkbox('Show part numbers matches in stock'):
            st.text('be careful, not exact alternatives.')
            matches = get_aStock(user_qry, df)
            st.dataframe(matches.assign(hack='').set_index('hack'))



