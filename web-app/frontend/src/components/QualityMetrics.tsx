import React from 'react'
import { TrendingUp, Zap, Eye } from 'lucide-react'

interface QualityMetricsProps {
  metrics: {
    brisque_original: number
    brisque_processed: number
    ssim: number
    sharpness_original: number
    sharpness_processed: number
    contrast_original: number
    contrast_processed: number
    brisque_improvement: number
  }
}

function QualityMetrics({ metrics }: QualityMetricsProps) {
  const getMetricColor = (value: number, isImprovement?: boolean) => {
    if (isImprovement === undefined) {
      if (value < 30) return 'text-green-400'
      if (value < 60) return 'text-yellow-400'
      return 'text-red-400'
    }

    return value > 0 ? 'text-green-400' : value < 0 ? 'text-red-400' : 'text-slate-400'
  }

  const formatValue = (value: number, decimals = 2) => {
    return value.toFixed(decimals)
  }

  return (
    <div className="space-y-4">
      {/* BRISQUE Score */}
      <div className="p-4 rounded-lg bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/20">
        <div className="flex items-center justify-between mb-2">
          <p className="flex items-center gap-2 font-semibold">
            <Zap className="w-4 h-4 text-blue-400" />
            BRISQUE Score
          </p>
          <p className={`font-bold text-lg ${getMetricColor(metrics.brisque_improvement, true)}`}>
            {metrics.brisque_improvement > 0 ? '+' : ''}{formatValue(metrics.brisque_improvement)}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-slate-400">Before</p>
            <p className={`font-semibold ${getMetricColor(metrics.brisque_original)}`}>
              {formatValue(metrics.brisque_original)}
            </p>
          </div>
          <div>
            <p className="text-slate-400">After</p>
            <p className={`font-semibold ${getMetricColor(metrics.brisque_processed)}`}>
              {formatValue(metrics.brisque_processed)}
            </p>
          </div>
        </div>
        <p className="text-xs text-slate-500 mt-2">Lower is better (0-100 scale)</p>
      </div>

      {/* SSIM */}
      <div className="p-4 rounded-lg bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20">
        <div className="flex items-center justify-between">
          <p className="flex items-center gap-2 font-semibold">
            <Eye className="w-4 h-4 text-purple-400" />
            Structural Similarity (SSIM)
          </p>
          <p className="font-bold text-lg text-purple-400">
            {formatValue(metrics.ssim)}
          </p>
        </div>
        <p className="text-xs text-slate-500 mt-2">
          {metrics.ssim > 0.9 ? 'Excellent' : metrics.ssim > 0.7 ? 'Good' : 'Fair'} similarity (-1 to 1 scale)
        </p>
      </div>

      {/* Sharpness & Contrast */}
      <div className="grid grid-cols-2 gap-3">
        <div className="p-4 rounded-lg bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/20">
          <p className="text-xs text-slate-400 mb-2">Sharpness</p>
          <div className="flex items-baseline gap-2">
            <p className={`text-sm font-semibold ${getMetricColor(metrics.sharpness_processed, true)}`}>
              {formatValue(metrics.sharpness_processed)}
            </p>
            <p className="text-xs text-slate-500">
              {metrics.sharpness_processed > metrics.sharpness_original ? '↑' : '↓'}
            </p>
          </div>
        </div>

        <div className="p-4 rounded-lg bg-gradient-to-br from-orange-500/10 to-red-500/10 border border-orange-500/20">
          <p className="text-xs text-slate-400 mb-2">Contrast</p>
          <div className="flex items-baseline gap-2">
            <p className={`text-sm font-semibold ${getMetricColor(metrics.contrast_processed, true)}`}>
              {formatValue(metrics.contrast_processed)}
            </p>
            <p className="text-xs text-slate-500">
              {metrics.contrast_processed > metrics.contrast_original ? '↑' : '↓'}
            </p>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="p-3 rounded-lg bg-slate-700/50 border border-slate-600">
        <p className="text-xs font-semibold text-slate-300 mb-2">Summary</p>
        <ul className="text-xs text-slate-400 space-y-1">
          <li>
            - Quality improved by{' '}
            <span className={getMetricColor(metrics.brisque_improvement, true)}>
              {Math.abs(Math.round(metrics.brisque_improvement))}
            </span>
            {' '}BRISQUE points
          </li>
          <li>
            - Structural similarity score:{' '}
            <span className="text-blue-400">
              {Math.round(metrics.ssim * 100)}%
            </span>
          </li>
          <li>
            - Image{' '}
            <span className={metrics.sharpness_processed > metrics.sharpness_original ? 'text-green-400' : 'text-slate-400'}>
              {metrics.sharpness_processed > metrics.sharpness_original ? 'increased' : 'maintained'}
            </span>
            {' '}sharpness
          </li>
        </ul>
      </div>
    </div>
  )
}

export default QualityMetrics
