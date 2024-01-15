import streamlit as st
import requests
import pandas as pd
import plotly.express as px


st.set_page_config(layout = 'wide')

def format_number (value, prefix = ''):
    for unity in ['','mil']:
        if value < 1000:
            return f'{prefix}{value:.2f}{unity}'
        value /= 1000
    return f'{prefix}{value:.2f} milhões'

st.title('SALES DASHBOARD :shopping_trolley:')

url = 'https://labdados.com/produtos'

regions = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
region = st.sidebar.selectbox('Region', regions)

if region == 'Brasil':
    region = ''
    
all_years = st.sidebar.checkbox('Dados de todo o período', value = True)

if all_years:
    year = ''
else:
    year = st.sidebar.slider('Year', 2020, 2023)
    
    
query_string = {'regiao':region.lower(), 'ano':year}
response = requests.get(url, params= query_string)

data = pd.DataFrame.from_dict(response.json())

data['Data da Compra'] = pd.to_datetime(data['Data da Compra'], format='%d/%m/%Y')

sellers_filter = st.sidebar.multiselect('Sellers', data['Vendedor'].unique())
if sellers_filter:
    data = data[data['Vendedor'].isin(sellers_filter)]
    

# Tables


## Revenue tables
revenue_states = data.groupby('Local da compra')[['Preço']].sum()
revenue_states = data.drop_duplicates(subset='Local da compra')[['Local da compra','lat','lon']].merge(revenue_states, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

revenue_month = data.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
revenue_month['Year'] = revenue_month['Data da Compra'].dt.year
revenue_month['Month'] = revenue_month['Data da Compra'].dt.month_name()

revenue_categories = data.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

## Sales tables

sales_states = pd.DataFrame(data.groupby('Local da compra')['Preço'].count())
sales_states = data.drop_duplicates(subset='Local da compra')[['Local da compra','lat','lon']].merge(sales_states, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)


sales_month = pd.DataFrame(data.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count()).reset_index()
sales_month['Year'] = sales_month['Data da Compra'].dt.year
sales_month['Month'] = sales_month['Data da Compra'].dt.month_name()


sales_categories = pd.DataFrame(data.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending=False))

## Sellers table

sellers = pd.DataFrame(data.groupby('Vendedor')['Preço'].agg(['sum','count']))



# Graphics Revenue

fig_map_revenue = px.scatter_geo(revenue_states, 
                                    lat='lat',
                                    lon='lon',
                                    scope='south america',
                                    size='Preço',
                                    template='seaborn',
                                    hover_name='Local da compra',
                                    hover_data={'lat': False,'lon': False},
                                    title='Revenue per state'
                                )


fig_revenue_month = px.line(revenue_month,
                            x = 'Month',
                            y = 'Preço',
                            markers = True,
                            range_y = (0, revenue_month.max()),
                            color = 'Year',
                            line_dash = 'Year',
                            title = 'Monthly Revenue'
                           )
fig_revenue_month.update_layout(yaxis_title= 'Revenue')

fig_revenue_states = px.bar(revenue_states.head(),
                            x = 'Local da compra',
                            y = 'Preço',
                            text_auto = True,
                            title = 'Best States (Revenue)' 
                           )
fig_revenue_states.update_layout(yaxis_title= 'Revenue')

fig_revenue_categories = px.bar(revenue_categories,
                                text_auto = True,
                                title = 'Revenue per category'
                               )
fig_revenue_categories.update_layout(yaxis_title= 'Revenue')


# Graphics Sales


fig_map_sales = px.scatter_geo(sales_states,
                               lat = 'lat',
                               lon = 'lon',
                               scope = 'south america',
                               size = 'Preço',
                               template = 'seaborn',
                               hover_name = 'Local da compra',
                               hover_data = {'lat': False, 'lon': False},
                               title = 'Sales per State'

)

fig_sales_month = px.line(sales_month,
                          x = 'Month',
                          y = 'Preço',
                          markers = True,
                          range_y = (0, sales_month.max()),
                          color = 'Year',
                          line_dash = 'Year',
                          title = 'Monthly Sales'
)
fig_sales_month.update_layout(yaxis_title= 'Sales')


fig_sales_states = px.bar(sales_states.head(),
                            x = 'Local da compra',
                            y = 'Preço',
                            text_auto = True,
                            title = 'Best States (Sales)' 
                           )
fig_sales_states.update_layout(yaxis_title= 'Sales')

fig_sales_categories = px.bar(sales_categories,
                                text_auto = True,
                                title = 'Sales per category'
                               )
fig_sales_categories.update_layout(yaxis_title= 'Sales')


# Visualization

tab1, tab2, tab3 = st.tabs(['Revenue','Sales Quantity','Sellers'])

with tab1:
    column1, column2 = st.columns(2)
    with column1:
        st.metric('Revenue',format_number( data['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_map_revenue, use_container_width = True)
        st.plotly_chart(fig_revenue_states, use_container_width = True)

    with column2:
        st.metric('Sales Quantity', format_number(data.shape[0]))
        st.plotly_chart(fig_revenue_month, use_container_width = True)
        st.plotly_chart(fig_revenue_categories, use_container_width = True)
        
with tab2:
    column1, column2 = st.columns(2)
    with column1:
        st.metric('Revenue',format_number( data['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_map_sales, use_container_width = True)
        st.plotly_chart(fig_sales_states, use_container_width = True)

    with column2:
        st.metric('Sales Quantity', format_number(data.shape[0]))
        st.plotly_chart(fig_sales_month, use_container_width = True)
        st.plotly_chart(fig_sales_categories, use_container_width = True)

with tab3:
    
    qtt_sellers = st.number_input('Sellers Quantity', 2, 10, 5)
    column1, column2 = st.columns(2)
    total_sales = sellers['sum'].head(qtt_sellers).sum()
    with column1:
        st.metric('Revenue',format_number( sellers['sum'].head(qtt_sellers).sum(), 'R$'))
        fig_revenue_sellers = px.bar(sellers[['sum']].sort_values('sum', ascending = False).head(qtt_sellers),
                                        x = 'sum',
                                        y = sellers[['sum']].sort_values('sum', ascending = False).head(qtt_sellers).index,
                                        text_auto = True,
                                        title = f'Top {qtt_sellers} Sellers (Revenue)'
                                    )
        st.plotly_chart(fig_revenue_sellers)
    with column2:
        st.metric('Sales Quantity', sellers[['count']].sort_values('count', ascending = True).head(qtt_sellers).sum())
        fig_sales_sellers = px.bar(sellers[['count']].sort_values('count', ascending = False).head(qtt_sellers),
                                        x = 'count',
                                        y = sellers[['count']].sort_values('count', ascending = False).head(qtt_sellers).index,
                                        text_auto = True,
                                        title = f'Top {qtt_sellers} Sellers (Sales Quantity)'
                                    )
        st.plotly_chart(fig_sales_sellers)



# st.dataframe(data, use_container_width = True)
