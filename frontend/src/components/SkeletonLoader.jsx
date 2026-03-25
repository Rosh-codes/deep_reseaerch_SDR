export function SkeletonLeadCard() {
  return (
    <div className="glass p-3.5 flex items-center gap-4">
      <div className="sk w-11 h-11 rounded-full flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <div className="sk h-3 rounded-full w-2/5" />
        <div className="sk h-2.5 rounded-full w-3/5" />
      </div>
      <div className="sk h-5 w-16 rounded-full" />
      <div className="sk h-5 w-12 rounded-full" />
    </div>
  )
}

export function SkeletonKPICard() {
  return (
    <div className="glass p-4">
      <div className="sk h-2.5 rounded-full w-16 mb-3" />
      <div className="sk h-7 rounded-lg w-20" />
    </div>
  )
}

export function SkeletonChartCard() {
  return (
    <div className="glass p-5">
      <div className="sk h-3 rounded-full w-32 mb-1" />
      <div className="sk h-2.5 rounded-full w-48 mb-6" />
      <div className="flex items-end gap-3 h-40">
        {[70, 55, 85, 45, 90, 60, 40, 75].map((h, i) => (
          <div key={i} className="sk flex-1 rounded-t-md" style={{ height: `${h}%` }} />
        ))}
      </div>
    </div>
  )
}
