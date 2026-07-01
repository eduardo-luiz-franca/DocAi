"use client"

import { useState, useEffect } from "react"
import { LogOut } from "lucide-react"
import { Button } from "@/components/ui/button"
import { DashboardHeader } from "@/components/dashboard-header"
import { StatsCards } from "@/components/stats-cards"
import { DocumentsPanel } from "@/components/documents-panel"
import { ChatPanel } from "@/components/chat-panel"
import { ConversationsSidebar } from "@/components/conversations-sidebar"
import type { DocumentItem, DocStatus } from "@/lib/docai-data"
import { API_URL } from "@/lib/api"

function mapStatus(status: string): DocStatus {
  switch (status) {
    case "done":
      return "processado"
    case "processing":
      return "processando"
    case "error":
      return "erro"
    default:
      return "na-fila"
  }
}

export default function Page() {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [totalChunks, setTotalChunks] = useState(0)
  const [currentConversationId, setCurrentConversationId] = useState<string>("")
  const [chatKey, setChatKey] = useState(0)

  const handleConversationChange = (id: string) => {
    setCurrentConversationId(id)
    setChatKey((k) => k + 1)
  }

  useEffect(() => {
    fetch(`${API_URL}/documents`)
      .then((res) => res.json())
      .then((data) => {
        const mappedDocs: DocumentItem[] = (data.documents || []).map((doc: any) => ({
          id: doc.id,
          name: doc.filename,
          pages: doc.total_pages,
          chunks: doc.chunks_generated ?? 0,
          status: mapStatus(doc.status),
        }))
        setDocuments(mappedDocs)
        setTotalChunks(data.total_chunks ?? 0)
      })
      .catch((error) => {
        console.error("Erro ao buscar documentos:", error)
      })
  }, [])

  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="mx-auto grid max-w-[1400px] grid-cols-1 gap-6 p-4 md:p-6 lg:grid-cols-[1fr_360px] lg:items-start">
        {/* Coluna principal */}
        <div className="flex flex-col gap-6">
          <DashboardHeader />
          <div className="flex items-center justify-end gap-2">
            <ConversationsSidebar
              currentConversationId={currentConversationId}
              onConversationChange={handleConversationChange}
            />
            <Button variant="outline" size="sm" className="gap-2">
              <LogOut className="size-4" />
              Sair
            </Button>
          </div>
          <StatsCards
            totalDocuments={documents.length}
            totalChunks={totalChunks}
          />
          <DocumentsPanel documents={documents} />
        </div>

        {/* Coluna lateral (fixa) */}
        <aside className="h-[600px] lg:sticky lg:top-6 lg:h-[calc(100vh-3rem)]">
          {currentConversationId && (
            <ChatPanel key={chatKey} conversationId={currentConversationId} />
          )}
        </aside>
      </div>
    </main>
  )
}