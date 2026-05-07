import { useEffect, useMemo, useState } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import Status from '../components/Status.jsx'
import { api, formatError, getGraphConnected } from '../services/api.js'

const labelColors = {
  Usuario: '#0090ff',
  Cuenta: '#00dbb4',
  Transaccion: '#ffb03a',
  Dispositivo: '#c084fc',
  Ubicacion: '#ff4d6d',
}

function nodeName(node) {
  const p = node.properties || {}
  return p.nombre || p.id_usuario || p.id_cuenta || p.id_transaccion || p.id_dispositivo || p.id_ubicacion || node.id
}

export default function GraphPage() {
  const [graph, setGraph] = useState({ nodes: [], links: [] })
  const [limit, setLimit] = useState(150)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState(null)
  const [graphStatus, setGraphStatus] = useState(null)

  async function loadGraph() {
    setLoading(true); setError('')
    try {
      const { data } = await api.get('/graph/sample', { params: { limit } })
      setGraph(data)
    } catch (err) { setError(formatError(err)) }
    finally { setLoading(false) }
  }

  async function checkGraph() {
    try {
      const data = await getGraphConnected()
      setGraphStatus(data)
    } catch (err) {
      setError(formatError(err))
    }
  }

  useEffect(() => { loadGraph() }, [])

  const stats = useMemo(() => {
    const labels = graph.nodes.reduce((acc, n) => {
      acc[n.label] = (acc[n.label] || 0) + 1
      return acc
    }, {})
    return Object.entries(labels).map(([label, total]) => ({ label, total }))
  }, [graph])

  return (
    <section>
      <div className="page-header">
        <div>
          <p className="eyebrow">Visualización</p>
          <h2>Grafo de entidades bancarias</h2>
          <p>Vista exploratoria interactiva — haz clic en un nodo para ver sus propiedades.</p>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <input className="small-input" type="number" value={limit} onChange={e => setLimit(e.target.value)} />
          <button className="primary" onClick={loadGraph}>↻ Cargar grafo</button>
          <button onClick={checkGraph}>✔ Validar grafo</button>
        </div>
      </div>

      <Status loading={loading} error={error} />

      <div className="grid-graph">
        <div className="graph-panel">
          <ForceGraph2D
            graphData={graph}
            backgroundColor="#111820"
            nodeLabel={node => `${node.label}: ${nodeName(node)}`}
            linkLabel={link => link.type}
            nodeCanvasObject={(node, ctx, globalScale) => {
              const label = nodeName(node)
              const fontSize = Math.max(10 / globalScale, 2)
              ctx.beginPath()
              ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false)
              ctx.fillStyle = labelColors[node.label] || '#e2eaf4'
              ctx.fill()
              if (globalScale > 1.5) {
                ctx.font = `${fontSize}px DM Sans, Arial`
                ctx.fillStyle = 'rgba(226,234,244,0.7)'
                ctx.fillText(label, node.x + 7, node.y + 3)
              }
            }}
            linkColor={() => 'rgba(255,255,255,0.12)'}
            linkDirectionalArrowLength={4}
            linkDirectionalArrowRelPos={1}
            onNodeClick={setSelected}
            cooldownTicks={80}
          />
        </div>
        <aside className="panel details-panel">
          <h3>Leyenda</h3>
          <ul className="legend">
            {Object.entries(labelColors).map(([label, color]) => {
              const stat = stats.find(s => s.label === label)
              return (
                <li key={label}>
                  <span className="legend-dot" style={{ background: color }} />
                  {label}{stat ? ` · ${stat.total}` : ''}
                </li>
              )
            })}
          </ul>
          <hr className="section-divider" />
          <h3>Nodo seleccionado</h3>
          {selected
            ? <pre className="json-box compact">{JSON.stringify(selected, null, 2)}</pre>
            : <p className="empty">Haz clic en un nodo para ver sus propiedades.</p>
          }

          <hr className="section-divider" />
          <h3>Estado del grafo</h3>

<div style={{ background: "#1a2332", padding: "12px", borderRadius: "8px", marginTop: "8px" }}>
  {graphStatus ? (
    <>
      <p><strong>Total nodos:</strong> {graphStatus.total_nodes}</p>
      <p><strong>Alcanzables:</strong> {graphStatus.reachable_nodes}</p>
      <p>
        <strong>Estado:</strong> {graphStatus.is_connected ? "Conexo ✅" : "No conexo ❌"}
      </p>
    </>
  ) : (
    <p className="empty">Presiona validar para verificar el grafo.</p>
  )}
</div>
        </aside>
      </div>
    </section>
  )
}
