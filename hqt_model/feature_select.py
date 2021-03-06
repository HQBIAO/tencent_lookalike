import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import OneHotEncoder,LabelEncoder
from scipy import sparse
from sklearn.linear_model import LogisticRegression,SGDClassifier
#from scikitplot.metrics import plot_roc_curve
from sklearn.metrics import roc_auc_score,roc_curve
from sklearn.externals import joblib
import os
from datetime import datetime
import re
from operator import sub,add
import matplotlib.pyplot as plt
from sklearn import grid_search

def sub_to_other(x):
    x_split=x.split(" ")
    set_tmp=set(map(int,x_split))
    intersec=list(set_tmp & target_set)
    if intersec:
        for target in intersec:
            x_split[x_split.index(str(target))]='other'  
    return ' '.join(x_split)

def plot_cv_train_auc_stdv(x,y):
    plt.figure()
    plt.title("AUC")
    max_value=max(x)
    max_index=x.index(max_value)
    max_value=round(max_value,8)
    print max_value
    show_max=str(max_value)
    mead_sub=map(sub,x,y)
    mead_add=map(add,x,y)
    plt.plot(x,'b--')
    plt.plot(mead_add,'r--')
    plt.plot(mead_sub,'r--')
    plt.plot(max_index,max_value,'gs')
    plt.annotate(show_max,xytext=(max_index,max_value),xy=(max_index,max_value))
    plt.show()
def plot_cv_valid_auc_stdv(x,y):
    plt.figure()
    plt.title("AUC")
    max_value=max(x)
    max_index=x.index(max_value)
    max_value=round(max_value,8)
    print max_value
    show_max=str(max_value)
    mead_sub=map(sub,x,y)
    mead_add=map(add,x,y)
    plt.plot(x,'b--')
    plt.plot(mead_add,'r--')
    plt.plot(mead_sub,'r--')
    plt.plot(max_index,max_value,'gs')
    plt.annotate(show_max,xytext=(max_index,max_value),xy=(max_index,max_value))
    plt.show()
def count_value(x):
    if x=='-1' or x==-1:
        return int(x)
    else:
        split_tmp=x.split(' ')
        return len(split_tmp)

def cv_valid():
    global test_cv_valid
    gbm_valid_data=lgb.Dataset(data_x_valid,y_valid.values.ravel())
    test_cv_valid=lgb.cv(tree_paramas,gbm_valid_data,num_boost_round=1000,metrics='auc',seed=20180512，early_stopping_rounds=100)
    x=test_cv_valid['auc-mean']
    y=test_cv_valid['auc-stdv']
    plot_cv_valid_auc_stdv(x,y)
def cv_train():
    global test_cv_train
    gbm_train_data=lgb.Dataset(data_x_train,y_train.values.ravel())
    test_cv_train=lgb.cv(tree_paramas,gbm_train_data,num_boost_round=1000,metrics='auc',seed=20180512,early_stopping_rounds=100)
    x=test_cv_train['auc-mean']
    y=test_cv_train['auc-stdv']
    plot_cv_train_auc_stdv(x,y)

def corr_2(x):
    return str(x[0])+' '+str(x[1])

run_day=datetime.now().strftime('%m%d%H%M%S')
save_path="/home/heqt/tencent/"+run_day+"/"
if not os.path.exists(save_path):
    os.makedirs(save_path)

#data_fit=pd.read_csv('/home/heqt/tencent/train_all.csv')
#data_test=pd.read_csv('/home/heqt/tencent/test1_all.csv')
#data_fit.loc[data_fit['label']==-1,'label']=0
#data_test.insert(2,'label',-1)
#data_x=pd.concat([data_fit,data_test])
#data_x.to_csv('/home/heqt/tencent/data_all.csv',index=None)
data_x=pd.read_csv('/home/heqt/tencent/data_all.csv')
data_x.fillna('-1',inplace=True)


#fit_model
#one_hot_feature=['lbs','age','carrier','consumptionability','education','gender','house','os','ct','marriagestatus','advertiserid','campaignid', 'creativeid',
#      'adcategoryid', 'creativesize','productid', 'producttype']
one_hot_feature=['producttype','age','creativesize','gender','consumptionability','os','marriagestatus','adcategoryid','carrier','ct','education']
#vector_feature=['appidaction','appidinstall','interest1','interest2','interest3','interest4','interest5','kw1','kw2','kw3','topic1','topic2','topic3']
vector_feature=['interest2']

df_feature_map=pd.DataFrame()
LE=LabelEncoder()
for feature in one_hot_feature:
    try:
        data_x[feature]=LE.fit_transform(data_x[feature].map(np.int))

    except:
        data_x[feature]=LE.fit_transform(data_x[feature])
    #feature important mapping
    finally:
        df_tmp=pd.DataFrame(LE.classes_,columns=['val'])
        df_tmp['feature']='%s' %feature
        df_feature_map=pd.concat([df_feature_map,df_tmp])

print 'LabelEncoder finish'

data_fit=data_x[data_x.label!=-1]
data_y=data_fit.pop('label')
#data_test=data_x[data_x.label==-1]

x_train,x_valid_2,y_train,y_valid= train_test_split(data_fit,data_y,test_size=0.2, random_state=20180505)
x_train,x_valid,y_train,y_valid= train_test_split(x_valid_2,y_valid,test_size=0.3, random_state=20180506)

data_x_train=pd.DataFrame()
data_x_valid=pd.DataFrame()
#data_x_test=pd.DataFrame()
OHE=OneHotEncoder()
for feature in one_hot_feature:
    OHE.fit(x_valid_2[feature].values.reshape(-1,1))
    train_a=OHE.transform(x_train[feature].values.reshape(-1,1))
    valid_a=OHE.transform(x_valid[feature].values.reshape(-1,1))
    #test_a=OHE.transform(data_test[feature].values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #data_x_test=sparse.hstack((data_x_test,test_a))
print 'one_hot finish'
CVec=CountVectorizer(analyzer='word',token_pattern=r'(?u)\b\w+\b',tokenizer =lambda x: x.split(' '))
#CVec=CountVectorizer()
for feature in vector_feature:
    CVec.fit(x_valid_2[feature])
    train_a=CVec.transform(x_train[feature])
    valid_a=CVec.transform(x_valid[feature])
    #test_a=CVec.transform(data_test[feature])
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #data_x_test=sparse.hstack((data_x_test,test_a))
    df_tmp=pd.DataFrame(CVec.get_feature_names(),columns=['val'])
    #feature important mapping
    df_tmp['feature']='%s' %feature
    df_feature_map=pd.concat([df_feature_map,df_tmp])
print ' countvec finish'
df_feature_map.to_csv(save_path+"feature_important_mapping.csv")

#sparse.save_npz(save_path+"data_x_train.npz",data_x_train)
#y_train.to_csv(save_path+"data_y_train.csv",index=None)

#sparse.save_npz(save_path+"data_x_valid.npz",data_x_valid)
#y_valid.to_csv(save_path+"data_y_valid.csv",index=None)

#sparse.save_npz(save_path+"data_x_test.npz",data_x_test)
#result=data_test[['aid','uid']]
#result.to_csv(save_path+"result.csv",index=None)

gbm_clf = lgb.LGBMClassifier(
        boosting_type='gbdt', num_leaves=31, reg_alpha=0.0, reg_lambda=1,
        max_depth=-1, n_estimators=300, objective='binary',
        subsample_freq=1,
        learning_rate=0.02, min_child_weight=50,random_state=20180505,n_jobs=3)

parama={'bin_feature':'appidaction',
        'top_N':100
        }

def aotu_bin(parama):
    global target_set
    file_path='/home/heqt/tencent/countvec/'+str(parama['bin_feature'])+'.csv'
    df_cut=pd.read_csv(file_path,header=None,names=['feature_value','import_value'])
    df_cut_m1=df_cut.loc[df_cut['feature_value']==-1]
    df_cut_nm1=df_cut.loc[df_cut['feature_value']!=-1]
    #prevente top_N less than default
    top_N=min(parama['top_N'],df_cut_nm1.shape[0])
    print top_N
    steps=0
    df_cut_inf=pd.DataFrame(columns=['cut_num','valid_0','valid_1'])
    while top_N>0:
        if steps==0:
            CVec.fit(x_valid_2[parama['bin_feature']])
            train_a=CVec.transform(x_train[parama['bin_feature']])
            valid_a=CVec.transform(x_valid[parama['bin_feature']])
            data_x_train_top=sparse.hstack((data_x_train,train_a))
            data_x_valid_top=sparse.hstack((data_x_valid,valid_a))
        elif steps ==1:
            df_cut_indic=df_cut_nm1.sort_values(by='import_value',ascending=False)[top_N:].feature_value.tolist()
            target_set=set(df_cut_indic)
            x_valid_2[parama['bin_feature']]=x_valid_2[parama['bin_feature']].apply(sub_to_other)
            x_train[parama['bin_feature']]=x_train[parama['bin_feature']].apply(sub_to_other)
            x_valid[parama['bin_feature']]=x_valid[parama['bin_feature']].apply(sub_to_other)
            CVec.fit(x_valid_2[parama['bin_feature']])
            train_a=CVec.transform(x_train[parama['bin_feature']])
            valid_a=CVec.transform(x_valid[parama['bin_feature']])
            data_x_train_top=sparse.hstack((data_x_train,train_a))
            data_x_valid_top=sparse.hstack((data_x_valid,valid_a))
        else:
            df_cut_indic=df_cut_nm1.sort_values(by='import_value',ascending=False).iloc[top_N].feature_value
            parten='\\b'+str(df_cut_indic)+'\\b'
            x_valid_2[parama['bin_feature']]=x_valid_2[parama['bin_feature']].apply(lambda x: re.sub(parten,'other',x))
            x_train[parama['bin_feature']]=x_train[parama['bin_feature']].apply(lambda x: re.sub(parten,'other',x))
            x_valid[parama['bin_feature']]=x_valid[parama['bin_feature']].apply(lambda x: re.sub(parten,'other',x))
            CVec.fit(x_valid_2[parama['bin_feature']])
            train_a=CVec.transform(x_train[parama['bin_feature']])
            valid_a=CVec.transform(x_valid[parama['bin_feature']])
            data_x_train_top=sparse.hstack((data_x_train,train_a))
            data_x_valid_top=sparse.hstack((data_x_valid,valid_a))

        eval_list=[(data_x_train_top,y_train),(data_x_valid_top,y_valid)]
        gbm_clf.fit(data_x_train,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)

        if top_N%10==0:
            print 'gmb_finish','----->',top_N
        #save cut_information
        df_inf_tmp=pd.DataFrame([top_N+1],columns=['cut_num'])
        df_inf_tmp['valid_0']=gbm_clf.best_score_['valid_0']['auc']
        df_inf_tmp['valid_1']=gbm_clf.best_score_['valid_1']['auc']
        df_cut_inf=pd.concat([df_cut_inf,df_inf_tmp])
        steps+=1
        top_N-=1
    df_cut_inf.to_csv(save_path+str(parama['bin_feature'])+"cut_information.csv",index=None)


#after cut,feature ennerging

def sub_to_other(x):
    x_split=x.split(" ")
    set_tmp=set(map(int,x_split))
    intersec=list(set_tmp & target_set)
    if intersec:
        for target in intersec:
            x_split[x_split.index(str(target))]='other'  
    return ' '.join(x_split)


save_path="/home/heqt/tencent/"+"ennerging_feature"+"/"
if not os.path.exists(save_path):
    os.makedirs(save_path)

data_fit=pd.read_csv('/home/heqt/tencent/train_all.csv')
data_fit.loc[data_fit['label']==-1,'label']=0
data_y=data_fit.pop('label')
x_train,x_valid_2,y_train,y_valid= train_test_split(data_fit,data_y,test_size=0.1, random_state=201805)

x_valid_2.insert(2,'label',y_valid)
data_fit=x_valid_2
data_test=pd.read_csv('/home/heqt/tencent/test1_all.csv')
data_test.insert(2,'label',-1)
data_x=pd.concat([data_fit,data_test])
data_x.fillna('-1',inplace=True)
data_x.to_csv(save_path+"data_x_80W.csv",index=None)

one_hot_feature=['lbs','age','carrier','consumptionability','education','gender','house','os','ct','marriagestatus','advertiserid','campaignid', 'creativeid',
       'adcategoryid', 'creativesize','productid', 'producttype']
vector_feature=['appidaction','appidinstall','interest1','interest2','interest3','interest4','interest5','kw1','kw2','kw3','topic1','topic2','topic3']
bin_feature=['appidaction','appidinstall','kw1','kw2','kw3','topic1','topic2','topic3']

paramas={
'appidaction':266,
'appidinstall':2875,
'kw1':5690,
'kw2':3698,
'kw3':224,
'topic1':6105,
'topic2':5496,
'topic3':309
}
for feature in bin_feature:
    file_path='/home/heqt/tencent/countvec/'+str(feature)+'.csv'
    df_cut=pd.read_csv(file_path,header=None,names=['feature_value','import_value'])
    df_cut_m1=df_cut.loc[df_cut['feature_value']==-1]
    df_cut_nm1=df_cut.loc[df_cut['feature_value']!=-1]
    top_N=paramas[feature]
    df_cut_indic=df_cut_nm1.sort_values(by='import_value',ascending=False)[top_N:].feature_value.tolist()
    target_set=set(df_cut_indic)
    data_x[feature]=data_x[feature].apply(sub_to_other)
    print feature


data_x.to_csv(save_path+"data_x_cut_80W.csv",index=None)


df_feature_map=pd.DataFrame()
LE=LabelEncoder()
for feature in one_hot_feature:
    try:
        data_x[feature]=LE.fit_transform(data_x[feature].map(np.int))

    except:
        data_x[feature]=LE.fit_transform(data_x[feature])
    #feature important mapping
    finally:
        df_tmp=pd.DataFrame(LE.classes_,columns=['val'])
        df_tmp['feature']='%s' %feature
        df_feature_map=pd.concat([df_feature_map,df_tmp])

print 'LabelEncoder finish'

data_fit=data_x[data_x.label!=-1]
data_y=data_fit.pop('label')
data_test=data_x[data_x.label==-1]

x_train,x_valid,y_train,y_valid= train_test_split(data_fit,data_y,test_size=0.3, random_state=20180506)

data_x_train=pd.DataFrame()
data_x_valid=pd.DataFrame()
data_x_test=pd.DataFrame()
OHE=OneHotEncoder()
for feature in one_hot_feature:
    OHE.fit(data_x[feature].values.reshape(-1,1))
    train_a=OHE.transform(x_train[feature].values.reshape(-1,1))
    valid_a=OHE.transform(x_valid[feature].values.reshape(-1,1))
    test_a=OHE.transform(data_test[feature].values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    data_x_test=sparse.hstack((data_x_test,test_a))
print 'one_hot finish'


CVec=CountVectorizer(analyzer='word',token_pattern=r'(?u)\b\w+\b',tokenizer =lambda x: x.split(' '))
#CVec=CountVectorizer()
for feature in vector_feature:
    CVec.fit(data_x[feature])
    train_a=CVec.transform(x_train[feature])
    valid_a=CVec.transform(x_valid[feature])
    test_a=CVec.transform(data_test[feature])
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    data_x_test=sparse.hstack((data_x_test,test_a))
    df_tmp=pd.DataFrame(CVec.get_feature_names(),columns=['val'])
    #feature important mapping
    df_tmp['feature']='%s' %feature
    df_feature_map=pd.concat([df_feature_map,df_tmp])
print ' countvec finish'
df_feature_map.to_csv(save_path+"feature_important_mapping_cut.csv")

sparse.save_npz(save_path+"data_x_train_cut.npz",data_x_train)
x_train.to_csv(save_path+"x_train_cut.csv",index=None)
y_train.to_csv(save_path+"data_y_train_cut.csv",index=None)

sparse.save_npz(save_path+"data_x_valid_cut.npz",data_x_valid)
x_valid.to_csv(save_path+"x_valid_cut.csv",index=None)
y_valid.to_csv(save_path+"data_y_valid_cut.csv",index=None)

sparse.save_npz(save_path+"data_x_test_cut.npz",data_x_test)
result=data_test[['aid','uid']]
result.to_csv(save_path+"result_cut.csv",index=None)
print 'save_cut_finish'

eval_list=[(data_x_train,y_train),(data_x_valid,y_valid)]

gbm_clf = lgb.LGBMClassifier(
        boosting_type='gbdt', num_leaves=31, reg_alpha=0.0, reg_lambda=1,
        max_depth=-1, n_estimators=1000, objective='binary',
        subsample=0.7, colsample_bytree=0.7, subsample_freq=1,
        learning_rate=0.02, min_child_weight=50,random_state=20180506,n_jobs=7)

gbm_clf.fit(data_x_train,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)
joblib.dump(gbm_clf, '/home/heqt/jupyter_project/model/gbm_clf_cnt_80W.pkl')


#交叉类特征

#house特征的-1取值情况影响不大,"os","ct","marriagestatus"影响不大
#feature_important:580,1920,1165,1305,1715,0,0,0,435
corr_feature=["lbs","age","carrier","education","gender","os","ct","marriagestatus","house"]

for feature in corr_feature:
    corr_feature_path='/home/heqt/tencent/corr_feature/'+str(feature)+'_corr_aid.csv'
    df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[feature,'aid','label','feacnt','cnt','corr_ctr'])
    df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
    print "df_cor_fea -----> shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=[feature,'aid'])['corr_ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[feature,'aid'])['corr_ctr']
    print "train_a after shape -------->",train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
    print "--------------------"
#统计兴趣的特征,影响不大
intersec_feature=["interest1","interest2","interest3","interest4","interest5"]
for feature in intersec_feature:

    #intersec_feature_path='/home/heqt/tencent/countvec/interest/'+str(feature)+'_count.csv'
    #df_cor_fea=pd.read_csv(intersec_feature_path,header=None,names=['uid',feature,'cnt'])
    #df_cor_fea[feature]=df_cor_fea[feature].map(str)
    #df_cor_fea['cnt']=df_cor_fea['cnt'].map(np.float)
    #print df_cor_fea.shape
    #print df_cor_fea.head(1)
    train_a=x_train[feature].map(count_value)
    valid_a=x_valid[feature].map(count_value)
    print train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
#统计兴趣与广告的交叉特征：1206, 1493,  627,  579, 1324
intersec_feature=["interest1","interest2","interest3","interest4","interest5"]
for feature in intersec_feature:
    intersec_count_path='/home/heqt/tencent/countvec/interest/'+str(feature)+'_count.csv'
    intersec_feature_path='/home/heqt/tencent/corr_feature/interst/'+str(feature)+'_corr_aid.csv'
    df_cnt_fea=pd.read_csv(intersec_count_path,header=None,names=['uid',feature,feature+'cnt'])
    print 'x_train ----> shape',x_train.shape
    x_train=pd.merge(x_train,df_cnt_fea,how='left',on=['uid',feature])
    x_valid=pd.merge(x_valid,df_cnt_fea,how='left',on=['uid',feature])
    print 'x_train after merge ----> shape',x_train.shape
    print 'x_valid after merge ----> shape',x_valid.shape
    df_cor_fea=pd.read_csv(intersec_feature_path,header=None,names=[feature+'cnt','aid','label','feacnt','to_talcnt','corr_ctr'])
    df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
    df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','to_talcnt'],axis=1)
    print df_cor_fea.shape
    print df_cor_fea.head(1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=[feature+'cnt','aid'])['corr_ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[feature+'cnt','aid'])['corr_ctr']
    print train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
    print '-----------------------------'
#gender交其他特征, [4,    1,    0,  258,  120,    0] :feature important
var_feature='gender'
corr_feature=["advertiserId","campaignId","creativeSize","adCategoryId","productId","productType"]
for feature in corr_feature:
    corr_feature_path="/home/heqt/tencent/corr_feature/"+var_feature+"/"+var_feature+"_corr_"+str(feature)+".csv"
    df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[var_feature,feature.lower(),'label','feacnt','cnt','corr_ctr'])
    df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
    print "df_cor_fea ------>shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=[var_feature,feature.lower()])['corr_ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[var_feature,feature.lower()])['corr_ctr']
    print "train_a ---> shape",train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
    print "-----------------------"
#age 交其他广告特征 7,    0,    0,  280,207, 0
var_feature='age'
corr_feature=["advertiserId","campaignId","creativeSize","adCategoryId","productId","productType"]
for feature in corr_feature:
    corr_feature_path="/home/heqt/tencent/corr_feature/"+var_feature+"/"+var_feature+"_corr_"+str(feature)+".csv"
    df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[var_feature,feature.lower(),'label','feacnt','cnt','corr_ctr'])
    df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
    print "df_cor_fea ------>shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=[var_feature,feature.lower()])['corr_ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[var_feature,feature.lower()])['corr_ctr']
    print "train_a ---> shape",train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
    print "-----------------------"
#其他特征与广告特征交叉,与上面一样，只有"adCategoryId","productId"比较显著,训练模型时不要"lbs","carrier","education","os","ct","marriagestatus","house"
var_features=["gender","age"]
for var_feature in var_features:
    corr_feature=["advertiserId","campaignId","creativeSize","adCategoryId","productId","productType"]
    for feature in corr_feature:
        corr_feature_path="/home/heqt/tencent/corr_feature/"+var_feature+"/"+var_feature+"_corr_"+str(feature)+".csv"
        df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[var_feature,feature.lower(),'label','feacnt','cnt','corr_ctr'])
        df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
        print "df_cor_fea ------>shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
        train_a=pd.merge(x_train,df_cor_fea,how='left',on=[var_feature,feature.lower()])['corr_ctr']
        valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[var_feature,feature.lower()])['corr_ctr']
        print "train_a ---> shape",train_a.shape
        print train_a.head(1)
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
        #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
        #feature important mapping
        #df_tmp['feature']='%s' %feature
        #df_feature_map=pd.concat([df_feature_map,df_tmp])
        print feature
        print "-----------------------"

#性别*(年龄/学历/消费能力/lbs/兴趣/移动营运商/房子)
source_feature=["gender"]
corr_feature=["lbs","age","carrier","education","consumptionability","house","interest1","interest2","interest3","interest4","interest5"]
for source in source_feature:
    for feature in corr_feature:
        corr_feature_path='/home/heqt/tencent/3corr_feature/'+str(source)+"_"+str(feature)+'_corr_aid.csv'
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature+"cnt",'aid','label','feacnt','cnt','corr_ctr'])
        else:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature,'aid','label','feacnt','cnt','corr_ctr'])
        df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            print "excute interest"
        else:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
        print "train_a after shape -------->",train_a.shape
        print train_a.head(1)
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
        #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
        #feature important mapping
        #df_tmp['feature']='%s' %feature
        #df_feature_map=pd.concat([df_feature_map,df_tmp])
        print feature
        print "--------------------"
#年龄*(学历/消费能力/lbs/兴趣/移动营运商/房子)       
source_feature=["age"]
corr_feature=["lbs","carrier","education","consumptionability","house","interest1","interest2","interest3","interest4","interest5"]
for source in source_feature:
    for feature in corr_feature:
        corr_feature_path='/home/heqt/tencent/3corr_feature/'+str(source)+"_"+str(feature)+'_corr_aid.csv'
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature+"cnt",'aid','label','feacnt','cnt','corr_ctr'])
        else:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature,'aid','label','feacnt','cnt','corr_ctr'])
        df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            print "excute interest"
        else:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
        print "train_a after shape -------->",train_a.shape
        print train_a.head(1)
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
        #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
        #feature important mapping
        #df_tmp['feature']='%s' %feature
        #df_feature_map=pd.concat([df_feature_map,df_tmp])
        print feature
        print "--------------------"
#lbs X(学历/消费能力/兴趣/移动营运商/房子)
source_feature=["lbs"]
corr_feature=["carrier","education","consumptionability","house","interest1","interest2","interest3","interest4","interest5"]
for source in source_feature:
    for feature in corr_feature:
        corr_feature_path='/home/heqt/tencent/3corr_feature/'+str(source)+"_"+str(feature)+'_corr_aid.csv'
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature+"cnt",'aid','label','feacnt','cnt','corr_ctr'])
        else:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature,'aid','label','feacnt','cnt','corr_ctr'])
        df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            print "excute interest"
        else:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
        print "train_a after shape -------->",train_a.shape
        print train_a.head(1)
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
        #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
        #feature important mapping
        #df_tmp['feature']='%s' %feature
        #df_feature_map=pd.concat([df_feature_map,df_tmp])
        print feature
        print "--------------------"
#移动营运商 X(学历/消费能力/兴趣/房子)
source_feature=["carrier"]
corr_feature=["education","consumptionability","house","interest1","interest2","interest3","interest4","interest5"]
for source in source_feature:
    for feature in corr_feature:
        corr_feature_path='/home/heqt/tencent/3corr_feature/'+str(source)+"_"+str(feature)+'_corr_aid.csv'
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature+"cnt",'aid','label','feacnt','cnt','corr_ctr'])
        else:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature,'aid','label','feacnt','cnt','corr_ctr'])
        df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            print "excute interest"
        else:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
        print "train_a after shape -------->",train_a.shape
        print train_a.head(1)
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
        #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
        #feature important mapping
        #df_tmp['feature']='%s' %feature
        #df_feature_map=pd.concat([df_feature_map,df_tmp])
        print feature
        print "--------------------"
#消费能力 X(学历/兴趣/房子)
source_feature=["consumptionability"]
corr_feature=["education","house","interest1","interest2","interest3","interest4","interest5"]
for source in source_feature:
    for feature in corr_feature:
        corr_feature_path='/home/heqt/tencent/3corr_feature/'+str(source)+"_"+str(feature)+'_corr_aid.csv'
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature+"cnt",'aid','label','feacnt','cnt','corr_ctr'])
        else:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature,'aid','label','feacnt','cnt','corr_ctr'])
        df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            print "excute interest"
        else:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
        print "train_a after shape -------->",train_a.shape
        print train_a.head(1)
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
        #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
        #feature important mapping
        #df_tmp['feature']='%s' %feature
        #df_feature_map=pd.concat([df_feature_map,df_tmp])
        print feature
        print "--------------------"

#学历 X(兴趣/房子)
source_feature=["education"]
corr_feature=["house","interest1","interest2","interest3","interest4","interest5"]
for source in source_feature:
    for feature in corr_feature:
        corr_feature_path='/home/heqt/tencent/3corr_feature/'+str(source)+"_"+str(feature)+'_corr_aid.csv'
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature+"cnt",'aid','label','feacnt','cnt','corr_ctr'])
        else:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature,'aid','label','feacnt','cnt','corr_ctr'])
        df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            print "excute interest"
        else:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
        print "train_a after shape -------->",train_a.shape
        print train_a.head(1)
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
        #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
        #feature important mapping
        #df_tmp['feature']='%s' %feature
        #df_feature_map=pd.concat([df_feature_map,df_tmp])
        print feature
        print "--------------------"

#房子 X(兴趣)
source_feature=["house"]
corr_feature=["interest1","interest2","interest3","interest4","interest5"]
for source in source_feature:
    for feature in corr_feature:
        corr_feature_path='/home/heqt/tencent/3corr_feature/'+str(source)+"_"+str(feature)+'_corr_aid.csv'
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature+"cnt",'aid','label','feacnt','cnt','corr_ctr'])
        else:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature,'aid','label','feacnt','cnt','corr_ctr'])
        df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            print "excute interest"
        else:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
        print "train_a after shape -------->",train_a.shape
        print train_a.head(1)
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
        #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
        #feature important mapping
        #df_tmp['feature']='%s' %feature
        #df_feature_map=pd.concat([df_feature_map,df_tmp])
        print feature
        print "--------------------"


#统计app个数

app_feature=["appidinstall","appidaction"]
for feature in app_feature:
    #intersec_feature_path='/home/heqt/tencent/countvec/interest/'+str(feature)+'_count.csv'
    #df_cor_fea=pd.read_csv(intersec_feature_path,header=None,names=['uid',feature,'cnt'])
    #df_cor_fea[feature]=df_cor_fea[feature].map(str)
    #df_cor_fea['cnt']=df_cor_fea['cnt'].map(np.float)
    #print df_cor_fea.shape
    #print df_cor_fea.head(1)
    train_a=x_train[feature].map(count_value)
    valid_a=x_valid[feature].map(count_value)
    print train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
#跑genderXage
corr_feature=["lbs","age","carrier","education","gender","os","ct","marriagestatus","house"]
for i in range(len(corr_feature)-1):
    for j in range(i+1,len(corr_feature)):
        var_name=corr_feature[i]+'X'+corr_feature[j]
        print var_name
        x_train[var_name]=x_train[[corr_feature[i],corr_feature[j]]].apply(corr_2,axis=1)
        x_valid[var_name]=x_valid[[corr_feature[i],corr_feature[j]]].apply(corr_2,axis=1)
        print x_train[var_name][0]
        print x_valid[var_name][0]
one_hot_feature=[]
corr_feature=["lbs","age","carrier","education","gender","os","ct","marriagestatus","house"]
for i in range(len(corr_feature)-1):
    for j in range(1,len(corr_feature)):
        var_name=corr_feature[i]+'X'+corr_feature[j]
        one_hot_feature.append(var_name)
x_train['qubie']=1
x_valid['qubie']=0
data_x=pd.concat([x_train,x_valid])
LE=LabelEncoder()
for feature in one_hot_feature:
    try:
        data_x[feature]=LE.fit_transform(data_x[feature].map(np.int))
    except:
        data_x[feature]=LE.fit_transform(data_x[feature])
print "LabelEncoder finish"
x_train=data_x[data_x.qubie==1]
x_valid=data_x[data_x.qubie==0]
data_x.pop('qubie'),x_train.pop('qubie'),x_valid.pop('qubie')


OHE=OneHotEncoder()
data_x_train_1=data_x_train.copy()
data_x_valid_1=data_x_valid.copy()
df_AUC=pd.DataFrame(columns=['var_name','AUC_0','AUC_1'])
for feature in one_hot_feature:
    OHE.fit(data_x[feature].values.reshape(-1,1))
    train_a=OHE.transform(x_train[feature].values.reshape(-1,1))
    valid_a=OHE.transform(x_valid[feature].values.reshape(-1,1))
    print 'train_a ----> one hot--->shape',train_a.shape
    data_x_train=sparse.hstack((data_x_train_1,train_a))
    data_x_valid=sparse.hstack((data_x_valid_1,valid_a))
    eval_list=[(data_x_train,y_train),(data_x_valid,y_valid)]
    gbm_clf.fit(data_x_train,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)

    df_tmp=pd.DataFrame([feature],columns=['var_name'])
    df_tmp['AUC_0']=gbm_clf.best_score_["valid_0"]["auc"]
    df_tmp['AUC_1']=gbm_clf.best_score_["valid_1"]["auc"]
    df_AUC=pd.concat([df_AUC,df_tmp])
    print "data_x_train ---->shape",data_x_train.shape
    print feature
    print "----------------"

#单个兴趣与广告相交：分数没提高，但是重要性有943
sigle_interest=['interest1']
for feature in sigle_interest:
    intersec_feature_path='/home/heqt/tencent/corr_feature/single_corr/interest/'+feature+'_single.csv'
    df_cor_fea=pd.read_csv(intersec_feature_path,header=None,names=['uid','aid',feature+'ctr'])
    print df_cor_fea.shape
    print df_cor_fea.head(1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])[feature+'ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])[feature+'ctr']
    print 'train_a ---> shape',train_a.shape
    print 'train_a --->head(1)',train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
sigle_interest=['interest3','interest4','interest5']
for feature in sigle_interest:
    intersec_feature_path='/home/heqt/tencent/corr_feature/single_corr/'+feature+'_single.csv'
    df_cor_fea=pd.read_csv(intersec_feature_path,header=None,names=['uid','aid',feature+'ctr'])
    print df_cor_fea.shape
    print df_cor_fea.head(1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])[feature+'ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])[feature+'ctr']
    print 'train_a ---> shape',train_a.shape
    print 'train_a --->head(1)',train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature

#appidaction 尝试贝叶斯平滑：效果不是很大
sigle_interest=['appidaction']
for feature in sigle_interest:
    intersec_feature_path='/home/heqt/tencent/corr_feature/single_corr/'+feature+'_single_smoot.csv'
    df_cor_fea=pd.read_csv(intersec_feature_path,header=None,names=['uid','aid',feature+'single',feature+'dianji',feature+'baoguang'])
    print df_cor_fea.shape
    print df_cor_fea.head(1)
    hyper = HyperParam(1, 1)
    hyper.update_from_data_by_FPI(df_cor_fea[feature+'baoguang'], df_cor_fea[feature+'dianji'], 1000, 0.00000001)
    print "alpha and beta",hyper.alpha, hyper.beta
    df_cor_fea[feature+'dianji']=df_cor_fea[feature+'dianji'].map(lambda x: x+hyper.alpha)
    df_cor_fea[feature+'baoguang']=df_cor_fea[feature+'baoguang'].map(lambda x: x+hyper.alpha+hyper.beta) 
    df_cor_fea[feature+'ctr']=df_cor_fea[[feature+'dianji',feature+'baoguang']].apply(lambda x:1-x[0]/x[1],axis=1)
    df_cor_fea_2=df_cor_fea.groupby(by=['uid','aid'])[feature+'ctr'].apply(lambda x:np.exp(sum(np.log(x))))
    df_cor_fea=df_cor_fea_2.reset_index()
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])[feature+'ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])[feature+'ctr']
    print 'train_a ---> shape',train_a.shape
    print 'train_a --->head(1)',train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
#产生树的索引
train_tree_index=gbm_clf_2.apply(data_x_train_1)
valid_tree_index=gbm_clf_2.apply(data_x_valid_1)
tree_index=np.concatenate([train_tree_index,valid_tree_index])
OHE=OneHotEncoder()
data_x_train_2=np.empty(shape=(0,31))
data_x_valid_2=np.empty(shape=(0,31))
for index in range(tree_index.shape[1]):
    OHE.fit(tree_index[:,index].reshape(-1,1))
    train_a=OHE.transform(train_tree_index[:,index].reshape(-1,1))
    valid_a=OHE.transform(valid_tree_index[:,index].reshape(-1,1))
    if index %50==0:
        print index
        print 'train_a ----> one hot--->shape',train_a.shape
    data_x_train_2=sparse.hstack((data_x_train_2,train_a))
    data_x_valid_2=sparse.hstack((data_x_valid_2,valid_a))


df_feature_map.to_csv(save_path+"feature_important_mapping_cut_corr.csv")
sparse.save_npz(save_path+"data_x_train_cut_corr.npz",data_x_train)
sparse.save_npz(save_path+"data_x_valid_cut_corr.npz",data_x_valid)

eval_list=[(data_x_train,y_train),(data_x_valid,y_valid)]

gbm_clf = lgb.LGBMClassifier(
        boosting_type='gbdt', num_leaves=31, reg_alpha=0.0, reg_lambda=1,
        max_depth=-1, n_estimators=1000, objective='binary',
        subsample=0.7, colsample_bytree=0.7, subsample_freq=1,
        learning_rate=0.02, min_child_weight=50,random_state=20180506,n_jobs=7)

gbm_clf.fit(data_x_train,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)
joblib.dump(gbm_clf, '/home/heqt/jupyter_project/model/gbm_clf_cnt_80W_corr.pkl')


SGDLR_clf=SGDClassifier(loss='log', penalty='l1', alpha=1.0, l1_ratio=0.15, 
     random_state=20150511,learning_rate='optimal',n_jobs=15)


SGDLR_clf.fit(data_x_train_LR,y_train)
joblib.dump(gbm_clf, '/home/heqt/jupyter_project/model/feature_SGDLR_clf.pkl')