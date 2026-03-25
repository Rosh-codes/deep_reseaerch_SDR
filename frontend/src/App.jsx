import { BrowserRouter, Routes, Route } from 'react-router-dom'
import CustomCursor from './components/CustomCursor'
import AnimatedBackground from './components/AnimatedBackground'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import Analytics from './pages/Analytics'

export default function App() {
  return (
    <BrowserRouter>
      <CustomCursor />
      <AnimatedBackground />
      <div className="relative z-10">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}
