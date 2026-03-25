import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Brain, BarChart3, Search, FileText, Target,
  ArrowRight, Sparkles, TrendingUp, Users, Building, Mail,
} from 'lucide-react'

const features = [
  { icon: Brain,    title:'Intent Scoring',          desc:'AI calculates 0–100 intent scores per lead based on seniority, engagement, company size, and revenue signals.', g:'from-violet-500 to-purple-700', glow:'rgba(124,58,237,0.35)' },
  { icon: Sparkles, title:'AI Pitch Generation',      desc:'Claude AI generates personalized 5-part cold emails tailored to each lead\'s role, industry, and detected pain point.', g:'from-blue-500 to-cyan-600', glow:'rgba(37,99,235,0.35)' },
  { icon: BarChart3,title:'Funnel Analytics',         desc:'Visualize your full pipeline from first contact to attended meeting with conversion rates and radar charts.', g:'from-emerald-500 to-teal-600', glow:'rgba(16,185,129,0.35)' },
  { icon: Search,   title:'Natural Language Search',  desc:'Search your lead database in plain English — "Find SaaS CEOs at mid-size companies with high engagement scores."', g:'from-orange-500 to-amber-500', glow:'rgba(249,115,22,0.35)' },
  { icon: Building, title:'Company Intelligence',     desc:'Live website scraping + Claude AI generates deep company profiles with growth signals and outreach opportunities.', g:'from-pink-500 to-rose-600', glow:'rgba(236,72,153,0.35)' },
  { icon: FileText, title:'Executive Reports',        desc:'AI-generated pipeline reports with bottleneck analysis, best performing segments, and actionable recommendations.', g:'from-indigo-500 to-violet-600', glow:'rgba(99,102,241,0.35)' },
]

const steps = [
  { num:'01', title:'Ingest CRM Data',   desc:'Upload your CSV. The pipeline normalizes contacts, companies, and leads into a relational database.' },
  { num:'02', title:'AI Enrichment',     desc:'Intent scoring, problem detection, sequence assignment, and pitch generation run automatically.' },
  { num:'03', title:'Simulate Pipeline', desc:'Realistic funnel simulation models open rates, replies, and meeting bookings by segment.' },
  { num:'04', title:'Analyze & Close',   desc:'Explore leads, generate deep intelligence reports, and export 3-variant personalized emails.' },
]

// Magnetic button hook
function useMagnetic(strength = 0.35) {
  const ref = useRef(null)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const move = (e) => {
      const r = el.getBoundingClientRect()
      const x = (e.clientX - r.left - r.width/2) * strength
      const y = (e.clientY - r.top - r.height/2) * strength
      el.style.transform = `translate(${x}px, ${y}px)`
    }
    const leave = () => { el.style.transform = '' }
    el.addEventListener('mousemove', move)
    el.addEventListener('mouseleave', leave)
    return () => { el.removeEventListener('mousemove', move); el.removeEventListener('mouseleave', leave) }
  }, [strength])
  return ref
}

// Animated counter
function Counter({ target, suffix='' }) {
  const [val, setVal] = useState(0)
  const ref = useRef(null)
  useEffect(() => {
    const io = new IntersectionObserver(([e]) => {
      if (!e.isIntersecting) return
      io.disconnect()
      const n = parseInt(target)
      if (isNaN(n)) { setVal(target); return }
      let i = 0
      const steps = 50
      const timer = setInterval(() => {
        i++
        setVal(Math.round((n * i) / steps))
        if (i >= steps) clearInterval(timer)
      }, 20)
    }, { threshold: 0.5 })
    if (ref.current) io.observe(ref.current)
    return () => io.disconnect()
  }, [target])
  return <span ref={ref} className="ticker">{typeof val === 'number' ? val + suffix : val}</span>
}

export default function Landing() {
  const cta1 = useMagnetic(0.3)
  const cta2 = useMagnetic(0.3)

  return (
    <div className="min-h-screen overflow-x-hidden">
      {/* ── Navbar ── */}
      <nav className="fixed top-0 left-0 right-0 z-50" style={{ background:'rgba(7,7,14,0.7)', backdropFilter:'blur(24px)', borderBottom:'1px solid rgba(255,255,255,0.06)' }}>
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background:'linear-gradient(135deg,#7c3aed,#2563eb)', boxShadow:'0 4px 16px rgba(124,58,237,0.4)' }}>
              <Brain size={17} className="text-white" />
            </div>
            <span className="font-bold text-base tracking-tight">PipelineIQ</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-slate-500">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-white transition-colors">How It Works</a>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/analytics" className="btn-ghost text-sm py-2 px-4">Analytics</Link>
            <Link to="/dashboard" className="btn-primary text-sm py-2 px-4">
              Dashboard <ArrowRight size={14} />
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative pt-36 pb-32 px-6 overflow-hidden">
        <div className="relative max-w-5xl mx-auto text-center">
          {/* Badge */}
          <div className="anim-fade-up inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-8 badge-animated"
            style={{ border:'1px solid rgba(124,58,237,0.35)', background:'rgba(124,58,237,0.1)', color:'#c4b5fd', fontSize:'0.8rem', fontWeight:600 }}>
            <Sparkles size={12} />
            Powered by Claude AI · Built for SDR Teams
          </div>

          {/* Headline */}
          <h1 className="anim-fade-up-d1 font-bold leading-[1.06] tracking-tight mb-6"
            style={{ fontSize:'clamp(2.8rem,6vw,4.5rem)' }}>
            <span className="grad-text">AI-Powered</span>
            {' '}Sales Intelligence
            <br />
            <span style={{ color:'#475569', fontSize:'0.65em', fontWeight:600 }}>
              for modern SDR teams
            </span>
          </h1>

          <p className="anim-fade-up-d2 text-lg text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Transform raw CRM data into intent-scored leads, personalized pitches,
            live company intelligence, and deep funnel analytics — all powered by Claude AI.
          </p>

          <div className="anim-fade-up-d3 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/dashboard" ref={cta1} className="btn-primary text-base px-8 py-3.5" style={{ transition:'transform 0.2s cubic-bezier(.34,1.56,.64,1), opacity 0.18s, box-shadow 0.18s' }}>
              Launch Dashboard <ArrowRight size={17} />
            </Link>
            <Link to="/analytics" ref={cta2} className="btn-ghost text-base px-8 py-3.5" style={{ transition:'transform 0.2s cubic-bezier(.34,1.56,.64,1), color 0.18s, background 0.18s' }}>
              View Analytics <BarChart3 size={16} />
            </Link>
          </div>

          {/* Stats strip */}
          <div className="anim-fade-up-d4 mt-20 grid grid-cols-2 md:grid-cols-4 rounded-2xl overflow-hidden"
            style={{ border:'1px solid rgba(255,255,255,0.07)', background:'rgba(255,255,255,0.03)' }}>
            {[
              { label:'Leads Analyzed', icon:Users,     target:'114',  suffix:'' },
              { label:'Intent Range',   icon:Target,    target:'0–100', suffix:'' },
              { label:'Email Variants', icon:Mail,      target:'3',    suffix:'×' },
              { label:'Web Research',   icon:Sparkles,  target:'Live', suffix:'' },
            ].map(({ label, icon: Icon, target, suffix }, i) => (
              <div key={label} className="flex flex-col items-center gap-2 py-7 px-4"
                style={{ borderLeft: i > 0 ? '1px solid rgba(255,255,255,0.06)' : 'none', background:'rgba(7,7,14,0.6)' }}>
                <Icon className="text-violet-400 mb-0.5" size={18} />
                <div className="text-2xl font-bold text-white">
                  <Counter target={target} suffix={suffix} />
                </div>
                <div className="text-xs text-slate-600 text-center">{label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section id="features" className="py-28 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest mb-5"
              style={{ border:'1px solid rgba(37,99,235,0.25)', background:'rgba(37,99,235,0.08)', color:'#93c5fd' }}>
              What's inside
            </div>
            <h2 className="text-3xl md:text-4xl font-bold mb-3">
              Everything your SDR team <span className="grad-text">needs</span>
            </h2>
            <p className="text-slate-400 text-lg max-w-xl mx-auto">
              Six AI-powered modules that turn cold lists into warm pipeline.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map(({ icon: Icon, title, desc, g, glow }) => (
              <div key={title} className="feature-card p-6 group">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${g} flex items-center justify-center mb-5 transition-all duration-300 group-hover:scale-110 group-hover:rotate-3`}
                  style={{ boxShadow:`0 8px 24px ${glow}` }}>
                  <Icon className="text-white" size={22} />
                </div>
                <h3 className="font-semibold text-white mb-2 text-sm">{title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How it works ── */}
      <section id="how-it-works" className="py-28 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest mb-5"
              style={{ border:'1px solid rgba(16,185,129,0.25)', background:'rgba(16,185,129,0.07)', color:'#6ee7b7' }}>
              The process
            </div>
            <h2 className="text-3xl md:text-4xl font-bold">
              Four steps to <span className="grad-text">closed deals</span>
            </h2>
          </div>

          <div className="grid md:grid-cols-4 gap-6 relative">
            <div className="hidden md:block absolute top-8 left-[12.5%] right-[12.5%] h-px"
              style={{ background:'linear-gradient(90deg, transparent, rgba(124,58,237,0.5), rgba(37,99,235,0.4), transparent)' }} />
            {steps.map(({ num, title, desc }) => (
              <div key={num} className="text-center relative group">
                <div className="w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center glow-pulse transition-all duration-300 group-hover:scale-110"
                  style={{ border:'1px solid rgba(124,58,237,0.3)', background:'rgba(124,58,237,0.08)' }}>
                  <span className="text-violet-400 font-bold text-sm">{num}</span>
                </div>
                <h3 className="font-semibold text-white mb-2 text-sm">{title}</h3>
                <p className="text-slate-500 text-xs leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="py-24 px-6">
        <div className="max-w-3xl mx-auto">
          <div className="relative rounded-2xl p-12 text-center overflow-hidden"
            style={{ background:'linear-gradient(135deg, rgba(124,58,237,0.1) 0%, rgba(37,99,235,0.08) 100%)', border:'1px solid rgba(124,58,237,0.2)' }}>
            <div className="absolute -top-20 -right-20 w-64 h-64 rounded-full" style={{ background:'rgba(124,58,237,0.08)', filter:'blur(60px)' }} />
            <div className="absolute -bottom-20 -left-20 w-64 h-64 rounded-full" style={{ background:'rgba(37,99,235,0.07)', filter:'blur(60px)' }} />
            <div className="relative">
              <Sparkles className="mx-auto text-violet-400 mb-4" size={30} />
              <h2 className="text-3xl font-bold mb-3">
                Ready to <span className="grad-text">supercharge</span> your pipeline?
              </h2>
              <p className="text-slate-400 mb-8">Your leads are already scored and enriched. Jump in and start closing.</p>
              <Link to="/dashboard" className="btn-primary text-base px-8 py-3.5">
                Launch Dashboard <ArrowRight size={17} />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 text-center" style={{ borderTop:'1px solid rgba(255,255,255,0.05)' }}>
        <div className="flex items-center justify-center gap-2 text-slate-700 text-sm">
          <div className="w-5 h-5 rounded bg-gradient-to-br from-violet-500 to-blue-600 flex items-center justify-center">
            <Brain size={11} className="text-white" />
          </div>
          PipelineIQ — AI Sales Intelligence
        </div>
      </footer>
    </div>
  )
}
