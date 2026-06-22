export type DocStatus = "processado" | "processando" | "na-fila" | "erro"

export const statusLabels: Record<DocStatus, string> = {
  processado: "Processado",
  processando: "Processando",
  "na-fila": "Na fila",
  erro: "Erro",
}

export interface DocumentItem {
  id: string
  name: string
  pages: number
  chunks: number
  status: DocStatus
}

export const sampleDocuments: DocumentItem[] = [
  {
    id: "1",
    name: "contrato_servicos_2024.pdf",
    pages: 12,
    chunks: 48,
    status: "processado",
  },
  {
    id: "2",
    name: "relatorio_financeiro_q3.pdf",
    pages: 34,
    chunks: 120,
    status: "processado",
  },
  {
    id: "3",
    name: "manual_tecnico_v2.pdf",
    pages: 89,
    chunks: 310,
    status: "processando",
  },
  {
    id: "4",
    name: "ata_reuniao_diretoria.pdf",
    pages: 5,
    chunks: 18,
    status: "na-fila",
  },
  {
    id: "5",
    name: "edital_processo_seletivo.pdf",
    pages: 22,
    chunks: 76,
    status: "erro",
  },
]

export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  technique?: string
  reasoning?: string
}

export const sampleMessages: ChatMessage[] = [
  {
    id: "1",
    role: "user",
    content: "Quais documentos tratam de contratos de serviço?",
  },
  {
    id: "2",
    role: "assistant",
    content:
      "Encontrei um documento relevante: 'contrato_servicos_2024.pdf', que detalha os termos de prestação de serviço vigentes.",
    technique: "Query Rewriting + Metadata Pre-filtering",
    reasoning:
      "1. Query reescrita para maior especificidade.\n2. Filtro aplicado por tipo de documento.\n3. Busca vetorial retornou 1 chunk com alta similaridade.",
  },
]