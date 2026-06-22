"use client"

import { useState, useEffect } from "react"
import { DashboardHeader } from "@/components/dashboard-header"
import { StatsCards } from "@/components/stats-cards"
import { DocumentsPanel } from "@/components/documents-panel"
import { ChatPanel } from "@/components/chat-panel"
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
          <StatsCards
            totalDocuments={documents.length}
            totalChunks={totalChunks}
          />
          <DocumentsPanel documents={documents} />
        </div>

        {/* Coluna lateral (fixa) */}
        <aside className="h-[600px] lg:sticky lg:top-6 lg:h-[calc(100vh-3rem)]">
          <ChatPanel />
        </aside>
      </div>
    </main>
  )
}