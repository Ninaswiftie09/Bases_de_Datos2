import { useEffect, useState } from 'react'
import { api, formatError } from '../services/api.js'
import DataTable from '../components/DataTable.jsx'
import Status from '../components/Status.jsx'

function MetricCard({ label, value, hint }) {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value ?? '—'}</div>
      {hint && <div className="metric-hint">{hint}</div>}
    </div>
  )
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function refresh() {
    setError('')
    try {
      const { data } = await api.get('/summary')
      setSummary(data)
    } catch (err) {
      setError(formatError(err))
    }
  }

  useEffect(() => { refresh() }, [])

  async function runAction(action, successMsg) {
    setLoading(true); setError(''); setMessage('')
    try {
      await action()
      setMessage(successMsg)
      await refresh()
    } catch (err) {
      setError(formatError(err))
    } finally { setLoading(false) }
  }

  const totals = summary?.totals || {}

  return (
    <section>
      <div className="page-header">
        <div>
          <p className="eyebrow">Panel general</p>
          <h2>Detección de Fraude con Neo4j</h2>
          <p>Estado actual de la base de datos, carga de datos y conteos por entidad.</p>
        </div>
        <button className="default" onClick={refresh}>↻ Actualizar</button>
      </div>

      <div className="metrics-grid">
        <MetricCard label="Total de nodos" value={totals.total_nodes?.toLocaleString()} hint="mínimo requerido: 5 000" />
        <MetricCard label="Total de relaciones" value={totals.total_relationships?.toLocaleString()} hint="10 tipos definidos" />
        <MetricCard label="Transacciones sospechosas" value={totals.suspicious_transactions?.toLocaleString()} hint="por monto, frecuencia o ubicación" />
      </div>

      <div className="grid-2">
        <div className="panel">
          <h3>Configuración e inicialización</h3>
          <p className="muted">Crea los constraints primero, luego carga el CSV para poblar la base de datos. El CSV genera más de 5 000 nodos distintos.</p>
          <div className="button-row">
            <button className="default" onClick={() => runAction(() => api.post('/setup/constraints'), 'Constraints creados.')}>
              Crear constraints
            </button>
            <button className="primary" onClick={() => runAction(() => api.post('/load/default?batch_size=500&clear_before_load=false'), 'CSV cargado correctamente.')}>
              ↑ Cargar CSV oficial
            </button>
            <button className="danger" onClick={() => runAction(() => api.delete('/setup/clear'), 'Base de datos limpiada.')}>
              ✕ Limpiar BD
            </button>
          </div>
          <Status loading={loading} error={error} message={message} />
        </div>

        <div className="panel">
          <h3>Nodos por label</h3>
          <DataTable rows={summary?.labels || []} />
        </div>
      </div>

      <div className="panel">
        <h3>Relaciones por tipo</h3>
        <DataTable rows={summary?.relationships || []} />
      </div>
    </section>
  )
}
