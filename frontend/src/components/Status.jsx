export default function Status({ loading, error, message }) {
  if (loading) return <div className="status loading">Procesando solicitud...</div>
  if (error) return <div className="status error">{error}</div>
  if (message) return <div className="status ok">{message}</div>
  return null
}
