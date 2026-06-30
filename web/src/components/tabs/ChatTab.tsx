import { useState, useRef, useEffect } from 'react'
import type { ParsedReport, AnalysisResult, ChatMessage } from '../../types'
import { streamChat } from '../../api'

interface Props {
  parsed: ParsedReport
  analysis: AnalysisResult
  history: ChatMessage[]
  onHistoryChange: (h: ChatMessage[]) => void
}

export default function ChatTab({ parsed, analysis, history, onHistoryChange }: Props) {
  const [input, setInput] = useState('')
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
          const finalAnswer = event.type === 'error' ? `❌ ${event.message}` : answer
          onHistoryChange([...history, userMsg, { role: 'assistant', content: finalAnswer }])
          setCurrentAnswer('')
          setStreaming(false)
        }
      })
    } catch (e) {
      onHistoryChange([...history, userMsg, { role: 'assistant', content: `❌ ${String(e)}` }])
      setCurrentAnswer('')
      setStreaming(false)
    }
  }

  return (
    <div className="flex flex-col h-[520px]">
      <p className="text-xs text-slate-400 mb-3">基于报表结构和 AI 分析结论，回答关于这张报表的具体问题。</p>

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-3 pr-1">
        {history.length === 0 && !streaming && (
          <div className="text-center py-10">
            <div className="text-3xl mb-2">💬</div>
            <div className="text-sm text-slate-400">
              你可以问：这张报表有哪些参数控件？某个字段代表什么业务含义？
            </div>
          </div>
        )}

        {history.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed
              ${msg.role === 'user'
                ? 'bg-blue-600 text-white rounded-br-sm'
                : 'bg-white border border-slate-100 text-slate-700 rounded-bl-sm shadow-sm'
              }`}>
              {msg.content}
            </div>
          </div>
        ))}

        {/* 流式输出中 */}
        {streaming && (
          <div className="flex justify-start">
            <div className={`max-w-[80%] px-3.5 py-2.5 rounded-2xl rounded-bl-sm text-sm leading-relaxed
              bg-white border border-slate-100 text-slate-700 shadow-sm
              ${currentAnswer ? '' : 'stream-cursor'}`}>
              {currentAnswer || <span className="text-slate-400">思考中</span>}
              {currentAnswer && <span className="stream-cursor" />}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* 输入框 */}
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
