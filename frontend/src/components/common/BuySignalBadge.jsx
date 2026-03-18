import { BUY_SIGNAL_CONFIG } from '../../utils/constants'

export default function BuySignalBadge({ signal }) {
  if (!signal) return null
  const config = BUY_SIGNAL_CONFIG[signal] || BUY_SIGNAL_CONFIG.hold
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${config.color}`}>
      {config.label}
    </span>
  )
}
