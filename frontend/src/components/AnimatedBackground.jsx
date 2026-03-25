export default function AnimatedBackground({ variant = 'default' }) {
  return (
    <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden" aria-hidden>

      {/* ── Drifting gradient orbs ── */}
      <div className="ab-orb ab-orb-1" />
      <div className="ab-orb ab-orb-2" />
      <div className="ab-orb ab-orb-3" />
      {variant === 'landing' && <div className="ab-orb ab-orb-4" />}

      {/* ── Dot grid ── */}
      <div
        className="absolute inset-0 opacity-[0.35]"
        style={{
          backgroundImage: `radial-gradient(circle, rgba(124,58,237,0.18) 1px, transparent 1px)`,
          backgroundSize: '40px 40px',
          maskImage: 'radial-gradient(ellipse 80% 80% at 50% 50%, black 40%, transparent 100%)',
          WebkitMaskImage: 'radial-gradient(ellipse 80% 80% at 50% 50%, black 40%, transparent 100%)',
        }}
      />

      {/* ── Scanline vignette ── */}
      <div
        className="absolute inset-0 opacity-[0.06]"
        style={{
          background: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.3) 2px, rgba(0,0,0,0.3) 4px)',
        }}
      />

      {/* ── Edge vignette ── */}
      <div
        className="absolute inset-0"
        style={{
          background: 'radial-gradient(ellipse 100% 100% at 50% 50%, transparent 50%, rgba(8,8,15,0.7) 100%)',
        }}
      />
    </div>
  )
}
