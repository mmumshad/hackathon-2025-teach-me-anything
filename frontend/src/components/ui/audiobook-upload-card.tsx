"use client"

import { useState, useRef, useEffect } from "react"
import { AnimatedCircularProgressBar } from "@/components/ui/animated-circular-progress-bar"

interface AudiobookUploadCardProps {
  isVisible: boolean
  isGenerating: boolean
  onFileUpload: (file: File) => void
  onClose: () => void
}

export function AudiobookUploadCard({ 
  isVisible, 
  isGenerating, 
  onFileUpload, 
  onClose 
}: AudiobookUploadCardProps) {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [progress, setProgress] = useState(0)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Simulate progress during generation
  useEffect(() => {
    if (!isGenerating) {
      setProgress(0)
      return
    }

    setProgress(0)
    const duration = 30000 // 30 seconds for audiobook generation
    const interval = 100 // Update every 100ms
    const increment = 100 / (duration / interval)

    const timer = setInterval(() => {
      setProgress(prev => {
        const newProgress = prev + increment
        if (newProgress >= 100) {
          clearInterval(timer)
          return 100
        }
        return newProgress
      })
    }, interval)

    return () => clearInterval(timer)
  }, [isGenerating])

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.type === "application/pdf") {
        setSelectedFile(file)
      } else {
        alert("Please upload a PDF file only")
      }
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      if (file.type === "application/pdf") {
        setSelectedFile(file)
      } else {
        alert("Please upload a PDF file only")
      }
    }
  }

  const handleUpload = () => {
    if (selectedFile) {
      onFileUpload(selectedFile)
      setSelectedFile(null)
    }
  }

  const handleClose = () => {
    setSelectedFile(null)
    onClose()
  }

  if (!isVisible) return null

  return (
    <div className="mb-8 max-w-4xl mx-auto">
      <div className="relative w-full bg-gradient-to-br from-purple-50 to-blue-50 rounded-[2rem] shadow-2xl p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-full">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" className="text-purple-600">
                <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z"/>
                <path d="M12 14c1.66 0 3-1.34 3-3V7h2v4c0 2.76-2.24 5-5 5s-5-2.24-5-5V7h2v4c0 1.66 1.34 3 3 3z" opacity="0.6"/>
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-gray-800">Create Audiobook</h2>
          </div>
          <button
            onClick={handleClose}
            disabled={isGenerating}
            className="p-2 hover:bg-white hover:bg-opacity-50 rounded-full transition-colors"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" className="text-gray-500">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>

        {isGenerating ? (
          /* Generating State */
          <div className="text-center py-8">
            <div className="mb-6 flex justify-center">
              <AnimatedCircularProgressBar
                max={100}
                min={0}
                value={progress}
                gaugePrimaryColor="rgb(147 51 234)" // Purple-600
                gaugeSecondaryColor="rgba(0, 0, 0, 0.1)"
              />
            </div>
            <div className="text-xl text-gray-600 font-light mb-2">
              Generating your audiobook...
            </div>
            <div className="text-sm text-gray-500">
              This may take a few minutes depending on the PDF size
            </div>
          </div>
        ) : (
          /* Upload State */
          <div>
            <div className="text-center mb-6">
              <p className="text-gray-600 mb-4">
                Upload a PDF file to convert it into an audiobook with AI-generated narration
              </p>
            </div>

            {/* File Upload Area */}
            <div
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
                dragActive 
                  ? 'border-purple-400 bg-purple-100' 
                  : 'border-purple-300 hover:border-purple-400 hover:bg-purple-100'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <div className="mb-4">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor" className="mx-auto text-purple-400">
                  <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
                </svg>
              </div>
              
              {selectedFile ? (
                <div className="text-center">
                  <div className="text-lg font-medium text-gray-800 mb-2">
                    📄 {selectedFile.name}
                  </div>
                  <div className="text-sm text-gray-500 mb-4">
                    {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                  </div>
                  <button
                    onClick={handleUpload}
                    className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    Generate Audiobook
                  </button>
                </div>
              ) : (
                <div>
                  <p className="text-lg font-medium text-gray-700 mb-2">
                    Drop your PDF here, or click to browse
                  </p>
                  <p className="text-sm text-gray-500 mb-4">
                    Supports PDF files up to 50MB
                  </p>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    Choose PDF File
                  </button>
                </div>
              )}
            </div>

            {/* Hidden File Input */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              className="hidden"
            />

            {/* Features List */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="text-green-500">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
                AI-powered voice synthesis
              </div>
              <div className="flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="text-green-500">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
                High-quality audio output
              </div>
              <div className="flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="text-green-500">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
                Automatic text chunking
              </div>
              <div className="flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="text-green-500">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
                Chapter-based playback
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
