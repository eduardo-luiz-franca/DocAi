import { LogOut } from "lucide-react"
import { Button } from "@/components/ui/button"

export function DashboardHeader() {
  return (
    <header className="flex items-center justify-between border-b border-border pb-5">
      <div className="flex items-center gap-3">
        <div className="flex size-9 items-center justify-center rounded-md bg-brand/15 text-brand">
          <svg
            aria-hidden="true"
            viewBox="0 0 24 24"
            className="size-5"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <path d="M14 2v6h6" />
            <path d="M9 13h6" />
            <path d="M9 17h3" />
          </svg>
        </div>
        <div>
          <h1 className="text-lg font-semibold leading-none tracking-tight">DocAI</h1>
          <p className="mt-1 text-xs text-muted-foreground">Pipeline de documentos & RAG</p>
        </div>
      </div>

      <Button variant="outline" size="sm" className="gap-2">
        <LogOut className="size-4" />
        Sair
      </Button>
    </header>
  )
}
