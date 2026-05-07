import { useEffect, useMemo, useState } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import { api, formatError } from '../services/api.js'
import Status from '../components/Status.jsx'

const labelColors = {
  Usuario: '#2f80ed',
  Cuenta: '#27ae60',
  Transaccion: '#f2994a',
  Dispositivo: '#9b51e0',
  Ubicacion: '#eb5757',
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

  async function loadGraph() {
    setLoading(true); setError('')
    try {
      const { data } = await api.get('/graph/sample', { params: { limit } })
      setGraph(data)
    } catch (err) { setError(formatError(err)) }
    finally { setLoading(false) }
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
          <p>Vista exploratoria de usuarios, cuentas, transacciones, dispositivos, ubicaciones y relaciones del modelo.</p>
        </div>
        <div className="button-row">
          <input className="small-input" type="number" value={limit} onChange={(e) => setLimit(e.target.value)} />
          <button className="primary" onClick={loadGraph}>Cargar grafo</button>
        </div>
      </div>

      <Status loading={loading} error={error} />

      <div className="grid-graph">
        <div className="graph-panel">
          <ForceGraph2D
            graphData={graph}
            nodeLabel={(node) => `${node.label}: ${nodeName(node)}`}
            linkLabel={(link) => link.type}
            nodeCanvasObject={(node, ctx, globalScale) => {
              const label = nodeName(node)
              const fontSize = 11 / globalScale
              ctx.beginPath()
              ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false)
              ctx.fillStyle = labelColors[node.label] || '#111827'
              ctx.fill()
              ctx.font = `${fontSize}px Inter, Arial`
              ctx.fillStyle = '#111827'
              ctx.fillText(label, node.x + 7, node.y + 3)
            }}
            linkDirectionalArrowLength={4}
            linkDirectionalArrowRelPos={1}
            onNodeClick={setSelected}
            cooldownTicks={80}
          />
        </div>
        <aside className="panel details-panel">
          <h3>Resumen visual</h3>
          <ul className="legend">
            {stats.map((item) => (
              <li key={item.label}><span style={{ background: labelColors[item.label] || '#111827' }} />{item.label}: {item.total}</li>
            ))}
          </ul>
          <h3>Nodo seleccionado</h3>
          {selected ? <pre className="json-box compact">{JSON.stringify(selected, null, 2)}</pre> : <p className="empty">Seleccione un nodo para ver sus propiedades.</p>}
        </aside>
      </div>
    </section>
  )
}
