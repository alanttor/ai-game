import * as THREE from 'three'

/**
 * Generic object pool for reusing objects and reducing garbage collection
 * Requirements: 5.3 - Performance optimization
 */
export class ObjectPool<T> {
  private pool: T[] = []
  private createFn: () => T
  private resetFn: (obj: T) => void
  private maxSize: number

  constructor(
    createFn: () => T,
    resetFn: (obj: T) => void,
    initialSize: number = 0,
    maxSize: number = 100
  ) {
    this.createFn = createFn
    this.resetFn = resetFn
    this.maxSize = maxSize

    // Pre-populate pool
    for (let i = 0; i < initialSize; i++) {
      this.pool.push(this.createFn())
    }
  }

  /**
   * Get an object from the pool or create a new one
   */
  acquire(): T {
    if (this.pool.length > 0) {
      return this.pool.pop()!
    }
    return this.createFn()
  }

  /**
   * Return an object to the pool
   */
  release(obj: T): void {
    if (this.pool.length < this.maxSize) {
      this.resetFn(obj)
      this.pool.push(obj)
    }
  }

  /**
   * Get current pool size
   */
  size(): number {
    return this.pool.length
  }

  /**
   * Clear the pool
   */
  clear(): void {
    this.pool = []
  }

  /**
   * Pre-warm the pool with objects
   */
  prewarm(count: number): void {
    const toCreate = Math.min(count, this.maxSize) - this.pool.length
    for (let i = 0; i < toCreate; i++) {
      this.pool.push(this.createFn())
    }
  }
}

/**
 * Vector3 pool for reusing THREE.Vector3 objects
 */
export class Vector3Pool {
  private static pool: THREE.Vector3[] = []
  private static maxSize: number = 200

  static acquire(): THREE.Vector3 {
    if (this.pool.length > 0) {
      return this.pool.pop()!
    }
    return new THREE.Vector3()
  }

  static release(vec: THREE.Vector3): void {
    if (this.pool.length < this.maxSize) {
      vec.set(0, 0, 0)
      this.pool.push(vec)
    }
  }

  static size(): number {
    return this.pool.length
  }

  static clear(): void {
    this.pool = []
  }
}

/**
 * Matrix4 pool for reusing THREE.Matrix4 objects
 */
export class Matrix4Pool {
  private static pool: THREE.Matrix4[] = []
  private static maxSize: number = 50

  static acquire(): THREE.Matrix4 {
    if (this.pool.length > 0) {
      return this.pool.pop()!
    }
    return new THREE.Matrix4()
  }

  static release(mat: THREE.Matrix4): void {
    if (this.pool.length < this.maxSize) {
      mat.identity()
      this.pool.push(mat)
    }
  }

  static size(): number {
    return this.pool.length
  }

  static clear(): void {
    this.pool = []
  }
}

/**
 * Raycaster pool for reusing THREE.Raycaster objects
 */
export class RaycasterPool {
  private static pool: THREE.Raycaster[] = []
  private static maxSize: number = 10

  static acquire(): THREE.Raycaster {
    if (this.pool.length > 0) {
      return this.pool.pop()!
    }
    return new THREE.Raycaster()
  }

  static release(raycaster: THREE.Raycaster): void {
    if (this.pool.length < this.maxSize) {
      this.pool.push(raycaster)
    }
  }

  static size(): number {
    return this.pool.length
  }

  static clear(): void {
    this.pool = []
  }
}

/**
 * Geometry pool for reusing common geometries
 */
export class GeometryPool {
  private static pools: Map<string, THREE.BufferGeometry[]> = new Map()
  private static maxPerType: number = 20

  static acquire(type: string, createFn: () => THREE.BufferGeometry): THREE.BufferGeometry {
    const pool = this.pools.get(type)
    if (pool && pool.length > 0) {
      return pool.pop()!
    }
    return createFn()
  }

  static release(type: string, geometry: THREE.BufferGeometry): void {
    if (!this.pools.has(type)) {
      this.pools.set(type, [])
    }
    const pool = this.pools.get(type)!
    if (pool.length < this.maxPerType) {
      pool.push(geometry)
    } else {
      geometry.dispose()
    }
  }

  static clear(): void {
    this.pools.forEach((pool) => {
      pool.forEach((geom) => geom.dispose())
    })
    this.pools.clear()
  }
}

/**
 * Material pool for reusing common materials
 */
export class MaterialPool {
  private static pools: Map<string, THREE.Material[]> = new Map()
  private static maxPerType: number = 20

  static acquire(type: string, createFn: () => THREE.Material): THREE.Material {
    const pool = this.pools.get(type)
    if (pool && pool.length > 0) {
      return pool.pop()!
    }
    return createFn()
  }

  static release(type: string, material: THREE.Material): void {
    if (!this.pools.has(type)) {
      this.pools.set(type, [])
    }
    const pool = this.pools.get(type)!
    if (pool.length < this.maxPerType) {
      pool.push(material)
    } else {
      material.dispose()
    }
  }

  static clear(): void {
    this.pools.forEach((pool) => {
      pool.forEach((mat) => mat.dispose())
    })
    this.pools.clear()
  }
}

/**
 * Clear all static pools - call on game cleanup
 */
export function clearAllPools(): void {
  Vector3Pool.clear()
  Matrix4Pool.clear()
  RaycasterPool.clear()
  GeometryPool.clear()
  MaterialPool.clear()
}
