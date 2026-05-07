import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/nodos', label: 'Nodos' },
  { to: '/relaciones', label: 'Relaciones' },
  { to: '/consultas', label: 'Consultas' },
  { to: '/grafo', label: 'Grafo' },
]

export default function Layout({ children }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">F</div>
          <div>
            <h1>Fraude Neo4j</h1>
            <p>Detección bancaria</p>
          </div>
        </div>
        <nav>
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
              {link.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-note">
          Modelo basado en Usuario, Cuenta, Transacción, Dispositivo y Ubicación.
        </div>
      </aside>
      <main className="content">{children}</main>
    </div>
  )
}
