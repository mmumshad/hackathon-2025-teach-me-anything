"use client"

import { cn } from "@/lib/utils"
import React, { useEffect, useRef } from "react"

interface ParticlesProps {
  className?: string
  quantity?: number
  color?: string
}

const Particles: React.FC<ParticlesProps> = ({
  className = "",
  quantity = 50,
  color = "#e5e7eb",
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    const resizeCanvas = () => {
      const rect = canvas.parentElement?.getBoundingClientRect()
      if (rect) {
        canvas.width = rect.width
        canvas.height = rect.height
      }
    }
    
    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    // Simple particles
    const particles: Array<{x: number, y: number, vx: number, vy: number, size: number}> = []
    
    // Create particles
    for (let i = 0; i < quantity; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5, // Much slower movement
        vy: (Math.random() - 0.5) * 0.5,
        size: Math.random() * 2 + 0.5, // Small particles
      })
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      particles.forEach(particle => {
        // Update position
        particle.x += particle.vx
        particle.y += particle.vy
        
        // Wrap around edges
        if (particle.x < 0) particle.x = canvas.width
        if (particle.x > canvas.width) particle.x = 0
        if (particle.y < 0) particle.y = canvas.height
        if (particle.y > canvas.height) particle.y = 0
        
        // Draw particle
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
        ctx.fillStyle = color
        ctx.globalAlpha = 0.6 // Subtle opacity
        ctx.fill()
        ctx.globalAlpha = 1 // Reset alpha
      })
      
      requestAnimationFrame(animate)
    }
    
    animate()

    return () => {
      window.removeEventListener('resize', resizeCanvas)
    }
  }, [quantity, color])

  return (
    <div className={cn("pointer-events-none absolute inset-0", className)}>
      <canvas 
        ref={canvasRef} 
        className="w-full h-full"
        style={{ zIndex: 0 }}
      />
    </div>
  )
}

export { Particles }