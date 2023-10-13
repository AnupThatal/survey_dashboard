from shiny import App, render, ui
import pandas as pd
import matplotlib.pyplot as plt
import math 
from htmltools import HTML, div
import shiny
import markdown
import seaborn as sns 
from IPython.display import HTML
import requests

def data_collection():
    odata_urls = [
        'https://survey.kuklpid.gov.np/v1/projects/7/forms/kukl_customer_survey_01.svc',
        'https://survey.kuklpid.gov.np/v1/projects/7/forms/kukl_customer_survey.svc',
        'https://survey.kuklpid.gov.np/v1/projects/15/forms/kukl_customer_survey_01.svc',
        'https://survey.kuklpid.gov.np/v1/projects/9/forms/kukl_customer_survey_01.svc',
        'https://survey.kuklpid.gov.np/v1/projects/6/forms/kukl_customer_survey_01.svc',
        'https://survey.kuklpid.gov.np/v1/projects/2/forms/kukl_customer_survey_01.svc',
        'https://survey.kuklpid.gov.np/v1/projects/2/forms/kukl_customer_survey.svc',
    ]
    submission_entity_set = 'Submissions'
    username = 'anupthatal2@gmail.com'
    password = 'NeeRM@n022!#'
    session = requests.Session()
    session.auth = (username, password)
    
    all_dfs = []  # List to store DataFrames from each URL
    
    for odata_url in odata_urls:
        submission_url = f"{odata_url}/{submission_entity_set}"
        response = session.get(submission_url)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data['value'])
            customer = []
            connection = []
            submittername = []
            reviewState = []
            # meternumber = []
            for i in df['gb12_skip']:
                customer.append(i['gc01_skp1']['gc20']['c20'])
                connection.append(i['gc01_skp1']['gc20']['c22'])
            for i in df['__system']:
                submittername.append(i['submitterName'])
                reviewState.append(i['reviewState'])
            # for i in df['gb12_skip']:
            #     meternumber.append(i['gc01_skp2']['d08'])
            df['ReviewState'] = reviewState
            df['SubmitterName'] = submittername
            df['gb12_skip-gc01_skp1-gc20-c20'] = customer
            df['gb12_skip-gc01_skp1-gc20-c22'] = connection
            # df['meternumber']=meternumber
            df['SubmitterName'] = df['SubmitterName'].str.upper()
            df = df[['b10_sub_dmi', 'unique_form_id', 'gb12_skip-gc01_skp1-gc20-c20', 'gb12_skip-gc01_skp1-gc20-c22','SubmitterName', 'ReviewState', 'unit_owners']]
            all_dfs.append(df)  # Append the processed DataFrame

    # Concatenate all DataFrames into a single DataFrame
    final_df = pd.concat(all_dfs, ignore_index=True)
    
    return final_df

df = data_collection()

df_hhc=pd.read_csv('HHC_Data.csv')
df.dropna(subset=['b10_sub_dmi'], inplace=True)

c1 = df['b10_sub_dmi'].unique().astype(int)
c3 = df['SubmitterName'].unique()
c1_list = c1.tolist()
c3_list = c3.tolist()

    

def data_cleaning_hhc(x):
    df_hhc.rename(columns={'sDMA ':'SDMA'},inplace=True)
    df_hhc['SDMA'] = df_hhc['SDMA'].str.replace(r'(\d+\.\d+\.\d+).*', r'\1')
    df_hhc['SDMA'] = df_hhc['SDMA'].str.replace('.','').astype(int)
    df_hhc['SDMA wise HHC'] = df_hhc['SDMA wise HHC'].str.replace(',','').astype(int)

    return df_hhc    

df_hhc1=data_cleaning_hhc(x=df_hhc)

app_ui = ui.page_fluid(
       
    ui.panel_title(ui.div({"style":"text-align:center;font-size:20px;"},
                   'Welcome to Survey dashboard')),
    ui.layout_sidebar(
        ui.panel_sidebar(
            # {"style": "background-color: rgba(0, 128, 255, 0.1)"},

            ui.input_select('sub_dma','Which Sub dma you wanna forecast',choices=c1_list),
            # ui.input_select('sub_dma','Which Sub dma you wanna forecast',choices=c3),

            ui.input_select('Enumertor','Select enumertor Name',choices=c3_list),
            ui.input_text('customer','Customer number or Connection number'),
            # ui.input_date_range(
            #        "daterange1", "Date range:", start="2022-01-01", end="2024-12-31"),
            # style={"class": "sidebar"},  # Apply the "sidebar" CSS class
            width=2
            ),
            
        ui.panel_main(
             # Use flexbox for layout
            ui.div({"style":"display: flex;flex-direction:row;gap:2rem;justify-content:space-evenly;"}, 
            ui.div( {"style":"font-weight:bold;text-align:center;"},
            ui.markdown(
                """
                ***Total***
                """
            ),                       
            ui.dataframe.output_data_frame('data_summary'),

            ),

              ui.div( {"style":"font-weight:bold;text-align:center;"},
            ui.markdown(
                """
                ***Customer details***
                """
            ),                       
            ui.dataframe.output_data_frame('customer1'),

            ),
           

            ),

            ui.output_plot('data_details1'),

            # ),
            ui.div({"style": "display: flex;flex-direction:row;gap:2rem;justify-content:space-evenly;"}, 
            ui.output_plot('mypie',width='170%',height='400px'),

            ui.output_plot('data_table',width='170%',height='500px'),

            ),
            ui.div({"style": "display: flex;flex-direction:row;gap:2rem;justify-content:space-evenly;"}, 

            ui.output_plot('myplot',width='100%',height='650px'),

            ),

            ui.output_plot('dma_measuring'),
            # output_widget('maps')


            ),
),
)


def server(input,output, session):
    @output
    @render.plot
    def myplot():
      x = input.sub_dma()   
      filtered_df = df[df['b10_sub_dmi'] == int(x)]
      filtered_df['ReviewState'].fillna('not checked',inplace=True)
      agg_df = filtered_df.groupby(['SubmitterName','ReviewState'])['unique_form_id'].count().reset_index()


      fig, ax = plt.subplots()
    
    # Create a bar plot using Seaborn on the specified axis
      sns.set(style="whitegrid")  # Set a white grid background
      sns.barplot(x='SubmitterName',y='unique_form_id', hue='ReviewState', data=agg_df)
      plt.xticks(rotation=10)
      ax.set_xlabel('SubmitterName')
      ax.set_ylabel('Total Count')
      ax.set_title('Counts by Submitter Name and Review State')
      for p in ax.patches:
          ax.annotate(f'{p.get_height():.0f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', fontsize=12, color='black', xytext=(0, 5),
                textcoords='offset points')

      return fig
    
    @output
    @render.plot
    def mypie():
        x=input.sub_dma()
        filtered_df=df[df['b10_sub_dmi']==int(x)]
        y1=filtered_df['SubmitterName'].unique()
        y1=filtered_df['b10_sub_dmi'].count()
        # print(y1)

        global y2

        y2=df_hhc1[df_hhc1['SDMA']==int(x)]
        y2['SDMA wise HHC']=y2['SDMA wise HHC'].astype(int)
        y2=y2.groupby('SDMA')['SDMA wise HHC'].sum().reset_index()

        new_data = {'SDMA':x, 'SDMA wise HHC':y1}

        new_data=pd.DataFrame(new_data,index=[0])

        df1=pd.concat([y2, new_data], ignore_index=True)
        # print(df1)
        
        df1.iloc[0,0]='Collected'

        df1.iloc[1,0]='remaining'
        
        return df1.groupby('SDMA')['SDMA wise HHC'].sum().plot(kind='pie',y=y1,autopct='%1.1f%%')

    @output
    @render.data_frame
    def data_summary():
        x=input.sub_dma()
        df['b10_sub_dmi']=df['b10_sub_dmi'].astype(int)
        # df=df['b10_sub_dmi'].astype(int)
        filtered_df=df[df['b10_sub_dmi']==int(x)]
        Total=filtered_df['b10_sub_dmi'].count()
        dma_total=y2['SDMA wise HHC'][0]
        approved=filtered_df[filtered_df['ReviewState']=='approved']
        approved=approved['unique_form_id'].count()
        rejected=filtered_df[(filtered_df['ReviewState']=='rejected') | (filtered_df['ReviewState']=='hasIssues')]
        rejected=rejected['unique_form_id'].count()
        # remaining=filtered_df[(filtered_df['ReviewState']!='rejected') | (filtered_df['ReviewState']!='hasIssues') | (filtered_df['ReviewState']=='approved')]
        # remaining=Total-(int(approved)+int(rejected))
        # print(df_hhc1['SDMA'])
        r=dma_total-Total
        df_summary = pd.DataFrame({'Total': [Total], 'DMA Total': [dma_total], 'Remaining': [r]})

        return df_summary


    @output
    @render.plot
    def data_details1():
        x=input.Enumertor()
        filtered_df=df[df['SubmitterName']==str(x)]
        # filtered_df.groupby('b10_sub_dmi')['unique_form_id'].count().reset_index()
        # heatmap = sns.heatmap(filtered_df.corr(), vmin=-1, vmax=1, annot=True)
        pivot_table = filtered_df.pivot_table(index='SubmitterName', columns='b10_sub_dmi',aggfunc='size',fill_value=0)
        pivot_table_sorted = pivot_table.sort_index(axis=1, ascending=False)
        print(pivot_table_sorted)

        return sns.heatmap(pivot_table_sorted, annot=True, cmap='coolwarm', fmt='d', linewidths=.5)
 
    @output
    @render.plot 
    def data_table():
        x=input.sub_dma()
        filtered_df=df[df['b10_sub_dmi']==int(x)]
        filtered_df['ReviewState'].fillna('needs to check',inplace=True)
        counts = filtered_df.groupby('ReviewState')['b10_sub_dmi'].count()
        custom_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        fig, ax = plt.subplots(figsize=(8, 4))
        counts.plot(kind='bar', color=custom_colors, legend=True, ax=ax)
        ax.set_xlabel('Review State')
        ax.set_ylabel('Collect')
        ax.set_title('Counts by Review State')
        for i, v in enumerate(counts):
            ax.text(i, v + 1, str(v), ha='center', va='bottom')
        return fig
    
    @output
    @render.plot
    def dma_measuring():
        data_collected=df.groupby('b10_sub_dmi')['unique_form_id'].count().reset_index()
        # df_hhc1.groupby('SDMA')['SDMA wise HHC'].reset_index()
        print(data_collected)
        hhc=df_hhc[['SDMA','SDMA wise HHC']]

        result = pd.merge(data_collected,hhc,left_on='b10_sub_dmi',right_on='SDMA', how='inner')

        result['diff']=result['SDMA wise HHC']-result['unique_form_id']
        # print(result)

        sorted_df = result.sort_values(by='diff', ascending=False)
        
        sorted_df=sorted_df[sorted_df['diff']>0]
        dot_size = sorted_df['diff'] * 100




        # scatter_plot = sns.scatterplot(x='SDMA', y='diff', size='diff', data=sorted_df, sizes=(10, 400), c=sorted_df['color_variable'], cmap='coolwarm', s=dot_size)
        scatter_plot = sns.scatterplot(x='SDMA', y='diff', size='diff', data=sorted_df, sizes=(10, 400), c=sorted_df['diff'], cmap='coolwarm', s=dot_size)
        # scatter_plot = sns.scatterplot(x='SDMA', y='diff', size='diff', data=sorted_df, sizes=(10, 400),cmap='coolwarm',s=dot_size)

        for i, txt in enumerate(sorted_df['SDMA']):
            plt.annotate(txt, (sorted_df['SDMA'].iloc[i], sorted_df['diff'].iloc[i]), fontsize=8, ha='center')
        plt.xlabel('SDMA')
        plt.ylabel('diff')
        plt.title('Scatterplot of SDMA vs. diff')


        return scatter_plot
    
    @output
    @render.data_frame
    def customer1():
        x=input.customer()

        df.rename(columns={'b10_dmi':'DMA'},inplace=True)

        df_c=df[df['gb12_skip-gc01_skp1-gc20-c20'] == str(x)]

        if df_c.empty:
            df_c = df[df['gb12_skip-gc01_skp1-gc20-c22'] == str(x)]
            df_c.rename(columns={
            'unique_form_id': 'ID',
            'b10_sub_dmi': 'Sub DMA',
            'gb12_skip-gc01_skp1-gc22':'Connection no',
            'unit_owners': 'Unit Owners',
            'SubmitterName': 'Enumerator'}, inplace=True)

            return df_c[['ID','Sub DMA','Unit Owners','Enumerator']]
        else:
            df_c.rename(columns={
            'unique_form_id': 'ID',
            'b10_sub_dmi': 'Sub DMA',
            'gb12_skip-gc01_skp1-gc22': 'Customer no',
            'unit_owners': 'Unit Owners',
            'SubmitterName': 'Enumerator'}, inplace=True)
            
            return df_c[['ID','Sub DMA','Unit Owners','Enumerator']]


app = App(app_ui, server)

