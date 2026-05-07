import { useEffect, useState } from 'react'
import { api, formatError } from '../services/api.js'
import DataTable from '../components/DataTable.jsx'
import Status from '../components/Status.jsx'

function Card({ label, value, hint }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value ?? '0'}</strong>
      {hint && <small>{hint}</small>}
    </div>
  )
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [url, setUrl] = useState('')
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

  async function runAction(action) {
    setLoading(true)
    setError('')
    setMessage('')
    try {
      await action()
      setMessage('Operación realizada correctamente.')
      await refresh()
    } catch (err) {
      setError(formatError(err))
    } finally {
      setLoading(false)
    }
  }

  async function uploadCsv(event) {
    const file = event.target.files?.[0]
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    await runAction(() => api.post('/load/upload?batch_size=500&clear_before_load=false', formData))
  }

  const totals = summary?.totals || {}

  return (
    <section>
      <div className="page-header">
        <div>
          <p className="eyebrow">Panel general</p>
          <h2>Detección de fraude con Neo4j</h2>
          <p>Administre la carga masiva, revise los nodos creados y ejecute las consultas del modelo.</p>
        </div>
        <button className="primary" onClick={refresh}>Actualizar</button>
      </div>

      <div className="metrics-grid">
        <Card label="Nodos" value={totals.total_nodes} hint="mínimo requerido: 5000" />
        <Card label="Relaciones" value={totals.total_relationships} hint="10 tipos definidos" />
        <Card label="Transacciones sospechosas" value={totals.suspicious_transactions} hint="por monto, frecuencia o ubicación" />
      </div>

      <div className="grid-2">
        <div className="panel">
          <h3>Carga y configuración</h3>
          <p className="muted">Primero cree constraints. Luego cargue el CSV local, un CSV subido o un CSV publicado en GitHub Raw.</p>
          <div className="button-row">
            <button onClick={() => runAction(() => api.post('/setup/constraints'))}>Crear constraints</button>
            <button onClick={() => runAction(() => api.post('/load/local', { path: '../data/transacciones_fraude.csv', batch_size: 500, clear_before_load: false }))}>Cargar CSV local</button>
            <button className="danger" onClick={() => runAction(() => api.delete('/setup/clear'))}>Limpiar BD</button>
          </div>
          <label className="file-label">
            Subir CSV desde la computadora
            <input type="file" accept=".csv" onChange={uploadCsv} />
          </label>
          <div className="url-loader">
            <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="Pegue URL raw del CSV" />
            <button onClick={() => runAction(() => api.post('/load/url', { csv_url: url, batch_size: 500, clear_before_load: false }))}>Cargar URL</button>
          </div>
          <Status loading={loading} error={error} message={message} />
        </div>

        <div className="panel">
          <h3>Conteo por label</h3>
          <DataTable rows={summary?.labels || []} />
        </div>
      </div>

      <div className="panel">
        <h3>Conteo por tipo de relación</h3>
        <DataTable rows={summary?.relationships || []} />
      </div>
    </section>
  )
}
