import { useState, useEffect, useCallback } from 'react'
import { Search, Sparkles, Brain, X, TrendingUp, Users, MessageSquare, Calendar, Globe, MapPin, Info, Database } from 'lucide-react'
import { getLeads, searchLeads, getPerformance, getLeadsMeta } from '../api/client'
import Sidebar from '../components/Sidebar'
import LeadModal from '../components/LeadModal'
import { SkeletonLeadCard, SkeletonKPICard } from '../components/SkeletonLoader'

const SEQ_FILTERS = ['All', 'Hot', 'Warm', 'Cold', 'Ignore']

// Status → funnel position (0 = earliest, higher = further down funnel)
const STATUS_RANK = { new:0, contacted:1, opened:2, clicked:3, replied:4, positive_reply:5, negative_reply:4, meeting_booked:6, meeting_attended:7 }
const STATUS_COLORS = {
  new:              { bg:'rgba(107,114,128,0.12)', color:'#9ca3af' },
  contacted:        { bg:'rgba(59,130,246,0.12)',  color:'#93c5fd' },
  opened:           { bg:'rgba(168,85,247,0.12)',  color:'#d8b4fe' },
  clicked:          { bg:'rgba(139,92,246,0.12)',  color:'#c4b5fd' },
  replied:          { bg:'rgba(16,185,129,0.12)',  color:'#6ee7b7' },
  positive_reply:   { bg:'rgba(34,197,94,0.12)',   color:'#86efac' },
  negative_reply:   { bg:'rgba(239,68,68,0.12)',   color:'#fca5a5' },
  meeting_booked:   { bg:'rgba(245,158,11,0.12)',  color:'#fcd34d' },
  meeting_attended: { bg:'rgba(6,182,212,0.12)',   color:'#67e8f9' },
}

function seqClass(seq) {
  if (seq === 'Hot') return 'seq-hot'
  if (seq === 'Warm') return 'seq-warm'
  if (seq === 'Cold') return 'seq-cold'
  return 'seq-ignore'
}

function scoreStyle(score) {
  if (score >= 80) return { bg:'rgba(239,68,68,0.14)', color:'#fca5a5', ring:'rgba(239,68,68,0.3)' }
  if (score >= 60) return { bg:'rgba(249,115,22,0.14)', color:'#fdba74', ring:'rgba(249,115,22,0.3)' }
  if (score >= 40) return { bg:'rgba(59,130,246,0.14)', color:'#93c5fd', ring:'rgba(59,130,246,0.3)' }
  return { bg:'rgba(107,114,128,0.14)', color:'#9ca3af', ring:'rgba(107,114,128,0.2)' }
}

function useCountUp(target, duration = 1200) {
  const [val, setVal] = useState(0)
  useEffect(() => {
    if (target == null) return
    const isPercent = String(target).includes('%')
    const num = parseFloat(String(target).replace('%',''))
    let i = 0; const steps = 60
    const timer = setInterval(() => {
      i++
      const v = Math.min(num, (num * i) / steps)
      setVal(i >= steps ? target : isPercent ? `${v.toFixed(1)}%` : Math.round(v))
      if (i >= steps) clearInterval(timer)
    }, duration / steps)
    return () => clearInterval(timer)
  }, [target, duration])
  return val || (target == null ? '—' : 0)
}

function KPICard({ label, value, icon: Icon, color }) {
  const display = useCountUp(value)
  return (
    <div className="glass p-4 group hover:border-white/[0.12] transition-all">
      <div className="flex items-center justify-between mb-3">
        <span className="text-[11px] text-slate-500 font-medium">{label}</span>
        <div className="w-7 h-7 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110" style={{ background:'rgba(255,255,255,0.05)' }}>
          <Icon size={13} className={color} />
        </div>
      </div>
      <div className={`text-2xl font-bold ticker ${color}`}>{display}</div>
    </div>
  )
}

// The "no results" panel with keyword hints
function EmptySearch({ meta, onKeyword }) {
  const groups = meta?.keyword_groups || {}
  const samples = meta?.sample_searches || []
  return (
    <div className="glass rounded-2xl p-8">
      <div className="flex items-start gap-3 mb-6">
        <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background:'rgba(124,58,237,0.12)', border:'1px solid rgba(124,58,237,0.25)' }}>
          <Database size={16} className="text-violet-400" />
        </div>
        <div>
          <div className="font-semibold text-white text-sm mb-0.5">Demo database active</div>
          <p className="text-xs text-slate-500 leading-relaxed">
            This is a curated demo dataset of 114 real B2B companies. The AI search uses keywords to match
            industry, description, and pain-point fields. Try a keyword below to get results.
          </p>
        </div>
      </div>

      {/* Sample full searches */}
      <div className="mb-5">
        <div className="text-[10px] text-slate-600 uppercase tracking-widest font-semibold mb-2.5">Try these searches</div>
        <div className="flex flex-wrap gap-2">
          {samples.map(s => (
            <button key={s} onClick={() => onKeyword(s)}
              className="text-xs px-3 py-1.5 rounded-lg transition-all hover:border-violet-500/40"
              style={{ background:'rgba(124,58,237,0.08)', border:'1px solid rgba(124,58,237,0.2)', color:'#c4b5fd' }}>
              "{s}"
            </button>
          ))}
        </div>
      </div>

      {/* Industry keyword buckets */}
      <div className="mb-5">
        <div className="text-[10px] text-slate-600 uppercase tracking-widest font-semibold mb-2.5">Browse by industry keyword</div>
        <div className="flex flex-wrap gap-2">
          {Object.keys(groups).map(kw => (
            <button key={kw} onClick={() => onKeyword(kw)}
              className="text-xs px-3 py-1.5 rounded-lg transition-all hover:border-blue-500/40"
              style={{ background:'rgba(37,99,235,0.08)', border:'1px solid rgba(37,99,235,0.2)', color:'#93c5fd' }}>
              {kw} <span className="opacity-50 ml-1">({groups[kw].length})</span>
            </button>
          ))}
        </div>
      </div>

      {/* Role keywords */}
      <div>
        <div className="text-[10px] text-slate-600 uppercase tracking-widest font-semibold mb-2.5">Browse by role</div>
        <div className="flex flex-wrap gap-2">
          {['Head of Sales','Head of Marketing','CEO','Growth','CFO','VP Sales','Operations','Head of SDR','Demand Generation'].map(role => (
            <button key={role} onClick={() => onKeyword(role)}
              className="text-xs px-3 py-1.5 rounded-lg transition-all hover:border-emerald-500/40"
              style={{ background:'rgba(16,185,129,0.07)', border:'1px solid rgba(16,185,129,0.18)', color:'#6ee7b7' }}>
              {role}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

// Status badge with funnel explanation tooltip
function StatusBadge({ status }) {
  const [tip, setTip] = useState(false)
  const sc = STATUS_COLORS[status] || STATUS_COLORS.new
  const EXPLANATIONS = {
    new:              'Lead created, not yet contacted.',
    contacted:        'Outreach email was sent. No open detected yet.',
    opened:           'Lead opened the email.',
    clicked:          'Lead clicked a link in the email.',
    replied:          'Lead sent a reply.',
    positive_reply:   'Lead replied with interest.',
    negative_reply:   'Lead opted out or declined.',
    meeting_booked:   'A meeting has been scheduled.',
    meeting_attended: 'Lead attended the meeting.',
  }
  return (
    <div className="relative hidden lg:block" onMouseEnter={() => setTip(true)} onMouseLeave={() => setTip(false)}>
      <span className="text-[10px] px-2 py-0.5 rounded-full capitalize font-medium"
        style={{ background: sc.bg, color: sc.color }}>
        {status?.replace(/_/g, ' ')}
      </span>
      {tip && (
        <div className="absolute right-0 bottom-full mb-2 w-52 p-2.5 rounded-lg text-xs text-slate-300 z-50 whitespace-normal leading-relaxed pointer-events-none"
          style={{ background:'#13131f', border:'1px solid rgba(255,255,255,0.1)', boxShadow:'0 8px 24px rgba(0,0,0,0.5)' }}>
          <div className="text-[10px] text-slate-500 uppercase tracking-wide mb-1 font-semibold">Funnel status</div>
          {EXPLANATIONS[status] || 'Unknown status.'}
        </div>
      )}
    </div>
  )
}

// Pipeline status explainer banner
function PipelineExplainer() {
  const [open, setOpen] = useState(false)
  return (
    <div className="mb-4">
      <button onClick={() => setOpen(v => !v)}
        className="flex items-center gap-2 text-xs text-slate-500 hover:text-slate-300 transition-colors">
        <Info size={12} className="text-violet-500" />
        Why does every lead show a funnel status?
        <span className="text-violet-500">{open ? '▲' : '▼'}</span>
      </button>
      {open && (
        <div className="mt-2 p-4 rounded-xl text-xs text-slate-400 leading-relaxed"
          style={{ background:'rgba(124,58,237,0.06)', border:'1px solid rgba(124,58,237,0.15)' }}>
          <strong className="text-slate-200">This is by design, not a bug.</strong> The pipeline simulation sends an outreach email to
          every lead ("contacted"), then models realistic engagement based on each lead's intent score.
          High-intent leads progress further (opened → clicked → replied → meeting booked).
          Lower-intent leads stay at "contacted" or "opened". The status shows the <em>furthest event</em> each lead has reached.
        </div>
      )}
    </div>
  )
}

export default function Dashboard() {
  const [leads, setLeads] = useState([])
  const [kpis, setKpis] = useState(null)
  const [meta, setMeta] = useState(null)
  const [loading, setLoading] = useState(true)
  const [searchLoading, setSearchLoading] = useState(false)
  const [query, setQuery] = useState('')
  const [filters, setFilters] = useState(null)
  const [activeSeq, setActiveSeq] = useState('All')
  const [selectedLead, setSelectedLead] = useState(null)
  const [error, setError] = useState(null)
  const [noResults, setNoResults] = useState(false)

  const loadLeads = useCallback(async () => {
    setLoading(true); setError(null); setNoResults(false)
    try {
      const params = activeSeq !== 'All' ? { sequence: activeSeq } : {}
      const res = await getLeads(params)
      setLeads(res.data)
    } catch {
      setError('Cannot reach the API. Start: cd pipeline_ai && uvicorn app.main:app --reload --port 8000')
    } finally { setLoading(false) }
  }, [activeSeq])

  const loadKPIs = useCallback(async () => {
    try { const r = await getPerformance(); setKpis(r.data.kpis) } catch {}
  }, [])

  const loadMeta = useCallback(async () => {
    try { const r = await getLeadsMeta(); setMeta(r.data) } catch {}
  }, [])

  useEffect(() => { loadLeads(); loadKPIs(); loadMeta() }, [loadLeads, loadKPIs, loadMeta])

  const runSearch = async (q) => {
    setSearchLoading(true); setError(null); setNoResults(false)
    try {
      const r = await searchLeads(q)
      setLeads(r.data.results)
      setFilters(r.data.filters_applied)
      setActiveSeq('All')
      if (r.data.results.length === 0) setNoResults(true)
    } catch { setError('Search failed.') }
    finally { setSearchLoading(false) }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) { setFilters(null); setNoResults(false); loadLeads(); return }
    setQuery(query)
    await runSearch(query)
  }

  const handleKeywordClick = async (kw) => {
    setQuery(kw)
    setFilters(null)
    await runSearch(kw)
  }

  const clearSearch = () => { setQuery(''); setFilters(null); setNoResults(false); loadLeads() }
  const seqCounts = leads.reduce((acc, l) => { acc[l.sequence] = (acc[l.sequence]||0)+1; return acc }, {})

  return (
    <div className="flex min-h-screen">
      <Sidebar active="dashboard" />
      <div className="flex-1 ml-60">

        {/* Search bar */}
        <div className="sticky top-0 z-20 px-6 py-3.5"
          style={{ background:'rgba(7,7,14,0.88)', backdropFilter:'blur(20px)', borderBottom:'1px solid rgba(255,255,255,0.06)' }}>
          <form onSubmit={handleSearch} className="flex items-center gap-3">
            <div className="relative flex-1 max-w-xl">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-600" size={14} />
              <input type="text"
                placeholder='"AI companies needing automation"  ·  "SaaS head of sales"  ·  "recruitment"'
                value={query}
                onChange={e => setQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 rounded-xl transition-all focus:outline-none"
                style={{ background:'rgba(255,255,255,0.04)', border:'1px solid rgba(255,255,255,0.08)' }}
                onFocus={e => { e.target.style.borderColor='rgba(124,58,237,0.4)'; e.target.style.background='rgba(255,255,255,0.06)' }}
                onBlur={e => { e.target.style.borderColor='rgba(255,255,255,0.08)'; e.target.style.background='rgba(255,255,255,0.04)' }}
              />
            </div>
            <button type="submit" disabled={searchLoading} className="btn-primary text-sm py-2.5 px-4">
              {searchLoading
                ? <><span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Searching</>
                : <><Sparkles size={13} /> AI Search</>}
            </button>
            {(filters || noResults) && (
              <button type="button" onClick={clearSearch}
                className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 hover:text-white transition-colors"
                style={{ border:'1px solid rgba(255,255,255,0.1)' }}>
                <X size={14} />
              </button>
            )}
          </form>

          {filters && Object.keys(filters).length > 0 && (
            <div className="mt-2 flex items-center gap-2 text-xs flex-wrap">
              <Sparkles size={10} className="text-violet-500" />
              <span className="text-slate-600">AI parsed:</span>
              {Object.entries(filters).map(([k, v]) => (
                <span key={k} className="px-2 py-0.5 rounded-full text-violet-300 font-medium"
                  style={{ background:'rgba(124,58,237,0.12)', border:'1px solid rgba(124,58,237,0.25)' }}>
                  {k}: {v}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="p-6">
          {/* KPI Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 mb-6">
            {loading && !kpis
              ? Array(5).fill(0).map((_,i) => <SkeletonKPICard key={i} />)
              : kpis ? <>
                  <KPICard label="Total Leads"  value={kpis.total_leads}         icon={Users}         color="text-violet-400" />
                  <KPICard label="Contacted"     value={kpis.contacted}           icon={MessageSquare} color="text-blue-400" />
                  <KPICard label="Reply Rate"    value={`${kpis.reply_rate}%`}    icon={TrendingUp}    color="text-emerald-400" />
                  <KPICard label="Booking Rate"  value={`${kpis.booking_rate}%`}  icon={Calendar}      color="text-orange-400" />
                  <KPICard label="Show-up Rate"  value={`${kpis.show_up_rate}%`}  icon={TrendingUp}    color="text-cyan-400" />
                </> : null}
          </div>

          {/* Pipeline explainer */}
          {!noResults && leads.length > 0 && <PipelineExplainer />}

          {/* Sequence tabs */}
          {!noResults && (
            <div className="flex items-center gap-1.5 mb-5 flex-wrap">
              {SEQ_FILTERS.map(seq => (
                <button key={seq}
                  onClick={() => { setActiveSeq(seq); setFilters(null); setQuery(''); setNoResults(false) }}
                  className="px-4 py-1.5 rounded-full text-xs font-semibold transition-all duration-200"
                  style={activeSeq === seq
                    ? { background:'linear-gradient(135deg,#7c3aed,#2563eb)', color:'white', boxShadow:'0 4px 14px rgba(124,58,237,0.35)' }
                    : { color:'#64748b', border:'1px solid rgba(255,255,255,0.07)' }}>
                  {seq}{seq !== 'All' && seqCounts[seq] ? <span className="ml-1.5 opacity-55">({seqCounts[seq]})</span> : null}
                </button>
              ))}
              <div className="ml-auto text-xs text-slate-600">{leads.length} leads</div>
            </div>
          )}

          {/* States */}
          {error ? (
            <div className="glass rounded-2xl p-10 text-center">
              <Brain size={40} className="mx-auto mb-4 text-slate-700" />
              <p className="text-sm text-red-400 whitespace-pre-line">{error}</p>
            </div>
          ) : loading ? (
            <div className="space-y-1.5">{Array(8).fill(0).map((_,i) => <SkeletonLeadCard key={i} />)}</div>
          ) : noResults ? (
            <EmptySearch meta={meta} onKeyword={handleKeywordClick} />
          ) : leads.length === 0 ? (
            <EmptySearch meta={meta} onKeyword={handleKeywordClick} />
          ) : (
            <div className="space-y-1.5">
              {leads.map((lead, i) => {
                const ss = scoreStyle(lead.intent_score)
                return (
                  <button key={lead.id}
                    onClick={() => setSelectedLead(lead)}
                    className="lead-item w-full glass-hover p-3.5 flex items-center gap-4 text-left"
                    style={{ animationDelay:`${Math.min(i*0.025, 0.35)}s` }}>
                    <div className="w-11 h-11 rounded-full flex items-center justify-center font-bold text-xs flex-shrink-0 ring-1"
                      style={{ background:ss.bg, color:ss.color, '--ring-color':ss.ring }}>
                      {Math.round(lead.intent_score)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold text-white truncate">{lead.employee.name}</div>
                      <div className="text-xs text-slate-500 truncate mt-0.5">
                        {lead.employee.job_title}<span className="text-slate-700 mx-1.5">·</span>
                        <span className="text-slate-400">{lead.company.name}</span>
                      </div>
                    </div>
                    <div className="hidden md:block text-xs text-slate-600 w-24 text-center truncate">{lead.company.industry?.split(' ')[0]}</div>
                    {lead.company.country && lead.company.country !== 'nan' && (
                      <div className="hidden lg:flex items-center gap-1 text-xs text-slate-600 w-24">
                        <MapPin size={10} className="flex-shrink-0" /><span className="truncate">{lead.company.country}</span>
                      </div>
                    )}
                    {lead.company.website_url && lead.company.website_url !== 'nan' && (
                      <div className="hidden xl:block text-slate-700 hover:text-violet-400 transition-colors"
                        onClick={e => { e.stopPropagation(); window.open(lead.company.website_url,'_blank') }}>
                        <Globe size={14} />
                      </div>
                    )}
                    <span className={seqClass(lead.sequence)}>{lead.sequence || '—'}</span>
                    <StatusBadge status={lead.status} />
                  </button>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {selectedLead && <LeadModal lead={selectedLead} onClose={() => setSelectedLead(null)} />}
    </div>
  )
}
