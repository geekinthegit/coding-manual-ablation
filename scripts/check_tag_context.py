import sys
import pandas as pd
from paths import TRAIN_FILE

# Usage: python scripts/check_tag_context.py <tag>
tag = int(sys.argv[1])

df = pd.read_excel(TRAIN_FILE)

# First 8 row indices of teacher utterances with the given tag
idx_list = df[(df['Speaker'] == 'T') & (df['Tag'] == tag)].index[:8]

for idx in idx_list:
    print(f'\n===== Row {idx} with preceding context (Tag {tag}) =====')
    start = max(0, idx - 3)
    context = df.loc[start:idx, ['Speaker', 'Sentence', 'Tag']]
    print(context.to_string())