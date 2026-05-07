import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Dashboard from './pages/Dashboard.jsx'
import NodesPage from './pages/NodesPage.jsx'
import RelationshipsPage from './pages/RelationshipsPage.jsx'
import QueriesPage from './pages/QueriesPage.jsx'
import GraphPage from './pages/GraphPage.jsx'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/nodos" element={<NodesPage />} />
        <Route path="/relaciones" element={<RelationshipsPage />} />
        <Route path="/consultas" element={<QueriesPage />} />
        <Route path="/grafo" element={<GraphPage />} />
      </Routes>
    </Layout>
  )
}
