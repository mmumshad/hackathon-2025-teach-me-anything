"use client"

import { useState, useRef, useEffect, useMemo } from "react"

interface AudiobookPlayerProps {
  audiobookChunks: string[]
  audiobookInfo: {
    fileName: string
    totalChunks: number
    textLength: number
    pdfInfo?: any
  }
  onClose: () => void
}

export function AudiobookPlayer({ 
  audiobookChunks, 
  audiobookInfo, 
  onClose 
}: AudiobookPlayerProps) {
  const [currentChunk, setCurrentChunk] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [playbackSpeed, setPlaybackSpeed] = useState(1)
  const [volume, setVolume] = useState(1)
  const [muted, setMuted] = useState(false)
  const audioRef = useRef<HTMLAudioElement>(null)

  // Convert base64 chunks to data URLs
  const convertChunksToDataUrls = (chunks: string[]) => {
    return chunks.map((chunk) => {
      // If it's already a data URL, return as is
      if (chunk.startsWith('data:')) {
        return chunk
      }
      // If it's base64, convert to data URL
      // Try to detect if it's WAV or MP3 based on the data
      if (chunk.startsWith('UklGR') || chunk.startsWith('RIFF')) {
        return `data:audio/wav;base64,${chunk}`
      } else {
        return `data:audio/mpeg;base64,${chunk}`
      }
    })
  }

  const audioDataUrls = useMemo(() => {
    return convertChunksToDataUrls(audiobookChunks)
  }, [audiobookChunks])

  // Update audio source when chunk changes
  useEffect(() => {
    if (audioRef.current && audioDataUrls[currentChunk]) {
      const newSrc = audioDataUrls[currentChunk]
      
      // Only set source if it's different from current source
      if (audioRef.current.src !== newSrc) {
        audioRef.current.src = newSrc
        audioRef.current.load()
      }
    }
  }, [currentChunk, audioDataUrls])

  // Handle audio events
  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const handleTimeUpdate = () => setCurrentTime(audio.currentTime)
    const handleDurationChange = () => setDuration(audio.duration)
    const handleEnded = () => {
      if (currentChunk < audioDataUrls.length - 1) {
        setCurrentChunk(prev => prev + 1)
      } else {
        setIsPlaying(false)
      }
    }
    const handlePlay = () => setIsPlaying(true)
    const handlePause = () => setIsPlaying(false)

    audio.addEventListener('timeupdate', handleTimeUpdate)
    audio.addEventListener('durationchange', handleDurationChange)
    audio.addEventListener('ended', handleEnded)
    audio.addEventListener('play', handlePlay)
    audio.addEventListener('pause', handlePause)

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate)
      audio.removeEventListener('durationchange', handleDurationChange)
      audio.removeEventListener('ended', handleEnded)
      audio.removeEventListener('play', handlePlay)
      audio.removeEventListener('pause', handlePause)
    }
  }, [currentChunk, audioDataUrls.length])

  const togglePlayPause = () => {
    if (audioRef.current) {
      // Ensure volume is set correctly
      audioRef.current.volume = volume
      audioRef.current.muted = muted
      
      if (isPlaying) {
        audioRef.current.pause()
      } else {
        audioRef.current.play().catch(e => {
          console.error("Error playing audio:", e)
        })
      }
      setIsPlaying(!isPlaying)
    }
  }

  const goToPreviousChunk = () => {
    if (currentChunk > 0) {
      setCurrentChunk(prev => prev - 1)
    }
  }

  const goToNextChunk = () => {
    if (currentChunk < audioDataUrls.length - 1) {
      setCurrentChunk(prev => prev + 1)
    }
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value)
    if (audioRef.current) {
      audioRef.current.currentTime = time
      setCurrentTime(time)
    }
  }

  const changePlaybackSpeed = (speed: number) => {
    setPlaybackSpeed(speed)
    if (audioRef.current) {
      audioRef.current.playbackRate = speed
    }
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  const overallProgress = ((currentChunk + (currentTime / duration)) / audioDataUrls.length) * 100

  return (
    <div className="mb-8 max-w-4xl mx-auto">
      <div className="relative w-full bg-gradient-to-br from-purple-50 to-blue-50 rounded-[2rem] shadow-2xl p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-full">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" className="text-purple-600">
                <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
              </svg>
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-gray-800">Audiobook Player</h2>
              <p className="text-sm text-gray-500">{audiobookInfo.fileName}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white hover:bg-opacity-50 rounded-full transition-colors"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" className="text-gray-500">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>

        {/* Progress Info */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-600">
              Chapter {currentChunk + 1} of {audiobookChunks.length}
            </span>
            <span className="text-sm text-gray-600">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-purple-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentTime / duration) * 100}%` }}
            />
          </div>
        </div>

        {/* Overall Progress */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-600">Overall Progress</span>
            <span className="text-sm text-gray-600">{Math.round(overallProgress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-gradient-to-r from-purple-500 to-purple-600 h-3 rounded-full transition-all duration-300"
              style={{ width: `${overallProgress}%` }}
            />
          </div>
        </div>

        {/* Audio Element */}
        <audio
          ref={audioRef}
          preload="metadata"
          className="hidden"
          volume={volume}
          muted={muted}
          onTimeUpdate={() => {
            if (audioRef.current) {
              setCurrentTime(audioRef.current.currentTime)
            }
          }}
        />

        {/* Controls */}
        <div className="flex items-center justify-center gap-4 mb-6">
          <button
            onClick={goToPreviousChunk}
            disabled={currentChunk === 0}
            className="p-3 rounded-full bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
            </svg>
          </button>

          <button
            onClick={togglePlayPause}
            className="p-4 rounded-full bg-purple-600 hover:bg-purple-700 text-white transition-colors"
          >
            {isPlaying ? (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
              </svg>
            ) : (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
              </svg>
            )}
          </button>

          <button
            onClick={goToNextChunk}
            disabled={currentChunk === audioDataUrls.length - 1}
            className="p-3 rounded-full bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
            </svg>
          </button>
        </div>

        {/* Speed Controls */}
        <div className="flex items-center justify-center gap-2 mb-6">
          <span className="text-sm text-gray-600">Speed:</span>
          {[0.5, 0.75, 1, 1.25, 1.5].map(speed => (
            <button
              key={speed}
              onClick={() => changePlaybackSpeed(speed)}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                playbackSpeed === speed
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {speed}x
            </button>
          ))}
        </div>

        {/* Volume Controls */}
        <div className="flex items-center justify-center gap-4 mb-6">
          <button
            onClick={() => {
              const newMuted = !muted
              setMuted(newMuted)
              if (audioRef.current) {
                audioRef.current.muted = newMuted
              }
            }}
            className={`p-2 rounded-full transition-colors ${
              muted ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {muted ? (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
              </svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
              </svg>
            )}
          </button>
          
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Volume:</span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={volume}
              onChange={(e) => {
                const newVolume = parseFloat(e.target.value)
                setVolume(newVolume)
                if (audioRef.current) {
                  audioRef.current.volume = newVolume
                }
              }}
              className="w-20"
            />
            <span className="text-sm text-gray-500 w-8">{Math.round(volume * 100)}%</span>
          </div>
        </div>

        {/* Chapter List */}
        <div className="max-h-40 overflow-y-auto">
          <h3 className="text-lg font-medium text-gray-800 mb-3">Chapters</h3>
          <div className="space-y-2">
            {audioDataUrls.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentChunk(index)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  currentChunk === index
                    ? 'bg-purple-100 text-purple-800 border border-purple-200'
                    : 'bg-gray-50 hover:bg-gray-100 text-gray-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">Chapter {index + 1}</span>
                  {currentChunk === index && (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="text-purple-600">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
