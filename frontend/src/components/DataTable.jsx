function normalizeValue(value) {
  if (value === null || value === undefined) return ''
  if (Array.isArray(value)) return value.join(', ')
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

export default function DataTable({ rows }) {
  if (!rows || rows.length === 0) return <p className="empty">No hay datos para mostrar.</p>
  const columns = Array.from(rows.reduce((set, row) => {
    Object.keys(row).forEach((key) => set.add(key))
    return set
  }, new Set()))

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>{columns.map((col) => <th key={col}>{col}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index}>
              {columns.map((col) => <td key={col}>{normalizeValue(row[col])}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
