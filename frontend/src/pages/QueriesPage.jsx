import { useEffect, useState } from 'react'
import { api, formatError } from '../services/api.js'
import DataTable from '../components/DataTable.jsx'
import Status from '../components/Status.jsx'

const queries = [
  { id: 'small-frequent', title: 'Microtransacciones', description: 'Cuentas con muchas transacciones < 100 en el mismo día.' },
  { id: 'shared-devices', title: 'Dispositivos compartidos', description: 'Dispositivos usados por más de un usuario.' },
  { id: 'unusual-locations', title: 'Ubicaciones inusuales', description: 'Transacciones fuera del país o ciudad de residencia.' },
  { id: 'high-amount', title: 'Montos altos', description: 'Transacciones mayores a $10,000.' },
  { id: 'new-or-inactive-accounts', title: 'Cuentas sospechosas', description: 'Cuentas nuevas o inactivas con transferencias entrantes.' },
  { id: 'transfer-chains', title: 'Cadenas de transferencia', description: 'Patrones de cuentas encadenadas por transferencias.' },
]

const cypherExamples = {
  'small-frequent': `MATCH (c:Cuenta)-[:EMITE]->(t:Transaccion)
WHERE t.monto < 100
WITH c, t.fecha AS dia, count(t) AS cantidad, sum(t.monto) AS total
WHERE cantidad >= 8
RETURN c.id_cuenta, dia, cantidad, total`,
  'shared-devices': `MATCH (u:Usuario)-[:USA]->(d:Dispositivo)
WITH d, collect(DISTINCT u.nombre) AS usuarios
WHERE size(usuarios) >= 2
RETURN d.id_dispositivo, size(usuarios), usuarios`,
  'unusual-locations': `MATCH (u:Usuario)-[:RESIDE_EN]->(ur:Ubicacion),
(u)-[:TIENE_CUENTA]->(c:Cuenta)-[:EMITE]->(t:Transaccion)-[:OCURRE_EN]->(ut:Ubicacion)
WHERE ur.pais <> ut.pais OR ur.ciudad <> ut.ciudad
RETURN u.nombre, c.id_cuenta, t.id_transaccion`,
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
      setRows(data); setSelected(id); setMessage('Consulta ejecutada.')
    } catch (err) { setError(formatError(err)) }
    finally { setLoading(false) }
  }

  async function loadScores() {
    setLoading(true); setError('')
    try {
      const { data } = await api.get('/fraud/score', { params: { limit: 75 } })
      setScoreRows(data); setMessage('Score calculado.')
    } catch (err) { setError(formatError(err)) }
    finally { setLoading(false) }
  }

  useEffect(() => { runQuery('small-frequent'); loadScores() }, [])

  return (
    <section>
      <div className="page-header">
        <div>
          <p className="eyebrow">Cypher · Data Science</p>
          <h2>Consultas de detección de fraude</h2>
          <p>Patrones de fraude implementados como consultas Cypher especializadas.</p>
        </div>
      </div>

      <div className="query-grid">
        {queries.map(q => (
          <button key={q.id} className={selected === q.id ? 'query-card selected' : 'query-card'} onClick={() => runQuery(q.id)}>
            <strong>{q.title}</strong>
            <span>{q.description}</span>
          </button>
        ))}
      </div>

      <Status loading={loading} error={error} message={message} />

      <div className="grid-2">
        <div className="panel">
          <h3>Resultados</h3>
          <DataTable rows={rows} />
        </div>
        <div className="panel">
          <h3>Cypher de ejemplo</h3>
          <pre className="code-box">{cypherExamples[selected] || '// Consulta implementada en el backend.'}</pre>
        </div>
      </div>

      <div className="panel">
        <div className="panel-title-row">
          <div>
            <h3>Score de riesgo</h3>
            <p className="muted" style={{ margin: 0 }}>Algoritmo basado en microtransacciones, dispositivos compartidos, ubicaciones y cuentas destino inactivas.</p>
          </div>
          <button className="default" onClick={loadScores}>↻ Recalcular</button>
        </div>
        <DataTable rows={scoreRows} />
      </div>
    </section>
  )
}
