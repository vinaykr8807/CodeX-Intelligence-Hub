"""
cleanup_datasets.py
────────────────────────────────────────────────────────────────────────────
Removes bad entries from all CSV datasets:
  1. REPL-style code (>>> prompt lines)
  2. Trivially short snippets (< 5 meaningful lines or < 80 chars of real code)
  3. Duplicate code entries
Then deletes stale FAISS index files so they rebuild cleanly on next app start.

Run once from the project root:
    python cleanup_datasets.py
"""
import os, re, hashlib
import pandas as pd

MIN_REAL_CHARS  = 80   # minimum non-whitespace characters
MIN_REAL_LINES  = 4    # minimum non-blank, non-comment, non-repl lines

def is_repl_code(code: str) -> bool:
    """Returns True if the snippet looks like interactive Python REPL output."""
    return bool(re.search(r'^\s*>>>', str(code), re.MULTILINE))

def is_trivial(code: str) -> bool:
    """Returns True if the snippet has too little real code to be useful."""
    text = str(code)
    real_chars = len(re.sub(r'\s+', '', text))
    real_lines = [l for l in text.splitlines()
                  if l.strip() and not l.strip().startswith(('#', '//', '/*', '*'))]
    return real_chars < MIN_REAL_CHARS or len(real_lines) < MIN_REAL_LINES

def code_fingerprint(code: str) -> str:
    normalised = re.sub(r'\s+', '', str(code))
    return hashlib.md5(normalised.encode()).hexdigest()

datasets = [
    ('data_python.csv',     'python_solutions'),
    ('data_cpp.csv',        'Answer'),
    ('data_java.csv',       'content'),
    ('data_javascript.csv', 'content'),
]

for csv_file, code_col in datasets:
    if not os.path.exists(csv_file):
        print(f'  ⚠  {csv_file} not found – skipping')
        continue

    df = pd.read_csv(csv_file)
    before = len(df)

    if code_col not in df.columns:
        print(f'  ⚠  {csv_file}: column "{code_col}" missing – skipping')
        continue

    # 1. Drop REPL-style entries
    repl_mask  = df[code_col].apply(is_repl_code)
    # 2. Drop trivially short entries
    triv_mask  = df[code_col].apply(is_trivial)
    # 3. Drop duplicates by code fingerprint
    df['_fp']  = df[code_col].apply(code_fingerprint)
    dup_mask   = df.duplicated(subset='_fp', keep='first')

    bad_mask   = repl_mask | triv_mask | dup_mask
    df = df[~bad_mask].drop(columns=['_fp']).reset_index(drop=True)
    df.to_csv(csv_file, index=False)

    n_repl = repl_mask.sum()
    n_triv = (triv_mask & ~repl_mask).sum()
    n_dup  = (dup_mask  & ~repl_mask & ~triv_mask).sum()
    removed = before - len(df)
    print(f'  ✅  {csv_file}: {before} → {len(df)} rows  '
          f'(removed {removed}: {n_repl} REPL, {n_triv} trivial, {n_dup} duplicates)')

# Delete stale FAISS index so it rebuilds from the clean CSV on next startup
for idx_file in ('embeddings.npy', 'code_faiss.index'):
    if os.path.exists(idx_file):
        os.remove(idx_file)
        print(f'  🗑️  Deleted stale {idx_file}')

print('\nDone. The search index will rebuild automatically on the next app start.')
print('You can also click "🔄 Refresh Data" → "🧠 Retrain" in the sidebar.')
