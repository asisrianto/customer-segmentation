# -*- coding: utf-8 -*-
"""Customer Segmentation for Marketing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TrJDWCbO2yvOcNcXv_JBvZ7lFiz9DVaC

## Required Dependencies
"""

import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
import pickle  
from kmodes.kmodes import KModes  
from kmodes.kprototypes import KPrototypes  
from kmodes.kmodes import KModes  
from kmodes.kprototypes import KPrototypes  

import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='white')

"""## Data Collection"""

df = pd.read_csv("https://storage.googleapis.com/dqlab-dataset/customer_segments.txt", sep="\t")
plt.clf()

df.head()

"""## Exploratory data analysis

EDA for numerical columns
"""

def observasi_num(features):
    fig, axs = plt.subplots(2, 2, figsize=(10,9))
    for i, kol in enumerate(features):
        sns.boxplot(df[kol], ax=axs[i][0])
        sns.distplot(df[kol], ax=axs[i][1])
        axs[i][0].set_title('mean = %.2f\n median = %.2f\n std = %.2f'%(df[kol].mean(), df[kol].median(), df[kol].std()))
    plt.setp(axs)
    plt.tight_layout()
    plt.savefig('eda_numeric.png')
    plt.show() 
kolom_numerik = ['Umur', 'NilaiBelanjaSetahun']
observasi_num(kolom_numerik)

"""EDA for categorical columns"""

kolom_kategorikal = ['Jenis Kelamin', 'Profesi', 'Tipe Residen']
fig, axs = plt.subplots(3, 1, figsize=(7,10))
for i, kol in enumerate(kolom_kategorikal):  
    sns.countplot(df[kol], order = df[kol].value_counts().index, ax = axs[i])  
    axs[i].set_title('\nCount Plot %s\n'%(kol), fontsize=15)        
    for p in axs[i].patches:  
        axs[i].annotate(format(p.get_height(), '.0f'),  
                        (p.get_x() + p.get_width() / 2., p.get_height()),  
                        ha = 'center',  
                        va = 'center',  
                        xytext = (0, 10),  
                        textcoords = 'offset points') 
    sns.despine(right=True, top=True, left=True)  
    axs[i].axes.yaxis.set_visible(False) 
    plt.setp(axs[i])
    plt.tight_layout()
plt.savefig('eda_categoric.png')
plt.show()

"""## Data Preparation

Standardize data on numeric columns
"""

print('\nbefore standardization')  
print(df[kolom_numerik].describe().round(1))  
  
df_std = StandardScaler().fit_transform(df[kolom_numerik])  
df_std = pd.DataFrame(data=df_std, index=df.index, columns=df[kolom_numerik].columns)  
    
print('\nafter standardization')  
print(df_std.describe().round(0))

print('\nsample of standardization result')  
df_std.head()

"""Konversi Kategorikal Data dengan Label Encoder (menjadi kolom numerik)"""

df_encode = df[kolom_kategorikal].copy()    
for col in kolom_kategorikal:  
    df_encode[col]= LabelEncoder().fit_transform(df_encode[col])
      
df_encode.head()

"""Menggabungkan data numerik dan data kategorik untuk pemodelan"""

df_model = df_encode.merge(df_std, left_index = True, right_index=True, how= 'left')  
df_model.head()

"""## Modeling

Mencari Jumlah Cluster yang Optimal
"""

cost = {}  
for k in range(2,10):  
    kproto = KPrototypes (n_clusters = k,random_state=75)  
    kproto.fit_predict(df_model, categorical=[0,1,2])  
    cost [k]= kproto.cost_  
  
sns.pointplot(x=list(cost.keys()), y=list(cost.values()))  
plt.savefig('cluster.png')
plt.show()

kproto = KPrototypes(n_clusters = 5, random_state = 75)  
kproto = kproto.fit(df_model, categorical=[0,1,2])  
pickle.dump(kproto, open('cluster.pkl', 'wb'))

"""Menentukan segment tiap pelanggan"""

clusters =  kproto.predict(df_model, categorical=[0,1,2])    
print('segmen pelanggan: {}\n'.format(clusters))    
    
# Menggabungkan data awal dan segmen pelanggan    
df_final = df.copy()    
df_final['cluster'] = clusters
df_final.head()

"""Menampilkan cluster tiap pelanggan"""

for i in range(0, 5):  
    print('\nPelanggan cluster: {}\n'.format(i))  
    print(df_final[df_final['cluster']== i])

"""Visualisasi Hasil Clustering - Box Plot"""

for i in kolom_numerik:  
    plt.figure(figsize=(6,4))  
    ax = sns.boxplot(x = 'cluster',y = i, data = df_final)  
    plt. title ('\nBox Plot {}\n'.format(i), fontsize=12)  
    plt.savefig('result_numeric.png')
    plt.show()

kolom_categorical = ['Jenis Kelamin','Profesi','Tipe Residen']  
  
for i in kolom_categorical:  
    plt.figure(figsize=(6,4))  
    ax = sns.countplot(data = df_final, x = 'cluster', hue = i )  
    plt.title('\nCount Plot {}\n'.format(i), fontsize=12)  
    ax. legend (loc="upper center")  
    for p in ax.patches:  
        ax.annotate(format(p.get_height(), '.0f'),  
                    (p.get_x() + p.get_width() / 2., p.get_height()),  
                     ha = 'center',  
                     va = 'center',  
                     xytext = (0, 10),  
                     textcoords = 'offset points')  
      
    sns.despine(right=True,top = True, left = True)  
    ax.axes.yaxis.set_visible(False)
    plt.savefig('result_categorical.png')  
    plt.show()

"""Mapping clusters name"""

clusters =  kproto.predict(df_model, categorical=[0,1,2]) 
df_final = df.copy()    
df_final['cluster'] = clusters 
df_final['segmen'] = df_final['cluster'].map({  
    0: 'Diamond Young Member',  
    1: 'Diamond Senior Member',  
    2: 'Silver Member',  
    3: 'Gold Young Member',  
    4: 'Gold Senior Member'  
})    

df_final.info()
df_final.head()

"""## Segmentation

Prepare input data
"""

data = [{  
    'Customer_ID': 'CUST-100' ,  
    'Nama Pelanggan': 'Joko' ,  
    'Jenis Kelamin': 'Pria',  
    'Umur': 45,  
    'Profesi': 'Wiraswasta',  
    'Tipe Residen': 'Cluster' ,  
    'NilaiBelanjaSetahun': 8230000        
}]    
new_df = pd.DataFrame(data)
new_df

"""Pre-processing of input data"""

def data_preprocess(data):  
    kolom_kategorikal = ['Jenis Kelamin','Profesi','Tipe Residen']  
    df_encode = data[kolom_kategorikal].copy()    
    df_encode['Jenis Kelamin'] = df_encode['Jenis Kelamin'].map({  
        'Pria': 0,  
        'Wanita' : 1  
    })  
    df_encode['Profesi'] = df_encode['Profesi'].map({  
        'Ibu Rumah Tangga': 0,  
        'Mahasiswa' : 1,  
        'Pelajar': 2,  
        'Professional': 3,  
        'Wiraswasta': 4  
    })  
    df_encode['Tipe Residen'] = df_encode['Tipe Residen'].map({  
        'Cluster': 0,  
        'Sector' : 1  
    })  
      
    kolom_numerik = ['Umur','NilaiBelanjaSetahun']  
    df_std = data[kolom_numerik].copy()  
    df_std['Umur'] = (df_std['Umur'] - 37.5)/14.7  
    df_std['NilaiBelanjaSetahun'] = (df_std['NilaiBelanjaSetahun'] - 7069874.8)/2590619.0  
      
    df_model = df_encode.merge(df_std, left_index = True,  
                           right_index=True, how = 'left')  
      
    return df_model  
  
new_df_model = data_preprocess(new_df)    
new_df_model

def modelling (data): 
    kpoto = pickle.load(open('cluster.pkl', 'rb'))
    clusters = kpoto.predict(data,categorical=[0,1,2])  
    return clusters  
    
clusters = modelling(new_df_model)

def menamakan_segmen (data_asli, clusters):  
      
    final_df = data_asli.copy()  
    final_df['cluster'] = clusters
      
    final_df['segmen'] = final_df['cluster'].map({  
        0: 'Diamond Young Member',  
        1: 'Diamond Senior Member',  
        2: 'Silver Students',  
        3: 'Gold Young Member',  
        4: 'Gold Senior Member'  
    })      
    return final_df
  
new_final_df = menamakan_segmen (new_df,clusters)  
new_final_df