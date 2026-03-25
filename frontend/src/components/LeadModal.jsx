import { useState, useEffect } from 'react'
import { X, Brain, Target, Mail, Building2, RefreshCw, Sparkles, Clock, CheckCircle, Globe, MapPin, Lightbulb } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { getLead, getIntelligence, getStrategy, getEmailVariants } from '../api/client'

const TABS = [
  { id: 'overview', label: 'Overview', icon: Brain },
  { id: 'intelligence', label: 'Intelligence', icon: Building2 },
  { id: 'strategy', label: 'Strategy', icon: Target },
  { id: 'emails', label: 'Emails', icon: Mail },
]

function seqClass(seq) {
  if (seq === 'Hot') return 'seq-hot'
  if (seq === 'Warm') return 'seq-warm'
  if (seq === 'Cold') return 'seq-cold'
  return 'seq-ignore'
}

function scoreStyle(score) {
  if (score >= 80) return { bg: 'rgba(239,68,68,0.15)', color: '#fca5a5', border: 'rgba(239,68,68,0.35)' }
  if (score >= 60) return { bg: 'rgba(249,115,22,0.15)', color: '#fdba74', border: 'rgba(249,115,22,0.35)' }
  if (score >= 40) return { bg: 'rgba(59,130,246,0.15)', color: '#93c5fd', border: 'rgba(59,130,246,0.35)' }
  return { bg: 'rgba(107,114,128,0.15)', color: '#9ca3af', border: 'rgba(107,114,128,0.25)' }
}

function InfoRow({ label, value, link }) {
  if (!value || value === 'nan' || value === 'None') return null
  return (
    <div className="flex gap-3 py-2 border-b border-white/[0.04] last:border-0">
      <span className="text-xs text-slate-500 w-28 flex-shrink-0 mt-0.5">{label}</span>
      {link ? (
        <a href={value} target="_blank" rel="noopener noreferrer"
          className="text-sm text-violet-400 hover:text-violet-300 truncate transition-colors flex items-center gap-1">
          <Globe size={12} /> {value.replace(/^https?:\/\//, '')}
        </a>
      ) : (
        <span className="text-sm text-slate-200 flex-1">{value}</span>
      )}
    </div>
  )
}

function AIPane({ loaded, loading, onGenerate, loadingLabel, emptyIcon: Icon, emptyTitle, emptyHint, children }) {
  if (loaded) {
    return <div className="md-prose">{children}</div>
  }
  return (
    <div className="text-center py-16">
      <div className="w-14 h-14 rounded-2xl bg-white/[0.03] border border-white/[0.07] flex items-center justify-center mx-auto mb-4">
        <Icon size={24} className="text-slate-600" />
      </div>
      <p className="text-slate-300 text-sm font-medium mb-1">{emptyTitle}</p>
      <p className="text-xs text-slate-600 mb-7">{emptyHint}</p>
      <button onClick={onGenerate} disabled={loading} className="btn-primary mx-auto text-sm">
        {loading ? <><RefreshCw size={13} className="animate-spin" />{loadingLabel}</> : <><Sparkles size={13} />Generate</>}
      </button>
    </div>
  )
}

export default function LeadModal({ lead: summary, onClose }) {
  const [tab, setTab] = useState('overview')
  const [lead, setLead] = useState(null)
  const [intelligence, setIntelligence] = useState(null)
  const [strategy, setStrategy] = useState(null)
  const [emails, setEmails] = useState(null)
  const [busy, setBusy] = useState({ lead: true, intelligence: false, strategy: false, emails: false })

  useEffect(() => {
    getLead(summary.id)
      .then(r => setLead(r.data))
      .catch(console.error)
      .finally(() => setBusy(p => ({ ...p, lead: false })))
  }, [summary.id])

  const gen = (key, fn) => async () => {
    setBusy(p => ({ ...p, [key]: true }))
    try {
      const r = await fn(summary.id)
      if (key === 'intelligence') setIntelligence(r.data.report)
      if (key === 'strategy') setStrategy(r.data.strategy)
      if (key === 'emails') setEmails(r.data)
    } catch (e) { console.error(e) }
    finally { setBusy(p => ({ ...p, [key]: false })) }
  }

  const ss = scoreStyle(summary.intent_score)
  const comp = lead?.company || summary.company

  return (
    <div className="fixed inset-0 z-50 flex items-stretch justify-end">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-[3px]" onClick={onClose} />

      <div className="modal-panel relative w-full max-w-[700px] bg-[#0d0d1a] border-l border-white/[0.09] flex flex-col shadow-2xl">
        {/* ── Header ── */}
        <div className="flex items-center gap-3 px-6 py-4 border-b border-white/[0.07]">
          <div
            className="w-12 h-12 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0 ring-2"
            style={{ background: ss.bg, color: ss.color, ringColor: ss.border }}
          >
            {Math.round(summary.intent_score)}
          </div>
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-white truncate">{summary.employee.name}</div>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-xs text-slate-400 truncate">{summary.employee.job_title}</span>
              <span className="text-slate-600">·</span>
              <span className="text-xs text-violet-400 truncate">{summary.company.name}</span>
              {summary.company.country && summary.company.country !== 'nan' && (
                <span className="text-xs text-slate-600 flex items-center gap-0.5">
                  <MapPin size={10} />{summary.company.country}
                </span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className={seqClass(summary.sequence)}>{summary.sequence || 'N/A'}</span>
            {summary.company.website_url && summary.company.website_url !== 'nan' && (
              <a href={summary.company.website_url} target="_blank" rel="noopener noreferrer"
                className="text-slate-500 hover:text-violet-400 transition-colors" title="Visit website">
                <Globe size={15} />
              </a>
            )}
            <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors">
              <X size={17} />
            </button>
          </div>
        </div>

        {/* ── Tabs ── */}
        <div className="flex border-b border-white/[0.07]">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={`flex-1 flex items-center justify-center gap-1.5 py-3 text-xs font-medium transition-colors ${
                tab === id ? 'text-violet-300 border-b-2 border-violet-500' : 'text-slate-600 hover:text-slate-300'
              }`}
            >
              <Icon size={13} /> {label}
            </button>
          ))}
        </div>

        {/* ── Body ── */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {busy.lead && tab === 'overview' ? (
            <div className="flex items-center justify-center h-48 text-slate-500 gap-2 text-sm">
              <RefreshCw size={14} className="animate-spin" /> Loading…
            </div>
          ) : (
            <>
              {/* ── OVERVIEW ── */}
              {tab === 'overview' && lead && (
                <div className="space-y-4">
                  {/* Status row */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={seqClass(lead.sequence)}>{lead.sequence}</span>
                    <span className="text-xs text-slate-500 capitalize px-2 py-0.5 rounded-full bg-white/[0.04] border border-white/[0.07]">
                      {lead.status}
                    </span>
                    <span className="text-xs text-slate-600">Intent: {lead.intent_score}/100</span>
                  </div>

                  {/* What they need / problem */}
                  {(lead.problem || comp.why_needs_help) && (
                    <div className="glass p-4">
                      <div className="flex items-center gap-1.5 text-[10px] text-slate-500 uppercase tracking-wide mb-2">
                        <Brain size={11} /> Why they need help
                      </div>
                      <p className="text-sm text-slate-200 leading-relaxed">{lead.problem || comp.why_needs_help}</p>
                    </div>
                  )}

                  {/* Outreach angle */}
                  {comp.outreach_angle && comp.outreach_angle !== 'nan' && (
                    <div className="glass p-4 border border-violet-500/15">
                      <div className="flex items-center gap-1.5 text-[10px] text-violet-400 uppercase tracking-wide mb-2 font-semibold">
                        <Lightbulb size={11} /> Suggested Outreach Angle
                      </div>
                      <p className="text-sm text-slate-300 leading-relaxed">{comp.outreach_angle}</p>
                    </div>
                  )}

                  {/* Company description */}
                  {comp.description && comp.description !== 'nan' && (
                    <div className="glass p-4">
                      <div className="text-[10px] text-slate-500 uppercase tracking-wide mb-2">Company Description</div>
                      <p className="text-sm text-slate-300 leading-relaxed">{comp.description}</p>
                    </div>
                  )}

                  {/* Company details */}
                  <div className="glass p-4">
                    <div className="text-[10px] text-slate-500 uppercase tracking-wide mb-3">Company Details</div>
                    <InfoRow label="Industry" value={comp.industry} />
                    <InfoRow label="Size" value={comp.size} />
                    <InfoRow label="Country" value={comp.country !== 'nan' ? comp.country : null} />
                    <InfoRow label="Website" value={comp.website_url !== 'nan' ? comp.website_url : null} link />
                    <InfoRow label="Revenue" value={comp.revenue ? `$${(comp.revenue / 1e6).toFixed(1)}M` : null} />
                    <InfoRow label="Mkt Spend" value={comp.marketing_spend ? `$${(comp.marketing_spend / 1e3).toFixed(0)}k` : null} />
                    <InfoRow label="Purchase Freq." value={comp.purchasing_frequency} />
                    <InfoRow label="Payment" value={comp.payment_behavior} />
                  </div>

                  {/* Contact details */}
                  <div className="glass p-4">
                    <div className="text-[10px] text-slate-500 uppercase tracking-wide mb-3">Contact</div>
                    <InfoRow label="Seniority" value={lead.employee.seniority} />
                    <InfoRow label="Tenure" value={lead.employee.tenure != null ? `${lead.employee.tenure} yrs` : null} />
                    <InfoRow label="Engagement" value={lead.employee.engagement_score != null ? String(lead.employee.engagement_score) : null} />
                    <InfoRow label="Prefers" value={lead.employee.contact_preference} />
                  </div>

                  {/* AI Pitch */}
                  {lead.pitch && (
                    <div className="glass p-4">
                      <div className="text-[10px] text-slate-500 uppercase tracking-wide mb-3">AI-Generated Pitch</div>
                      <p className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed font-mono text-[0.8rem]">{lead.pitch}</p>
                    </div>
                  )}

                  {/* Event timeline */}
                  {lead.events?.length > 0 && (
                    <div className="glass p-4">
                      <div className="text-[10px] text-slate-500 uppercase tracking-wide mb-3">Event Timeline</div>
                      <div className="relative pl-3">
                        <div className="absolute left-0 top-2 bottom-2 w-px bg-violet-500/20" />
                        {lead.events.map((ev, i) => (
                          <div key={i} className="flex items-center gap-2.5 text-xs mb-2.5 relative">
                            <div className="absolute -left-[13px] w-2 h-2 rounded-full bg-violet-500/50 ring-2 ring-violet-500/20" />
                            <span className="text-violet-300 font-medium capitalize">{ev.type.replace(/_/g, ' ')}</span>
                            <span className="text-slate-600">{new Date(ev.timestamp).toLocaleDateString()}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  {lead.actions?.length > 0 && (
                    <div className="glass p-4">
                      <div className="text-[10px] text-slate-500 uppercase tracking-wide mb-3">Recommended Actions</div>
                      {lead.actions.slice(0, 5).map((a, i) => (
                        <div key={i} className="flex items-start gap-2 text-xs mb-2">
                          {a.status === 'completed'
                            ? <CheckCircle size={12} className="text-emerald-400 mt-0.5 flex-shrink-0" />
                            : <Clock size={12} className="text-slate-600 mt-0.5 flex-shrink-0" />}
                          <span className="text-slate-300">{a.action}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* ── INTELLIGENCE ── */}
              {tab === 'intelligence' && (
                <AIPane
                  loaded={!!intelligence} loading={busy.intelligence}
                  onGenerate={gen('intelligence', getIntelligence)}
                  loadingLabel=" Researching company…"
                  emptyIcon={Building2}
                  emptyTitle="Generate live company intelligence"
                  emptyHint="Scrapes the company website + Claude AI analysis · ~20–40 seconds"
                >
                  <ReactMarkdown>{intelligence}</ReactMarkdown>
                </AIPane>
              )}

              {/* ── STRATEGY ── */}
              {tab === 'strategy' && (
                <AIPane
                  loaded={!!strategy} loading={busy.strategy}
                  onGenerate={gen('strategy', getStrategy)}
                  loadingLabel=" Building strategy…"
                  emptyIcon={Target}
                  emptyTitle="Generate personalized outreach strategy"
                  emptyHint="Tailored to this lead's intent score, role, and outreach angle · ~10 seconds"
                >
                  <ReactMarkdown>{strategy}</ReactMarkdown>
                </AIPane>
              )}

              {/* ── EMAILS ── */}
              {tab === 'emails' && (
                emails ? (
                  <div className="space-y-4">
                    {emails.recommendation && (
                      <div className="glass p-4 border border-violet-500/25">
                        <div className="text-[10px] text-violet-400 uppercase tracking-wide font-bold mb-1.5">
                          AI Recommendation
                        </div>
                        <p className="text-sm text-slate-300">{emails.recommendation}</p>
                      </div>
                    )}
                    {[
                      { key: 'email_a_problem', label: 'Version A — Problem Focused', color: 'text-red-400' },
                      { key: 'email_b_roi', label: 'Version B — ROI Focused', color: 'text-emerald-400' },
                      { key: 'email_c_case_study', label: 'Version C — Case Study', color: 'text-blue-400' },
                    ].map(({ key, label, color }) => emails[key] && (
                      <div key={key} className="glass p-4">
                        <div className={`text-[10px] uppercase tracking-wide font-bold mb-2 ${color}`}>{label}</div>
                        <p className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">{emails[key]}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <AIPane
                    loaded={false} loading={busy.emails}
                    onGenerate={gen('emails', getEmailVariants)}
                    loadingLabel=" Generating emails…"
                    emptyIcon={Mail}
                    emptyTitle="Generate 3 personalized cold email variants"
                    emptyHint="Problem · ROI · Case Study angles — each tailored to this lead's specific pain · ~15 seconds"
                  >
                    {null}
                  </AIPane>
                )
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
