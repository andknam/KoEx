import React from 'react';

type Props = {
  inputRef: React.RefObject<HTMLInputElement>;
  onSubmit: () => void;
};

function InputForm({ inputRef, onSubmit }: Props) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="flex items-center gap-2 mb-6">
      <input
        ref={inputRef}
        className="border border-gray-300 rounded px-3 py-2 w-64"
        type="text"
        placeholder="Enter Korean word or phrase"
        onKeyDown={handleKeyDown}
      />
      <button
        onClick={onSubmit}
        className="bg-black text-white px-4 py-2 rounded hover:bg-gray-800"
      >
        Analyze
      </button>
    </div>
  );
}

export default React.memo(InputForm); // ✅ still memoized
