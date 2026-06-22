import { LoginForm } from "@/components/login-form"

export default function Page() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="mb-10 flex flex-col items-center gap-2 text-center">
          <h1 className="text-3xl font-semibold tracking-tight text-foreground">
            DocAI
          </h1>
          <p className="text-sm text-muted-foreground text-balance">
            Acesse sua conta para continuar
          </p>
        </div>

        <LoginForm />
      </div>
    </main>
  )
}