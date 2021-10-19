# #!/usr/bin/env python
# # coding: utf-8
#
# # In[36]:
#
#
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import linearmodels as plm
import numpy as np
import joblib

# # In[6]:
#
#
# data = pd.read_excel(r"./factors_new.xlsx", sheet_name=None, index_col=0, parse_dates=True)
# fundsdata15=pd.read_excel(r"./2015-2020historyfunds.xlsx", sheet_name=None, index_col=0, parse_dates=True)
#
#
# # In[7]:
#
#
# #开始学习月度实证的过程
#
# index=data["index"]
#
#
# # 指数日频变月频
# index_month = index.resample('1M').last()
# # 指数月度收益率
# indexret_month = index_month.pct_change()
#
# # 分离bondfactor中的到期收益率数据和指数数据
# bondfactor=data["bondfactor"]
# bondindex=bondfactor[["one-three","seven-ten","tenplus","AAA","AA+","AA","CD","HY","HQ"]]
# bondret=bondfactor[["term1m","term1y","term3y","term10y","AA3y","AAA1y","AAA-1y","AA+1y","AA1y","AA-1y","CD1y"]]
# #债券指数日频变月频
# bondindex_month=bondindex.resample('1m').last()
# #求取指数月度收益率
# bondindexret_month = bondindex_month.pct_change()
# #求取到期收益率的月度平均值
# bondret_month =  bondret.resample('1M').mean()/1200
#
# #做term和credit的差值
# bondret_month["term2"]=bondret_month["term10y"]-bondret_month["term1y"]
# bondret_month["credit2"]=bondret_month["AA1y"]-bondret_month["CD1y"]
# bondret_month["dterm"]=bondret_month["term2"].pct_change()
# bondret_month["dcredit"]=bondret_month["credit2"].pct_change()
#
# #将指数收益率拼接
# allindexret_month=indexret_month.join(bondindexret_month)
#
# #股票市场因子是日度收益率，需要转化为指数再取月度频率
# stockfactor=data["stockfactor"]
# RiskPremium1=stockfactor["RiskPremium1"]
# SMB1=stockfactor["SMB1"]
# HML1=stockfactor["HML1"]
# RiskPremium2=stockfactor["RiskPremium2"]
# SMB2=stockfactor["SMB2"]
# HML2=stockfactor["HML2"]
# RMW2=stockfactor["RMW2"]
# CMA2=stockfactor["CMA2"]
#
# #创造指数，再对指数求收益率：
# xx = (1+RiskPremium1).cumprod()
# RiskPremium1_index=(1+RiskPremium1).cumprod()
#
# RiskPremium1_month=RiskPremium1_index.resample('1M').last()
# RiskPremium1ret_month=RiskPremium1_month.pct_change()
# SMB1_index=(1+SMB1).cumprod()
# SMB1_month=SMB1_index.resample('1m').last()
# SMB1ret_month=SMB1_month.pct_change()
# HML1_index=(1+HML1).cumprod()
# HML1_month=HML1_index.resample('1m').last()
# HML1ret_month=HML1_month.pct_change()
# RiskPremium2_index=(1+RiskPremium2).cumprod()
# RiskPremium2_month=RiskPremium2_index.resample('1M').last()
# RiskPremium2ret_month=RiskPremium2_month.pct_change()
# SMB2_index=(1+SMB2).cumprod()
# SMB2_month=SMB2_index.resample('1m').last()
# SMB2ret_month=SMB2_month.pct_change()
# HML2_index=(1+HML2).cumprod()
# HML2_month=HML2_index.resample('1m').last()
# HML2ret_month=HML2_month.pct_change()
# RMW2_index=(1+RMW2).cumprod()
# RMW2_month=RMW2_index.resample('1m').last()
# RMW2ret_month=RMW2_month.pct_change()
# CMA2_index=(1+CMA2).cumprod()
# CMA2_month=CMA2_index.resample('1m').last()
# CMA2ret_month=CMA2_month.pct_change()
# #建立一个新的dataframe来做月度收益率数据的存放
# stockfactor_month=[]
# stockfactor_month=pd.DataFrame(list(zip(RiskPremium1ret_month,SMB1ret_month,HML1ret_month,RiskPremium2ret_month,SMB2ret_month,HML2ret_month,
#                                        RMW2ret_month,CMA2ret_month)))
# stockfactor_month.columns=["RiskPremium1ret_month","SMB1ret_month","HML1ret_month","RiskPremium2ret_month","SMB2ret_month","HML2ret_month",
#                                        "RMW2ret_month","CMA2ret_month"]
# stockfactor_month.index=RiskPremium1ret_month.index
#
# #carhart因子整理
# carhart=data["carhart"]
# carhart.index=stockfactor_month.index
# allindexret_month.head()
#
#
# # In[8]:
#
#
# #第一步：单因子（仅有股票市场超额收益率作为因子）
# #先以2015年之前成立的基金来做，剔除第一行空值
# def step1(fund_sheetname, allindexret_month, bondret_month, start='2015-02-28', end='2020-12-31'):
#     # 分组
#     fund = fundsdata15[fund_sheetname]
#     # 基金日频变月频
#     fund_month = fund.resample('1M').last()
#     # 混合型基金月度收益率
#     fundret_month = fund_month.pct_change()
#     # 时间范围
#     fundret_month = fundret_month.loc[start:end]
#     allindexret_month = allindexret_month.loc[start:end]
#     bondret_month = bondret_month.loc[start:end]
#     # 解释变量矩阵
#     X = pd.DataFrame({'stock-rf':stockfactor_month['RiskPremium1ret_month'].loc[start:end]
#                       })
#     X = sm.add_constant(X)
#     # 结果存储 列为值 行为混合型基金
#     df_1 = pd.DataFrame(columns=['alpha', 'b1',
#                                  'adj_r2', 'alpha_pvalue',
#                                  'b1_pvalue'],
#                         index=fundret_month.columns)
#     for fund in fundret_month.columns:
#         # 基金超额收益率
#
#         y = fundret_month[fund] - bondret_month['term1m']
#         y=y.stack()
#         # 异方差稳健标准误
#         result = plm.PanelOLS(y, X).fit(entity_effects=True,time_effects=True,cov_type='heteroskedastic')
#         # 截距
#         df_1.loc[fund, 'alpha'] = result.params['const']
#         df_1.loc[fund, 'alpha_pvalue'] = result.pvalues['const']
#         # 斜率
#         df_1.loc[fund, 'b1'] = result.params['stock-rf']
#         df_1.loc[fund, 'b1_pvalue'] = result.pvalues['stock-rf']
#         # r方
#         df_1.loc[fund, 'r2'] = result.rsquared
#         df_1.loc[fund, 'adj_r2'] = result.rsquared_adj
#
#     return df_1
#
#
# # In[9]:
#
#
# help(plm.PanelOLS)
#
#
# # 核心诉求是：对于 fund fund1 fund2 fund3 fund4 分别做面板数据回归，收益率还是用月度的，时间固定效应以年为单位，同时固定时间效应和个体效应
# # 被解释变量是 那些个fund的数据  - bondret_month['term1m']
# #
# # 然后解释变量的形式为如下三个：X_s1、X1、X2、X3
# #
# # 希望输出的结果：
# # （1）结构处理好的面板数据
# # （2）对于各个  fund的回归结果
#
# # In[19]:
#
#
# start='2015-02-28'
# end='2020-12-31'
#
# def monthret(fund_sheetname,start,end):
#  # 分组
#     fund = fundsdata15[fund_sheetname]
#     # 基金日频变月频
#     fund_month = fund.resample('1M').last()
#     # 混合型基金月度收益率
#     fundret_month = fund_month.pct_change()
#     #截取有效的区间
#     #fundret_month = fundret1_month.loc[start:end]
#
#     return fundret_month
#
#
# # In[20]:
#
#
# # monthret('fund1')
# fund0 = fundsdata15['fund']
# fund0_month = fund0.resample('1M').last()
# fund0ret_month = fund0_month.pct_change()
# fund0ret_month.head()
#
# fund1 = fundsdata15['fund1']
# fund1_month = fund1.resample('1M').last()
# fund1ret_month = fund1_month.pct_change()
# fund1ret_month.head()
#
# fund2 = fundsdata15['fund2']
# fund2_month = fund2.resample('1M').last()
# fund2ret_month = fund2_month.pct_change()
# fund2ret_month.head()
#
# fund3 = fundsdata15['fund3']
# fund3_month = fund3.resample('1M').last()
# fund3ret_month = fund3_month.pct_change()
# fund3ret_month.head()
#
# fund4 = fundsdata15['fund3']
# fund4_month = fund4.resample('1M').last()
# fund4ret_month = fund4_month.pct_change()
# fund4ret_month.head()
#
#
# # In[23]:
#
#
# dict_monthret = {} #创造一个空字典存放step1的结果
# for fund_sheetname in ['fund','fund1', 'fund2', 'fund3', 'fund4']:
#     dict_monthret[fund_sheetname] = monthret(fund_sheetname,start='2015-02-28', end='2020-12-31')
#     dict_monthret[fund_sheetname].to_csv(f'{fund_sheetname}_monthret.csv')
#
#
# # In[35]:
#
#
#
#
#
# #
#
# # In[26]:
#
#
# start='2015-02-28'
# end='2020-12-31'
#
#
#
#
#
# X1 = pd.DataFrame({'stock-rf':stockfactor_month['RiskPremium1ret_month'].loc[start:end],
#                       'SMB1':stockfactor_month['SMB1ret_month'].loc[start:end],
#                       'HML1':stockfactor_month['HML1ret_month'].loc[start:end]
#                       })
# time = X1.index.tolist()
# ind = []
# for i  in range(len(time)):
#     ind.append(i)
# X1['Company'] = ind
# X1['Time'] = time
# X1=X1.set_index(['Company','Time'])
#
# X1 = sm.add_constant(X1)
#
# X2 = pd.DataFrame({'stock-rf':stockfactor_month['RiskPremium1ret_month'].loc[start:end],
#                       'SMB1':stockfactor_month['SMB1ret_month'].loc[start:end],
#                       'HML1':stockfactor_month['HML1ret_month'].loc[start:end],
#                       'longterm':allindexret_month['tenplus'].loc[start:end]-bondret_month['term1m'].loc[start:end],
#                       'shortterm':allindexret_month['one-three'].loc[start:end]-bondret_month['term1m'].loc[start:end],
#                       'lowquality':allindexret_month['HY'].loc[start:end]-bondret_month['term1m'].loc[start:end],
#                       'convertible':allindexret_month['convertible'].loc[start:end]-bondret_month['term1m'].loc[start:end]
#                       })
#
# X2 = sm.add_constant(X2)
#
# X3 = pd.DataFrame({'stock-rf':stockfactor_month['RiskPremium1ret_month'].loc[start:end],
#                       'SMB1':stockfactor_month['SMB1ret_month'].loc[start:end],
#                       'HML1':stockfactor_month['HML1ret_month'].loc[start:end],
#                       'cbci-rf':allindexret_month['cbci'].loc[start:end]-bondret_month['term1m'].loc[start:end],
#                       'term':allindexret_month["tenplus"].loc[start:end]-allindexret_month['one-three'].loc[start:end],
#                       'credit':allindexret_month['AA'].loc[start:end]-allindexret_month['CD'].loc[start:end],
#                       'convertible':allindexret_month['convertible'].loc[start:end]-bondret_month['term1m'].loc[start:end]
#                       })
# time = X3.index.tolist()
# ind = []
# for i  in range(len(time)):
#     ind.append(i)
# X3['Company'] = ind
# X3['Time'] = time
# X3=X3.set_index(['Company','Time'])
# X3 = sm.add_constant(X3)
#
# X1.to_csv("Fama3.csv")
# X2.to_csv("Fama3+index.csv")
# X3.to_csv('Fama3+gap.csv')
#
#
# # In[27]:
#
#
# fund0ret_month.to_csv("fund.csv")
# fund1ret_month.to_csv("fund1.csv")
# fund2ret_month.to_csv("fund2.csv")
# fund3ret_month.to_csv("fund3.csv")
# fund4ret_month.to_csv("fund4.csv")
#
#
# # In[ ]:
#
# #构建解释变量矩阵
# start='2015-02-28'
# end='2020-12-31'
# y = fund1ret_month.loc[start:end]
# z = list (fund1ret_month.columns.values)
# # X_s1 = pd.DataFrame({'stock-rf':stockfactor_month['RiskPremium1ret_month'].loc[start:end]})
# # X_s1 = sm.add_constant(X_s1)
# #
# # # X_s1 = X_s1.T
# # # X_s1 = X_s1.stack()
#
#
# # ind = []
# #
# # y['Company'] = z#将每个公司的名字加进去
# # y['Time'] = time
# # y=y.set_index(['Company','Time'])
# #
# # names = list(y.columns.values)
# joblib.dump(y,'./y_data')
# joblib.dump(X1,'./x_data')

import time, datetime
def hh(data):

    timeArray = time.strptime(str(data), "%Y-%m-%d %H:%M:%S")
    # data = int(time.strftime("%Y%m%d", timeArray))#月
    data = int(time.strftime("%Y", timeArray))#年
    return data
y = joblib.load('./y_data')
x = joblib.load('./x_data')

names = list (y.columns.values)
company = [ names[0] for i in range(x.shape[0])]
x_ = x

x_['Company'] = company
x_['y']  = y[names[0]].tolist()
x_['Time'] = y.index.tolist()
x_['Time'] = x_['Time'].apply(hh)
x_['Time'] = x_['Time'].astype('int64')
x_=x.set_index(['Company','Time'])




for i in range(1,len(names)):
    xx = x
    xx['Company'] = [ names[i] for j in range(x.shape[0])]
    xx['y'] = y[names[i]].tolist()
    xx['Time'] = y.index.tolist()
    xx['Time'] = xx['Time'].apply(hh)
    xx['Time'] = xx['Time'].astype('int64')
    xx = x.set_index(['Company', 'Time'])
    x_ = pd.concat([x_, xx], axis=0, ignore_index=False)  # 拼接表格

# x1 = x_.iloc[:,:-1]
x = sm.add_constant(x_[['stock-rf','SMB1','HML1']])
y = x_.iloc[:,-1]
from linearmodels.panel import PanelOLS

mod1 = PanelOLS(y, x,entity_effects=True,time_effects=True )
res1=mod1.fit(cov_type='clustered', cluster_entity=True)
print(res1.summary)

