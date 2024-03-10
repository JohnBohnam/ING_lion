import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns

def date_convert(x):
    if x == '31Dec9999':
        return pd.to_datetime('31Dec2200', format='%d%b%Y') 
        # 31Dec9999 is a placeholder for NA ? 
    return pd.to_datetime(x, format='mixed')


def transform(in_datapath, out_datapath):
    data = pd.read_csv(in_datapath)

    #adding some new columns

    data_maciek = pd.read_csv(in_datapath)
    data_1 = data_maciek.copy()
    data_1.dropna(subset=['target'], inplace=True)
    data_extension = pd.DataFrame(data_1["ID"].copy())

    data_extension['Var32'] = (data_1['Var7'] * 12 / data_1['Var6'] + data['Var17']) / data_1['Var9']
    data_extension['Var33'] = np.where(data_extension['Var32'] == np.inf, 1, 0)
    data_extension['Var32'] = np.where(data_extension['Var32'] == np.inf, 0, data_extension['Var32'])
    data_extension['Var34'] = np.where(data_extension['Var32'] == np.nan, 1, 0)
    data_extension['Var32'] = np.where(pd.isna(data_extension['Var32']), 0, data_extension['Var32'])
    data_extension["Var35"] = data_1['Var4'] / data_1['Var9']
    data_extension['Var36'] = np.where(data_extension['Var35'] == np.inf, 1, 0)
    data_extension['Var35'] = np.where(data_extension['Var35'] == np.inf, 0, data_extension['Var35'])
    data_extension["Var37"] = data_1["Var30"] / data_1["Var4"]

    data_extension.to_csv('./data/testing_dla_daniela.csv')



    column_mapping = {
        "Var1": "no_applicants",
        "Var2": "loan_purpose",
        "target": "y",
        "Var3": "distr_channel",
        "Var4": "application_amount",
        "Var5": "credit_duration",
        "Var6": "payment_frequency",
        "Var7": "installment_amount",
        "Var8": "car_value",
        "Var9": "income_M",
        "Var10": "income_S",
        "Var11": "profession_M",
        "Var12": "profession_S",
        "Var13": "empl_date_M",
        "Var14": "material_status_M",
        "Var15": "no_children_M",
        "Var16": "no_dependencies_M",
        "Var17": "spendings",
        "Var18": "property_ownership_renovation",
        "Var19": "car_or_motorbike",
        "Var20": "requests_3m",
        "Var21": "requests_6m",
        "Var22": "requests_9m",
        "Var23": "requests_12m",
        "Var24": "credit_card_limit",
        "Var25": "account",
        "Var26": "savings",
        "Var27": "arrear_3m",
        "Var28": "arrear_12m",
        "Var29": "credit_score",
        "Var30": "income"
    }

    data.rename(columns=column_mapping, inplace=True)


    ### merge with Maciek

    data = data[data["Application_status"] == "Approved"] # ??

    # maciek_filepath = "./data/testing_dla_daniela.csv"
    # data_extension = pd.read_csv(maciek_filepath)

    data = data.merge(data_extension, on="ID", how="left")
    data.drop(columns=["ID", "customer_id", "_r_"], inplace=True)

    data.loc[data["Var35"] == float("inf"), "Var35"] = 0


    data.drop(columns=["Application_status"], inplace=True)

    #/ merge with Maciek


    data['secondary_applicant'] = ~data['profession_S'].isna()
    data['savings_na'] = data['savings'].isna()
    data['account_na'] = data['account'].isna()
    data['spendings_na'] = data['spendings'].isna()


    data['profession_S'] = pd.factorize(data['profession_S'].fillna('N_A'))[0]
    data['loan_purpose'] = pd.factorize(data['loan_purpose'].fillna('N_A'))[0]
    data['property_ownership_renovation'] = pd.factorize(data['property_ownership_renovation'].fillna('N_A'))[0]
    data['car_or_motorbike'] = pd.factorize(data['car_or_motorbike'].fillna('N_A'))[0]



    columns_to_convert = ['y', 'loan_purpose', 'distr_channel', 'profession_M', 'profession_S', 'material_status_M', 'property_ownership_renovation', 'car_or_motorbike', 'arrear_3m', 'arrear_12m', 'credit_score']
    data[columns_to_convert] = data[columns_to_convert].astype('category')

    debud_data = data.copy()


    data['loan_purpose'].replace({'1.0': 'car', '2.0': 'house', '3.0': 'cash'}, inplace=True)

    # def sanity_check1():
    #     condition_car_motorbike = \
    #         ~(data['loan_purpose'] == 'car') == data['car_or_motorbike'].isna()
    #     condition_car_value = \
    #         ~(data['loan_purpose'] == 'car') == data['car_value'].isna()
    #     condition_property_ownership \
    #         = ~(data['loan_purpose'] == 'house') == data['property_ownership_renovation'].isna()
    #     condition_profession_income \
    #         = data['income_S'].isna() == data['profession_S'].isna()


    #     result_car_motorbike = all(condition_car_motorbike.dropna())
    #     result_car_value = all(condition_car_value.dropna())
    #     result_property_ownership = all(condition_property_ownership.dropna())
    #     result_profession_income = all(condition_profession_income.dropna())

    #     # Print results
    #     print("Result for condition: loan_purpose == 'car' and (car_or_motorbike is NA):", result_car_motorbike)
    #     print("Result for condition: loan_purpose == 'car' and (car_value is NA):", result_car_value)
    #     print("Result for condition: loan_purpose == 'house' and (property_ownership_renovation is NA):", result_property_ownership)
    #     print("Result for condition: is.na(income_S) == is.na(profession_S):", result_profession_income)
        
    #     if result_car_motorbike and result_car_value and result_property_ownership and result_profession_income:
    #         print("Sanity check 1 passed")
    #     else:
    #         print("Sanity check 1 failed")
            
    # sanity_check1()


    data['credit_score_bucketed'] = pd.cut(pd.to_numeric(data['credit_score'], errors='coerce'), 
                                        bins=[-1, 0, 10, 20, 30, 70, 100, 250])

    # Calculate the mean of y - 1 for each credit_score interval
    # result = data.groupby('credit_score_bucketed')['y'].mean() - 1




    data['application_date'] = data['application_date'].apply(date_convert)
    data['empl_date_M'] = data['empl_date_M'].apply(date_convert)

    data['empl_to_app_time'] = (data['application_date'] - data['empl_date_M']).dt.days
        

    columns_to_zero_fill = ["account", "car_value", "income_S", "spendings", "savings"]
    data[columns_to_zero_fill] = data[columns_to_zero_fill].fillna(0)


    data['distr_channel'].replace({'1': 'Direct', '2': 'Broker', '3': 'Online', '': 'NA'}, inplace=True)
    data['distr_channel'] = data['distr_channel'].astype('category')


    if out_datapath:
        if not os.path.exists(out_datapath):
            os.makedirs(out_datapath)
        data.to_csv(out_datapath, index=False)
    
    return data
