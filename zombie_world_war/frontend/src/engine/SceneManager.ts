import * as THREE from 'three'
import type { EventCallback } from './types'
import { CitySceneBuilder } from './scene/CitySceneBuilder'

/**
 * Scene events emitted by SceneManager
 */
export enum SceneEvent {
  SCENE_LOADED = 'scene:loaded',
  OBJECT_ADDED = 'scene:objectadded',
  OBJECT_REMOVED = 'scene:objectremoved',
  LIGHTING_CHANGED = 'scene:lightingchanged',
}

/**
 * Lighting preset configurations
 */
export interface LightingPreset {
  ambientColor: number
  ambientIntensity: number
  directionalColor: number
  directionalIntensity: number
  directionalPosition: THREE.Vector3
  hemisphereTopColor: number
  hemisphereBottomColor: number
  hemisphereIntensity: number
}

/**
 * Default lighting presets
 */
export const LightingPresets: Record<string, LightingPreset> = {
  exterior: {
    ambientColor: 0x606060,
    ambientIntensity: 0.8,
    directionalColor: 0xffffff,
    directionalIntensity: 1.5,
    directionalPosition: new THREE.Vector3(50, 100, 50),
    hemisphereTopColor: 0x87ceeb,
    hemisphereBottomColor: 0x444444,
    hemisphereIntensity: 0.5,
  },
  interior: {
    ambientColor: 0x303030,
    ambientIntensity: 0.8,
    directionalColor: 0xfff5e6,
    directionalIntensity: 0.3,
    directionalPosition: new THREE.Vector3(0, 10, 0),
    hemisphereTopColor: 0x444444,
    hemisphereBottomColor: 0x222222,
    hemisphereIntensity: 0.2,
  },
  night: {
    ambientColor: 0x101020,
    ambientIntensity: 0.3,
    directionalColor: 0x8888ff,
    directionalIntensity: 0.2,
    directionalPosition: new THREE.Vector3(-50, 80, -50),
    hemisphereTopColor: 0x0a0a20,
    hemisphereBottomColor: 0x000000,
    hemisphereIntensity: 0.1,
  },
}

/**
 * SceneManager - Manages Three.js scene, camera, renderer, and lighting
 * Requirements: 5.1, 5.2
 */
export class SceneManager {
  // Three.js core components
  private scene: THREE.Scene
  private camera: THREE.PerspectiveCamera
  private renderer: THREE.WebGLRenderer
  private container: HTMLElement

  // Lighting components
  private ambientLight: THREE.AmbientLight
  private directionalLight: THREE.DirectionalLight
  private hemisphereLight: THREE.HemisphereLight

  // Current lighting preset
  private currentPreset: string = 'exterior'

  // Raycaster for collision detection
  private raycaster: THREE.Raycaster

  // Event listeners
  private eventListeners: Map<string, Set<EventCallback>> = new Map()

  // Object tracking
  private gameObjects: Map<string, THREE.Object3D> = new Map()

  // City scene builder
  private citySceneBuilder: CitySceneBuilder | null = null

  // Store bound resize handler for proper cleanup (initialized in init)
  private boundHandleResize!: () => void

  constructor(container: HTMLElement) {
    this.container = container

    // Initialize scene
    this.scene = new THREE.Scene()
    this.scene.background = new THREE.Color(0x333355) // Brighter background for debugging
    // Disable fog temporarily for debugging
    // this.scene.fog = new THREE.Fog(0x1a1a2e, 50, 200)

    // Initialize camera
    this.camera = new THREE.PerspectiveCamera(
      75,
      container.clientWidth / container.clientHeight,
      0.1,
      1000
    )
    this.camera.position.set(0, 1.7, 0) // Eye height

    // Initialize renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true })
    this.renderer.setSize(container.clientWidth, container.clientHeight)
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    this.renderer.shadowMap.enabled = true
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap
    this.renderer.outputColorSpace = THREE.SRGBColorSpace
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping
    this.renderer.toneMappingExposure = 1.0

    // Initialize lighting
    this.ambientLight = new THREE.AmbientLight(0x404040, 0.5)
    this.directionalLight = new THREE.DirectionalLight(0xffffff, 1)
    this.hemisphereLight = new THREE.HemisphereLight(0x87ceeb, 0x362d26, 0.3)

    // Initialize raycaster
    this.raycaster = new THREE.Raycaster()
  }


  /**
   * Initialize the scene manager
   */
  async init(): Promise<void> {
    // Append renderer to container
    this.container.appendChild(this.renderer.domElement)

    // Setup lighting
    this.setupLighting()

    // Setup default scene
    this.setupDefaultScene()

    // Handle window resize - store bound reference for cleanup
    this.boundHandleResize = this.handleResize.bind(this)
    window.addEventListener('resize', this.boundHandleResize)

    this.emit(SceneEvent.SCENE_LOADED, { preset: this.currentPreset })
  }

  /**
   * Setup scene lighting
   */
  private setupLighting(): void {
    console.log('[SceneManager] 设置光照...')
    
    // Add ambient light - increase intensity for better visibility
    this.ambientLight.intensity = 0.8
    this.scene.add(this.ambientLight)

    // Configure directional light (sun)
    this.directionalLight.position.set(50, 100, 50)
    this.directionalLight.intensity = 1.5 // Increase for better visibility
    this.directionalLight.castShadow = true
    this.directionalLight.shadow.mapSize.width = 2048
    this.directionalLight.shadow.mapSize.height = 2048
    this.directionalLight.shadow.camera.near = 0.5
    this.directionalLight.shadow.camera.far = 500
    this.directionalLight.shadow.camera.left = -100
    this.directionalLight.shadow.camera.right = 100
    this.directionalLight.shadow.camera.top = 100
    this.directionalLight.shadow.camera.bottom = -100
    this.directionalLight.shadow.bias = -0.0001
    this.scene.add(this.directionalLight)

    // Add hemisphere light - increase intensity
    this.hemisphereLight.intensity = 0.5
    this.scene.add(this.hemisphereLight)

    // Apply default preset
    this.applyLightingPreset('exterior')
    console.log('[SceneManager] 光照设置完成')
  }

  /**
   * Setup default scene with ground plane and city
   */
  private setupDefaultScene(): void {
    console.log('[SceneManager] 开始构建默认场景...')
    
    // Ground plane - use brighter color for visibility
    const groundGeometry = new THREE.PlaneGeometry(200, 200)
    const groundMaterial = new THREE.MeshStandardMaterial({
      color: 0x555555,
      roughness: 0.9,
      metalness: 0.1,
    })
    const ground = new THREE.Mesh(groundGeometry, groundMaterial)
    ground.rotation.x = -Math.PI / 2
    ground.receiveShadow = true
    ground.name = 'ground'
    this.scene.add(ground)
    this.gameObjects.set('ground', ground)
    console.log('[SceneManager] 地面已添加')

    // Add a test cube in front of the camera to verify rendering works
    // Using MeshBasicMaterial which doesn't need lighting
    const testCubeGeometry = new THREE.BoxGeometry(2, 2, 2)
    const testCubeMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 })
    const testCube = new THREE.Mesh(testCubeGeometry, testCubeMaterial)
    testCube.position.set(0, 1.7, -5) // Same height as camera, 5 units in front
    testCube.name = 'test_cube'
    this.scene.add(testCube)
    console.log('[SceneManager] 测试立方体已添加在位置:', testCube.position)

    // Build the apocalyptic city scene
    this.citySceneBuilder = new CitySceneBuilder(this.scene)
    this.citySceneBuilder.build()
    console.log('[SceneManager] 城市场景已构建，场景对象数量:', this.scene.children.length)
    
    // Debug: Log camera position
    console.log('[SceneManager] 相机位置:', this.camera.position)
    console.log('[SceneManager] 相机朝向:', this.camera.rotation)
  }

  /**
   * Load a specific scene by name
   */
  async loadScene(sceneName: string): Promise<void> {
    // Clear existing scene objects (except lights)
    this.clearScene()

    switch (sceneName) {
      case 'city':
      default:
        this.setupDefaultScene()
        break
    }

    this.emit(SceneEvent.SCENE_LOADED, { scene: sceneName })
  }

  /**
   * Clear all scene objects except lights
   */
  private clearScene(): void {
    // Dispose city scene builder if exists
    if (this.citySceneBuilder) {
      this.citySceneBuilder.dispose()
      this.citySceneBuilder = null
    }

    // Remove all objects except lights
    const objectsToRemove: THREE.Object3D[] = []
    this.scene.traverse((object) => {
      if (!(object instanceof THREE.Light) && object !== this.scene) {
        objectsToRemove.push(object)
      }
    })

    objectsToRemove.forEach((obj) => {
      if (obj.parent === this.scene) {
        this.scene.remove(obj)
      }
    })

    this.gameObjects.clear()
  }

  /**
   * Get zombie spawn points from city scene
   */
  getZombieSpawnPoints(): THREE.Vector3[] {
    if (this.citySceneBuilder) {
      return this.citySceneBuilder.getZombieSpawnPoints()
    }
    // Default spawn points if no city scene
    return [
      new THREE.Vector3(50, 0, 0),
      new THREE.Vector3(-50, 0, 0),
      new THREE.Vector3(0, 0, 50),
      new THREE.Vector3(0, 0, -50),
    ]
  }

  /**
   * Get collision meshes for physics
   */
  getCollisionMeshes(): THREE.Mesh[] {
    if (this.citySceneBuilder) {
      return this.citySceneBuilder.getCollisionMeshes()
    }
    return []
  }

  /**
   * Apply a lighting preset
   */
  applyLightingPreset(presetName: string): void {
    const preset = LightingPresets[presetName]
    if (!preset) {
      console.warn(`Lighting preset "${presetName}" not found`)
      return
    }

    this.currentPreset = presetName

    // Apply ambient light settings
    this.ambientLight.color.setHex(preset.ambientColor)
    this.ambientLight.intensity = preset.ambientIntensity

    // Apply directional light settings
    this.directionalLight.color.setHex(preset.directionalColor)
    this.directionalLight.intensity = preset.directionalIntensity
    this.directionalLight.position.copy(preset.directionalPosition)

    // Apply hemisphere light settings
    this.hemisphereLight.color.setHex(preset.hemisphereTopColor)
    this.hemisphereLight.groundColor.setHex(preset.hemisphereBottomColor)
    this.hemisphereLight.intensity = preset.hemisphereIntensity

    // Update fog color based on preset
    if (presetName === 'night') {
      this.scene.fog = new THREE.Fog(0x0a0a20, 30, 150)
      this.scene.background = new THREE.Color(0x0a0a20)
    } else if (presetName === 'interior') {
      this.scene.fog = new THREE.Fog(0x222222, 20, 100)
      this.scene.background = new THREE.Color(0x222222)
    } else {
      this.scene.fog = new THREE.Fog(0x1a1a2e, 50, 200)
      this.scene.background = new THREE.Color(0x1a1a2e)
    }

    this.emit(SceneEvent.LIGHTING_CHANGED, { preset: presetName })
  }

  /**
   * Update lighting based on player position (interior/exterior detection)
   */
  updateLighting(playerPosition: THREE.Vector3): void {
    // Simple interior detection - check if player is inside a building
    // This can be expanded with actual building bounds checking
    const isInterior = this.checkIfInterior(playerPosition)
    
    const targetPreset = isInterior ? 'interior' : 'exterior'
    if (targetPreset !== this.currentPreset) {
      this.applyLightingPreset(targetPreset)
    }
  }

  /**
   * Check if position is inside a building
   */
  private checkIfInterior(position: THREE.Vector3): boolean {
    // Cast ray upward to check for ceiling
    this.raycaster.set(position, new THREE.Vector3(0, 1, 0))
    const intersects = this.raycaster.intersectObjects(this.scene.children, true)
    
    // If there's something above within 10 units, consider it interior
    return intersects.some(hit => hit.distance < 10 && hit.object.name.includes('ceiling'))
  }

  // ==================== Object Management ====================

  /**
   * Add an object to the scene
   */
  addObject(object: THREE.Object3D, id?: string): void {
    this.scene.add(object)
    
    if (id) {
      this.gameObjects.set(id, object)
    }
    
    this.emit(SceneEvent.OBJECT_ADDED, { object, id })
  }

  /**
   * Remove an object from the scene
   */
  removeObject(object: THREE.Object3D): void {
    this.scene.remove(object)
    
    // Remove from tracking map
    for (const [id, obj] of this.gameObjects) {
      if (obj === object) {
        this.gameObjects.delete(id)
        break
      }
    }
    
    this.emit(SceneEvent.OBJECT_REMOVED, { object })
  }

  /**
   * Remove an object by ID
   */
  removeObjectById(id: string): void {
    const object = this.gameObjects.get(id)
    if (object) {
      this.scene.remove(object)
      this.gameObjects.delete(id)
      this.emit(SceneEvent.OBJECT_REMOVED, { object, id })
    }
  }

  /**
   * Get an object by ID
   */
  getObjectById(id: string): THREE.Object3D | undefined {
    return this.gameObjects.get(id)
  }

  // ==================== Collision Detection ====================

  /**
   * Check for collisions using raycaster
   */
  checkCollision(origin: THREE.Vector3, direction: THREE.Vector3, maxDistance: number = Infinity): THREE.Intersection[] {
    this.raycaster.set(origin, direction.normalize())
    this.raycaster.far = maxDistance
    return this.raycaster.intersectObjects(this.scene.children, true)
  }

  /**
   * Check collision from camera center (for shooting)
   */
  checkCameraCollision(maxDistance: number = Infinity): THREE.Intersection[] {
    this.raycaster.setFromCamera(new THREE.Vector2(0, 0), this.camera)
    this.raycaster.far = maxDistance
    return this.raycaster.intersectObjects(this.scene.children, true)
  }

  // ==================== Rendering ====================

  /**
   * Render the scene
   */
  render(): void {
    // Debug: Log render call occasionally
    if (Math.random() < 0.01) {
      console.log('[SceneManager] 渲染中... 场景对象:', this.scene.children.length, '相机位置:', this.camera.position)
    }
    this.renderer.render(this.scene, this.camera)
  }

  /**
   * Handle window resize
   */
  private handleResize(): void {
    const width = this.container.clientWidth
    const height = this.container.clientHeight

    this.camera.aspect = width / height
    this.camera.updateProjectionMatrix()
    this.renderer.setSize(width, height)
  }

  // ==================== Cleanup ====================

  /**
   * Dispose of all resources
   */
  dispose(): void {
    // Remove resize listener with bound reference
    if (this.boundHandleResize) {
      window.removeEventListener('resize', this.boundHandleResize)
    }

    // Dispose city scene builder
    if (this.citySceneBuilder) {
      this.citySceneBuilder.dispose()
      this.citySceneBuilder = null
    }

    // Dispose of all objects with proper cleanup
    const objectsToDispose: THREE.Object3D[] = []
    this.scene.traverse((object: THREE.Object3D) => {
      objectsToDispose.push(object)
    })
    
    for (const object of objectsToDispose) {
      if (object instanceof THREE.Mesh) {
        if (object.geometry) {
          object.geometry.dispose()
        }
        if (object.material) {
          if (Array.isArray(object.material)) {
            object.material.forEach((material: THREE.Material) => {
              this.disposeMaterial(material)
            })
          } else {
            this.disposeMaterial(object.material)
          }
        }
      }
    }

    // Clear scene
    while (this.scene.children.length > 0) {
      this.scene.remove(this.scene.children[0])
    }

    // Dispose renderer
    this.renderer.dispose()
    this.renderer.forceContextLoss()

    // Remove canvas from DOM
    if (this.renderer.domElement.parentNode) {
      this.renderer.domElement.parentNode.removeChild(this.renderer.domElement)
    }

    this.gameObjects.clear()
    this.eventListeners.clear()
  }

  /**
   * Dispose a material and its textures
   */
  private disposeMaterial(material: THREE.Material): void {
    material.dispose()
    
    // Dispose textures if present
    const mat = material as THREE.MeshStandardMaterial
    if (mat.map) mat.map.dispose()
    if (mat.normalMap) mat.normalMap.dispose()
    if (mat.roughnessMap) mat.roughnessMap.dispose()
    if (mat.metalnessMap) mat.metalnessMap.dispose()
    if (mat.aoMap) mat.aoMap.dispose()
    if (mat.emissiveMap) mat.emissiveMap.dispose()
  }

  // ==================== Getters ====================

  getScene(): THREE.Scene {
    return this.scene
  }

  getCamera(): THREE.PerspectiveCamera {
    return this.camera
  }

  getRenderer(): THREE.WebGLRenderer {
    return this.renderer
  }

  getCurrentPreset(): string {
    return this.currentPreset
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
}
