import json
from pathlib import Path
from collections import defaultdict


def build_inverted_index(lemmas_dir):
    inverted_index = defaultdict(list)
    
    lemmas_path = Path(lemmas_dir)
    lemma_files = sorted(lemmas_path.glob('lemmas_page_*.txt'))
    
    for lemma_file in lemma_files:
        page_name = lemma_file.stem.replace('lemmas_', '')
        page_num = int(page_name.split('_')[1])
        
        with open(lemma_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(' ', 1)
                if len(parts) >= 1:
                    lemma = parts[0]
                    if page_num not in inverted_index[lemma]:
                        inverted_index[lemma].append(page_num)
    
    return dict(inverted_index)


def save_inverted_index_json(inverted_index, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(inverted_index, f, ensure_ascii=False, indent=2)
    
    print(f"JSON inverted index saved: {output_file}")
    print(f"Total lemmas: {len(inverted_index)}")


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    lemmas_dir = script_dir / "tokens_lemmas"
    output_json = script_dir / "inverted_index.json"
    
    inverted_index = build_inverted_index(lemmas_dir)
    save_inverted_index_json(inverted_index, output_json)
