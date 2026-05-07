import { useState } from 'react'
import { api, formatError } from '../services/api.js'
import DataTable from '../components/DataTable.jsx'
import JsonBox from '../components/JsonBox.jsx'
import Status from '../components/Status.jsx'

const defaultNode = JSON.stringify({
  id_usuario: 'USU_MANUAL_001',
  nombre: 'Usuario Manual',
  edad: 30,
  verificado: true,
  correos_asociados: ['manual@demo.com'],
  fecha_registro: '2026-05-01',
}, null, 2)

export default function NodesPage() {
  const [labels, setLabels] = useState('Usuario')
  const [properties, setProperties] = useState(defaultNode)
  const [searchLabel, setSearchLabel] = useState('Usuario')
  const [matchProperty, setMatchProperty] = useState('id_usuario')
  const [matchValue, setMatchValue] = useState('')
  const [rows, setRows] = useState([])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [updateProps, setUpdateProps] = useState(JSON.stringify({ revisado: true, comentario: 'Actualizado desde interfaz' }, null, 2))
  const [deleteProps, setDeleteProps] = useState('comentario')

  function parseJson(text) {
    try { return JSON.parse(text || '{}') }
    catch { throw new Error('El JSON de propiedades no es válido.') }
  }

  async function run(action, success = 'Operación realizada correctamente.') {
    setLoading(true); setError(''); setMessage(''); setResult(null)
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

  async function createNode() {
    const payload = { labels: labels.split(',').map(x => x.trim()).filter(Boolean), properties: parseJson(properties) }
    await run(() => api.post('/nodes', payload), 'Nodo creado correctamente.')
  }

  async function searchNodes() {
    setLoading(true); setError(''); setMessage('')
    try {
      const params = { limit: 100 }
      if (matchProperty && matchValue) {
        params.match_property = matchProperty
        params.match_value = matchValue
      }
      const { data } = await api.get(`/nodes/${searchLabel}`, { params })
      setRows(data)
      setMessage('Consulta realizada correctamente.')
    } catch (err) {
      setError(formatError(err))
    } finally {
      setLoading(false)
    }
  }

  async function updateNode() {
    await run(() => api.patch('/nodes', {
      label: searchLabel,
      match_property: matchProperty,
      match_value: matchValue,
      properties: parseJson(updateProps),
    }), 'Propiedades actualizadas.')
  }

  async function deleteNodeProperties() {
    await run(() => api.delete('/nodes/properties', { data: {
      label: searchLabel,
      match_property: matchProperty,
      match_value: matchValue,
      property_names: deleteProps.split(',').map(x => x.trim()).filter(Boolean),
    }}), 'Propiedades eliminadas.')
  }

  async function deleteNode() {
    await run(() => api.delete('/nodes', { data: {
      label: searchLabel,
      match_property: matchProperty,
      match_value: matchValue,
    }}), 'Nodo eliminado.')
  }

  async function bulkUpdate() {
    await run(() => api.patch('/nodes/bulk', {
      label: searchLabel,
      match_property: matchProperty || null,
      match_value: matchValue || null,
      properties: parseJson(updateProps),
      limit: 25,
    }), 'Actualización múltiple realizada.')
  }

  async function bulkDeleteProperties() {
    await run(() => api.delete('/nodes/bulk/properties', { data: {
      label: searchLabel,
      match_property: matchProperty || null,
      match_value: matchValue || null,
      property_names: deleteProps.split(',').map(x => x.trim()).filter(Boolean),
      limit: 25,
    }}), 'Eliminación múltiple de propiedades realizada.')
  }

  return (
    <section>
      <div className="page-header">
        <div>
          <p className="eyebrow">CRUD de nodos</p>
          <h2>Gestión de nodos y propiedades</h2>
          <p>Cree nodos con una o varias labels, consulte registros y modifique propiedades individuales o múltiples.</p>
        </div>
      </div>

      <div className="grid-2">
        <div className="panel">
          <h3>Crear nodo</h3>
          <label>Labels separadas por coma</label>
          <input value={labels} onChange={(e) => setLabels(e.target.value)} placeholder="Usuario, Sospechoso" />
          <label>Propiedades JSON</label>
          <textarea value={properties} onChange={(e) => setProperties(e.target.value)} rows={12} />
          <button className="primary" onClick={createNode}>Crear nodo</button>
        </div>

        <div className="panel">
          <h3>Buscar y gestionar</h3>
          <div className="form-grid">
            <div>
              <label>Label</label>
              <input value={searchLabel} onChange={(e) => setSearchLabel(e.target.value)} />
            </div>
            <div>
              <label>Propiedad de búsqueda</label>
              <input value={matchProperty} onChange={(e) => setMatchProperty(e.target.value)} />
            </div>
            <div>
              <label>Valor</label>
              <input value={matchValue} onChange={(e) => setMatchValue(e.target.value)} />
            </div>
          </div>
          <button onClick={searchNodes}>Consultar nodos</button>
          <label>Propiedades para agregar/actualizar</label>
          <textarea value={updateProps} onChange={(e) => setUpdateProps(e.target.value)} rows={6} />
          <div className="button-row">
            <button onClick={updateNode}>Actualizar 1 nodo</button>
            <button onClick={bulkUpdate}>Actualizar varios</button>
          </div>
          <label>Propiedades a eliminar, separadas por coma</label>
          <input value={deleteProps} onChange={(e) => setDeleteProps(e.target.value)} />
          <div className="button-row">
            <button onClick={deleteNodeProperties}>Eliminar propiedades</button>
            <button onClick={bulkDeleteProperties}>Eliminar propiedades en varios</button>
            <button className="danger" onClick={deleteNode}>Eliminar nodo</button>
          </div>
        </div>
      </div>

      <Status loading={loading} error={error} message={message} />
      <JsonBox data={result} />
      <div className="panel">
        <h3>Resultado de consulta</h3>
        <DataTable rows={rows} />
      </div>
    </section>
  )
}
