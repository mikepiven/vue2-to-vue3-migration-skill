type Handler = (payload?: unknown) => void

const handlers = new Map<string, Set<Handler>>()

export const bus = {
  on(event: string, handler: Handler) {
    const set = handlers.get(event) ?? new Set<Handler>()
    set.add(handler)
    handlers.set(event, set)
  },
  off(event: string, handler: Handler) {
    handlers.get(event)?.delete(handler)
  },
  emit(event: string, payload?: unknown) {
    handlers.get(event)?.forEach((handler) => handler(payload))
  }
}
