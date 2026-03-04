import re
import os
from pathlib import Path
from collections import defaultdict
import pymorphy3
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords')

STOP_WORDS = set(stopwords.words('russian'))

def extract_text_from_html(html_content):
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def tokenize(text):
    pattern = r'[a-zA-Zа-яА-ЯёЁ-]{2,}'
    tokens = re.findall(pattern, text)
    return tokens

def filter_tokens(tokens):
    filtered = []
    for token in tokens:
        if re.search(r'\d', token):
            continue
        if token.lower() in STOP_WORDS:
            continue
        if not re.search(r'[а-яА-ЯёЁ]', token):
            continue
        if token.startswith('-') or token.endswith('-'):
            continue
        if re.match(r'^(d-|edtech-|fdm-|iptv-|it-|qr-|telegram-|xct-|ar-|pro)', token, re.IGNORECASE):
            continue
        filtered.append(token)
    return filtered

def lemmatize_tokens(tokens, morph):
    lemma_groups = defaultdict(list)
    seen = set()
    
    for token in tokens:
        token_lower = token.lower()
        if token_lower in seen:
            continue
        seen.add(token_lower)
        
        parsed = morph.parse(token)[0]
        lemma = parsed.normal_form.lower()
        lemma_groups[lemma].append(token_lower)
    
    return lemma_groups

def process_files(input_dir, output_dir):
    morph = pymorphy3.MorphAnalyzer()
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    txt_files = sorted(input_path.glob('*.txt'))
    
    for txt_file in txt_files:
        page_name = txt_file.stem
        
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        text = extract_text_from_html(content)
        tokens = tokenize(text)
        filtered = filter_tokens(tokens)

        seen = set()
        unique_tokens = []
        for token in filtered:
            token_lower = token.lower()
            if token_lower not in seen:
                seen.add(token_lower)
                unique_tokens.append(token_lower)

        lemma_groups = lemmatize_tokens(unique_tokens, morph)

        tokens_file = output_path / f"tokens_{page_name}.txt"
        lemmas_file = output_path / f"lemmas_{page_name}.txt"

        with open(tokens_file, 'w', encoding='utf-8') as f:
            for token in unique_tokens:
                f.write(f"{token}\n")
        
        with open(lemmas_file, 'w', encoding='utf-8') as f:
            for lemma in sorted(lemma_groups.keys()):
                tokens_list = ' '.join(sorted(set(lemma_groups[lemma])))
                f.write(f"{lemma} {tokens_list}\n")
        
        print(f"{page_name}: {len(unique_tokens)} tokens, {len(lemma_groups)} lemmas")
    
    print(f"\nOutput saved to: {output_path}")

if __name__ == "__main__":
    script_dir = Path(__file__).parent
    input_dir = script_dir / "crawl_output"
    output_dir = script_dir / "tokens_lemmas"
    
    process_files(input_dir, output_dir)
