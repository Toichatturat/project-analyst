import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import warnings
import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import base64
warnings.filterwarnings('ignore')


# Setting
st.set_page_config(page_title="Dashboard By Natthaphat", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: Store Analysis")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)
box_date = str(datetime.datetime.now().strftime("%d %B %Y"))
st.write(f"Last updated by:  \n {box_date}")

with open("howtouse-Natthaphat.pdf", "rb") as pdf_file:
    pdf_data = pdf_file.read()
    
pdf_base64 = base64.b64encode(pdf_data).decode()

download_link = f'<a href="data:application/pdf;base64,{pdf_base64}" download="download.pdf">Download PDF</a>'

st.write('You can download How to use and Analysis Data in this link')
st.markdown(download_link, unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file for Update",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
else:
    df = pd.read_csv("test_data.csv")
    
df["Date"] = pd.to_datetime(df["Date"])
df['Serve Time'] = pd.to_datetime(df['Serve Time'])
df['Order Time'] = pd.to_datetime(df['Order Time'])
df['Serve Duration'] = df['Serve Time'] - df['Order Time']
df['Duration'] = df['Serve Duration'].dt.total_seconds().astype(int)
df = df.dropna()
df['Weektype'] = df['Date'].dt.isocalendar().week
df['Week'] = df['Weektype'].astype(int)

#Date--------------------------------------------------------------------------------
startDate = pd.to_datetime(df["Date"]).min()
endDate = pd.to_datetime(df["Date"]).max()
st.write(f"This data {startDate} - {endDate}")
col1, col2 = st.columns((2))
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Date"] >= date1) & (df["Date"] <= date2)].copy()

#Total Sale--------------------------------------------------------------------------------
df_weekly_sales = df[['Week', 'Price']]

df_weekly_sales = df_weekly_sales.groupby('Week')['Price'].sum().reset_index()

st.header("Total Weekly sales")

fig, axes = plt.subplots(2, 1, figsize=(12, 16))
sns.barplot(x='Week', y='Price', data=df_weekly_sales, palette='viridis', ax=axes[0])
axes[0].set_title('Total Weekly Sales (Barplot)')
axes[0].set_xlabel('Week')
axes[0].set_ylabel('Total Sales')
sns.lineplot(x='Week', y='Price', data=df_weekly_sales, marker='o', ax=axes[1])
axes[1].set_title('Total Weekly Sales (Lineplot)')
axes[1].set_xlabel('Week')
axes[1].set_ylabel('Total Sales')
plotly_fig = make_subplots(rows=1, cols=2)
plotly_fig.add_trace(go.Bar(x=df_weekly_sales['Week'], y=df_weekly_sales['Price'], name='Bar Chart'), row=1, col=2)
plotly_fig.add_trace(go.Scatter(x=df_weekly_sales['Week'], y=df_weekly_sales['Price'], mode='lines+markers', name='Line Chart'), row=1, col=1)
st.plotly_chart(plotly_fig,use_container_width=True)
_, view1, dwn1, _ = st.columns((4))
with view1:
    expander = st.expander("Weekly sales Report")
    data = df[["Week","Price"]].groupby(by="Week")["Price"].sum()
    expander.write(data)
with dwn1:
    st.download_button("Get Data", data = data.to_csv().encode("utf-8"), 
                       file_name="Weekly-sales.csv", mime="text/csv")

#Sales by Day of week--------------------------------------------------------------------------------
df_Day_sales = df[['Day Of Week']]

fig = px.bar(df_Day_sales.groupby('Day Of Week').size().reset_index(name='Order ID'), x='Day Of Week', y='Order ID', 
             color='Day Of Week', 
             labels={'Day Of Week': 'Day Of Week', 'Order ID': 'Order Count'},
             title='Order Count by Day Of Week',
             color_discrete_sequence=px.colors.qualitative.Plotly)  # สีที่ใช้

fig.update_layout(xaxis_title='Day Of Week', yaxis_title='Order Count')

st.plotly_chart(fig, use_container_width=True)
report = df_Day_sales.groupby(['Day Of Week']).size().reset_index(name='Orders')
_, view2, dwn2, _ = st.columns((4))
with view2:
    expander = st.expander("Day Of Week sales Report")
    data = report[["Day Of Week","Orders"]]
    expander.write(data)
with dwn2:
    st.download_button("Get Data", data = data.to_csv().encode("utf-8"), 
                       file_name="Day-sales.csv", mime="text/csv")

#Staff--------------------------------------------------------------------------------
# Employee performance is measured by service time.
st.title("Employee performance")
st.subheader("Employee performance is measured by service time.")


cl5,_ = st.columns((2))

df_staff_duration = df[['Kitchen Staff', 'Drinks Staff', 'Category', 'Duration','Hour']]
df_staff_food = df_staff_duration[df_staff_duration['Category'] == 'food']
df_staff_drink = df_staff_duration[df_staff_duration['Category'] == 'drink']

with cl5:
    selected_hour = st.selectbox('Select Hour Filter', ['All Time', 'Most Order Time', 'Fewest Order Time'])

if selected_hour == 'All Time':
    filtered_df_food = df_staff_food
    filtered_df_drink = df_staff_drink
elif selected_hour == 'Most Order Time':
    filtered_df_food = df_staff_food.groupby('Hour').size().nlargest(2).reset_index(name='Order Count')
    filtered_df_food = df_staff_food[df['Hour'].isin(filtered_df_food['Hour'])]
    filtered_df_drink = df_staff_drink.groupby('Hour').size().nlargest(2).reset_index(name='Order Count')
    filtered_df_drink = df_staff_drink[df['Hour'].isin(filtered_df_drink['Hour'])]
elif selected_hour == 'Fewest Order Time':
    filtered_df_food = df_staff_food.groupby('Hour').size().nsmallest(2).reset_index(name='Order Count')
    filtered_df_food = df_staff_food[df_staff_food['Hour'].isin(filtered_df_food['Hour'])]
    filtered_df_drink = df_staff_drink.groupby('Hour').size().nsmallest(2).reset_index(name='Order Count')
    filtered_df_drink = df_staff_drink[df_staff_drink['Hour'].isin(filtered_df_drink['Hour'])]

average_duration_food = filtered_df_food.groupby('Kitchen Staff')['Duration'].mean().reset_index()

average_duration_drink = filtered_df_drink.groupby('Drinks Staff')['Duration'].mean().reset_index()

cl3, cl4 = st.columns((2))
with cl3:
    fig1 = px.bar(average_duration_food, x='Kitchen Staff', y='Duration',color='Kitchen Staff', title='Average Duration by Kitchen Staff', labels={'Kitchen Staff': 'Kitchen Staff', 'Duration': 'Average Duration'})
    st.plotly_chart(fig1,use_container_width=True)
with cl4:
    fig2 = px.bar(average_duration_drink, x='Drinks Staff', y='Duration', color='Drinks Staff', title='Average Duration by Drinks Staff', labels={'Drinks Staff': 'Drinks Staff', 'Duration': 'Average Duration'})
    st.plotly_chart(fig2,use_container_width=True)


v3, d3, v4, d4 = st.columns((4))
with v3:
    expander = st.expander("Kitchen Staff Report")
    data = average_duration_food[["Kitchen Staff","Duration"]]
    expander.write(data)
with d3:
    st.download_button("Get Data", data = data.to_csv().encode("utf-8"), 
                       file_name="Kitchen-Duration.csv", mime="text/csv")
with v4:
    expander = st.expander("Drinks Staff Report")
    data = average_duration_drink[["Drinks Staff","Duration"]]
    expander.write(data)
with d4:
    st.download_button("Get Data", data = data.to_csv().encode("utf-8"), 
                       file_name="Drinks-Duration.csv", mime="text/csv")
#Sales by Hour--------------------------------------------------------------------------------
# Sales analysis
st.title('Sales analysis')

st.subheader("Sales by Hour")
df_Hour_sales = df[['Hour']]

df_table = df[['Menu', 'Hour', 'Price', 'Category']]    

t1,_ = st.columns((2))

with t1:
    category = st.selectbox("Pick Category", ['All Categories'] + list(df["Category"].unique()),key=2, index=0)

if category == 'All Categories':
    filtered_df_Category = df_table.copy()
else:
    filtered_df_Category = df_table[df_table['Category'] == category]

fig = px.line(filtered_df_Category.groupby('Hour').size().reset_index(name='Order ID'), x='Hour', y='Order ID', 
              markers=True, line_shape='linear', labels={'Order ID': 'Order Count'})
fig.update_layout(title='Order Count by Hour', xaxis_title='Hour', yaxis_title='Order Count', template='plotly')

st.plotly_chart(fig, use_container_width=True)

report = filtered_df_Category.groupby('Hour').size().reset_index(name='Order ID')
v5, d5= st.columns((2))
with v5:
    expander = st.expander("Hour Sales Report")
    data = report[["Hour","Order ID"]]
    expander.write(data,use_container_width=True)
with d5:
    st.download_button("Get Data", data = data.to_csv().encode("utf-8"),
                       file_name="Hour-Sales-Duration.csv", mime="text/csv")

#Table--------------------------------------------------------------------------------
t2,_ = st.columns((2))

with t2:
    time = st.multiselect('Select Hour', filtered_df_Category['Hour'].unique())

if not time:
    filtered_df = filtered_df_Category.copy()
else:
    filtered_df = filtered_df_Category[filtered_df_Category['Hour'].isin(time)]

menu_counts = filtered_df.groupby(['Hour', 'Menu']).size().reset_index(name='Orders')

top_menus = menu_counts.sort_values(['Hour', 'Orders'], ascending=[True, False]).groupby('Hour').head(2).reset_index(drop=True)

bottom_menus = menu_counts.sort_values(['Hour', 'Orders']).groupby('Hour').head(2).reset_index(drop=True)

t3, t4 = st.columns((2))

with t3:
    st.subheader("Top 2 menu by Hour")
    st.write(top_menus, use_container_width=True)

with t4:
    st.subheader("Bottom 2 menu by Hour")
    st.write(bottom_menus, use_container_width=True)

#Sales by Menu--------------------------------------------------------------------------------
df_menu = df[['Menu', 'Week', 'Price', 'Category']]

st.subheader("Choose your filter: ")
ca1, ca2 = st.columns((2))
with ca1:
    selected_category = st.selectbox("Pick Category", ['All Categories'] + list(df["Category"].unique()),key=1, index=0)

if selected_category == 'All Categories':
    filtered_df_Category = df_menu.copy()
else:
    filtered_df_Category = df_menu[df_menu['Category'] == selected_category]

with ca2:
    selected_menus = st.multiselect('Select Menu', filtered_df_Category['Menu'].unique())

if not selected_menus:
    filtered_df = filtered_df_Category.copy()
else:
    filtered_df = filtered_df_Category[filtered_df_Category['Menu'].isin(selected_menus)]

sale_Menu_df = filtered_df.groupby(by=["Week", "Menu"], as_index=False)["Price"].sum()

fig = go.Figure()

for menu in sale_Menu_df['Menu'].unique():
    menu_data = sale_Menu_df[sale_Menu_df['Menu'] == menu]
    fig.add_trace(go.Scatter(x=menu_data['Week'], y=menu_data['Price'],
                             mode='lines+markers', name=menu))

fig.update_layout(title='Weekly Menu Sales Over the Year (Entire Week)',
                  xaxis_title='Week',
                  yaxis_title='Total Sales',
                  legend_title='Menu')

st.plotly_chart(fig, use_container_width=True)

report = sale_Menu_df.sort_values(["Week", "Menu","Price"], ascending=[True, False,True])
view5, dwn5= st.columns((2))
with view5:
    expander = st.expander("Menu Sales Report")
    data = report[["Week", "Menu","Price"]]
    expander.write(data,use_container_width=True)
with dwn5:
    st.download_button("Get Data", data = data.to_csv().encode("utf-8"),
                       file_name="Menu-Sales-Duration.csv", mime="text/csv")

st.subheader("Choose your filter: ")

Week = st.multiselect("Pick Week of Year", df["Week"].unique())
if not Week:
    filtered_df = df.copy()
else:
    filtered_df = df[df["Week"].isin(Week)]

cl1, cl2 = st.columns((2))
Menu_df = filtered_df.groupby(by = ["Menu"], as_index = False)["Price"].sum()

with cl1:
    st.subheader("Menu wise Sales")
    fig = px.bar(Menu_df, x = "Menu", y = "Price", text = ['${:,.2f}'.format(x) for x in Menu_df["Price"]],
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with cl2:
    st.subheader("Category wise Sales")
    fig = px.pie(filtered_df, values = "Price", names = "Category", hole = 0.5)
    fig.update_traces(text = filtered_df["Category"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)
    
st.write("Designed by Nanthaphat Toichatturat")
st.write("All rights reserved")