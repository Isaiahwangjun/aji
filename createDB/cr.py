from openai import OpenAI
import pandas as pd
import csv
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.environ.get('OPENAI_API_KEY')

client = OpenAI(api_key=openai_api_key)


def CR(content):

    response = client.chat.completions.create(
        temperature=0.0,
        model="gpt-4o-mini",
        messages=[{
            "role":
            "system",
            "content":
            "Solve the coreference resolution of the following sentences, and replace pronouns or noun phrases with their referents in the text, \
            then return the original text with the replacements applied.\
            第一人稱代名詞 (特別是 '余') 請改成'林獻堂', 別自己亂加名稱",
        }, {
            "role": "user",
            "content": content
        }])

    return response.choices[0].message.content


## 沒有 label 版本，較麻煩
def authority_record():

    df = pd.read_csv('./authority.csv')

    while not df.empty:

        first_evt_label = df.iloc[0]['evtLabel']

        process_df = df[df['evtLabel'] == first_evt_label]

        process_df = process_df.sort_values(
            by=['year', 'month', 'day', 'newEndPos', 'newStartPos'],
            ascending=[True, True, True, False, False])

        new_evt_label = first_evt_label
        last_start_pos = -1
        last_end_pos = -1
        last_len_name = -1

        for index, row in process_df.iterrows():
            start_pos = row['newStartPos']
            end_pos = row['newEndPos']
            name = row['name']
            if start_pos == end_pos:
                new_evt_label = name + '，' + new_evt_label
            elif start_pos == last_start_pos and end_pos == last_end_pos:
                new_evt_label = new_evt_label[:last_start_pos +
                                              last_len_name] + '，' + name + row[
                                                  'evtLabel'][end_pos:]
            elif start_pos == last_start_pos and end_pos < last_end_pos:
                continue
            else:
                new_evt_label = new_evt_label[:
                                              start_pos] + name + new_evt_label[
                                                  end_pos:]
            last_start_pos = start_pos
            last_end_pos = end_pos
            last_len_name = len(name)
            print(new_evt_label)

        with open('result.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # 写入一行数据
            writer.writerow([
                df.iloc[0]['year'], df.iloc[0]['month'], df.iloc[0]['day'],
                new_evt_label
            ])
        df = df[df['evtLabel'] != first_evt_label]


## 有 label， 直接字串比較 & 取代
def have_label():

    df = pd.read_csv('lxt0723.csv')

    def merge_source(df):
        df['date'] = df['year'].astype(str) + '-' + df['month'].astype(
            str) + '-' + df['day'].astype(str)
        df['date'] = df['date'].astype(str)
        df['evtLabel'] = df['evtLabel'].astype(str)

        def merge_sources(sources):
            return ''.join(sorted(sources.unique()))

        grouped = df.groupby('date')['evtLabel'].apply(
            merge_sources).reset_index()
        grouped.columns = ['date', 'source_merged']

        # 將合併後的 source 與原始資料合併
        merged_df = pd.merge(df, grouped, on='date', how='left')

        # 替換原始 source
        merged_df['evtLabel'] = merged_df['source_merged']
        merged_df = merged_df.drop(columns=['source_merged'])

        return merged_df

    df = merge_source(df)

    temp = ''
    date = ''

    for i in df:
        temp = df['date']
        if temp == date:
            date.replace()


have_label()


def te():

    df = pd.read_csv('./result2.csv', encoding='utf-8-sig')
    df = df.assign(date=lambda x: x['year'].astype(str) + '/' + x['month'].
                   astype(str) + '/' + x['day'].astype(str))

    df.to_csv('result3.csv', index=False, encoding='utf-8-sig')
