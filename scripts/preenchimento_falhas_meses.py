# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 14:49:12 2024

@author: 99dom
"""

import pandas as pd
import datetime

#%% 
file_path = 'todos_os_dados_conso_meses.csv'  
df = pd.read_csv(file_path)

#%% 
df['data_mes'] = pd.to_datetime(df['data_mes'], errors='coerce')

#%%
df = df[df['data_mes'].dt.year <= 2023]

#%% Verificar o período de datas
start_date = df['data_mes'].min()
end_date = df['data_mes'].max()
print(f"Período de datas: {start_date} a {end_date}")


#%% Criar uma base com sequência completa de meses por local
locais = df['local'].unique()  # Lista única de locais
all_months = pd.date_range(start=start_date, end=end_date, freq='MS') 
complete_data = pd.DataFrame([(month, local) for month in all_months for local in locais],
                             columns=['data_mes', 'local'])

#%% Mesclar a base original com a base completa
df_merged = pd.merge(complete_data, df, on=['data_mes', 'local'], how='left')

#%% Preencher valores faltantes
# Preenchimento de pm25, pm10, temp e ur por interpolação linear
for col in ['pm25', 'pm10', 'temp', 'ur']:
    df_merged[col] = (
        df_merged.groupby('local')[col]
        .apply(lambda group: group.interpolate(method='linear', limit_direction='both'))
        .reset_index(level=0, drop=True)  # Alinha o índice após a interpolação
    )

#%% Preenchimento de latitude e longitude por propagação (forward e backward fill)
df_merged[['latitude', 'longitude']] = (
    df_merged.groupby('local')[['latitude', 'longitude']]
    .apply(lambda group: group.ffill().bfill())
    .reset_index(level=0, drop=True)  # Alinha o índice após o preenchimento
)

#%% Ordenar os dados por local e data mensal
df_merged = df_merged.sort_values(by=['local', 'data_mes']).reset_index(drop=True)

#%% Salvar os dados preenchidos em um arquivo CSV
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
output_path = f'D:\\TESTES ESTATÍSTICOS\\concatena dados\\concatena dados\\dados_mensais_preenchido_{timestamp}.csv'

df_merged.to_csv(output_path, index=False, encoding='utf-8')
print(f"Dados preenchidos, organizados e salvos em: {output_path}")
