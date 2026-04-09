import math
import json
from pathlib import Path
from collections import defaultdict
from lemmatizator import tokenize, filter_tokens, lemmatize_tokens
import pymorphy3


class VectorSearchEngine:
    def __init__(self, lemmas_dir, tfidf_lemmas_dir, index_file=None):
        self.lemmas_dir = Path(lemmas_dir)
        self.tfidf_lemmas_dir = Path(tfidf_lemmas_dir)
        self.index_file = Path(index_file) if index_file else None

        self.documents = {}
        self.tfidf_vectors = {}
        self.index = {}
        self.morph = pymorphy3.MorphAnalyzer()

        self._load_documents()
        self._load_tfidf_vectors()
        self._load_index()

    def _load_documents(self):
        for lemma_file in sorted(self.lemmas_dir.glob('lemmas_page_*.txt')):
            page_num = int(lemma_file.stem.split('_')[2])
            lemmas = []
            with open(lemma_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(' ', 1)
                    if parts:
                        lemmas.append(parts[0])
            self.documents[page_num] = lemmas

    def _load_tfidf_vectors(self):
        if not self.tfidf_lemmas_dir.exists():
            return

        for tfidf_file in sorted(self.tfidf_lemmas_dir.glob('lemmas_tfidf_page_*.txt')):
            page_num = int(tfidf_file.stem.split('_')[3])
            tfidf_vector = {}
            with open(tfidf_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        term = parts[0]
                        tfidf_val = float(parts[2])
                        tfidf_vector[term] = tfidf_val
            self.tfidf_vectors[page_num] = tfidf_vector

    def _load_index(self):
        if self.index_file and self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self.index = json.load(f)

    def _compute_vector_norm(self, vector):
        return math.sqrt(sum(val ** 2 for val in vector.values()))

    def _cosine_similarity(self, query_vector, doc_vector, query_norm, doc_norm):
        dot_product = 0.0
        for term, val in query_vector.items():
            if term in doc_vector:
                dot_product += val * doc_vector[term]

        if query_norm == 0 or doc_norm == 0:
            return 0.0

        return dot_product / (query_norm * doc_norm)

    def _fallback_match(self, query_terms):
        scores = []
        for doc_id, doc_lemmas in self.documents.items():
            doc_lemma_set = set(doc_lemmas)
            match_count = sum(1 for term in query_terms if term in doc_lemma_set)
            if match_count > 0:
                score = match_count / len(query_terms)
                scores.append((doc_id, score, doc_lemmas))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def _build_query_vector(self, query_terms):
        if not query_terms:
            return {}

        num_docs = len(self.documents)
        doc_freq = defaultdict(int)

        for doc_lemmas in self.documents.values():
            unique_terms = set(doc_lemmas)
            for term in unique_terms:
                doc_freq[term] += 1

        query_vector = {}
        term_counts = defaultdict(int)
        for term in query_terms:
            term_counts[term] += 1

        total_query_terms = len(query_terms)
        for term, count in term_counts.items():
            tf = count / total_query_terms
            df = doc_freq.get(term, 0)
            if df > 0:
                idf = math.log(1 + num_docs / df)
            else:
                idf = math.log(1 + num_docs)
            query_vector[term] = tf * idf

        return query_vector

    def _lemmatize_query(self, query):
        tokens = tokenize(query)
        filtered = filter_tokens(tokens)
        lemma_groups = lemmatize_tokens(filtered, self.morph)
        lemmas = list(lemma_groups.keys())
        return lemmas

    def _expand_query_terms(self, lemmas):
        expanded = set(lemmas)
        return list(expanded)

    def search(self, query, top_k=10):
        lemmas = self._lemmatize_query(query)
        lemmas = self._expand_query_terms(lemmas)

        if not lemmas:
            return []

        query_vector = self._build_query_vector(lemmas)
        query_norm = self._compute_vector_norm(query_vector)

        if query_norm == 0:
            return self._fallback_match(lemmas)[:top_k]

        scores = []
        for doc_id, doc_tfidf in self.tfidf_vectors.items():
            doc_norm = self._compute_vector_norm(doc_tfidf)
            similarity = self._cosine_similarity(query_vector, doc_tfidf, query_norm, doc_norm)
            if similarity > 0:
                scores.append((doc_id, similarity, self.documents.get(doc_id, [])))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def search_with_highlights(self, query, top_k=10):
        lemmas = self._lemmatize_query(query)
        query_vector = self._build_query_vector(lemmas)
        query_norm = self._compute_vector_norm(query_vector)

        if query_norm == 0:
            fallback_results = self._fallback_match(lemmas)[:top_k]
            results = []
            for doc_id, score, doc_lemmas in fallback_results:
                results.append({
                    'doc_id': doc_id,
                    'score': score,
                    'matching_terms': [t for t in lemmas if t in set(doc_lemmas)],
                    'top_lemmas': sorted(set(doc_lemmas))[:10],
                    'all_lemmas': doc_lemmas
                })
            return results

        results = []
        for doc_id, doc_tfidf in self.tfidf_vectors.items():
            doc_norm = self._compute_vector_norm(doc_tfidf)
            similarity = self._cosine_similarity(query_vector, doc_tfidf, query_norm, doc_norm)

            if similarity > 0:
                matching_terms = []
                for term in query_vector:
                    if term in doc_tfidf:
                        matching_terms.append(term)

                sorted_lemmas = sorted(doc_tfidf.items(), key=lambda x: x[1], reverse=True)[:10]

                results.append({
                    'doc_id': doc_id,
                    'score': similarity,
                    'matching_terms': matching_terms,
                    'top_lemmas': [lemma for lemma, _ in sorted_lemmas],
                    'all_lemmas': self.documents.get(doc_id, [])
                })

        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

    def get_document_info(self, doc_id):
        info = {
            'doc_id': doc_id,
            'lemmas_count': len(self.documents.get(doc_id, [])),
            'url': None
        }

        if self.index_file and self.index_file.exists():
            index_path = self.lemmas_dir.parent / 'index.txt'
            if index_path.exists():
                with open(index_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('#'):
                            continue
                        parts = line.strip().split('\t')
                        if len(parts) >= 2:
                            try:
                                page_num = int(parts[0])
                                if page_num == doc_id:
                                    info['url'] = parts[1]
                                    break
                            except ValueError:
                                continue

        return info


def format_results(results, show_details=False):
    if not results:
        return "Результатов не найдено."

    output_lines = []
    output_lines.append(f"Найдено результатов: {len(results)}:\n")
    output_lines.append("=" * 70)

    for i, result in enumerate(results, 1):
        if isinstance(result, tuple):
            doc_id, score, lemmas = result
            output_lines.append(f"\n{i}. Документ {doc_id} (Оценка: {score:.4f})")
            output_lines.append(f"   Ключевые леммы: {', '.join(lemmas[:10])}")
        elif isinstance(result, dict):
            doc_id = result['doc_id']
            score = result['score']
            matching = result['matching_terms']
            top_lemmas = result['top_lemmas']

            output_lines.append(f"\n{i}. Документ {doc_id} (Оценка: {score:.4f})")
            output_lines.append(f"   Совпадения: {', '.join(matching)}")
            output_lines.append(f"   Ключевые леммы: {', '.join(top_lemmas)}")

            if show_details:
                doc_info = search_engine.get_document_info(doc_id)
                if doc_info['url']:
                    output_lines.append(f"   URL: {doc_info['url']}")

        output_lines.append("-" * 70)

    return '\n'.join(output_lines)


def main():
    script_dir = Path(__file__).parent
    lemmas_dir = script_dir / "tokens_lemmas"
    tfidf_lemmas_dir = script_dir / "tfidf_output" / "lemmas"
    index_file = script_dir / "inverted_index.json"

    global search_engine
    search_engine = VectorSearchEngine(lemmas_dir, tfidf_lemmas_dir, index_file)


    print(f"Загружено документов: {len(search_engine.documents)}")
    print(f"Загружено TF-IDF векторов: {len(search_engine.tfidf_vectors)}")
    print("\nКоманды:")
    print("  <запрос>          - Поиск документов")
    print("  quit/exit         - Выход из системы поиска")
    print("=" * 70)

    while True:
        try:
            query = input("\nПоиск> ").strip()

            if not query:
                continue

            if query.lower() in ('quit', 'exit'):
                print("Пока!")
                break

            results = search_engine.search_with_highlights(query, top_k=10)
            print(format_results(results, show_details=True))

        except KeyboardInterrupt:
            print("\n\nПока!")
            break
        except EOFError:
            print("\nПока!")
            break


if __name__ == "__main__":
    main()
