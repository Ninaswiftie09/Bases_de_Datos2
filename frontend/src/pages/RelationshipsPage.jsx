import { useEffect, useState } from 'react'
import { api, formatError } from '../services/api.js'
import DataTable from '../components/DataTable.jsx'
import JsonBox from '../components/JsonBox.jsx'
import Status from '../components/Status.jsx'

export default function RelationshipsPage() {
  const [form, setForm] = useState({
    from_label: 'Usuario', from_property: 'id_usuario', from_value: 'USU_0001',
    to_label: 'Dispositivo', to_property: 'id_dispositivo', to_value: 'DEV_0001',
    relationship_type: 'USA',
  })
  const [properties, setProperties] = useState(JSON.stringify({
    fecha_creacion: '2026-05-01', fuente: 'manual', confianza: 0.91, frecuencia_uso: 1, verificado: true,
  }, null, 2))
  const [relType, setRelType] = useState('USA')
  const [rows, setRows] = useState([])
  const [elementId, setElementId] = useState('')
  const [updateProps, setUpdateProps] = useState(JSON.stringify({ revisada: true, observacion: 'Actualizada desde interfaz' }, null, 2))
  const [deleteProps, setDeleteProps] = useState('observacion')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  function updateField(key, value) { setForm({ ...form, [key]: value }) }
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
      await loadRelationships()
    } catch (err) {
      setError(formatError(err))
    } finally { setLoading(false) }
  }

  async function loadRelationships() {
    try {
      const params = { limit: 50 }
      if (relType) params.relationship_type = relType
      const { data } = await api.get('/relationships', { params })
      setRows(data)
      if (data?.[0]?.element_id && !elementId) setElementId(data[0].element_id)
    } catch (err) { setError(formatError(err)) }
  }

  useEffect(() => { loadRelationships() }, [])

  async function createRelationship() {
    await run(() => api.post('/relationships', { ...form, properties: parseJson(properties) }), 'Relación creada correctamente.')
  }

  async function updateRelationship() {
    await run(() => api.patch('/relationships', { element_id: elementId, properties: parseJson(updateProps) }), 'Relación actualizada.')
  }

  async function deleteRelationshipProperties() {
    await run(() => api.delete('/relationships/properties', { data: { element_id: elementId, property_names: deleteProps.split(',').map(x => x.trim()).filter(Boolean) }}), 'Propiedades eliminadas.')
  }

  async function deleteRelationship() {
    await run(() => api.delete('/relationships', { data: { element_id: elementId }}), 'Relación eliminada.')
  }

  async function bulkUpdate() {
    await run(() => api.patch('/relationships/bulk', { relationship_type: relType, properties: parseJson(updateProps), limit: 25 }), 'Actualización múltiple realizada.')
  }

  async function bulkDeleteProperties() {
    await run(() => api.delete('/relationships/bulk/properties', { data: { relationship_type: relType, property_names: deleteProps.split(',').map(x => x.trim()).filter(Boolean), limit: 25 }}), 'Propiedades eliminadas en varias relaciones.')
  }

  async function bulkDelete() {
    await run(() => api.delete('/relationships/bulk', { data: { relationship_type: relType, limit: 5 }}), 'Relaciones eliminadas.')
  }

  return (
    <section>
      <div className="page-header">
        <div>
          <p className="eyebrow">CRUD de relaciones</p>
          <h2>Gestión de relaciones con propiedades</h2>
          <p>Cree, consulte, actualice y elimine relaciones entre nodos existentes del grafo.</p>
        </div>
      </div>

      <div className="grid-2">
        <div className="panel">
          <h3>Crear relación</h3>
          <div className="form-grid">
            {Object.entries(form).map(([key, value]) => (
              <div key={key}>
                <label>{key}</label>
                <input value={value} onChange={(e) => updateField(key, e.target.value)} />
              </div>
            ))}
          </div>
          <label>Propiedades JSON</label>
          <textarea value={properties} onChange={(e) => setProperties(e.target.value)} rows={8} />
          <button className="primary" onClick={createRelationship}>Crear relación</button>
        </div>

        <div className="panel">
          <h3>Consultar y modificar</h3>
          <label>Tipo de relación</label>
          <input value={relType} onChange={(e) => setRelType(e.target.value)} placeholder="TIENE_CUENTA" />
          <button onClick={loadRelationships}>Consultar relaciones</button>
          <label>elementId de relación</label>
          <input value={elementId} onChange={(e) => setElementId(e.target.value)} />
          <label>Propiedades para actualizar</label>
          <textarea value={updateProps} onChange={(e) => setUpdateProps(e.target.value)} rows={6} />
          <div className="button-row">
            <button onClick={updateRelationship}>Actualizar 1</button>
            <button onClick={bulkUpdate}>Actualizar varias</button>
          </div>
          <label>Propiedades a eliminar</label>
          <input value={deleteProps} onChange={(e) => setDeleteProps(e.target.value)} />
          <div className="button-row">
            <button onClick={deleteRelationshipProperties}>Eliminar propiedades</button>
            <button onClick={bulkDeleteProperties}>Eliminar propiedades en varias</button>
            <button className="danger" onClick={deleteRelationship}>Eliminar 1 relación</button>
            <button className="danger" onClick={bulkDelete}>Eliminar varias</button>
          </div>
        </div>
      </div>

      <Status loading={loading} error={error} message={message} />
      <JsonBox data={result} />
      <div className="panel">
        <h3>Relaciones consultadas</h3>
        <DataTable rows={rows} />
      </div>
    </section>
  )
}
