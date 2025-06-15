import Tabs from './components/Tabs';

export default function App() {
  return (
    <div className="min-h-screen w-full flex flex-col items-start px-6 py-4 bg-gray-50">
      <div className="w-full max-w-3xl space-y-6">
        <header className="space-y-1">
          <h1 className="text-3xl font-bold text-gray-800">KoEx</h1>
          <p className="text-sm text-gray-500 pl-0.5">
            Korean Explainer: analyze Korean, search across YouTube
          </p>
          <p className="text-xs italic text-gray-400 pl-0.5">
            Powered by <code className="text-[11px] font-mono text-gray-500">GPT</code>,{' '}
            <code className="text-[11px] font-mono text-gray-500">Qdrant</code>, and custom grammar + romanization rules
          </p>
        </header>

        <main className="w-full max-w-3xl mt-6">
          <Tabs />
        </main>
      </div>
    </div>
  );
}
