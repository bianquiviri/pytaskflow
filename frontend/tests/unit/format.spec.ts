import { describe, expect, it } from 'vitest'
import { dueDateLabel, formatDate, fromDatetimeLocal, toDatetimeLocal } from '@/utils/format'

describe('formatDate', () => {
  it('returns a dash for null/undefined', () => {
    expect(formatDate(null)).toBe('—')
    expect(formatDate(undefined)).toBe('—')
  })
})

describe('dueDateLabel', () => {
  it('classifies overdue, today, upcoming and none', () => {
    const yesterday = new Date(Date.now() - 86_400_000).toISOString()
    const today = new Date()
    today.setHours(12, 0, 0, 0)
    const tomorrow = new Date(Date.now() + 86_400_000).toISOString()
    expect(dueDateLabel(yesterday)).toBe('overdue')
    expect(dueDateLabel(today.toISOString())).toBe('today')
    expect(dueDateLabel(tomorrow)).toBe('upcoming')
    expect(dueDateLabel(null)).toBe('none')
  })
})

describe('datetime-local helpers', () => {
  it('round-trips through the local-input format', () => {
    const iso = new Date(2026, 4, 10, 14, 30).toISOString()
    const local = toDatetimeLocal(iso)
    expect(local).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/)
    const roundTripped = fromDatetimeLocal(local)
    expect(new Date(roundTripped as string).getMinutes()).toBe(30)
  })

  it('maps empty input to null', () => {
    expect(fromDatetimeLocal('')).toBeNull()
  })
})
