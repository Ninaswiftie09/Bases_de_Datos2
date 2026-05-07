import { useState } from 'react'
import { api, formatError } from '../services/api.js'
import DataTable from '../components/DataTable.jsx'
import JsonBox from '../components/JsonBox.jsx'
import Status from '../components/Status.jsx'

const defaultProps = JSON.stringify({
  id_usuario: 'USU_MANUAL_001',
  nombre: 'Usuario Manual',
  edad: 30,
  verificado: true,
  correos_asociados: ['manual@demo.com'],
  fecha_registro: '2026-05-01',
}, null, 2)

const aggregationOptions = {
  nodes_by_label: {
    title: 'Cantidad de nodos por label',
    description: 'Muestra cuántos nodos existen por cada etiqueta del grafo.',
  },
  avg_amount_by_transaction_type: {
    title: 'Promedio de monto por tipo de transacción',
    description: 'Agrupa las transacciones por tipo y calcula el monto promedio.',
  },
  suspicious_transactions_by_city: {
    title: 'Transacciones sospechosas por ciudad',
    description: 'Cuenta las transacciones marcadas como sospechosas según la ciudad donde ocurrieron.',
  },
}

export default function NodesPage() {
  const [labels, setLabels] = useState('Usuario')
  const [properties, setProperties] = useState(defaultProps)

  const [searchLabel, setSearchLabel] = useState('Usuario')
  const [matchProperty, setMatchProperty] = useState('id_usuario')
  const [matchValue, setMatchValue] = useState('')
  const [rows, setRows] = useState([])

  const [singleNodeId, setSingleNodeId] = useState('')
  const [singleNodeRows, setSingleNodeRows] = useState([])

  const [aggregationKey, setAggregationKey] = useState('nodes_by_label')
  const [aggregationRows, setAggregationRows] = useState([])

  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const [updateProps, setUpdateProps] = useState(JSON.stringify({
    revisado: true,
    comentario: 'Actualizado',
  }, null, 2))

  const [deleteProps, setDeleteProps] = useState('comentario')
  const [bulkLimit, setBulkLimit] = useState(25)

  function parseJson(text) {
    try {
      return JSON.parse(text || '{}')
    } catch {
      throw new Error('JSON no válido.')
    }
  }

  async function run(action, success) {
    setLoading(true)
    setError('')
    setMessage('')
    setResult(null)

    try {
      const { data } = await action()
      setResult(data)
      setMessage(success)
    } catch (err) {
      setError(formatError(err))
    } finally {
      setLoading(false)
    }
  }

  async function searchNodes() {
    setLoading(true)
    setError('')
    setMessage('')

    try {
      const params = { limit: 100 }

      if (matchProperty && matchValue) {
        params.match_property = matchProperty
        params.match_value = matchValue
      }

      const { data } = await api.get(`/nodes/${searchLabel}`, { params })
      setRows(data)
      setMessage('Consulta de muchos nodos realizada.')
    } catch (err) {
      setError(formatError(err))
    } finally {
      setLoading(false)
    }
  }

  async function searchOneNodeById() {
    if (!singleNodeId.trim()) {
      setError('Ingresa el element_id del nodo que quieres consultar.')
      return
    }

    setLoading(true)
    setError('')
    setMessage('')
    setSingleNodeRows([])

    try {
      const { data } = await api.get(`/nodes/by-id/${encodeURIComponent(singleNodeId.trim())}`)
      setSingleNodeRows([data])
      setResult(data)
      setMessage('Consulta de 1 nodo por ID realizada.')
    } catch (err) {
      setError(formatError(err))
    } finally {
      setLoading(false)
    }
  }

  async function loadAggregation(key = aggregationKey) {
    setLoading(true)
    setError('')
    setMessage('')
    setAggregationRows([])

    try {
      const { data } = await api.get('/nodes/aggregations/summary')
      setAggregationKey(key)
      setAggregationRows(data[key] || [])
      setResult(data[key] || [])
      setMessage(`Consulta agregada: ${aggregationOptions[key].title}.`)
    } catch (err) {
      setError(formatError(err))
    } finally {
      setLoading(false)
    }
  }

  async function deleteManyNodes() {
    const payload = {
      label: searchLabel,
      match_property: matchProperty || null,
      match_value: matchValue || null,
      limit: Number(bulkLimit) || 25,
    }

    const filterText = payload.match_property && payload.match_value !== null && payload.match_value !== ''
      ? `${payload.match_property} = ${payload.match_value}`
      : 'sin filtro adicional'

    const ok = window.confirm(
      `Se eliminarán hasta ${payload.limit} nodos con label ${payload.label} (${filterText}). ¿Seguro?`
    )

    if (!ok) return

    await run(
      () => api.delete('/nodes/bulk', { data: payload }),
      'Eliminación múltiple de nodos realizada.'
    )
  }

  return (
    <section>
      <div className="page-header">
        <div>
          <p className="eyebrow">CRUD · Nodos</p>
          <h2>Gestión de nodos</h2>
          <p>Crea, consulta, actualiza y elimina nodos y sus propiedades.</p>
        </div>
      </div>

      <div className="grid-2">
        <div className="panel">
          <h3>Consultar 1 nodo por ID</h3>
          <p className="muted">
            Usa el <code>element_id</code> que aparece en los resultados de la consulta de nodos o en Neo4j Browser.
          </p>

          <label>ID del nodo</label>
          <input
            value={singleNodeId}
            onChange={e => setSingleNodeId(e.target.value)}
            placeholder="Ejemplo: 4:abc123:0"
          />

          <div className="button-row">
            <button className="default" onClick={searchOneNodeById}>
              ⌕ Consultar 1 nodo por ID
            </button>
          </div>
        </div>

        <div className="panel">
          <h3>Consultas agregadas de nodos</h3>
          <p className="muted">
            Estas consultas ayudan a demostrar la visualización y agregación de datos dentro de la sección de nodos.
          </p>

          <div className="button-row">
            {Object.entries(aggregationOptions).map(([key, option]) => (
              <button
                key={key}
                className={aggregationKey === key ? 'primary' : 'default'}
                onClick={() => loadAggregation(key)}
              >
                {option.title}
              </button>
            ))}
          </div>

          <p className="muted" style={{ marginTop: 12 }}>
            {aggregationOptions[aggregationKey].description}
          </p>
        </div>
      </div>

      <div className="grid-2">
        <div className="panel">
          <h3>Crear nodo</h3>

          <label>Labels separadas por coma</label>
          <input
            value={labels}
            onChange={e => setLabels(e.target.value)}
            placeholder="Usuario, Sospechoso"
          />

          <label>Propiedades JSON</label>
          <textarea
            value={properties}
            onChange={e => setProperties(e.target.value)}
            rows={10}
          />

          <div className="button-row">
            <button
              className="primary"
              onClick={() => run(() => api.post('/nodes', {
                labels: labels.split(',').map(x => x.trim()).filter(Boolean),
                properties: parseJson(properties),
              }), 'Nodo creado.')}
            >
              + Crear nodo
            </button>
          </div>
        </div>

        <div className="panel">
          <h3>Buscar y gestionar</h3>

          <div className="form-grid">
            <div>
              <label>Label</label>
              <input
                value={searchLabel}
                onChange={e => setSearchLabel(e.target.value)}
              />
            </div>

            <div>
              <label>Propiedad filtro</label>
              <input
                value={matchProperty}
                onChange={e => setMatchProperty(e.target.value)}
                placeholder="id_usuario"
              />
            </div>

            <div style={{ gridColumn: 'span 2' }}>
              <label>Valor</label>
              <input
                value={matchValue}
                onChange={e => setMatchValue(e.target.value)}
                placeholder="Dejar vacío para traer todos"
              />
            </div>
          </div>

          <div className="button-row">
            <button className="default" onClick={searchNodes}>
              ⌕ Consultar muchos nodos
            </button>
          </div>

          <hr className="section-divider" />

          <label>Propiedades a agregar / actualizar JSON</label>
          <textarea
            value={updateProps}
            onChange={e => setUpdateProps(e.target.value)}
            rows={5}
          />

          <div className="button-row">
            <button
              className="default"
              onClick={() => run(() => api.patch('/nodes', {
                label: searchLabel,
                match_property: matchProperty,
                match_value: matchValue,
                properties: parseJson(updateProps),
              }), 'Propiedades actualizadas.')}
            >
              Actualizar 1 nodo
            </button>

            <button
              className="default"
              onClick={() => run(() => api.patch('/nodes/bulk', {
                label: searchLabel,
                match_property: matchProperty || null,
                match_value: matchValue || null,
                properties: parseJson(updateProps),
                limit: 25,
              }), 'Actualización múltiple.')}
            >
              Actualizar varios
            </button>
          </div>

          <hr className="section-divider" />

          <label>Propiedades a eliminar separadas por coma</label>
          <input
            value={deleteProps}
            onChange={e => setDeleteProps(e.target.value)}
          />

          <div className="button-row">
            <button
              className="default"
              onClick={() => run(() => api.delete('/nodes/properties', {
                data: {
                  label: searchLabel,
                  match_property: matchProperty,
                  match_value: matchValue,
                  property_names: deleteProps.split(',').map(x => x.trim()).filter(Boolean),
                },
              }), 'Propiedades eliminadas.')}
            >
              Elim. propiedades
            </button>

            <button
              className="default"
              onClick={() => run(() => api.delete('/nodes/bulk/properties', {
                data: {
                  label: searchLabel,
                  match_property: matchProperty || null,
                  match_value: matchValue || null,
                  property_names: deleteProps.split(',').map(x => x.trim()).filter(Boolean),
                  limit: 25,
                },
              }), 'Propiedades eliminadas en varios.')}
            >
              Elim. en varios
            </button>

            <button
              className="danger"
              onClick={() => run(() => api.delete('/nodes', {
                data: {
                  label: searchLabel,
                  match_property: matchProperty,
                  match_value: matchValue,
                },
              }), 'Nodo eliminado.')}
            >
              ✕ Eliminar 1 nodo
            </button>
          </div>

          <hr className="section-divider" />

          <h3>Eliminar múltiples nodos</h3>
          <p className="muted">
            Usa el mismo label y filtro de arriba. Si dejas el valor vacío, eliminará hasta el límite indicado para ese label.
          </p>

          <label>Límite de nodos a eliminar</label>
          <input
            type="number"
            min="1"
            max="500"
            value={bulkLimit}
            onChange={e => setBulkLimit(e.target.value)}
          />

          <div className="button-row">
            <button className="danger" onClick={deleteManyNodes}>
              ✕ Eliminar varios nodos
            </button>
          </div>
        </div>
      </div>

      <Status loading={loading} error={error} message={message} />
      <JsonBox data={result} />

      {singleNodeRows.length > 0 && (
        <div className="panel">
          <h3>Resultado de consulta de 1 nodo</h3>
          <DataTable rows={singleNodeRows} />
        </div>
      )}

      {aggregationRows.length > 0 && (
        <div className="panel">
          <h3>{aggregationOptions[aggregationKey].title}</h3>
          <DataTable rows={aggregationRows} />
        </div>
      )}

      {rows.length > 0 && (
        <div className="panel">
          <h3>Resultado de consulta de muchos nodos</h3>
          <DataTable rows={rows} />
        </div>
      )}
    </section>
  )
}