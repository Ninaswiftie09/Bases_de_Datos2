import { useEffect, useState } from 'react'
import { api, formatError } from '../services/api.js'
import DataTable from '../components/DataTable.jsx'
import Status from '../components/Status.jsx'

const queries = [
  { id: 'small-frequent', title: 'Transacciones pequeñas y constantes', description: 'Cuentas con muchas transacciones menores a 100 en un mismo día.' },
  { id: 'shared-devices', title: 'Dispositivos compartidos', description: 'Dispositivos utilizados por más de un usuario.' },
  { id: 'unusual-locations', title: 'Ubicaciones inusuales', description: 'Transacciones fuera de la ciudad o país de residencia.' },
  { id: 'high-amount', title: 'Montos altos', description: 'Transacciones mayores a 10000.' },
  { id: 'new-or-inactive-accounts', title: 'Cuentas nuevas o inactivas', description: 'Cuentas nuevas o inactivas que reciben varias transferencias.' },
  { id: 'transfer-chains', title: 'Cadenas de transferencias', description: 'Patrones de cuentas relacionadas por transferencias encadenadas.' },
]

const cypherExamples = {
  'small-frequent': `MATCH (c:Cuenta)-[:EMITE]->(t:Transaccion)\nWHERE t.monto < 100\nWITH c, t.fecha AS dia, count(t) AS cantidad, sum(t.monto) AS total\nWHERE cantidad >= 8\nRETURN c.id_cuenta, dia, cantidad, total`,
  'shared-devices': `MATCH (u:Usuario)-[:USA]->(d:Dispositivo)\nWITH d, collect(DISTINCT u.nombre) AS usuarios\nWHERE size(usuarios) >= 2\nRETURN d.id_dispositivo, size(usuarios), usuarios`,
  'unusual-locations': `MATCH (u:Usuario)-[:RESIDE_EN]->(ur:Ubicacion),\n(u)-[:TIENE_CUENTA]->(c:Cuenta)-[:EMITE]->(t:Transaccion)-[:OCURRE_EN]->(ut:Ubicacion)\nWHERE ur.pais <> ut.pais OR ur.ciudad <> ut.ciudad\nRETURN u.nombre, c.id_cuenta, t.id_transaccion`,
}

export default function QueriesPage() {
  const [selected, setSelected] = useState('small-frequent')
  const [rows, setRows] = useState([])
  const [scoreRows, setScoreRows] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function runQuery(id = selected) {
    setLoading(true); setError(''); setMessage('')
    try {
      const { data } = await api.get(`/queries/${id}`, { params: { limit: 75 } })
      setRows(data)
      setSelected(id)
      setMessage('Consulta ejecutada correctamente.')
    } catch (err) {
      setError(formatError(err))
    } finally { setLoading(false) }
  }

  async function loadScores() {
    setLoading(true); setError('')
    try {
      const { data } = await api.get('/fraud/score', { params: { limit: 75 } })
      setScoreRows(data)
      setMessage('Score de riesgo calculado correctamente.')
    } catch (err) { setError(formatError(err)) }
    finally { setLoading(false) }
  }

  useEffect(() => { runQuery('small-frequent'); loadScores() }, [])

  return (
    <section>
      <div className="page-header">
        <div>
          <p className="eyebrow">Cypher y Data Science</p>
          <h2>Consultas de detección de fraude</h2>
          <p>Ejecute consultas orientadas a microtransacciones, dispositivos compartidos, ubicaciones inusuales y cadenas de transferencia.</p>
        </div>
      </div>

      <div className="query-grid">
        {queries.map((query) => (
          <button key={query.id} className={selected === query.id ? 'query-card selected' : 'query-card'} onClick={() => runQuery(query.id)}>
            <strong>{query.title}</strong>
            <span>{query.description}</span>
          </button>
        ))}
      </div>

      <Status loading={loading} error={error} message={message} />

      <div className="grid-2">
        <div className="panel">
          <h3>Resultado de consulta</h3>
          <DataTable rows={rows} />
        </div>
        <div className="panel">
          <h3>Cypher de ejemplo</h3>
          <pre className="code-box">{cypherExamples[selected] || 'La consulta se encuentra implementada en el backend.'}</pre>
        </div>
      </div>

      <div className="panel">
        <div className="panel-title-row">
          <div>
            <h3>Score de riesgo</h3>
            <p className="muted">Algoritmo simple basado en microtransacciones, dispositivos no confiables, dispositivos compartidos y cuentas destino nuevas o inactivas.</p>
          </div>
          <button onClick={loadScores}>Recalcular score</button>
        </div>
        <DataTable rows={scoreRows} />
      </div>
    </section>
  )
}
