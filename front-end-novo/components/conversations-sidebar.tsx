"use client"

import { useState, useEffect } from "react"
import { Plus, Trash2, MessageCircle, ChevronDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { API_URL } from "@/lib/api"

interface Conversation {
  id: string
  created_at: string
}

interface ConversationsSidebarProps {
  currentConversationId: string
  onConversationChange: (id: string) => void
}

export function ConversationsSidebar({
  currentConversationId,
  onConversationChange,
}: ConversationsSidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen) {
      fetchConversations()
    }
  }, [isOpen])

  async function fetchConversations() {
    try {
      const response = await fetch(`${API_URL}/conversations`)
      const data = await response.json()
      setConversations(data || [])
    } catch (error) {
      console.error("Erro ao carregar conversas:", error)
    }
  }

  async function handleNewChat() {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/conversations`, {
        method: "POST",
      })
      const data = await response.json()
      onConversationChange(data.conversation_id)
      await fetchConversations()
      setIsOpen(false)
    } catch (error) {
      console.error("Erro ao criar conversa:", error)
    } finally {
      setLoading(false)
    }
  }

  async function handleDeleteChat(id: string) {
    try {
      await fetch(`${API_URL}/conversations/${id}`, { method: "DELETE" })
      setConversations((prev) => prev.filter((c) => c.id !== id))
      if (currentConversationId === id && conversations.length > 0) {
        const nextChat = conversations.find((c) => c.id !== id)
        if (nextChat) onConversationChange(nextChat.id)
      }
    } catch (error) {
      console.error("Erro ao deletar conversa:", error)
    }
  }

  return (
    <div className="relative">
      <Button
        onClick={() => setIsOpen(!isOpen)}
        variant="outline"
        size="sm"
        className="gap-2"
      >
        <MessageCircle className="size-4" />
        Chats
        <ChevronDown className={`size-4 transition-transform ${isOpen ? "rotate-180" : ""}`} />
      </Button>

      {isOpen && (
        <div className="absolute top-full mt-2 w-80 rounded-lg border border-border bg-card shadow-lg p-4 z-50">
          <div className="space-y-3">
            <Button
              onClick={handleNewChat}
              disabled={loading}
              className="w-full gap-2"
            >
              <Plus className="size-4" />
              Novo Chat
            </Button>

            <div className="border-t border-border pt-3 max-h-64 overflow-y-auto space-y-2">
              {conversations.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-4">
                  Nenhuma conversa ainda
                </p>
              ) : (
                conversations.map((conv, index) => (
                  <div
                    key={conv.id}
                    className={`flex items-center justify-between p-2 rounded-md cursor-pointer transition-colors group ${
                      currentConversationId === conv.id
                        ? "bg-brand/20 border border-brand/50"
                        : "hover:bg-muted"
                    }`}
                    onClick={() => {
                      onConversationChange(conv.id)
                      setIsOpen(false)
                    }}
                  >
                    <div className="flex-1">
                      <span className="text-xs font-medium">
                        Chat {conversations.length - index}
                      </span>
                      <p className="text-[10px] text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity">
                        {new Date(conv.created_at).toLocaleDateString("pt-BR", {
                          month: "short",
                          day: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeleteChat(conv.id)
                      }}
                      className="p-1 hover:bg-destructive/20 rounded transition-colors ml-2 opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 className="size-3 text-destructive" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
