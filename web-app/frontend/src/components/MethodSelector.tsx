import React from 'react'
import { Zap, Gauge, Clock } from 'lucide-react'
import { MethodInfo } from '../api/client'

interface MethodSelectorProps {
  methods: MethodInfo[]
  selectedMethod: string
  onMethodChange: (methodId: string) => void
}

function MethodSelector({ methods, selectedMethod, onMethodChange }: MethodSelectorProps) {
  const getSpeedIcon = (speed: string) => {
    switch (speed) {
      case 'fast':
        return <Zap className="w-4 h-4" />
      case 'medium':
        return <Clock className="w-4 h-4" />
      default:
        return <Gauge className="w-4 h-4" />
    }
  }

  const getSpeedLabel = (speed: string) => {
    return speed.charAt(0).toUpperCase() + speed.slice(1).replace('_', ' ')
  }

  const getQualityLabel = (quality: string) => {
    const labels: Record<string, string> = {
      medium: 'Medium',
      'medium-high': 'Medium-High',
      high: 'High',
      'very_high': 'Very High',
    }
    return labels[quality] || quality
  }

  return (
    <div className="space-y-3">
      {methods.map(method => (
        <button
          key={method.id}
          onClick={() => onMethodChange(method.id)}
          disabled={!method.available}
          className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
            selectedMethod === method.id
              ? 'border-blue-400 bg-blue-500/10'
              : 'border-slate-600 hover:border-slate-500'
          } ${!method.available ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        >
          <div className="flex justify-between items-start mb-2">
            <div>
              <p className="font-semibold text-white">{method.name}</p>
              <p className="text-xs text-slate-400">{method.description}</p>
            </div>
            {selectedMethod === method.id && (
              <div className="px-2 py-1 bg-blue-500 rounded text-xs font-semibold">
                Selected
              </div>
            )}
          </div>

          <div className="flex items-center gap-4 pt-2 border-t border-slate-700">
            <div className="flex items-center gap-1 text-xs text-slate-400">
              {getSpeedIcon(method.speed)}
              {getSpeedLabel(method.speed)}
            </div>
            <div className="text-xs text-slate-400">
              Quality: {getQualityLabel(method.quality)}
            </div>
            {!method.available && (
              <div className="ml-auto text-xs text-yellow-400">
                Not installed
              </div>
            )}
          </div>
        </button>
      ))}
    </div>
  )
}

export default MethodSelector
