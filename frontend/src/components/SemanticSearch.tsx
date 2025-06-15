import { useEffect, useRef, useState } from 'react';

interface SearchResult {
  text: string;
  match_tokens?: string[];
  score?: number;
}

export default function SemanticSearch({
  input,
  onDone,
  trigger,
}: {
  input: string;
  onDone: () => void;
  trigger: number;
}) {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const hasMountedRef = useRef(false);

  useEffect(() => {
    // Skip the first render (when the component mounts)
    if (!hasMountedRef.current) {
      hasMountedRef.current = true;
      return;
    }

    if (!input.trim()) return;

    setLoading(true);
    setHasSearched(true);

    fetch(`http://localhost:8000/api/search?q=${encodeURIComponent(input)}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (!Array.isArray(data)) throw new Error('Expected array');
        const safeResults = data.filter(
          (item) => item && typeof item.text === 'string'
        );
        setResults(safeResults);
      })
      .catch((err) => {
        console.error('Search failed:', err);
        setResults([]);
      })
      .finally(() => {
        setLoading(false);
        onDone();
      });
  }, [trigger]);

  return (
    <>
      {loading && <p className="text-sm text-gray-600">Searching...</p>}

      {!loading && hasSearched && results.length === 0 && (
        <p className="text-sm text-gray-500 pl-1">No results found.</p>
      )}

      {results.map((res, i) => (
        <div
          key={i}
          className="rounded-xl border bg-white p-4 shadow-sm transition hover:shadow-md"
        >
          <p className="font-medium text-gray-800">{res.text}</p>
          {Array.isArray(res.match_tokens) && (
            <p className="text-xs text-gray-500 mt-1">
              Matched: {res.match_tokens.join(', ')}
            </p>
          )}
        </div>
      ))}
    </>
  );
}
