import { Link, useLocation } from 'react-router-dom'
import { Brain, LayoutDashboard, BarChart3, Home } from 'lucide-react'

const nav = [
  { path: '/', label: 'Home', icon: Home },
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/analytics', label: 'Analytics', icon: BarChart3 },
]

export default function Sidebar({ active }) {
  return (
    <div
      className="fixed left-0 top-0 bottom-0 w-60 flex flex-col z-30"
      style={{
        background: 'rgba(7,7,14,0.92)',
        borderRight: '1px solid rgba(255,255,255,0.06)',
        backdropFilter: 'blur(20px)',
      }}
    >
      {/* Logo */}
      <div className="px-5 py-5" style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <Link to="/" className="flex items-center gap-3 group">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-all duration-200 group-hover:scale-110"
            style={{
              background: 'linear-gradient(135deg, #7c3aed, #2563eb)',
              boxShadow: '0 4px 20px rgba(124,58,237,0.4)',
            }}
          >
            <Brain size={18} className="text-white" />
          </div>
          <div>
            <div className="font-bold text-white text-sm leading-none tracking-tight">PipelineIQ</div>
            <div className="text-[10px] text-slate-600 leading-none mt-0.5">AI Sales Intelligence</div>
          </div>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 space-y-1">
        {nav.map(({ path, label, icon: Icon }) => {
          const isActive = active === label.toLowerCase()
          return (
            <Link
              key={path}
              to={path}
              className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'nav-active'
                  : 'text-slate-500 hover:text-slate-100 hover:bg-white/[0.05]'
              }`}
            >
              <Icon
                size={16}
                className={isActive ? 'text-violet-400' : ''}
              />
              {label}
              {isActive && (
                <div
                  className="ml-auto w-1.5 h-1.5 rounded-full"
                  style={{ background: '#7c3aed', boxShadow: '0 0 6px #7c3aed' }}
                />
              )}
            </Link>
          )
        })}
      </nav>

      {/* Version tag */}
      <div className="p-4" style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}>
        <div
          className="flex items-center gap-2 px-3 py-2 rounded-lg"
          style={{ background: 'rgba(16,185,129,0.07)', border: '1px solid rgba(16,185,129,0.15)' }}
        >
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 glow-pulse flex-shrink-0" />
          <span className="text-xs text-emerald-400 font-medium">API Online</span>
          <span className="ml-auto text-[10px] text-emerald-600">v2.0</span>
        </div>
      </div>
    </div>
  )
}
