"use client"

import { useEffect, useState } from "react"
import { AnimatedCircularProgressBar } from "@/components/ui/animated-circular-progress-bar"

interface VideoGenerationProgressProps {
  isGenerating: boolean
  onComplete?: () => void
}

export function VideoGenerationProgress({ isGenerating, onComplete }: VideoGenerationProgressProps) {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    if (!isGenerating) {
      setProgress(0)
      return
    }

    // Reset progress when starting
    setProgress(0)

    // Calculate progress over 80 seconds
    const duration = 100000 // 100 seconds in milliseconds
    const interval = 100 // Update every 100ms for smooth animation
    const increment = 100 / (duration / interval) // Calculate increment per interval

    const timer = setInterval(() => {
      setProgress(prev => {
        const newProgress = prev + increment
        if (newProgress >= 100) {
          clearInterval(timer)
          onComplete?.()
          return 100
        }
        return newProgress
      })
    }, interval)

    return () => clearInterval(timer)
  }, [isGenerating, onComplete])

  if (!isGenerating) return null

  return (
    <div className="text-center">
      <div className="mb-6">
        <AnimatedCircularProgressBar
          max={100}
          min={0}
          value={progress}
          gaugePrimaryColor="rgb(59 130 246)" // Blue-500
          gaugeSecondaryColor="rgba(0, 0, 0, 0.1)"
        />
      </div>
      <div className="text-xl text-gray-600 font-light">
        Generating your video...
      </div>
      <div className="text-sm text-gray-500 mt-2">
        This may take a few minutes
      </div>
    </div>
  )
}
