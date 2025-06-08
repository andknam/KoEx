import { useRef, useEffect, useState } from 'react';
import CharacterBreakdown from './CharacterBreakdown';
import { ArrowLeft, ArrowRight } from 'lucide-react';

export default function ScrollableWordCards({ words }: { words: any }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [showLeft, setShowLeft] = useState(false);
  const [showRight, setShowRight] = useState(false);

  const updateScrollState = () => {
    const el = scrollRef.current;
    if (!el) return;
    setShowLeft(el.scrollLeft > 0);
    setShowRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 1);
  };

  const scrollLeft = () => {
    scrollRef.current?.scrollBy({ left: -200, behavior: 'smooth' });
  };

  const scrollRight = () => {
    scrollRef.current?.scrollBy({ left: 200, behavior: 'smooth' });
  };

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;

    updateScrollState();
    el.addEventListener('scroll', updateScrollState);
    return () => el.removeEventListener('scroll', updateScrollState);
  }, []);

  return (
    <div className="relative">
      {/* Left Arrow */}
      <button
        onClick={scrollLeft}
        className={`absolute left-0 top-1/2 -translate-y-1/2 z-10 p-2 rounded-full bg-transparent hover:bg-white/20 transition-all duration-700 ease-in-out ${
          showLeft
            ? 'opacity-100 scale-100 pointer-events-auto'
            : 'opacity-0 scale-95 pointer-events-none'
        }`}
      >
        <ArrowLeft className="w-6 h-6 text-gray-700" />
      </button>

      {/* Scrollable Word Cards */}
      <div
        ref={scrollRef}
        className="flex overflow-x-auto gap-4 p-2 scrollbar-hidden scroll-smooth snap-x snap-mandatory"
      >
        {words.map((word, i) => (
          <div
            key={i}
            className="snap-start min-w-[200px] max-w-xs shrink-0 p-3 border rounded bg-white/80 shadow text-sm"
          >
            <p className="font-semibold mb-2">
              {word.korean} ({word.hanja})
            </p>
            <CharacterBreakdown characters={word.characters} />
          </div>
        ))}
      </div>

      {/* Right Arrow */}
      <button
        onClick={scrollRight}
        className={`absolute right-0 top-1/2 -translate-y-1/2 z-10 p-2 rounded-full bg-transparent hover:bg-white/20 transition-all duration-700 ease-in-out ${
          showRight
            ? 'opacity-100 scale-100 pointer-events-auto'
            : 'opacity-0 scale-95 pointer-events-none'
        }`}
      >
        <ArrowRight className="w-6 h-6 text-gray-700" />
      </button>
    </div>
  );
}
