import { useEffect, useRef, useState } from 'react'

export default function CustomCursor() {
  const dotRef = useRef(null)
  const ringRef = useRef(null)
  const pos = useRef({ x: -100, y: -100 })
  const ring = useRef({ x: -100, y: -100 })
  const raf = useRef(null)
  const [state, setState] = useState('default') // default | hover | click | text

  useEffect(() => {
    const onMove = (e) => {
      pos.current = { x: e.clientX, y: e.clientY }
    }

    const onDown = () => setState('click')
    const onUp = () => setState(s => s === 'click' ? 'default' : s)

    const onOver = (e) => {
      const el = e.target
      if (el.closest('button, a, [role="button"]')) setState('hover')
      else if (el.closest('input, textarea')) setState('text')
      else setState('default')
    }

    window.addEventListener('mousemove', onMove, { passive: true })
    window.addEventListener('mousedown', onDown)
    window.addEventListener('mouseup', onUp)
    window.addEventListener('mouseover', onOver, { passive: true })

    const animate = () => {
      const ease = 0.11
      ring.current.x += (pos.current.x - ring.current.x) * ease
      ring.current.y += (pos.current.y - ring.current.y) * ease

      if (dotRef.current) {
        dotRef.current.style.transform = `translate(${pos.current.x}px, ${pos.current.y}px)`
      }
      if (ringRef.current) {
        ringRef.current.style.transform = `translate(${ring.current.x}px, ${ring.current.y}px)`
      }
      raf.current = requestAnimationFrame(animate)
    }
    raf.current = requestAnimationFrame(animate)

    return () => {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mousedown', onDown)
      window.removeEventListener('mouseup', onUp)
      window.removeEventListener('mouseover', onOver)
      cancelAnimationFrame(raf.current)
    }
  }, [])

  const dotSize   = state === 'click' ? 4  : state === 'hover' ? 10 : 6
  const ringSize  = state === 'click' ? 20 : state === 'hover' ? 44 : 32
  const ringColor = state === 'hover' ? 'rgba(167,139,250,0.6)' : 'rgba(124,58,237,0.4)'
  const dotColor  = state === 'hover' ? '#c4b5fd' : state === 'text' ? 'rgba(255,255,255,0.3)' : 'white'

  return (
    <>
      {/* Dot */}
      <div
        ref={dotRef}
        style={{
          position: 'fixed', top: 0, left: 0, zIndex: 99999,
          pointerEvents: 'none', willChange: 'transform',
          marginLeft: -dotSize / 2, marginTop: -dotSize / 2,
          width: dotSize, height: dotSize,
          background: dotColor,
          borderRadius: '50%',
          transition: 'width 0.12s, height 0.12s, background 0.2s, margin 0.12s',
          mixBlendMode: 'difference',
        }}
      />
      {/* Ring */}
      <div
        ref={ringRef}
        style={{
          position: 'fixed', top: 0, left: 0, zIndex: 99998,
          pointerEvents: 'none', willChange: 'transform',
          marginLeft: -ringSize / 2, marginTop: -ringSize / 2,
          width: ringSize, height: ringSize,
          border: `1.5px solid ${ringColor}`,
          borderRadius: '50%',
          transition: 'width 0.25s cubic-bezier(.34,1.56,.64,1), height 0.25s cubic-bezier(.34,1.56,.64,1), border-color 0.2s, margin 0.25s',
          boxShadow: state === 'hover' ? '0 0 18px rgba(124,58,237,0.25)' : 'none',
        }}
      />
    </>
  )
}
