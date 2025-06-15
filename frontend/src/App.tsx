import Tabs from './components/Tabs';

export default function App() {
  return (
    <div className="min-h-screen w-full flex flex-col items-start px-6 py-4 bg-gray-50">
      <div className="w-full max-w-3xl space-y-6">
        <header>
          <h1 className="text-3xl font-bold text-gray-800">KoEx</h1>
          {/* <p className="text-sm text-gray-500 mt-1"></p> */}
        </header>

        <main>
          <Tabs />
        </main>
      </div>
    </div>
  );
}