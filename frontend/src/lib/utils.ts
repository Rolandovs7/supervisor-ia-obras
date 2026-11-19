import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

import type { Alerta } from './types'

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs))
}

export function initials(email: string): string {
  const name = email.split('@')[0] ?? '?'
  return name.slice(0, 2).toUpperCase()
}

export function formatDate(value?: string | null): string {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('es-PE', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

export function formatTime(value?: string | null): string {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('es-PE', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

export function shortId(value: string): string {
  return value.length > 8 ? `${value.slice(0, 8)}…` : value
}

export function esAlertaCaida(alerta: Pick<Alerta, 'tipo' | 'descripcion'>): boolean {
  const normalizar = (texto: string) =>
    texto.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
  return (
    normalizar(alerta.tipo) === 'caida' ||
    normalizar(alerta.descripcion).includes('caida')
  )
}
