import json
import re
from pathlib import Path


class BooleanSearch:
    def __init__(self, index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            self.index = json.load(f)
    
    def _get_posting_list(self, term):
        return set(self.index.get(term.lower(), []))
    
    def _tokenize_query(self, query):
        pattern = r'\(|\)|\bNOT\b|\bAND\b|\bOR\b|[\w\-]+'
        tokens = re.findall(pattern, query, re.IGNORECASE)
        return tokens
    
    def _parse(self, tokens):
        result, _ = self._parse_or(tokens, 0)
        return result
    
    def _parse_or(self, tokens, pos):
        left, pos = self._parse_and(tokens, pos)
        
        while pos < len(tokens) and tokens[pos].upper() == 'OR':
            pos += 1
            right, pos = self._parse_and(tokens, pos)
            left = left | right
        
        return left, pos
    
    def _parse_and(self, tokens, pos):
        left, pos = self._parse_not(tokens, pos)

        while pos < len(tokens):
            if tokens[pos].upper() == 'AND':
                pos += 1
                right, pos = self._parse_not(tokens, pos)
                left = left & right
            elif tokens[pos].upper() == 'NOT':
                pos += 1
                right, pos = self._parse_primary(tokens, pos)
                left = left - right
            else:
                break

        return left, pos
    
    def _parse_not(self, tokens, pos):
        if pos < len(tokens) and tokens[pos].upper() == 'NOT':
            pos += 1
            operand, pos = self._parse_primary(tokens, pos)
            return set(range(1, 101)) - operand, pos
        
        return self._parse_primary(tokens, pos)
    
    def _parse_primary(self, tokens, pos):
        if pos >= len(tokens):
            return set(), pos
        
        if tokens[pos] == '(':
            pos += 1
            result, pos = self._parse_or(tokens, pos)
            if pos < len(tokens) and tokens[pos] == ')':
                pos += 1
            return result, pos
        
        term = tokens[pos].lower()
        pos += 1
        return self._get_posting_list(term), pos
    
    def search(self, query):
        tokens = self._tokenize_query(query)

        if not tokens:
            return set()

        try:
            results = self._parse(tokens)
            return sorted(results)
        except (IndexError, ValueError) as e:
            print(f"Query parsing error: {e}")
            return set()
    
    def search_with_details(self, query):
        results = self.search(query)
        
        print(f"Query: {query}")
        print(f"Found in {len(results)} document(s): {results}")
        
        return results


def main():
    script_dir = Path(__file__).parent
    index_file = script_dir / "inverted_index.json"
    
    searcher = BooleanSearch(index_file)
    
    print("Boolean Search Engine")
    print("=" * 50)
    print("Operators: AND, OR, NOT")
    print("Use parentheses for complex queries")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            query = input("Search> ").strip()
            
            if query.lower() == 'quit':
                break
            
            if not query:
                continue
            
            searcher.search_with_details(query)
            print()
            
        except KeyboardInterrupt:
            print("\n")
            break
        except EOFError:
            print()
            break


if __name__ == "__main__":
    main()
