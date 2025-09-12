import { Link } from 'react-router-dom'
export default function App(){
  return (
    <div className="p-6">
      <h1>Conta</h1>
      <nav>
        <Link to="/ingesta">Ingesta</Link> ·{" "}
        <Link to="/revision">Revisión</Link> ·{" "}
        <Link to="/asientos">Asientos</Link> ·{" "}
        <Link to="/eeff">EEFF</Link>
      </nav>
    </div>
  )
}