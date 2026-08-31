import pandas as pd

from paths import TRAIN_FILE
df = pd.read_excel(TRAIN_FILE)
# 태그별로 교사 발화 5개씩 출력
for tag in [1, 2, 3, 4, 5, 6]:
    sample = df[(df['Speaker'] == 'T') & (df['Tag'] == tag)]
    print(f'\n===== Tag {tag} ({len(sample)}건) =====')
    for s in sample['Sentence'].head(5):
        print(' -', s)