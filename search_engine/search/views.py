from django.shortcuts import render
from django.http import JsonResponse
from pathlib import Path
import sys

# Add parent directory to path to import vector_search
parent_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(parent_dir))

from vector_search import VectorSearchEngine

# Initialize search engine
script_dir = parent_dir
lemmas_dir = script_dir / "tokens_lemmas"
tfidf_lemmas_dir = script_dir / "tfidf_output" / "lemmas"
index_file = script_dir / "inverted_index.json"

search_engine = VectorSearchEngine(lemmas_dir, tfidf_lemmas_dir, index_file)


def index(request):
    return render(request, 'search/index.html', {
        'num_docs': len(search_engine.documents),
        'num_vectors': len(search_engine.tfidf_vectors),
    })


def search_results(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return render(request, 'search/_empty_results.html')
    
    # Perform search with ranking (top 10 results)
    results = search_engine.search_with_highlights(query, top_k=10)
    
    # Format results for display
    formatted_results = []
    for result in results:
        doc_info = search_engine.get_document_info(result['doc_id'])
        formatted_results.append({
            'doc_id': result['doc_id'],
            'score': round(result['score'], 4),
            'matching_terms': result['matching_terms'],
            'top_lemmas': result['top_lemmas'][:10],
            'url': doc_info.get('url', '')
        })
    
    return render(request, 'search/_search_results.html', {
        'query': query,
        'results': formatted_results,
        'num_results': len(formatted_results),
    })


def api_search(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'error': 'Query parameter "q" is required'}, status=400)
    
    results = search_engine.search_with_highlights(query, top_k=10)
    
    formatted_results = []
    for result in results:
        doc_info = search_engine.get_document_info(result['doc_id'])
        formatted_results.append({
            'doc_id': result['doc_id'],
            'score': round(result['score'], 4),
            'matching_terms': result['matching_terms'],
            'top_lemmas': result['top_lemmas'][:10],
            'url': doc_info.get('url', '')
        })
    
    return JsonResponse({
        'query': query,
        'total_results': len(formatted_results),
        'results': formatted_results,
    })
