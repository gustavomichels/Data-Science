import streamlit as st
import requests
import pandas as pd
import time

@st.cache_data

def convert_csv(df):
    return df.to_csv(index = False).encode('utf-8')
def success():
    success = st.success('Download Sucess', icon='✅')
    time.sleep(5)
    success.empty()

st.set_page_config(layout = 'wide')

st.title('RAW DATA')

url = 'https://labdados.com/produtos'

response = requests.get(url)
data = pd.DataFrame.from_dict(response.json())
data['Data da Compra'] = pd.to_datetime(data['Data da Compra'], format = '%d/%m/%Y')

with st.expander('Columns'):
    columns = st.multiselect('Select the columns', list(data.columns), list(data.columns))

with st.sidebar.expander('Product Name'):
    products = st.multiselect('Select the product', data['Produto'].unique(), data['Produto'].unique())
with st.sidebar.expander('Product Category'):
    category = st.multiselect('Select the categories', data['Categoria do Produto'].unique(), data['Categoria do Produto'].unique())
with st.sidebar.expander('Product Price'):
    price = st.slider('Select Price', 0, 5000, (0,5000))
with st.sidebar.expander('Sale shipping'):
    portage = st.slider('Shipping', 0,250, (0,250))
with st.sidebar.expander('Buy Date'):
    buy_date = st.date_input('Select date', (data['Data da Compra'].min(), data['Data da Compra'].max()))
with st.sidebar.expander('Seller'):
    sellers = st.multiselect('Select sellers', data['Vendedor'].unique(), data['Vendedor'].unique())
with st.sidebar.expander('Purchase Location'):
    local_buy = st.multiselect('Select purchase location', data['Local da compra'].unique(), data['Local da compra'].unique())
with st.sidebar.expander('Purchase evaluation'):
    rate = st.slider('Select purchase evaluation',1,5, value = (1,5))
with st.sidebar.expander('Payment Type'):
    payment_type = st.multiselect('Select payment type',data['Tipo de pagamento'].unique(), data['Tipo de pagamento'].unique())
with st.sidebar.expander('Number of installments'):
    parcel_qtt = st.slider('Select Number of installments', 1, 24, (1,24))
    
query = '''
Produto in @products and \
`Categoria do Produto` in @category and \
@price[0] <= Preço <= @price[1] and \
@buy_date[0] <= `Data da Compra` <= @buy_date[1] and \
Vendedor in @sellers and \
`Local da compra` in @local_buy and \
@rate[0] <= `Avaliação da compra` <= @rate[1] and \
`Tipo de pagamento` in @payment_type and \
@parcel_qtt[0] <= `Quantidade de parcelas` <= @parcel_qtt[1]

'''

filter_data = data.query(query)
filter_data = filter_data[columns]

st.dataframe(filter_data)

st.markdown(f'A tabela possui :blue[{filter_data.shape[0]}] linhas e :blue[{filter_data.shape[1]}] colunas')

st.markdown('Write a name for the file')

column1, column2 = st.columns(2)
with column1:
    file_name = st.text_input('', label_visibility = 'collapsed', value = 'data')
    file_name += '.csv'
with column2:
    st.download_button('Download File', data = convert_csv(filter_data), file_name = file_name, mime='text/csv', on_click = success)
