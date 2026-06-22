"use client"

import type React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { API_URL } from "@/lib/api"

export function LoginForm() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")

  async function handleSubmit(e: React.FormEvent) {
  e.preventDefault()

  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    })

    const data = await response.json()

    if (data.status === "ok") {
      window.location.href = "/dashboard"
    } else {
      alert("Usuário ou senha incorretos")
    }
  } catch (error) {
    alert("Erro ao conectar com o servidor")
  }
}

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
      <div className="flex flex-col gap-2">
        <Label htmlFor="username" className="text-sm text-muted-foreground">
          Usuário
        </Label>
        <Input
          id="username"
          type="text"
          autoComplete="username"
          placeholder="Digite seu usuário"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="h-11"
          required
        />
      </div>

      <div className="flex flex-col gap-2">
        <Label htmlFor="password" className="text-sm text-muted-foreground">
          Senha
        </Label>
        <Input
          id="password"
          type="password"
          autoComplete="current-password"
          placeholder="Digite sua senha"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="h-11"
          required
        />
      </div>

      <Button type="submit" className="mt-2 h-11 w-full text-sm font-medium">
        Entrar
      </Button>
    </form>
  )
}