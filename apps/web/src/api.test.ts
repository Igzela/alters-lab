import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ApiError, fetchJson, postJson, deleteJson } from './api'

describe('ApiError', () => {
  it('has correct properties', () => {
    const err = new ApiError(404, 'NOT_FOUND', 'Resource not found', 'abc123')
    expect(err.name).toBe('ApiError')
    expect(err.status).toBe(404)
    expect(err.errorCode).toBe('NOT_FOUND')
    expect(err.message).toBe('Resource not found')
    expect(err.requestId).toBe('abc123')
    expect(err).toBeInstanceOf(Error)
  })
})

describe('fetchJson', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('returns parsed JSON on success', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), { status: 200 }),
    )
    const result = await fetchJson('/test')
    expect(result).toEqual({ ok: true })
  })

  it('throws ApiError on non-OK response with JSON body', async () => {
    const makeResponse = () =>
      new Response(JSON.stringify({ error: 'NOT_FOUND', message: 'gone', request_id: 'x1' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      })
    vi.spyOn(globalThis, 'fetch').mockImplementation(async () => makeResponse())
    try {
      await fetchJson('/missing')
      expect.unreachable('should have thrown')
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError)
      expect((e as ApiError).status).toBe(404)
      expect((e as ApiError).errorCode).toBe('NOT_FOUND')
      expect((e as ApiError).message).toBe('gone')
      expect((e as ApiError).requestId).toBe('x1')
    }
  })

  it('throws ApiError with defaults on non-JSON error', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('Internal error', { status: 500 }),
    )
    try {
      await fetchJson('/fail')
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError)
      expect((e as ApiError).status).toBe(500)
      expect((e as ApiError).errorCode).toBe('UNKNOWN_ERROR')
    }
  })
})

describe('postJson', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('sends POST with JSON body', async () => {
    const spy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ created: true }), { status: 200 }),
    )
    await postJson('/create', { name: 'test' })
    expect(spy).toHaveBeenCalledWith('/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'test' }),
    })
  })
})

describe('deleteJson', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('sends DELETE with JSON body', async () => {
    const spy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ deleted: true }), { status: 200 }),
    )
    await deleteJson('/remove', { id: 'abc' })
    expect(spy).toHaveBeenCalledWith('/remove', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: 'abc' }),
    })
  })
})
