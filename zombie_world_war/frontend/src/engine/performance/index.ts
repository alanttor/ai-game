/**
 * Performance module exports
 * Requirements: 5.3 - Performance optimization
 */

export { PerformanceMonitor, PerformanceEvent } from './PerformanceMonitor'
export type { PerformanceMetrics } from './PerformanceMonitor'

export {
  ObjectPool,
  Vector3Pool,
  Matrix4Pool,
  RaycasterPool,
  GeometryPool,
  MaterialPool,
  clearAllPools,
} from './ObjectPool'
