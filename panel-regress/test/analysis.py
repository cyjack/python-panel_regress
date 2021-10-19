import pandas as pd
import numpy as np

#==========================Clean Frame========================
data=pd.read_excel('data of dissertation.xlsx',
                   sheet_name='Sheet1')

data['class']=data.iloc[:,0].map(lambda x:x.split()[0])
data['time']=data.iloc[:,0].map(lambda x:x.split()[2])

def trans(x):
    if '一季' in x:
        x=x.replace('一季','0331')
    elif '中报' in x:
        x=x.replace('中报','0630')
    elif '三季' in x:
        x=x.replace('三季','0930')
    else:
        x=x.replace('年报','1231')
    return x

data['time']=data['time'].map(trans)

data=data.iloc[:,1:]
data1=data.set_index(['class','time'])
data2=data1.unstack().T
data3=data2.reset_index()

data3.columns=['证券代码', '时间', '一年内到期的非流动负债', '以公允价值计量且其变动计入当期损益的金融负债',
       '企业自由现金流量FCFF', '净利润', '固定资产净额', '存货净额', '应付债券', '当日总市值/负债总计',
       '所有者权益合计', '未分配利润', '流动负债合计', '盈余公积金', '短期借款', '衍生金融负债', '负债合计', '资产总计',
       '长期借款', '非流动负债合计']

clean=data3.copy()
#=======================Process for NAN======================================================
drop_subset=['资产总计','负债合计','所有者权益合计','未分配利润',
             '盈余公积金','流动负债合计','非流动负债合计',
             '当日总市值/负债总计','企业自由现金流量FCFF',
             '固定资产净额','存货净额']
clean=clean.dropna(subset=drop_subset,how='any',axis=0)
#=======================Merge with hp results==============================================
hp=pd.read_csv('hp.csv')
clean['时间']=clean['时间'].astype('int64')
clean=pd.merge(clean,hp,left_on='时间',right_on='Time',how='left')
clean=clean[clean['当日总市值/负债总计']!=' ']
#========================Separate dataset by===============================================
company=list(clean['证券代码'].value_counts().index)
subset=[]
for i in company:
    subset.append(clean[clean['证券代码']==i])
#=========================Compute function================================================
def compute_add(data):
    data_lag=data.shift(1)
    data_add=data-data_lag
    return data_add

def compute(data):
    data['v8']=data['资产总计'].shift(1)
    data['v11']=compute_add(data['短期借款'])
    data['v4']=compute_add(data['长期借款'])
    data['v13']=compute_add(data['一年内到期的非流动负债'])
    data['v7']=compute_add(data['应付债券'])
    data['DEBT1']=(data['v11']+data['v4']+data['v13']+data['v7'])/data['v8']
    data['v1']=compute_add(data['负债合计'])
    data['DEBT2']=data['v1']/data['v8']
    data['v2']=compute_add(data['所有者权益合计'])
    data['v16']=compute_add(data['未分配利润'])
    data['v9']=compute_add(data['盈余公积金'])
    data['Equity1']=(data['v2']-data['v16']-data['v9'])/data['v8']
    data['Equity2']=data['v2']/data['v8']
    data['v14']=compute_add(data['流动负债合计'])
    data['SL']=data['v14']/data['v8']
    data['v10']=compute_add(data['非流动负债合计'])
    data['LL']=data['v10']/data['v8']
    data['v11']=compute_add(data['短期借款'])
    data['v5']=compute_add(data['以公允价值计量且其变动计入当期损益的金融负债'])
    data['v15']=compute_add(data['衍生金融负债'])
    data['FL']=(data['v10']+data['v11']+data['v13']+data['v5']+data['v15'])/data['v8']
    data['OL']=(data['v14']-data['v11']-data['v13']-data['v5']-data['v15'])/data['v8']
    data['v6']=compute_add(data['企业自由现金流量FCFF'])
    data['CF']=data['v6']/data['v8']
    data['CA']=(data['存货净额']+data['固定资产净额'])/data['v8']
    data['Scale']=data['资产总计'].map(np.log)
    data['ROA']=data['净利润']/data['v8']
    data['Cycle']=data['Cycle factor']
    data['Cycle*CF']=data['Cycle'].mul(data['CF'])
    data['Cycle*CA']=data['Cycle'].mul(data['CA'])
    data['Q']=(data['当日总市值/负债总计'].astype('float')*data['负债合计'])/data['资产总计']
    data['Q']=data['Q'].map(np.log)
    data['Cycle*Q']=data['Cycle'].mul(data['Q'])
    Final=data[['证券代码', '时间','DEBT1', 'DEBT2', 'Equity1', 'Equity2', 'SL', 'LL', 'FL', 'OL','Q',
       'CF', 'CA','Cycle','Cycle*Q','Cycle*CF','Cycle*CA','ROA','Scale']]
    Final.columns=['Company', 'Time','Debt1', 'Debt2', 'Equity1', 'Equity2', 'SL', 'LL', 'FL', 'OL','Q',
       'CF', 'CA','Cycle','Cycle*Q','Cycle*CF','Cycle*CA','ROA','Scale']
    Final.fillna(0,inplace=True)
    return Final.iloc[1:,:]
#======================loop for all company======================================================
subset=[compute(i) for i in subset]
subset=subset[:294]
analysis=pd.concat(subset,axis=0)
analysis.to_csv('analysis.csv',index=False)

#========================Model===================================================================
from linearmodels.panel import PanelOLS
from linearmodels.panel import RandomEffects
import statsmodels.api as sm

#表4-4
data=analysis.set_index(['Company','Time'])
dependent1=data['Debt1']
dependent2=data['Equity1']
dependent3=data['FL']
dependent4=data['OL']
dependent5=data['SL']
dependent6=data['LL']
dependent7=data['Debt2']
dependent8=data['Equity2']

exog1=sm.add_constant(data[['Q','CF','CA']])
exog2=sm.add_constant(data[['Q','CF', 'CA','Cycle*Q','Cycle*CF','Cycle*CA','ROA','Scale']])
exog3=sm.add_constant(data[['Q','CF', 'CA','Cycle','Cycle*Q','Cycle*CF','Cycle*CA','ROA','Scale']])


mod1=PanelOLS(dependent1, exog1,entity_effects=True,time_effects=True)
res1=mod1.fit(cov_type='clustered', cluster_entity=True)
print(res1.summary)

mod2=PanelOLS(dependent2, exog1,entity_effects=True,time_effects=True)
res2=mod2.fit(cov_type='clustered', cluster_entity=True)
res2.summary


mod3=PanelOLS(dependent1, exog2,entity_effects=True,time_effects=True)
res3=mod3.fit(cov_type='clustered', cluster_entity=True)
res3.summary

mod4=PanelOLS(dependent2, exog2,entity_effects=True,time_effects=True)
res4=mod4.fit(cov_type='clustered', cluster_entity=True)
res4.summary

#表4-5

mod5=PanelOLS(dependent3, exog1,entity_effects=True,time_effects=True)
res5=mod5.fit(cov_type='clustered', cluster_entity=True)
res5.summary

mod6=PanelOLS(dependent4, exog1,entity_effects=True,time_effects=True)
res6=mod6.fit(cov_type='clustered', cluster_entity=True)
res6.summary

mod7=PanelOLS(dependent3, exog2,entity_effects=True,time_effects=True)
res7=mod7.fit(cov_type='clustered', cluster_entity=True)
res7.summary

mod8=PanelOLS(dependent4, exog2,entity_effects=True,time_effects=True)
res8=mod8.fit(cov_type='clustered', cluster_entity=True)
res8.summary

#表4-6
mod9=PanelOLS(dependent5, exog1,entity_effects=True,time_effects=True)
res9=mod9.fit(cov_type='clustered', cluster_entity=True)
res9.summary

mod10=PanelOLS(dependent6, exog1,entity_effects=True,time_effects=True)
res10=mod10.fit(cov_type='clustered', cluster_entity=True)
res10.summary

mod11=PanelOLS(dependent5, exog2,entity_effects=True,time_effects=True)
res11=mod11.fit(cov_type='clustered', cluster_entity=True)
res11.summary

mod12=PanelOLS(dependent6, exog2,entity_effects=True,time_effects=True)
res12=mod12.fit(cov_type='clustered', cluster_entity=True)
res12.summary

#表4-7
mod13=RandomEffects(dependent1, exog2)
res13=mod13.fit(cov_type='clustered', cluster_entity=True)
res13.summary

mod14=RandomEffects(dependent2, exog2)
res14=mod14.fit(cov_type='clustered', cluster_entity=True)
res14.summary

mod15=RandomEffects(dependent7, exog3)
res15=mod15.fit(cov_type='clustered', cluster_entity=True)
res15.summary

mod16=RandomEffects(dependent8, exog3)
res16=mod16.fit(cov_type='clustered', cluster_entity=True)
res16.summary

#表4-14
mod17=PanelOLS(dependent1, exog2,entity_effects=True,time_effects=True)
res17=mod17.fit(cov_type='clustered', cluster_entity=True)
res17.summary

mod18=PanelOLS(dependent2, exog2,entity_effects=True,time_effects=True)
res18=mod18.fit(cov_type='clustered', cluster_entity=True)
res18.summary

mod19=PanelOLS(dependent7, exog2,entity_effects=True,time_effects=True)
res19=mod19.fit(cov_type='clustered', cluster_entity=True)
res19.summary

mod20=PanelOLS(dependent8, exog2,entity_effects=True,time_effects=True)
res20=mod20.fit(cov_type='clustered', cluster_entity=True)
res20.summary
















    
    
