import { useEffect, useRef, useState } from 'react'
import type { AnalysisResult, ChatMessage, ParsedReport } from '../../types'
import { streamChat } from '../../api'

interface Props {
  parsed: ParsedReport
  analysis: AnalysisResult
  history: ChatMessage[]
  onHistoryChange: (h: ChatMessage[]) => void
  initialQuestion?: string
}

export default function ChatTab({ parsed, analysis, history, onHistoryChange, initialQuestion }: Props) {
  const [input, setInput] = useState(() => initialQuestion ?? '')
  const [streaming, setStreaming] = useState(false)
  const [currentAnswer, setCurrentAnswer] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history, currentAnswer])

  async function handleSend() {
    if (!input.trim() || streaming) return
    const question = input.trim()
    setInput('')
    setStreaming(true)
    setCurrentAnswer('')

    const userMsg: ChatMessage = { role: 'user', content: question }
    onHistoryChange([...history, userMsg])

    let answer = ''
    try {
      await streamChat(parsed, analysis, question, history, (event) => {
        if (event.type === 'token') {
          answer += event.text as string
          setCurrentAnswer(answer)
        } else if (event.type === 'done' || event.type === 'error') {
          const finalAnswer = event.type === 'error' ? `错误：${event.message}` : answer
          onHistoryChange([...history, userMsg, { role: 'assistant', content: finalAnswer }])
          setCurrentAnswer('')
          setStreaming(false)
        }
      })
    } catch (e) {
      onHistoryChange([...history, userMsg, { role: 'assistant', content: `错误：${String(e)}` }])
      setCurrentAnswer('')
      setStreaming(false)
    }
  }

  return (
    <div className="flex flex-col h-[520px]">
      <div className="mb-3 rounded-lg px-3 py-2" style={{ background: 'var(--bg)', border: '1px solid var(--border)' }}>
        <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
          基于报表结构和 AI 分析结论回答当前 CPT 的具体问题。也可以从工作台节点进入，系统会自动带入控件、数据集、字段或风险上下文。
        </p>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 mb-3 pr-1">
        {history.length === 0 && !streaming && (
          <div className="text-center py-10">
            <div className="text-sm text-slate-400">
              你可以问：这张报表有哪些参数控件？某个字段代表什么业务含义？
            </div>
          </div>
        )}

        {history.map((msg, i) => (
          <div key={`${msg.role}-${i}`} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed
              ${msg.role === 'user'
                ? 'bg-blue-600 text-white rounded-br-sm'
                : 'bg-white border border-slate-100 text-slate-700 rounded-bl-sm shadow-sm'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {streaming && (
          <div className="flex justify-start">
            <div className={`max-w-[80%] px-3.5 py-2.5 rounded-2xl rounded-bl-sm text-sm leading-relaxed
              bg-white border border-slate-100 text-slate-700 shadow-sm
              ${currentAnswer ? '' : 'stream-cursor'}`}
            >
              {currentAnswer || <span className="text-slate-400">思考中</span>}
              {currentAnswer && <span className="stream-cursor" />}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
          disabled={streaming}
          placeholder="问一个关于这张报表的问题..."
          className="flex-1 text-sm border border-slate-200 rounded-xl px-3.5 py-2.5
            focus:outline-none focus:border-blue-400 disabled:bg-slate-50 disabled:text-slate-400"
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || streaming}
          className="px-4 py-2.5 rounded-xl bg-blue-600 text-white text-sm font-semibold
            hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 transition-colors"
        >
          发送
        </button>
      </div>
    </div>
  )
}
