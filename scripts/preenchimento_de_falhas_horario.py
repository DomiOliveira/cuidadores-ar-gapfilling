# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 23:13:56 2024

@author: 99dom
"""
#%%
import pandas as pd
import datetime

#%% 
file_path = 'dados_horarios_novo.csv'  
df = pd.read_csv(file_path)

#%%
df['datah'] = df['datah'].astype(str)


#%%
print(df['datah'].unique())

#%%
df['datah'] = df['datah'].apply(lambda x: f"{x} 00:00:00" if len(x) == 10 else x)


#%% 
df['datah'] = pd.to_datetime(df['datah'], errors='coerce') 
df = df.sort_values(by=['datah']).reset_index(drop=True) 

#%%

df = df[df['datah'].dt.year <= 2023]#%% Verificar o período de datas

#%%
start_date = df['datah'].min()
end_date = df['datah'].max()
print(f"Período de datas: {start_date} a {end_date}")

#%% Criar uma base com sequência completa de data-hora por local
locais = df['local'].unique()  # Lista única de locais
all_datetimes = pd.date_range(start=start_date, end=end_date, freq='H')  # Sequência completa de data-horas
complete_data = pd.DataFrame([(datetime, local) for datetime in all_datetimes for local in locais],
                             columns=['datah', 'local'])

#%% Mesclar a base original com a base completa
df_merged = pd.merge(complete_data, df, on=['datah', 'local'], how='left')

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

#%% Ordenar os dados por local e data-hora
df_merged = df_merged.sort_values(by=['local', 'datah']).reset_index(drop=True)

#%% Salvar os dados preenchidos em um arquivo CSV
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
output_path = f'D:\\TESTES ESTATÍSTICOS\\concatena dados\\concatena dados\\dados_horario_preenchido_{timestamp}.csv'

df_merged.to_csv(output_path, index=False, encoding='utf-8')
print(f"Dados preenchidos, organizados e salvos em: {output_path}")
