export default function JsonBox({ data }) {
  if (!data) return null
  return <pre className="json-box">{JSON.stringify(data, null, 2)}</pre>
}
