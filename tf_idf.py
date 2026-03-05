import math
from pathlib import Path
from collections import defaultdict


def load_tokens(tokens_dir):
    documents = {}
    tokens_path = Path(tokens_dir)
    
    for tokens_file in sorted(tokens_path.glob('tokens_page_*.txt')):
        page_num = int(tokens_file.stem.split('_')[2])
        
        with open(tokens_file, 'r', encoding='utf-8') as f:
            tokens = [line.strip() for line in f if line.strip()]
        
        documents[page_num] = tokens
    
    return documents


def load_lemmas(lemmas_dir):
    documents = {}
    lemmas_path = Path(lemmas_dir)
    
    for lemmas_file in sorted(lemmas_path.glob('lemmas_page_*.txt')):
        page_num = int(lemmas_file.stem.split('_')[2])
        
        lemmas = []
        with open(lemmas_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(' ', 1)
                if parts:
                    lemmas.append(parts[0])
        
        documents[page_num] = lemmas
    
    return documents


def compute_tf(tokens):
    tf = defaultdict(float)
    total_terms = len(tokens)
    
    if total_terms == 0:
        return tf
    
    term_counts = defaultdict(int)
    for token in tokens:
        term_counts[token] += 1
    
    for term, count in term_counts.items():
        tf[term] = count / total_terms
    
    return tf


def compute_idf(documents):
    num_docs = len(documents)
    doc_freq = defaultdict(int)
    
    for doc_tokens in documents.values():
        unique_terms = set(doc_tokens)
        for term in unique_terms:
            doc_freq[term] += 1
    
    idf = {}
    for term, df in doc_freq.items():
        idf[term] = math.log(num_docs / df)
    
    return idf


def compute_tfidf(tf, idf):
    tfidf = {}
    for term, tf_val in tf.items():
        if term in idf:
            tfidf[term] = tf_val * idf[term]
    return tfidf


def save_tfidf_output(data, output_dir, prefix, format_str):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for page_num, items in data.items():
        filename = output_path / f"{prefix}_tfidf_page_{page_num:04d}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            for term, idf_val, tfidf_val in items:
                f.write(format_str.format(term, idf_val, tfidf_val))


def main():
    script_dir = Path(__file__).parent
    tokens_lemmas_dir = script_dir / "tokens_lemmas"
    output_dir = script_dir / "tfidf_output"
    
    token_docs = load_tokens(tokens_lemmas_dir)
    lemma_docs = load_lemmas(tokens_lemmas_dir)
    
    term_idf = compute_idf(token_docs)
    lemma_idf = compute_idf(lemma_docs)
    
    token_tfidf_data = {}
    for page_num, tokens in token_docs.items():
        tf = compute_tf(tokens)
        tfidf = compute_tfidf(tf, term_idf)
        
        items = []
        for term in sorted(tfidf.keys()):
            items.append((term, term_idf.get(term, 0), tfidf[term]))
        token_tfidf_data[page_num] = items
    
    lemma_tfidf_data = {}
    for page_num, lemmas in lemma_docs.items():
        tf = compute_tf(lemmas)
        tfidf = compute_tfidf(tf, lemma_idf)
        
        items = []
        for lemma in sorted(tfidf.keys()):
            items.append((lemma, lemma_idf.get(lemma, 0), tfidf[lemma]))
        lemma_tfidf_data[page_num] = items
    
    save_tfidf_output(
        token_tfidf_data, 
        output_dir / "terms", 
        "terms", 
        "{} {:.6f} {:.6f}\n"
    )
    
    save_tfidf_output(
        lemma_tfidf_data, 
        output_dir / "lemmas", 
        "lemmas", 
        "{} {:.6f} {:.6f}\n"
    )
    
    print(f"Processed {len(token_docs)} documents")
    print(f"Unique terms: {len(term_idf)}")
    print(f"Unique lemmas: {len(lemma_idf)}")
    print(f"Output saved to: {output_dir}")


if __name__ == "__main__":
    main()
