#%%
import re
#%%
def participants_list(df):

    Participant_start_index = df.index[df.iloc[:,0] == 'Company Participants'].tolist() #  'Company Participants' index
    Participant_middle_index = df.index[df.iloc[:,0] == 'Other Participants'].tolist() #  'Other Participants' index

    #  'MANAGEMENT DISCUSSION SECTION' index, is the beginning of the management discussion, would stop before this row
    Participant_end_index = df.index[df.iloc[:,0] == 'MANAGEMENT DISCUSSION SECTION' ].tolist()
    # try to find the 'MANAGEMENT DISCUSSION SECTION' or 'Presentation' index
    if Participant_end_index == []:
        Participant_end_index = df.index[df.iloc[:,0] == 'Presentation'].tolist()
        if Participant_end_index == []:
            Participant_end_index = df.index[df.iloc[:,0] == 'Questions And Answers' ].tolist()
            Participant_end_index = [Participant_end_index[-1]]
            if Participant_end_index == []:
                Participant_end_index = df.index[df.iloc[:,0] == 'Q&A' ].tolist()
                Participant_end_index = [Participant_end_index[-1]]
        else:
            Participant_end_index = [Participant_end_index[-1]]    
    # some transcript dont have 'Other Participants'
    if Participant_middle_index == []:
        Participant_middle_index = Participant_end_index.copy()
    #print(Participant_start_index, Participant_middle_index, Participant_end_index)

    # make the list of company_paticipants 
    company_paticipants = df.loc[Participant_start_index[0]+1:Participant_middle_index[0]-1]
    company_paticipants.drop(company_paticipants.index[company_paticipants.iloc[:,0] == ''].tolist(), inplace=True)
    company_paticipants = company_paticipants.values.tolist()
    # and other_participants
    other_paticipants = df.loc[Participant_middle_index[0]+1:Participant_end_index[0]-1]
    other_paticipants.drop(other_paticipants.index[other_paticipants.iloc[:,0] == ''].tolist(), inplace=True)
    other_paticipants = other_paticipants.values.tolist()

    # after extract the paticipants, we can drop those information to make the transcript more clear
    df = df.reset_index(drop=True)
    df = df.drop(range(df.index[df.iloc[:,0] == 'Company Participants'].tolist()[0],df.index[df.iloc[:,0].isin(['MANAGEMENT DISCUSSION SECTION','Presentation'])].tolist()[0]))
    df = df.drop(df[df[0] == 'heading'].index)
    # drop the row that end with 'Investor Day' by re
    df = df[~df[0].str.contains('Investor Day')]
    # drop the first row of the df
    df = df.reset_index(drop=True)
    df = df.iloc[1: , :]
    # reset the index again to make sure the index is continuous for better processing
    df = df.reset_index(drop=True)
    # # save to csv
    # df.to_csv('/Users/timliu/Desktop/output/df.csv')
    return df, company_paticipants, other_paticipants





# %%
def clean_participants_list(def_participants):
    # get the value inside the def_participants 
    def_participants = [item for sublist in def_participants for item in sublist]
    def_participants = [i[0] for i in def_participants]
    # print(def_participants)
    # %%
    # exclude the title of the participants, i.e.'Roland Vogel, CFO' to 'Roland Vogel" by using re
    def_participants = [re.sub(r'\,.*', '', participant) for participant in def_participants]
    # exclude the thing below
    def_participants = [re.sub(r'Property & Casualty Reinsurance', '', participant) for participant in def_participants]
    def_participants = [re.sub(r'\[0682QB-E Ulrich Wallin\]', '', participant) for participant in def_participants]
    def_participants = [re.sub(r'\[05HFRJ-E Denis Kessler]', '', participant) for participant in def_participants]
    # drop duplicated participants
    # def_participants = [i[0] for i in def_participants]
    # drop the empty string
    def_participants = [participant for participant in def_participants if participant != '']
    # remove the sapce in the string
    def_participants = [participant.strip() for participant in def_participants]
    # add the 'Operator' to the list
    def_participants.append('Operator')

    # drop the duplicated participants
    def_participants_copy = def_participants.copy()
    def_participants = []
    # drop the duplicated participants
    for i in def_participants_copy: 
        if i not in def_participants: 
            def_participants.append(i) 
    def_participants = sorted(def_participants)
    
    return def_participants