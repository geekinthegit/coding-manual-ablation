import pandas as pd

from paths import TRAIN_FILE
df = pd.read_excel(TRAIN_FILE)

# Tag 3이 붙은 교사 발화 행의 인덱스 앞쪽 8개
idx_list = df[(df['Speaker'] == 'T') & (df['Tag'] == 3)].index[:8]

for idx in idx_list:
    print(f'\n===== 행 {idx} 주변 =====')
    start = max(0, idx - 3)
    context = df.loc[start:idx, ['Speaker', 'Sentence', 'Tag']]
    print(context.to_string())