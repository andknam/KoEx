import { useRef, useEffect, useState } from 'react';
import HanjaBreakdown from './HanjaBreakdown';
import { ArrowLeft, ArrowRight } from 'lucide-react';

export default function ScrollableWordCards({ words }: { words: any }) {
    const scrollRef = useRef<HTMLDivElement>(null);
    const [showLeft, setShowLeft] = useState(false);
    const [showRight, setShowRight] = useState(false);

    const updateScrollState = () => {
        const el = scrollRef.current;
        if (!el) return;

        // curr horizontal scroll pos, total scrollable width, visible width
        const scrollLeft = el.scrollLeft;
        const scrollWidth = el.scrollWidth;
        const clientWidth = el.clientWidth;

        // check if we are at start of end of range
        // use threshold of 10 px to avoid rounding issue errors
        const atStart = scrollLeft <= 10;
        const atEnd = scrollLeft + clientWidth >= scrollWidth - 10;

        // show/hide arrows based on pos
        setShowLeft(!atStart);
        setShowRight(!atEnd);
    };

    useEffect(() => {
        const el = scrollRef.current;
        if (!el) return;

        // Ensure visibility is set after layout/render
        const handleResize = () => {
            requestAnimationFrame(updateScrollState);
        };
        updateScrollState();

        // add scroll and resize listeners
        el.addEventListener('scroll', updateScrollState);
        window.addEventListener('resize', handleResize);

        // cleanup listeners on dismount
        return () => {
            el.removeEventListener('scroll', updateScrollState);
            window.removeEventListener('resize', handleResize);
        };
    }, []);

    const scrollByCard = (direction: 'left' | 'right') => {
        const el = scrollRef.current;
        if (!el) return;

        // find first card with snap-start elem, used for width calculation
        const firstCard = el.querySelector('.snap-start') as HTMLElement;
        if (!firstCard) return;

        // get width of card, account for gap betwen cards
        const cardWidth = firstCard.getBoundingClientRect().width;
        const gap = 16; // Tailwind gap-4 = 16px
        const scrollAmount = cardWidth + gap;

        // scroll to the left by one card
        if (direction === 'left') {
            el.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        } else {
            // Clamp scroll to not overshoot
            const remainingScroll = el.scrollWidth - el.clientWidth - el.scrollLeft;
            const actualScroll = Math.min(scrollAmount, remainingScroll);
            el.scrollBy({ left: actualScroll, behavior: 'smooth' });
        }
    };

    const scrollLeft = () => scrollByCard('left');
    const scrollRight = () => scrollByCard('right');

    // no words with hanja
    if (!words || words.length === 0) {
        return (
        <p className="text-sm text-gray-500">
            No words with Chinese character origin found.
        </p>
        );
    }

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
            className="flex overflow-x-auto gap-4 p-2 scroll-smooth snap-x snap-mandatory scrollbar-none"
        >
            {words.map((word, i) => (
            <div
                key={i}
                className="snap-start min-w-[200px] max-w-xs shrink-0 p-3 border rounded bg-white/80 shadow text-sm"
            >
                <p className="font-semibold mb-2">
                {word.korean} ({word.hanja})
                </p>
                <HanjaBreakdown characters={word.characters} />
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
