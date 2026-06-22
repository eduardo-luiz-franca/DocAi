"use client"

import { useMemo, useRef, useState } from "react"
import {
  Upload,
  FileText,
  ChevronLeft,
  ChevronRight,
  FileStack,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import {
  type DocumentItem,
  type DocStatus,
  statusLabels,
} from "@/lib/docai-data"
import { API_URL } from "@/lib/api"

const statusStyles: Record<DocStatus, string> = {
  processado: "border-success/30 bg-success/10 text-success",
  processando: "border-brand/30 bg-brand/10 text-brand",
  "na-fila": "border-border bg-muted text-muted-foreground",
  erro: "border-destructive/30 bg-destructive/10 text-destructive",
}

function StatusBadge({ status }: { status: DocStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        statusStyles[status],
      )}
    >
      <span className="size-1.5 rounded-full bg-current" />
      {statusLabels[status]}
    </span>
  )
}

const PAGE_SIZE_OPTIONS = [5, 20] as const

export function DocumentsPanel({ documents }: { documents: DocumentItem[] }) {
  const [batchSize, setBatchSize] = useState(10)
  const [pageSize, setPageSize] = useState<number>(5)
  const [page, setPage] = useState(0)
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const totalPages = Math.max(1, Math.ceil(documents.length / pageSize))
  const currentPage = Math.min(page, totalPages - 1)

  const pageItems = useMemo(
    () =>
      documents.slice(
        currentPage * pageSize,
        currentPage * pageSize + pageSize,
      ),
    [documents, currentPage, pageSize],
  )

  const isEmpty = documents.length === 0

  function handleUploadClick() {
    fileInputRef.current?.click()
  }

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files
    if (!files || files.length === 0) return

    setUploading(true)
    const formData = new FormData()
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i])
    }

    try {
      const response = await fetch(
        `${API_URL}/ingest?batch_size=${batchSize}`,
        {
          method: "POST",
          body: formData,
        },
      )
      await response.json()
      window.location.reload()
    } catch (error) {
      alert("Erro ao enviar arquivos")
    } finally {
      setUploading(false)
    }
  }

  return (
    <section className="flex flex-col gap-4">
      {/* Input de arquivo escondido */}
      <input
        ref={fileInputRef}
        type="file"
        accept="application/pdf"
        multiple
        className="hidden"
        onChange={handleFileChange}
      />

      {/* Upload controls */}
      <div className="flex flex-col gap-3 rounded-lg border border-border bg-card p-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="flex flex-col gap-1.5">
          <label
            htmlFor="batch-size"
            className="text-xs font-medium text-muted-foreground"
          >
            Batch Size
          </label>
          <input
            id="batch-size"
            type="number"
            min={1}
            max={100}
            value={batchSize}
            onChange={(e) => setBatchSize(Number(e.target.value))}
            className="h-9 w-32 rounded-md border border-input bg-background px-3 text-sm tabular-nums outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
        </div>
        <Button className="gap-2" onClick={handleUploadClick} disabled={uploading}>
          <Upload className="size-4" />
          {uploading ? "Enviando..." : "Upload de PDFs"}
        </Button>
      </div>

      {/* Table card */}
      <div className="overflow-hidden rounded-lg border border-border bg-card">
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <h2 className="text-sm font-medium">Documentos</h2>
          <span className="text-xs text-muted-foreground">
            {documents.length.toLocaleString("pt-BR")} no total
          </span>
        </div>

        {isEmpty ? (
          <EmptyState onUploadClick={handleUploadClick} uploading={uploading} />
        ) : (
          <div className="w-full">
            <table className="w-full table-fixed border-collapse text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs text-muted-foreground">
                  <th className="w-[46%] px-4 py-2.5 font-medium">Nome</th>
                  <th className="w-[16%] px-4 py-2.5 text-right font-medium">
                    Páginas
                  </th>
                  <th className="w-[16%] px-4 py-2.5 text-right font-medium">
                    Chunks
                  </th>
                  <th className="w-[22%] px-4 py-2.5 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {pageItems.map((doc) => (
                  <tr
                    key={doc.id}
                    className="border-b border-border/60 last:border-0 transition-colors hover:bg-accent/40"
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2.5 min-w-0">
                        <FileText className="size-4 shrink-0 text-muted-foreground" />
                        <span className="truncate font-medium">{doc.name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums text-muted-foreground">
                      {doc.pages}
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums text-muted-foreground">
                      {doc.chunks.toLocaleString("pt-BR")}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={doc.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {!isEmpty && (
          <div className="flex flex-col gap-3 border-t border-border px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span>Itens por página</span>
              <div className="flex overflow-hidden rounded-md border border-border">
                {PAGE_SIZE_OPTIONS.map((size) => (
                  <button
                    key={size}
                    type="button"
                    onClick={() => {
                      setPageSize(size)
                      setPage(0)
                    }}
                    className={cn(
                      "px-2.5 py-1 text-xs tabular-nums transition-colors",
                      pageSize === size
                        ? "bg-foreground text-background"
                        : "text-muted-foreground hover:bg-accent",
                    )}
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <span className="text-xs text-muted-foreground tabular-nums">
                Página {currentPage + 1} de {totalPages}
              </span>
              <div className="flex items-center gap-1">
                <Button
                  variant="outline"
                  size="icon"
                  className="size-8"
                  disabled={currentPage === 0}
                  onClick={() => setPage((p) => Math.max(0, p - 1))}
                  aria-label="Página anterior"
                >
                  <ChevronLeft className="size-4" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  className="size-8"
                  disabled={currentPage >= totalPages - 1}
                  onClick={() =>
                    setPage((p) => Math.min(totalPages - 1, p + 1))
                  }
                  aria-label="Próxima página"
                >
                  <ChevronRight className="size-4" />
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}

function EmptyState({
  onUploadClick,
  uploading,
}: {
  onUploadClick: () => void
  uploading: boolean
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 px-6 py-16 text-center">
      <div className="flex size-12 items-center justify-center rounded-full border border-border bg-muted text-muted-foreground">
        <FileStack className="size-6" />
      </div>
      <div className="space-y-1">
        <p className="text-sm font-medium">Nenhum documento ainda</p>
        <p className="max-w-xs text-pretty text-sm text-muted-foreground">
          Faça o upload dos seus PDFs para começar a indexar e conversar com
          seus documentos.
        </p>
      </div>
      <Button className="mt-1 gap-2" onClick={onUploadClick} disabled={uploading}>
        <Upload className="size-4" />
        {uploading ? "Enviando..." : "Upload de PDFs"}
      </Button>
    </div>
  )
}