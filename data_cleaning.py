# %%
import pandas as pd
import numpy as np
import re

# %%
def cleaning_text(df):
    # remove the unnessary string
    df[0] = df[0].str.replace('\n','')
    df[0] = df[0].str.replace('Bloomberg Transcript','')
    df[0] = df[0].str.replace('\x0c\n','')
    df[0] = df[0].str.replace('FINAL','')
    df[0] = df[0].str.replace('*','')
    df[0] = df[0].str.replace('[','')
    df[0] = df[0].str.replace(']','')
    df[0] = df[0].str.replace(':','')
    df[0] = df[0].str.replace('A - ','')
    df[0] = df[0].str.replace('Q - ','')
    # repalce the {BIO and the digit after it
    df[0] = df[0].str.replace('{BIO','')
    df[0] = df[0].str.replace('}','')
    # df[0] = df[0].str.replace('\d+','')
    df[0] = df[0].str.replace('<','')
    df[0] = df[0].str.replace('>','')
    df[0] = df[0].str.replace('GO','')

    # using re to remove the unnessary string
    def drop_unnessary(x):
        page = re.findall(r'Page \d+ of \d+', x) # 'page ... of ... '
        # BIO = re.findall(r'{BIO', x) # '{BIO 18731996 <GO>}'
        Company_Name = re.findall(r'Company N ame', x) # 'Company N ame: H annover Rueck SE'
        Company_Ticker = re.findall(r'Company Ticker', x) # 'Company Ticker: H N R1 GR Equity'
        Date = re.findall(r'Date', x) # Date: 2015-03-10
        if page == []  and Company_Name == [] and Company_Ticker == [] and Date == []: # and BIO == []
            return True
        else:
            return False

    true_false = df[0].apply(lambda x: drop_unnessary(x))
    df = df[true_false]

    # drop the final page declaration
    df = df[df[0] != 'This transcript may not be 100 percent accurate and may contain misspellings and other']
    df = df[df[0] != 'inaccuracies. This transcript is provided "as is", without express or implied warranties of']
    df = df[df[0] != 'inaccuracies. This transcript is provided as is, without express or implied warranties of']
    df = df[df[0] != 'any kind. Bloomberg retains all rights to this transcript and provides it solely for your']
    df = df[df[0] != 'personal, non-commercial use. Bloomberg, its suppliers and third-party agents shall']
    df = df[df[0] != 'have no liability for errors in this transcript or for lost profits, losses, or direct, indirect,']
    df = df[df[0] != 'incidental, consequential, special or punitive damages in connection with the']
    df = df[df[0] != 'furnishing, performance or use of such transcript. Neither the information nor any']
    df = df[df[0] != 'opinion expressed in this transcript constitutes a solicitation of the purchase or sale of']
    df = df[df[0] != 'securities or commodities. Any opinion expressed in the transcript does not necessarily']
    df = df[df[0] != 'reflect the views of Bloomberg LP. ¬© COPYRIGHT 2022, BLOOMBERG LP. All rights']  # we will need this to identify the last participant
    df = df[df[0] != 'reserved. Any reproduction, redistribution or retransmission is expressly prohibited.']
    # ¬© could not be identified, would apply re
    def drop_Bloomberg_mark(x):
        Bloomberg_mark = re.findall(r'reflect the views of Bloomberg LP', x) # 'reflect the views of Bloomberg LP. ¬© COPYRIGHT 2022, BLOOMBERG LP. All rights'
        if Bloomberg_mark == []:
            return True
        else:
            return False

    true_false_bm = df[0].apply(lambda x: drop_Bloomberg_mark(x))
    df = df[true_false_bm]

    # drop the empthy row
    df = df[df[0] != '']
    df = df[df[0] != '']

    # ################################## for the usage of not seperating Q&A ###################################
    # if the row == "Questions And Answers" or "Q&A" will drop the row
    df = df[df[0] != 'Questions And Answers']
    df = df[df[0] != 'Q&A']
    # ##########################################################################################################

    # ################################## for the usage of not seperating Q&A ###################################
    # # drop the Questions And Answers and the following rows
    # QA_index = df.index[df.iloc[:,0] == 'Questions And Answers'].tolist()
    # # get the index of the last row of df
    # end_index = [len(df)]
    # if QA_index == []:
    #     QA_index = df.index[df.iloc[:,0] == 'Q&A'].tolist()
    #     end_index = [len(df)]
    #     if QA_index == []:
    #         # get the index of the last row of df
    #         end_index = []

    # # drop the row between QA_index and end_index
    # if QA_index != []:
    #     df = df.drop(df.index[QA_index[0]+1:end_index[0]])
    # ###################################################################################################

    # reset the index to make sure the index is continuous for better processing
    df = df.reset_index(drop=True)
    
    return df
# %%
def sentence_df(concat_df, company_paticipants_list, other_paticipants_list):
    model_df = pd.DataFrame()
    for i in range(int(len(concat_df.columns.to_list())/3)):
        #print(i)
        tmp_df = pd.DataFrame()
        tmp_df = concat_df.iloc[:,(i*3):(i*3)+3].copy()
        # extract the index as column from the text
        tmp_df['file_name'] = tmp_df.columns.to_list()[0]
        # extract the date from the index column
        tmp_df['date'] = tmp_df['file_name'].apply(lambda x: x.split('_')[0])
        # change the date column to datetime
        tmp_df['date'] = pd.to_datetime(tmp_df['date'])
        # rename to be consistent with the column name
        tmp_df.columns = ["line", "participants",  "idx", "file_name","date"]
        # if the 'participants' column's value equals to any of the company_paticipants_list, other_paticipants_list, then set the value to 0
        tmp_df['company_paticipants_yes'] = tmp_df['participants'].apply(lambda x: 1 if x in company_paticipants_list else 0)
        tmp_df['other_paticipants_yes'] = tmp_df['participants'].apply(lambda x: 1 if x in other_paticipants_list else 0)
        # drop the row if the column "line" is NaN
        tmp_df = tmp_df.dropna(subset=['line'], how='all')
        tmp_df['company_name1']  = tmp_df['file_name'].apply(lambda x: x.split('_')[1])
        tmp_df['company_name2']  = tmp_df['file_name'].apply(lambda x: x.split('_')[2])
        tmp_df['company_name'] = tmp_df["company_name1"] + " " + tmp_df["company_name2"]
        # drop the 'company_name1' and 'company_name2' column
        tmp_df = tmp_df.drop(columns=['company_name1', 'company_name2']).reset_index(drop=True)
        # drop line contains only participants name
        id_rows = tmp_df[tmp_df['line']==tmp_df['participants']].index
        tmp_df = tmp_df.drop(id_rows)
        # append into dataframe
        model_df = model_df.append(tmp_df)
        return model_df
# %%
def cleaning_text_MD(df):
    # remove the unnessary string
    df[0] = df[0].str.replace('\n','')
    df[0] = df[0].str.replace('Bloomberg Transcript','')
    df[0] = df[0].str.replace('\x0c\n','')
    df[0] = df[0].str.replace('FINAL','')
    df[0] = df[0].str.replace('*','')
    df[0] = df[0].str.replace('[','')
    df[0] = df[0].str.replace(']','')
    df[0] = df[0].str.replace(':','')
    df[0] = df[0].str.replace('A - ','')
    df[0] = df[0].str.replace('Q - ','')
    # repalce the {BIO and the digit after it
    df[0] = df[0].str.replace('{BIO','')
    df[0] = df[0].str.replace('}','')
    # df[0] = df[0].str.replace('\d+','')
    df[0] = df[0].str.replace('<','')
    df[0] = df[0].str.replace('>','')
    df[0] = df[0].str.replace('GO','')

    # using re to remove the unnessary string
    def drop_unnessary(x):
        page = re.findall(r'Page \d+ of \d+', x) # 'page ... of ... '
        # BIO = re.findall(r'{BIO', x) # '{BIO 18731996 <GO>}'
        Company_Name = re.findall(r'Company N ame', x) # 'Company N ame: H annover Rueck SE'
        Company_Ticker = re.findall(r'Company Ticker', x) # 'Company Ticker: H N R1 GR Equity'
        Date = re.findall(r'Date', x) # Date: 2015-03-10
        if page == [] and Company_Name == [] and Company_Ticker == [] and Date == []: #and BIO == [] 
            return True
        else:
            return False

    true_false = df[0].apply(lambda x: drop_unnessary(x))
    df = df[true_false]

    # drop the final page declaration
    df = df[df[0] != 'This transcript may not be 100 percent accurate and may contain misspellings and other']
    df = df[df[0] != 'inaccuracies. This transcript is provided "as is", without express or implied warranties of']
    df = df[df[0] != 'inaccuracies. This transcript is provided as is, without express or implied warranties of']
    df = df[df[0] != 'any kind. Bloomberg retains all rights to this transcript and provides it solely for your']
    df = df[df[0] != 'personal, non-commercial use. Bloomberg, its suppliers and third-party agents shall']
    df = df[df[0] != 'have no liability for errors in this transcript or for lost profits, losses, or direct, indirect,']
    df = df[df[0] != 'incidental, consequential, special or punitive damages in connection with the']
    df = df[df[0] != 'furnishing, performance or use of such transcript. Neither the information nor any']
    df = df[df[0] != 'opinion expressed in this transcript constitutes a solicitation of the purchase or sale of']
    df = df[df[0] != 'securities or commodities. Any opinion expressed in the transcript does not necessarily']
    df = df[df[0] != 'reflect the views of Bloomberg LP. ¬© COPYRIGHT 2022, BLOOMBERG LP. All rights']  # we will need this to identify the last participant
    df = df[df[0] != 'reserved. Any reproduction, redistribution or retransmission is expressly prohibited.']
    # ¬© could not be identified, would apply re
    def drop_Bloomberg_mark(x):
        Bloomberg_mark = re.findall(r'reflect the views of Bloomberg LP', x) # 'reflect the views of Bloomberg LP. ¬© COPYRIGHT 2022, BLOOMBERG LP. All rights'
        if Bloomberg_mark == []:
            return True
        else:
            return False

    true_false_bm = df[0].apply(lambda x: drop_Bloomberg_mark(x))
    df = df[true_false_bm]

    # drop the empthy row
    df = df[df[0] != '']
    df = df[df[0] != '']

    # ################################## for the usage of not seperating Q&A ###################################
    # # if the row == "Questions And Answers" or "Q&A" will drop the row
    # df = df[df[0] != 'Questions And Answers']
    # df = df[df[0] != 'Q&A']
    # ##########################################################################################################

    ################################## for the usage of MD ###################################
    # drop the Questions And Answers and the following rows
    QA_index = df.index[df.iloc[:,0] == 'Questions And Answers'].tolist()
    # get the index of the last row of df
    end_index = [len(df)]
    if QA_index == []:
        QA_index = df.index[df.iloc[:,0] == 'Q&A'].tolist()
        end_index = [len(df)]
        if QA_index == []:
            # get the index of the last row of df
            end_index = []

    # drop the row between QA_index and end_index
    if QA_index != []:
        df = df.drop(df.index[QA_index[0]+1:end_index[0]])
    # ###################################################################################################

    # reset the index to make sure the index is continuous for better processing
    df = df.reset_index(drop=True)
    
    return df

# %%
def cleaning_text_QA(df):
    # remove the unnessary string
    df[0] = df[0].str.replace('\n','')
    df[0] = df[0].str.replace('Bloomberg Transcript','')
    df[0] = df[0].str.replace('\x0c\n','')
    df[0] = df[0].str.replace('FINAL','')
    df[0] = df[0].str.replace('*','')
    df[0] = df[0].str.replace('[','')
    df[0] = df[0].str.replace(']','')
    df[0] = df[0].str.replace(':','')
    df[0] = df[0].str.replace('A - ','')
    df[0] = df[0].str.replace('Q - ','')
    # repalce the {BIO and the digit after it
    df[0] = df[0].str.replace('{BIO','')
    df[0] = df[0].str.replace('}','')
    df[0] = df[0].str.replace('<','')
    df[0] = df[0].str.replace('>','')
    df[0] = df[0].str.replace('GO','')
    # df[0] = df[0].str.replace('\d+','')

    # using re to remove the unnessary string
    def drop_unnessary(x):
        page = re.findall(r'Page \d+ of \d+', x) # 'page ... of ... '
        # BIO = re.findall(r'{BIO', x) # '{BIO 18731996 <GO>}'
        Company_Name = re.findall(r'Company N ame', x) # 'Company N ame: H annover Rueck SE'
        Company_Ticker = re.findall(r'Company Ticker', x) # 'Company Ticker: H N R1 GR Equity'
        Date = re.findall(r'Date', x) # Date: 2015-03-10
        # drop the empty row, such as "" or "" or " "
        Emptyrow = re.findall(r'^$', x)

        if page == [] and Company_Name == [] and Company_Ticker == [] and Date == [] and Emptyrow==[]: #BIO == [] and
            return True
        else:
            return False

    true_false = df[0].apply(lambda x: drop_unnessary(x))
    df = df[true_false]

    # drop the final page declaration
    df = df[df[0] != 'This transcript may not be 100 percent accurate and may contain misspellings and other']
    df = df[df[0] != 'inaccuracies. This transcript is provided "as is", without express or implied warranties of']
    df = df[df[0] != 'inaccuracies. This transcript is provided as is, without express or implied warranties of']
    df = df[df[0] != 'any kind. Bloomberg retains all rights to this transcript and provides it solely for your']
    df = df[df[0] != 'personal, non-commercial use. Bloomberg, its suppliers and third-party agents shall']
    df = df[df[0] != 'have no liability for errors in this transcript or for lost profits, losses, or direct, indirect,']
    df = df[df[0] != 'incidental, consequential, special or punitive damages in connection with the']
    df = df[df[0] != 'furnishing, performance or use of such transcript. Neither the information nor any']
    df = df[df[0] != 'opinion expressed in this transcript constitutes a solicitation of the purchase or sale of']
    df = df[df[0] != 'securities or commodities. Any opinion expressed in the transcript does not necessarily']
    df = df[df[0] != 'reflect the views of Bloomberg LP. ¬© COPYRIGHT 2022, BLOOMBERG LP. All rights']  # we will need this to identify the last participant
    df = df[df[0] != 'reserved. Any reproduction, redistribution or retransmission is expressly prohibited.']
    # ¬© could not be identified, would apply re
    def drop_Bloomberg_mark(x):
        Bloomberg_mark = re.findall(r'reflect the views of Bloomberg LP', x) # 'reflect the views of Bloomberg LP. ¬© COPYRIGHT 2022, BLOOMBERG LP. All rights'
        if Bloomberg_mark == []:
            return True
        else:
            return False

    true_false_bm = df[0].apply(lambda x: drop_Bloomberg_mark(x))
    df = df[true_false_bm]

    # drop the empthy row
    df = df[df[0] != '']
    df = df[df[0] != '']

    # # ################################## for the usage of QA ################################### 我現在要修這個地方
    # # get only the QA part
    # QA_index = df.index[df.iloc[:,0] == 'Questions And Answers'].tolist()
    # # get the index of the last row of tmp_df_text
    # end_index = [len(df)]
    # if QA_index == []:
    #     QA_index = df.index[df.iloc[:,0] == 'Q&A'].tolist()
    #     end_index = [len(df)]
    #     # if QA_index == []:
    #     #     QA_index = tmp_df_text.index[tmp_df_text.iloc[:,0] == '(Questions And Answers)'].tolist()
    #     #     end_index = [len(tmp_df_text)]
    #     #     if QA_index == []:
    #     #         QA_index = tmp_df_text.index[tmp_df_text.iloc[:,0] == '(Q&A)'].tolist()
    #     #         end_index = [len(tmp_df_text)]
    #     if QA_index == []:
    #         df = pd.DataFrame(np.zeros((2500,1)))
    #         df.iloc[:,0] = np.nan
        
    # if QA_index != []:
    #     df = df.iloc[QA_index[0]+1:end_index[0]]
    # # ###################################################################################################

    # reset the index to make sure the index is continuous for better processing\
    df = df.reset_index(drop=True)
    
    return df