#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import pandas as pd
from tqdm import tqdm

# Permitir passar o caminho do .txt como argumento
if len(sys.argv) > 1:
    TXT_PATH = sys.argv[1]
else:
    TXT_PATH = '/dataset/seu_arquivo.txt'  # Valor padrão

CSV_OUT = 'dataset/fashion_clip.csv'
CSV_PART_OUT = 'dataset/fashion_clip_part.csv'
os.makedirs('dataset', exist_ok=True)

# Diretório base do .txt
base_dir = os.path.dirname(TXT_PATH)

# Ler linhas do txt
with open(TXT_PATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Pular header e linha de contagem, se houver
offset = 0
if lines[0].strip().isdigit():
    offset = 2
else:
    offset = 1
lines = lines[offset:]

data = []
for line in tqdm(lines, desc='Processando dataset'):
    parts = line.strip().split()
    if len(parts) < 3:
        continue
    rel_image_path = parts[0]
    image_path = os.path.join(base_dir, rel_image_path)  # Caminho absoluto
    try:
        category = rel_image_path.split('/')[2]
    except IndexError:
        category = 'Unknown'
    text = category
    data.append({'image_path': image_path, 'text': text})

# Salva CSV completo
df = pd.DataFrame(data)
df.to_csv(CSV_OUT, index=False)
print(f'Dataset completo salvo em: {CSV_OUT}')

# Gerar CSV reduzido com até 10.000 registros, mantendo diversidade de categorias
max_total = 1000
if len(df) > max_total:
    # Seleciona até max_total registros, balanceando por categoria
    grouped = df.groupby('text')
    n_per_cat = max(1, max_total // grouped.ngroups)
    part_df = grouped.apply(lambda x: x.sample(min(len(x), n_per_cat), random_state=42)).reset_index(drop=True)
    # Se ainda não atingiu 10k, completa com amostras aleatórias
    if len(part_df) < max_total:
        restantes = df.drop(part_df.index).sample(max_total - len(part_df), random_state=42)
        part_df = pd.concat([part_df, restantes]).reset_index(drop=True)
    part_df = part_df.sample(frac=1, random_state=42).reset_index(drop=True)  # embaralha
else:
    part_df = df
part_df.to_csv(CSV_PART_OUT, index=False)
print(f'Dataset reduzido salvo em: {CSV_PART_OUT}') 