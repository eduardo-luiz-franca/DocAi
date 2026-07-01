"use client"

import { useState, useEffect } from "react"
import { Send, Sparkles, ChevronDown, MessageSquare } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { type ChatMessage } from "@/lib/docai-data"
import { API_URL } from "@/lib/api"

interface ChatPanelProps {
  conversationId: string
}

export function ChatPanel({ conversationId }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(false)

  useEffect(() => {
    if (conversationId) {
      setLoadingHistory(true)
      setMessages([])

      fetch(`${API_URL}/conversations/${conversationId}/messages`)
        .then(r => {
          if (!r.ok) throw new Error("Erro ao carregar histórico")
          return r.json()
        })
        .then(data => {
          const chatMessages: ChatMessage[] = (data.messages || []).map((msg: any) => ({
            id: `${msg.role}-${Date.now()}`,
            role: msg.role as "user" | "assistant",
            content: msg.content,
          }))
          setMessages(chatMessages)
        })
        .catch(err => {
          console.error("Erro ao carregar histórico:", err)
          setMessages([])
        })
        .finally(() => setLoadingHistory(false))
    }
  }, [conversationId])

  async function handleSend(e: React.FormEvent) {
    e.preventDefault()
    const text = input.trim()
    if (!text) return

    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      content: text,
    }

    setMessages((prev) => [...prev, userMsg])
    setInput("")
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text, conversation_id: conversationId }),
      })
      const data = await response.json()

      const assistantMsg: ChatMessage = {
        id: `a-${Date.now()}`,
        role: "assistant",
        content: data.answer || "Não consegui gerar uma resposta.",
        technique: data.retrieval_log?.technique_applied,
        reasoning: data.retrieval_log?.reasoning,
      }

      setMessages((prev) => [...prev, assistantMsg])
    } catch (error) {
      const errorMsg: ChatMessage = {
        id: `e-${Date.now()}`,
        role: "assistant",
        content: "Erro ao conectar com o servidor. Tente novamente.",
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-lg border border-border bg-card">
      {/* Header */}
      <div className="flex items-center gap-2.5 border-b border-border px-4 py-3.5">
        <div className="flex size-7 items-center justify-center rounded-md bg-brand/15 text-brand">
          <MessageSquare className="size-4" />
        </div>
        <div>
          <h2 className="text-sm font-semibold leading-none">Chat Documental</h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Pergunte sobre seus documentos
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 space-y-4 overflow-y-auto px-4 py-4">
        {loadingHistory && (
          <p className="text-center text-xs text-muted-foreground">
            Carregando histórico do chat...
          </p>
        )}
        {!loadingHistory && messages.length === 0 && (
          <p className="text-center text-xs text-muted-foreground">
            Faça uma pergunta sobre os documentos indexados.
          </p>
        )}
        {messages.map((msg) =>
          msg.role === "user" ? (
            <div key={msg.id} className="flex justify-end">
              <div className="max-w-[85%] rounded-2xl rounded-br-sm bg-brand px-3.5 py-2 text-sm text-brand-foreground">
                {msg.content}
              </div>
            </div>
          ) : (
            <div key={msg.id} className="flex flex-col gap-2">
              <div className="max-w-[90%] rounded-2xl rounded-bl-sm border border-border bg-muted px-3.5 py-2 text-sm">
                {msg.content}
              </div>
              {msg.technique && msg.reasoning && (
                <ReasoningPanel
                  technique={msg.technique}
                  reasoning={msg.reasoning}
                />
              )}
            </div>
          ),
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="max-w-[85%] rounded-2xl rounded-bl-sm border border-border bg-muted px-3.5 py-2 text-sm text-muted-foreground">
              Pensando...
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <form
        onSubmit={handleSend}
        className="border-t border-border p-3"
      >
        <div className="flex items-end gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Faça uma pergunta..."
            className="h-10 flex-1 rounded-md border border-input bg-background px-3 text-sm outline-none placeholder:text-muted-foreground focus-visible:ring-2 focus-visible:ring-ring"
            disabled={loading}
          />
          <Button
            type="submit"
            size="icon"
            className="size-10 shrink-0"
            aria-label="Enviar pergunta"
            disabled={!input.trim() || loading}
          >
            <Send className="size-4" />
          </Button>
        </div>
      </form>
    </div>
  )
}

function ReasoningPanel({
  technique,
  reasoning,
}: {
  technique: string
  reasoning: string
}) {
  const [open, setOpen] = useState(false)

  return (
    <div className="max-w-[90%] overflow-hidden rounded-lg border border-border bg-background/60">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between gap-2 px-3 py-2 text-left"
        aria-expanded={open}
      >
        <span className="flex items-center gap-1.5 text-xs font-medium text-brand">
          <Sparkles className="size-3.5" />
          Técnica de pre-retrieval aplicada
        </span>
        <ChevronDown
          className={cn(
            "size-4 shrink-0 text-muted-foreground transition-transform",
            open && "rotate-180",
          )}
        />
      </button>
      {open && (
        <div className="space-y-2.5 border-t border-border px-3 py-2.5">
          <div>
            <p className="text-[11px] uppercase tracking-wide text-muted-foreground">
              Técnica
            </p>
            <p className="mt-0.5 text-xs font-medium">{technique}</p>
          </div>
          <div>
            <p className="text-[11px] uppercase tracking-wide text-muted-foreground">
              Raciocínio (Chain of Thought)
            </p>
            <p className="mt-1 whitespace-pre-line text-xs leading-relaxed text-muted-foreground">
              {reasoning}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}