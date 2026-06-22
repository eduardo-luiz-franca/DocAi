import { FileText, Layers, Activity } from "lucide-react"
import type { LucideIcon } from "lucide-react"

interface StatCardProps {
  label: string
  value: string
  hint: string
  icon: LucideIcon
  accent?: boolean
}

function StatCard({ label, value, hint, icon: Icon, accent }: StatCardProps) {
  return (
    <div className="flex flex-col justify-between rounded-lg border border-border bg-card p-4">
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted-foreground">{label}</span>
        <Icon className="size-4 text-muted-foreground" aria-hidden="true" />
      </div>
      <div className="mt-4">
        <div className="text-2xl font-semibold tracking-tight">{value}</div>
        <div className="mt-1 flex items-center gap-1.5 text-xs">
          {accent ? (
            <span className="inline-flex items-center gap-1.5 text-success">
              <span className="size-1.5 rounded-full bg-success" />
              {hint}
            </span>
          ) : (
            <span className="text-muted-foreground">{hint}</span>
          )}
        </div>
      </div>
    </div>
  )
}

interface StatsCardsProps {
  totalDocuments: number
  totalChunks: number
}

export function StatsCards({ totalDocuments, totalChunks }: StatsCardsProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <StatCard
        label="Total de Documentos"
        value={totalDocuments.toLocaleString("pt-BR")}
        hint="arquivos indexados"
        icon={FileText}
      />
      <StatCard
        label="Total de Chunks"
        value={totalChunks.toLocaleString("pt-BR")}
        hint="vetores gerados"
        icon={Layers}
      />
      <StatCard
        label="Status do Pipeline"
        value="Operacional"
        hint="processando normalmente"
        icon={Activity}
        accent
      />
    </div>
  )
}
