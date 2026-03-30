import { useState } from 'react';

function App() {
  const [command, setCommand] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const handleGenerate = async () => {
    if (!command.trim()) return;
    
    setIsGenerating(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch('/contracts/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: command }),
      });

      if (!res.ok) {
        const text = await res.text().catch(() => '');
        throw new Error(text || `HTTP ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
      setCommand('');
    } catch (e: any) {
      setError(e?.message ?? 'Ошибка запроса');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleGenerate();
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#0A0A0A]">
      {/* Градиентные эффекты фона */}
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(1200px_600px_at_50%_-140px,rgba(18,28,50,0.25),rgba(0,0,0,0)_65%)]" />
      <div className="pointer-events-none absolute bottom-[-10%] left-[-10%] aspect-[1/1.2] w-[min(14vw,380px)] rounded-full blur-[72px] bg-[radial-gradient(circle_at_45%_55%,rgba(255,255,255,0.2),rgba(255,255,255,0.09)_45%,rgba(255,255,255,0)_80%)]" />
      <div className="pointer-events-none absolute right-[-10%] top-[-10%] aspect-[1/1.1] w-[min(16vw,420px)] rounded-full blur-[72px] bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.22),rgba(255,255,255,0.1)_45%,rgba(255,255,255,0)_80%)]" />

      {/* Основной контент */}
      <div className="relative flex min-h-screen items-center justify-center p-6">
        <div className="w-full max-w-2xl">
          {/* Заголовок */}
          <h1 className="text-center text-5xl md:text-6xl font-bold text-amber-50 mb-8 tracking-tight">
            Document Generator
          </h1>

          {/* Инструкции */}
          <div className="space-y-2 text-center mb-10">
            <p className="text-gray-300 text-lg">
              1. Input your command in the box below.
            </p>
            <p className="text-gray-300 text-lg">
              2. Wait...
            </p>
            <p className="text-gray-300 text-lg">
              3. Receive your generated file.
            </p>
          </div>

          {/* Поле ввода */}
          <div className="mb-6">
            <textarea
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Input your command..."
              rows={4}
              className="w-full px-5 py-4 bg-white/5 border border-white/10 rounded-2xl text-gray-200 placeholder-gray-500 focus:outline-none focus:border-amber-500/50 focus:ring-2 focus:ring-amber-500/20 transition-all duration-200 resize-none"
              disabled={isGenerating}
            />
          </div>

          {/* Кнопка генерации */}
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !command.trim()}
            className={`
              w-full py-4 rounded-2xl font-semibold text-lg transition-all duration-200
              ${isGenerating || !command.trim()
                ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                : 'bg-linear-to-r from-amber-500 to-amber-600 text-white hover:from-amber-600 hover:to-amber-700 hover:shadow-lg hover:shadow-amber-500/25 active:scale-[0.98]'
              }
            `}
          >
            {isGenerating ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Generating...
              </span>
            ) : (
              'Generate'
            )}
          </button>

          {error && (
            <div className="mt-6 rounded-2xl border border-red-500/25 bg-red-500/10 px-5 py-4 text-red-200">
              {error}
            </div>
          )}

          {result && (
            <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 px-5 py-4 text-gray-200">
              <div className="mb-2 font-semibold text-amber-50">Ответ API</div>
              <pre className="whitespace-pre-wrap wrap-break-word text-sm text-gray-300">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

export default App;