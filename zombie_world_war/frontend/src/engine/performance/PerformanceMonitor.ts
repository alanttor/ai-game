import * as THREE from 'three'
import type { EventCallback } from '../types'

/**
 * Performance metrics interface
 */
export interface PerformanceMetrics {
  fps: number
  frameTime: number
  avgFrameTime: number
  minFrameTime: number
  maxFrameTime: number
  drawCalls: number
  triangles: number
  geometries: number
  textures: number
  memoryUsed: number
  zombieCount: number
  visibleObjects: number
}

/**
 * Performance events
 */
export enum PerformanceEvent {
  FPS_DROP = 'performance:fpsDrop',
  FPS_RECOVER = 'performance:fpsRecover',
  MEMORY_WARNING = 'performance:memoryWarning',
}

/**
 * PerformanceMonitor - Tracks and reports game performance metrics
 * Requirements: 5.3 - Performance optimization and 60 FPS target
 */
export class PerformanceMonitor {
  private renderer: THREE.WebGLRenderer | null = null
  
  // Frame timing
  private frameCount: number = 0
  private lastFPSUpdate: number = 0
  private currentFPS: number = 60
  private frameTimes: number[] = []
  private maxFrameTimeSamples: number = 120
  
  // Performance thresholds
  private targetFPS: number = 60
  private lowFPSThreshold: number = 45
  private criticalFPSThreshold: number = 30
  
  // State tracking
  private isLowFPS: boolean = false
  private consecutiveLowFrames: number = 0
  private lowFrameThreshold: number = 30 // Frames before triggering warning
  
  // Memory tracking
  private lastMemoryCheck: number = 0
  private memoryCheckInterval: number = 5000 // Check every 5 seconds
  
  // External counts
  private zombieCount: number = 0
  private visibleObjectCount: number = 0
  
  // Event system
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  constructor() {
    this.lastFPSUpdate = performance.now()
    this.lastMemoryCheck = performance.now()
  }

  /**
   * Set the renderer for accessing render info
   */
  setRenderer(renderer: THREE.WebGLRenderer): void {
    this.renderer = renderer
  }

  /**
   * Set target FPS
   */
  setTargetFPS(fps: number): void {
    this.targetFPS = Math.max(30, Math.min(144, fps))
    this.lowFPSThreshold = this.targetFPS * 0.75
    this.criticalFPSThreshold = this.targetFPS * 0.5
  }


  /**
   * Update performance metrics - call every frame
   */
  update(deltaTime: number): void {
    const frameTimeMs = deltaTime * 1000
    
    // Track frame times
    this.frameTimes.push(frameTimeMs)
    if (this.frameTimes.length > this.maxFrameTimeSamples) {
      this.frameTimes.shift()
    }
    
    this.frameCount++
    
    // Update FPS every second
    const now = performance.now()
    if (now - this.lastFPSUpdate >= 1000) {
      this.currentFPS = this.frameCount
      this.frameCount = 0
      this.lastFPSUpdate = now
      
      // Check for FPS issues
      this.checkFPSHealth()
    }
    
    // Periodic memory check
    if (now - this.lastMemoryCheck >= this.memoryCheckInterval) {
      this.checkMemory()
      this.lastMemoryCheck = now
    }
  }

  /**
   * Check FPS health and emit events if needed
   */
  private checkFPSHealth(): void {
    if (this.currentFPS < this.lowFPSThreshold) {
      this.consecutiveLowFrames++
      
      if (!this.isLowFPS && this.consecutiveLowFrames >= this.lowFrameThreshold / 60) {
        this.isLowFPS = true
        this.emit(PerformanceEvent.FPS_DROP, {
          fps: this.currentFPS,
          target: this.targetFPS,
          isCritical: this.currentFPS < this.criticalFPSThreshold,
        })
      }
    } else {
      if (this.isLowFPS) {
        this.isLowFPS = false
        this.emit(PerformanceEvent.FPS_RECOVER, {
          fps: this.currentFPS,
          target: this.targetFPS,
        })
      }
      this.consecutiveLowFrames = 0
    }
  }

  /**
   * Check memory usage
   */
  private checkMemory(): void {
    // Check if performance.memory is available (Chrome only)
    const perf = performance as Performance & {
      memory?: { usedJSHeapSize: number; jsHeapSizeLimit: number }
    }
    
    if (perf.memory) {
      const usedMB = perf.memory.usedJSHeapSize / (1024 * 1024)
      const limitMB = perf.memory.jsHeapSizeLimit / (1024 * 1024)
      const usagePercent = (usedMB / limitMB) * 100
      
      if (usagePercent > 80) {
        this.emit(PerformanceEvent.MEMORY_WARNING, {
          usedMB: Math.round(usedMB),
          limitMB: Math.round(limitMB),
          usagePercent: Math.round(usagePercent),
        })
      }
    }
  }

  /**
   * Set external zombie count for metrics
   */
  setZombieCount(count: number): void {
    this.zombieCount = count
  }

  /**
   * Set visible object count for metrics
   */
  setVisibleObjectCount(count: number): void {
    this.visibleObjectCount = count
  }

  /**
   * Get current performance metrics
   */
  getMetrics(): PerformanceMetrics {
    const avgFrameTime = this.frameTimes.length > 0
      ? this.frameTimes.reduce((a, b) => a + b, 0) / this.frameTimes.length
      : 16.67
    
    const minFrameTime = this.frameTimes.length > 0
      ? Math.min(...this.frameTimes)
      : 16.67
    
    const maxFrameTime = this.frameTimes.length > 0
      ? Math.max(...this.frameTimes)
      : 16.67
    
    let drawCalls = 0
    let triangles = 0
    let geometries = 0
    let textures = 0
    
    if (this.renderer) {
      const info = this.renderer.info
      drawCalls = info.render.calls
      triangles = info.render.triangles
      geometries = info.memory.geometries
      textures = info.memory.textures
    }
    
    // Get memory usage if available
    let memoryUsed = 0
    const perf = performance as Performance & {
      memory?: { usedJSHeapSize: number }
    }
    if (perf.memory) {
      memoryUsed = Math.round(perf.memory.usedJSHeapSize / (1024 * 1024))
    }
    
    return {
      fps: this.currentFPS,
      frameTime: this.frameTimes[this.frameTimes.length - 1] ?? 16.67,
      avgFrameTime,
      minFrameTime,
      maxFrameTime,
      drawCalls,
      triangles,
      geometries,
      textures,
      memoryUsed,
      zombieCount: this.zombieCount,
      visibleObjects: this.visibleObjectCount,
    }
  }

  /**
   * Get current FPS
   */
  getFPS(): number {
    return this.currentFPS
  }

  /**
   * Check if performance is currently degraded
   */
  isPerformanceDegraded(): boolean {
    return this.isLowFPS
  }

  // ==================== Event System ====================

  on(event: string, callback: EventCallback): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set())
    }
    this.eventListeners.get(event)!.add(callback)
  }

  off(event: string, callback: EventCallback): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.delete(callback)
    }
  }

  private emit(event: string, data?: unknown): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.forEach((callback) => callback(data))
    }
  }

  /**
   * Reset all metrics
   */
  reset(): void {
    this.frameCount = 0
    this.currentFPS = 60
    this.frameTimes = []
    this.isLowFPS = false
    this.consecutiveLowFrames = 0
  }

  /**
   * Dispose resources
   */
  dispose(): void {
    this.eventListeners.clear()
    this.frameTimes = []
    this.renderer = null
  }
}
