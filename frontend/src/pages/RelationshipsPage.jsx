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
  const [updateProps, setUpdateProps] = useState(JSON.stringify({ revisada: true, observacion: 'Actualizada' }, null, 2))
  const [deleteProps, setDeleteProps] = useState('observacion')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  function parseJson(text) {
    try { return JSON.parse(text || '{}') }
    catch { throw new Error('JSON no válido.') }
  }

  async function run(action, success) {
    setLoading(true); setError(''); setMessage(''); setResult(null)
    try {
      const { data } = await action()
      setResult(data); setMessage(success)
      await loadRelationships()
    } catch (err) { setError(formatError(err)) }
    finally { setLoading(false) }
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

  return (
    <section>
      <div className="page-header">
        <div>
          <p className="eyebrow">CRUD · Relaciones</p>
          <h2>Gestión de relaciones</h2>
          <p>Crea, consulta, actualiza y elimina relaciones entre nodos del grafo.</p>
        </div>
      </div>

      <div className="grid-2">
        {/* CREAR */}
        <div className="panel">
          <h3>Crear relación</h3>
          <div className="form-grid">
            {Object.entries(form).map(([key, value]) => (
              <div key={key}>
                <label>{key.replace(/_/g,' ')}</label>
                <input value={value} onChange={e => setForm({ ...form, [key]: e.target.value })} />
              </div>
            ))}
          </div>
          <label>Propiedades (JSON)</label>
          <textarea value={properties} onChange={e => setProperties(e.target.value)} rows={8} />
          <div className="button-row">
            <button className="primary" onClick={() => run(() => api.post('/relationships', {
              ...form, properties: parseJson(properties),
            }), 'Relación creada.')}>+ Crear relación</button>
          </div>
        </div>

        {/* GESTIONAR */}
        <div className="panel">
          <h3>Consultar y modificar</h3>
          <label>Tipo de relación</label>
          <div style={{ display: 'flex', gap: 8 }}>
            <input value={relType} onChange={e => setRelType(e.target.value)} placeholder="USA, TIENE_CUENTA..." />
            <button className="default" style={{ flexShrink: 0 }} onClick={loadRelationships}>⌕</button>
          </div>
          <label>element_id de relación</label>
          <input value={elementId} onChange={e => setElementId(e.target.value)} placeholder="Se llena automáticamente al consultar" />

          <hr className="section-divider" />

          <label>Propiedades a actualizar (JSON)</label>
          <textarea value={updateProps} onChange={e => setUpdateProps(e.target.value)} rows={5} />
          <div className="button-row">
            <button className="default" onClick={() => run(() => api.patch('/relationships', {
              element_id: elementId, properties: parseJson(updateProps),
            }), 'Relación actualizada.')}>Actualizar 1</button>
            <button className="default" onClick={() => run(() => api.patch('/relationships/bulk', {
              relationship_type: relType, properties: parseJson(updateProps), limit: 25,
            }), 'Actualización múltiple.')}>Actualizar varias</button>
          </div>

          <hr className="section-divider" />

          <label>Propiedades a eliminar (separadas por coma)</label>
          <input value={deleteProps} onChange={e => setDeleteProps(e.target.value)} />
          <div className="button-row">
            <button className="default" onClick={() => run(() => api.delete('/relationships/properties', { data: {
              element_id: elementId, property_names: deleteProps.split(',').map(x => x.trim()).filter(Boolean),
            }}), 'Propiedades eliminadas.')}>Elim. propiedades</button>
            <button className="default" onClick={() => run(() => api.delete('/relationships/bulk/properties', { data: {
              relationship_type: relType, property_names: deleteProps.split(',').map(x => x.trim()).filter(Boolean), limit: 25,
            }}), 'Eliminado en varias.')}>Elim. en varias</button>
            <button className="danger" onClick={() => run(() => api.delete('/relationships', { data: { element_id: elementId }}), 'Relación eliminada.')}>✕ Eliminar 1</button>
            <button className="danger" onClick={() => run(() => api.delete('/relationships/bulk', { data: { relationship_type: relType, limit: 5 }}), 'Relaciones eliminadas.')}>✕ Eliminar varias</button>
          </div>
        </div>
      </div>

      <Status loading={loading} error={error} message={message} />
      <JsonBox data={result} />
      {rows.length > 0 && (
        <div className="panel">
          <h3>Relaciones consultadas</h3>
          <DataTable rows={rows} />
        </div>
      )}
    </section>
  )
}
