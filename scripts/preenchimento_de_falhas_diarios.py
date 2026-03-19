# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 14:18:06 2024

@author: 99dom
"""
#%%
import pandas as pd
import datetime

#%% 
file_path = 'todos_os_dados_conso_dia.csv' 
df = pd.read_csv(file_path)

#%% 
df['data_dia'] = pd.to_datetime(df['data_dia'])

#%% 
df = df[df['data_dia'].dt.year == 2023]

#%% Verificar o período de datas
start_date = df['data_dia'].min()
end_date = df['data_dia'].max()

#%% Criar uma base com sequência completa de datas por local
# Obter lista única de locais
locais = df['local'].unique()

#%% Gerar todas as combinações de datas e locais
all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
complete_data = pd.DataFrame([(date, local) for date in all_dates for local in locais], 
                             columns=['data_dia', 'local'])

#%% Mesclar a base original com a base completa
df_merged = pd.merge(complete_data, df, on=['data_dia', 'local'], how='left')

#%% Preencher valores faltantes
# Preenchimento de pm25, pm10, temp e ur por interpolação linear
for col in ['pm25', 'pm10', 'temp', 'ur']:
    df_merged[col] = (
        df_merged.groupby('local')[col]
        .apply(lambda group: group.interpolate(method='linear', limit_direction='both'))
        .reset_index(level=0, drop=True)  # Alinha o índice após a interpolação
    )

#%% Preenchimento de latitude e longitude por propagação 
df_merged[['latitude', 'longitude']] = (
    df_merged.groupby('local')[['latitude', 'longitude']]
    .apply(lambda group: group.ffill().bfill())
    .reset_index(level=0, drop=True)  # Alinha o índice após o preenchimento
)

#%% Ordenar os dados por local e data
df_merged = df_merged.sort_values(by=['local', 'data_dia']).reset_index(drop=True)

#%%
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
output_path = f'D:\\TESTES ESTATÍSTICOS\\concatena dados\\concatena dados\\arquivo_diarios_preenchido_{timestamp}.csv'

df_merged.to_csv(output_path, index=False, encoding='utf-8')
print(f"Dados preenchidos, organizados e salvos em: {output_path}")
