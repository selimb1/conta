import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import App from './App'
import Ingesta from './pages/Ingesta'
import Revision from './pages/Revision'
import Asientos from './pages/Asientos'
import EEFF from './pages/EEFF'

createRoot(document.getElementById('root')!).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App/>} />
      <Route path="/ingesta" element={<Ingesta/>} />
      <Route path="/revision" element={<Revision/>} />
      <Route path="/asientos" element={<Asientos/>} />
      <Route path="/eeff" element={<EEFF/>} />
    </Routes>
  </BrowserRouter>
)