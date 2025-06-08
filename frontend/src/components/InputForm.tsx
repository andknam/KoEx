type Props = {
  input: string;
  setInput: (val: string) => void;
  onSubmit: () => void;
};

export default function InputForm({ input, setInput, onSubmit }: Props) {
  return (
    <div className="flex items-center gap-2 mb-6">
      <input
        className="border border-gray-300 rounded px-3 py-2 w-64"
        type="text"
        placeholder="Enter Korean word or phrase"
        value={input}
        onChange={(e) => setInput(e.target.value)}
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
