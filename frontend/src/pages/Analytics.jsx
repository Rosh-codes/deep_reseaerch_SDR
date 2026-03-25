import { useState, useEffect } from 'react'
import {
  BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  AreaChart, Area, RadarChart, Radar, PolarGrid, PolarAngleAxis, Legend,
} from 'recharts'
import { Sparkles, RefreshCw, TrendingUp, Users, MessageSquare, Calendar, Globe } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { getFunnel, getPerformance, getAnalyticsReport } from '../api/client'
import Sidebar from '../components/Sidebar'

const SEQ_COLORS = { Hot: '#f87171', Warm: '#fb923c', Cold: '#60a5fa', Ignore: '#9ca3af' }
const PALETTE = ['#a78bfa', '#38bdf8', '#34d399', '#fbbf24', '#f472b6', '#fb7185', '#818cf8', '#2dd4bf']

// ── Shared tooltip style — high contrast on dark bg ──
const TT = {
  contentStyle: {
    background: 'rgba(15,15,28,0.97)',
    border: '1px solid rgba(167,139,250,0.35)',
    borderRadius: '10px',
    color: '#f1f5f9',
    fontSize: '12px',
    padding: '10px 14px',
    boxShadow: '0 8px 32px rgba(0,0,0,0.6), 0 0 0 1px rgba(167,139,250,0.1)',
  },
  labelStyle: { color: '#c4b5fd', fontWeight: 600, marginBottom: 4 },
  itemStyle: { color: '#e2e8f0' },
  cursor: { fill: 'rgba(167,139,250,0.08)', stroke: 'rgba(167,139,250,0.2)', strokeWidth: 1 },
}

// Shared axis props
const AXIS = {
  x: { tick: { fill: '#94a3b8', fontSize: 11 }, axisLine: false, tickLine: false },
  y: { tick: { fill: '#94a3b8', fontSize: 11 }, axisLine: false, tickLine: false },
}

const GRID = <CartesianGrid strokeDasharray="4 4" stroke="rgba(148,163,184,0.1)" vertical={false} />

function KPICard({ label, value, icon: Icon, color, sub }) {
  return (
    <div className="glass p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] text-slate-500">{label}</span>
        <Icon size={13} className={color} />
      </div>
      <div className={`text-2xl font-bold ${color}`}>{value ?? '—'}</div>
      {sub && <div className="text-[10px] text-slate-600 mt-1">{sub}</div>}
    </div>
  )
}

function ChartCard({ title, subtitle, children, span }) {
  return (
    <div className={`glass p-5 ${span === 2 ? 'lg:col-span-2' : ''}`}>
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-white">{title}</h3>
        {subtitle && <p className="text-[11px] text-slate-500 mt-0.5">{subtitle}</p>}
      </div>
      {children}
    </div>
  )
}

export default function Analytics() {
  const [funnel, setFunnel] = useState(null)
  const [performance, setPerformance] = useState(null)
  const [report, setReport] = useState(null)
  const [loadingReport, setLoadingReport] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([getFunnel(), getPerformance()])
      .then(([f, p]) => { setFunnel(f.data); setPerformance(p.data) })
      .catch(() => setError('Cannot reach the API. Make sure FastAPI is running on port 8000.'))
      .finally(() => setLoading(false))
  }, [])

  // Chart data transformations
  const funnelData = funnel ? [
    { stage: 'Leads', value: funnel.total_leads },
    { stage: 'Contacted', value: funnel.contacted },
    { stage: 'Opened', value: funnel.opened },
    { stage: 'Clicked', value: funnel.clicked },
    { stage: 'Replied', value: funnel.replied },
    { stage: 'Positive', value: funnel.positive_reply },
    { stage: 'Booked', value: funnel.meeting_booked },
    { stage: 'Attended', value: funnel.meeting_attended },
  ] : []

  const conversionData = funnelData.slice(1).map((d, i) => ({
    stage: d.stage,
    rate: funnelData[i].value ? Math.round(d.value / funnelData[i].value * 100) : 0,
  }))

  const industryData = performance
    ? Object.entries(performance.by_industry)
        .map(([name, d]) => ({ name: name.length > 14 ? name.slice(0, 14) + '…' : name, reply_rate: d.reply_rate, total: d.total }))
        .sort((a, b) => b.reply_rate - a.reply_rate)
        .slice(0, 8)
    : []

  const seqPieData = performance
    ? Object.entries(performance.by_sequence).map(([name, d]) => ({ name, value: d.total }))
    : []

  const seqRadarData = performance
    ? Object.entries(performance.by_sequence).map(([name, d]) => ({
        sequence: name,
        'Reply Rate': d.reply_rate,
        'Booking Rate': d.booking_rate,
      }))
    : []

  const countryData = performance
    ? Object.entries(performance.by_country || {})
        .map(([name, d]) => ({ name, value: d.total }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 10)
    : []

  const handleGenerateReport = async () => {
    setLoadingReport(true)
    try { const r = await getAnalyticsReport(); setReport(r.data.report) }
    catch (e) { console.error(e) }
    finally { setLoadingReport(false) }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen">
        <Sidebar active="analytics" />
        <div className="flex-1 ml-60 flex items-center justify-center text-slate-500 gap-2 text-sm">
          <RefreshCw size={15} className="animate-spin" /> Loading analytics…
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar active="analytics" />

      <div className="flex-1 ml-60 p-6 space-y-6">
        {/* Page header */}
        <div>
          <h1 className="text-xl font-bold text-white">Analytics &amp; Reports</h1>
          <p className="text-sm text-slate-500 mt-0.5">Pipeline performance, conversion analysis, and AI-generated insights</p>
        </div>

        {error && <div className="glass rounded-xl p-5 text-center text-red-400 text-sm">{error}</div>}

        {/* ── KPI Cards ── */}
        {performance?.kpis && (
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
            <KPICard label="Total Leads" value={performance.kpis.total_leads} icon={Users} color="text-violet-400" />
            <KPICard label="Contacted" value={performance.kpis.contacted} icon={MessageSquare} color="text-blue-400" />
            <KPICard label="Reply Rate" value={`${performance.kpis.reply_rate}%`} icon={TrendingUp} color="text-emerald-400" sub="of contacted" />
            <KPICard label="Booking Rate" value={`${performance.kpis.booking_rate}%`} icon={Calendar} color="text-orange-400" sub="of contacted" />
            <KPICard label="Show-up Rate" value={`${performance.kpis.show_up_rate}%`} icon={TrendingUp} color="text-cyan-400" sub="of booked" />
          </div>
        )}

        {/* ── Row 1: Funnel (full width) ── */}
        <ChartCard title="Sales Funnel" subtitle="Lead volume at each stage of the pipeline" span={2}>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={funnelData} margin={{ top: 8, right: 16, left: 0, bottom: 4 }}>
              {GRID}
              <XAxis dataKey="stage" {...AXIS.x} />
              <YAxis {...AXIS.y} />
              <Tooltip {...TT} formatter={(v, name) => [v.toLocaleString(), 'Leads']} />
              <Bar dataKey="value" radius={[5, 5, 0, 0]}
                activeBar={{ fill: '#c4b5fd', stroke: '#a78bfa', strokeWidth: 1 }}>
                {funnelData.map((_, i) => {
                  const colors = ['#a78bfa','#818cf8','#60a5fa','#38bdf8','#34d399','#4ade80','#facc15','#fb923c']
                  return <Cell key={i} fill={colors[i] || '#a78bfa'} />
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* ── Row 2: Conversion rates + Sequence donut ── */}
        <div className="grid lg:grid-cols-2 gap-6">
          <ChartCard title="Stage-to-Stage Conversion Rates" subtitle="% that progressed from the previous stage">
            <ResponsiveContainer width="100%" height={210}>
              <AreaChart data={conversionData} margin={{ top: 8, right: 16, left: 0, bottom: 4 }}>
                <defs>
                  <linearGradient id="cvGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#a78bfa" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#a78bfa" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                {GRID}
                <XAxis dataKey="stage" {...AXIS.x} />
                <YAxis {...AXIS.y} tickFormatter={v => `${v}%`} />
                <Tooltip {...TT} formatter={v => [`${v}%`, 'Conversion rate']} />
                <Area type="monotone" dataKey="rate"
                  stroke="#a78bfa" strokeWidth={2.5}
                  fill="url(#cvGrad)"
                  dot={{ fill: '#a78bfa', r: 4, stroke: '#1e1b4b', strokeWidth: 2 }}
                  activeDot={{ fill: '#c4b5fd', r: 6, stroke: '#fff', strokeWidth: 1.5 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Leads by Sequence" subtitle="Distribution across Hot / Warm / Cold / Ignore">
            <ResponsiveContainer width="100%" height={170}>
              <PieChart>
                <Pie data={seqPieData} cx="50%" cy="50%"
                  innerRadius={52} outerRadius={82}
                  paddingAngle={3} dataKey="value"
                  stroke="none"
                  activeShape={{ outerRadius: 90 }}>
                  {seqPieData.map(({ name }) => <Cell key={name} fill={SEQ_COLORS[name] || '#9ca3af'} />)}
                </Pie>
                <Tooltip {...TT} formatter={(v, name) => [v, name]} />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex flex-wrap justify-center gap-4 mt-2">
              {seqPieData.map(({ name, value }) => (
                <div key={name} className="flex items-center gap-1.5 text-xs text-slate-300">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ background: SEQ_COLORS[name] }} />
                  {name} <span className="text-slate-500">({value})</span>
                </div>
              ))}
            </div>
          </ChartCard>
        </div>

        {/* ── Row 3: Industry bar + Sequence radar ── */}
        <div className="grid lg:grid-cols-2 gap-6">
          <ChartCard title="Reply Rate by Industry" subtitle="Top 8 industries by engagement rate">
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={industryData} layout="vertical" margin={{ top: 4, right: 24, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="4 4" stroke="rgba(148,163,184,0.1)" horizontal={false} />
                <XAxis type="number" domain={[0, 100]} {...AXIS.x} tickFormatter={v => `${v}%`} />
                <YAxis type="category" dataKey="name" width={75} {...AXIS.y} />
                <Tooltip {...TT} formatter={v => [`${v}%`, 'Reply rate']} />
                <Bar dataKey="reply_rate" radius={[0, 5, 5, 0]}
                  activeBar={{ stroke: '#fff', strokeWidth: 0.5, opacity: 1 }}>
                  {industryData.map((_, i) => <Cell key={i} fill={PALETTE[i % PALETTE.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Sequence Performance Radar" subtitle="Reply rate vs booking rate by sequence">
            <ResponsiveContainer width="100%" height={240}>
              <RadarChart data={seqRadarData} cx="50%" cy="50%" outerRadius={85}>
                <PolarGrid stroke="rgba(148,163,184,0.15)" />
                <PolarAngleAxis dataKey="sequence"
                  tick={{ fill: '#cbd5e1', fontSize: 12, fontWeight: 500 }} />
                <Radar name="Reply Rate"   dataKey="Reply Rate"
                  stroke="#a78bfa" fill="#a78bfa" fillOpacity={0.25} strokeWidth={2} />
                <Radar name="Booking Rate" dataKey="Booking Rate"
                  stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.2} strokeWidth={2} />
                <Legend wrapperStyle={{ fontSize: '11px', color: '#cbd5e1', paddingTop: '8px' }} />
                <Tooltip {...TT} formatter={v => [`${v}%`]} />
              </RadarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* ── Row 4: Country distribution + Sequence table ── */}
        <div className="grid lg:grid-cols-2 gap-6">
          {countryData.length > 0 && (
            <ChartCard title="Leads by Country" subtitle="Geographic distribution">
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={countryData} layout="vertical" margin={{ top: 4, right: 24, left: 0, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="4 4" stroke="rgba(148,163,184,0.1)" horizontal={false} />
                  <XAxis type="number" {...AXIS.x} />
                  <YAxis type="category" dataKey="name" width={95} {...AXIS.y} />
                  <Tooltip {...TT} formatter={v => [v, 'Leads']} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]} fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          )}

          <ChartCard title="Sequence Performance Table" subtitle="Full conversion breakdown">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-[10px] text-slate-600 uppercase tracking-wide">
                    <th className="text-left py-2 pr-3">Seq</th>
                    <th className="text-right py-2 px-2">Leads</th>
                    <th className="text-right py-2 px-2">Replied</th>
                    <th className="text-right py-2 px-2">Reply%</th>
                    <th className="text-right py-2 px-2">Booked</th>
                    <th className="text-right py-2 pl-2">Book%</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(performance?.by_sequence || {}).map(([seq, d]) => (
                    <tr key={seq} className="border-t border-white/[0.04]">
                      <td className="py-2.5 pr-3">
                        <span className={seq === 'Hot' ? 'seq-hot' : seq === 'Warm' ? 'seq-warm' : seq === 'Cold' ? 'seq-cold' : 'seq-ignore'}>
                          {seq}
                        </span>
                      </td>
                      <td className="text-right py-2.5 px-2 text-slate-400">{d.total}</td>
                      <td className="text-right py-2.5 px-2 text-slate-400">{d.replied}</td>
                      <td className="text-right py-2.5 px-2 text-emerald-400 font-semibold">{d.reply_rate}%</td>
                      <td className="text-right py-2.5 px-2 text-slate-400">{d.meeting_booked}</td>
                      <td className="text-right py-2.5 pl-2 text-orange-400 font-semibold">{d.booking_rate}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </ChartCard>
        </div>

        {/* ── AI Executive Report ── */}
        <div className="glass p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-white">AI Executive Pipeline Report</h2>
              <p className="text-xs text-slate-500 mt-0.5">Claude-generated analysis — bottlenecks, top segments, and recommendations</p>
            </div>
            <button onClick={handleGenerateReport} disabled={loadingReport} className="btn-primary text-sm py-2 px-4">
              {loadingReport
                ? <><RefreshCw size={13} className="animate-spin" /> Generating…</>
                : <><Sparkles size={13} /> Generate Report</>}
            </button>
          </div>

          {report ? (
            <div className="prose prose-invert prose-sm max-w-none bg-white/[0.02] rounded-xl p-5 border border-white/[0.06]
              prose-headings:text-slate-200 prose-p:text-slate-400 prose-strong:text-slate-200
              prose-li:text-slate-400 prose-hr:border-white/10">
              <ReactMarkdown>{report}</ReactMarkdown>
            </div>
          ) : (
            <div className="text-center py-14 border border-dashed border-white/[0.07] rounded-xl text-slate-600">
              <Sparkles size={28} className="mx-auto mb-3 opacity-25" />
              <p className="text-sm">Click "Generate Report" for AI-powered pipeline analysis</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
