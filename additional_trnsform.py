import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('plik.csv')
data_1 = data.copy()
data_1.dropna(subset=['target'], inplace=True)
data_2 = pd.DataFrame(data_1["ID"].copy())

data_2['Var32'] = (data_1['Var7'] * 12 / data_1['Var6'] + data['Var17']) / data_1['Var9']
data_2['Var33'] = np.where(data_2['Var32'] == np.inf, 1, 0)
data_2['Var32'] = np.where(data_2['Var32'] == np.inf, 0, data_2['Var32'])
data_2['Var34'] = np.where(data_2['Var32'] == np.nan, 1, 0)
data_2['Var32'] = np.where(pd.isna(data_2['Var32']), 0, data_2['Var32'])
data_2["Var35"] = data_1['Var4'] / data_1['Var9']
data_2['Var36'] = np.where(data_2['Var35'] == np.inf, 1, 0)
data_2['Var35'] = np.where(data_2['Var35'] == np.inf, 0, data_2['Var35'])
data_2["Var37"] = data_1["Var30"] / data_1["Var4"]

data_2.to_csv('dla_daniela.csv')