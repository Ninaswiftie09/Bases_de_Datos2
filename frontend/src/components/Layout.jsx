import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Dashboard', icon: '⬡' },
  { to: '/nodos', label: 'Nodos', icon: '◉' },
  { to: '/relaciones', label: 'Relaciones', icon: '⟷' },
  { to: '/consultas', label: 'Consultas', icon: '⌖' },
  { to: '/grafo', label: 'Grafo', icon: '⬡' },
]

export default function Layout({ children }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-top">
          <div className="brand">
            <div className="brand-icon">F</div>
            <div className="brand-text">
              <h1>TriData</h1>
              <p>Neo4j · Detección bancaria</p>
            </div>
          </div>
        </div>
        <nav>
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === '/'}
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <span className="nav-icon">{link.icon}</span>
              {link.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          Modelo: <strong>Usuario · Cuenta · Transacción · Dispositivo · Ubicación</strong>
        </div>
      </aside>
      <main className="content">{children}</main>
    </div>
  )
}
