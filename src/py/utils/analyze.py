from ..netease import netease_database as db
import pandas as pd
from datetime import datetime
def get_generation(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    return str(int(dt.year/10)%10).ljust(2,'0')
def get_hour_minute(timestamp):
    dt=datetime.fromtimestamp(timestamp)
    return f'{str(dt.hour).rjust(2,"0")}:{str(dt.minute).rjust(2,"0")}'
def analyze(database,table):
    data=db.query(database,table,('*',),'')
    comment_time_list=[]
    location_list=[]
    platform_list=[]
    birthday_list=[]
    gender_list=[]
    keywords_lsit=[]
    emotion_list=[]
    for d in data:
        comment_time_list.append(d[2])
        if d[4] !=None and d[4]!='' and d[4]!='未知':
            location_list.append(d[4])
        if d[5] !=None and d[5]!='':
            platform_list.append(d[5])
        if d[7]!=0:
            birthday_list.append(d[7])
        if d[8]!=None and d[8]!='':
            gender_list.append(d[8])
        if d[10]!=None and d[10]!='':
            keywords_lsit.extend(d[10].split('/'))
        if d[11]!=None and d[11]!='':
            emotion_list.append(d[11])
    comment_time=pd.DataFrame(data={'time_tamps':comment_time_list})
    comment_time.insert(1,column='hour_minute',value=comment_time['time_tamps'].apply(get_hour_minute))
    location=pd.Series(data=location_list)
    platform=pd.Series(data=platform_list)
    birthday=pd.DataFrame(data={'time_tamps':birthday_list})
    birthday.insert(1,column='generation',value=birthday['time_tamps'].apply(get_generation))
    gender=pd.Series(data=gender_list)
    keywords=pd.Series(data=keywords_lsit)
    emotion=pd.Series(data=emotion_list)
    return {
        'comment_hour_minute':(comment_time['hour_minute'].value_counts()).to_json(force_ascii=False),
        'location':(location.value_counts()).to_json(force_ascii=False),
        'platform':(platform.value_counts()).to_json(force_ascii=False),
        'generation':(birthday['generation'].value_counts()).to_json(force_ascii=False),
        'gender':(gender.value_counts()).to_json(force_ascii=False),
        'keywords':(keywords.value_counts()).to_json(force_ascii=False),
        'emotion':(emotion.value_counts()).to_json(force_ascii=False)
    }
