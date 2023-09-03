import streamlit as st
import plotly.express as px
import data_cleaning

### This is the Python script for creating the dashboard.

### Import cleaned data
data = data_cleaning.data
data_missing = data_cleaning.data_missing

### Page set up
st.set_page_config(
    page_title="Customer Health Score",
    page_icon="🦦",
    layout="wide",
)

st.title("Otter Customer Health Score Dashboard")

# side bar selection set up
view_option = st.sidebar.selectbox(
    "Who is viewing?",
    ("Team Manager", "Customer Success Associate")
)

csa_name = st.sidebar.selectbox(
    "Customer Success Associate Name",
    ["None Selected"] + list(data["Customer Success Associate"].unique())
)

### Dashboard

## View 1: team manager
if view_option == "Team Manager":
    if csa_name != "None Selected":
        st.markdown("Cannot select CSA name for Team Manager view")
    else:
        # page set up
        st.markdown('This is the dashboard for team managers to view the overall health of the customers in the market and team performance.')
        st.header('Overview of Customer Health Score Counts', divider = 'blue')

        # columns for figures
        empty1, plot1, empty2, plot2 = st.columns([0.00001, 0.5, 0.2, 1.2])
        with empty1:
            st.empty()

        chs_grouped = data.groupby("Customer Health")["Customer Health Score"].count().to_frame().reset_index()
        
        # pie chart of counts of customer health
        p = px.pie(chs_grouped, values = "Customer Health Score", 
                   names = "Customer Health",
                   color = "Customer Health",
                   color_discrete_map = {
                       'Healthy': 'seagreen',
                       'Neutral': 'goldenrod',
                       'Unhealthy': 'firebrick'
                   })
        plot1.plotly_chart(p,use_container_width=True)

        with empty2:
            st.empty()

        # stacked bar chart of count of diff customer health for each customer success associate
        csa_stacked_grouped = data.groupby(by=["Customer Success Associate","Customer Health"]).count().reset_index().rename(columns={"Customer Health Score": "Customer Health Count"})
        b2 = px.bar(csa_stacked_grouped,
                    x = "Customer Success Associate",
                    y = "Customer Health Count",
                    color = "Customer Health",
                    color_discrete_map = {
                       'Healthy': 'seagreen',
                       'Neutral': 'goldenrod',
                       'Unhealthy': 'firebrick'
                   }, text_auto=True)
        plot2.plotly_chart(b2,use_container_width=True)

        # each associate's average CHS
        st.header('Average Customer Health Score by Customer Success Associate', divider = 'blue')
        csa_grouped = data.groupby("Customer Success Associate")["Customer Health Score"].mean().to_frame().reset_index().sort_values("Customer Health Score", ascending=False).rename(columns={"Customer Health Score": "Average Customer Health Score"})
        b = px.bar(csa_grouped, x = "Customer Success Associate", 
                   y = "Average Customer Health Score",
                   color_discrete_sequence=["royalblue"]*len(csa_grouped)).update_layout(yaxis_range=[20,65])
        st.plotly_chart(b,use_container_width=True)

## View 2: customer success associate
elif view_option == "Customer Success Associate":
    if csa_name == "None Selected":
        st.markdown("Please select Customer Success Associate name.")
    else:
        # columns for subheaders
        st.markdown("This is the dashboard for Customer Success Associates to see an overview as well as individual customers' health scores.")
        hd1, hd2 = st.columns([0.7, 1.2])
        hd1.header('Customer Health Overview', divider = 'blue')
        hd2.header('Top 10 Performing Customers', divider = 'blue')

        # columns for figures
        empty1, plot1, empty2, plot2 = st.columns([0.00001, 0.5, 0.2, 1.2])
        with empty1:
            st.empty()

        # filter data to specific csa
        csa_data = data[data["Customer Success Associate"] == csa_name]
        chs_grouped = csa_data.groupby("Customer Health")["Customer Health Score"].count().to_frame().reset_index()

        # pie chart of counts of customer health counts
        p = px.pie(chs_grouped, values = "Customer Health Score", 
                   names = "Customer Health",
                   color = "Customer Health",
                   color_discrete_map = {
                       'Healthy': 'seagreen',
                       'Neutral': 'goldenrod',
                       'Unhealthy': 'firebrick'
                   })
        plot1.plotly_chart(p,use_container_width=True)

        with empty2:
            st.empty()
        
        # bar graph of top 10 customers
        top_10 = csa_data.sort_values("Customer Health Score", ascending=False).head(10)
        b = px.bar(top_10,
                   x = "Unique Location ID", 
                   y = "Customer Health Score",
                   color_discrete_sequence=["royalblue"]*10).update_layout(yaxis_range=[top_10['Customer Health Score'].min()-top_10['Customer Health Score'].std(),top_10['Customer Health Score'].max()+top_10['Customer Health Score'].std()])
        plot2.plotly_chart(b,use_container_width=True)

        # all data table
        st.header('All Data', divider = 'blue')

        # just overall health score, then individual broken down scores
        table_data = csa_data[["Unique Location ID", "Customer Health", "Customer Health Score", "LPU Score", "HP Score", "PS Score", "Normalized & Scaled PGR"]]
        
        filter1, filter2 = st.columns(2)
        
        # filters/sort for table
        table_filter = filter1.selectbox(
            "Filter", 
            ("None Selected", "Healthy", "Neutral", "Unhealthy")
        )
        table_sort = filter2.selectbox(
            "Sort by Customer Health Score",
            ("None Selected", "Ascending", "Descending")
        )
        
        # color code customer health
        def color_ch(value):
            if value == 'Healthy':
                color = 'seagreen'
            elif value == 'Neutral':
                color = 'goldenrod'
            else:
                color = 'firebrick'
            return 'color: %s' % color
        
        # apply filter/sort
        if table_sort == 'Ascending':
            table_data = table_data.sort_values(by=['Customer Health Score'], ascending=True)
        elif table_sort == 'Descending':
            table_data = table_data.sort_values(by=['Customer Health Score'], ascending=False)
        else:
            pass

        if table_filter == "None Selected":
            st.dataframe(table_data.style.applymap(color_ch, subset=['Customer Health']),use_container_width=True)
        else:
            st.dataframe(table_data[table_data["Customer Health"] == table_filter].style.applymap(color_ch, subset=['Customer Health']),use_container_width=True)

        # missing data table
        st.header('Missing Data', divider = 'blue')
        try: 
            missing_csa = data_missing[data_missing["Customer Success Associate"] == csa_name]
            useful_columns_list = ['Customer Success Associate', 'Parent Restaurant name','Unique Location ID', 'Highest Product','Orders Week 2', 'Orders Week 1','Cancellations Week 2', 'Cancellations Week 1','Missed Orders Week 2', 'Missed Orders Week 1', 'Average Order Week 2','Average Order Value week 1', 'Last Product Usage Date', 'Payment Status']
            missing_columns_list = ['Customer Success Associate', 'Parent Restaurant name','Unique Location ID','Missing Columns']
            data_missing = missing_csa[useful_columns_list]
            data_missing['Missing Columns'] = data_missing.apply(lambda x: ','.join(x[x.isnull()].index), axis=1)
            st.dataframe(data_missing[['Parent Restaurant name', 'Unique Location ID', 'Missing Columns']],use_container_width=True)
        except:
            # add case for if a csa doesn't have any missing data
            missing_csa = False
