import * as THREE from 'three'

/**
 * Building configuration for procedural generation
 */
export interface BuildingConfig {
  width: number
  depth: number
  height: number
  floors: number
  hasWindows: boolean
  isDamaged: boolean
  position: THREE.Vector3
}

/**
 * Street configuration
 */
export interface StreetConfig {
  width: number
  length: number
  position: THREE.Vector3
  rotation: number
}

/**
 * Obstacle types for the scene
 */
export enum ObstacleType {
  CAR = 'car',
  BARRIER = 'barrier',
  DEBRIS = 'debris',
  DUMPSTER = 'dumpster',
  CRATE = 'crate',
}

/**
 * CitySceneBuilder - Creates procedural apocalyptic city environment
 * Requirements: 5.1, 5.2
 */
export class CitySceneBuilder {
  private scene: THREE.Scene
  private buildings: THREE.Group
  private streets: THREE.Group
  private obstacles: THREE.Group
  private decorations: THREE.Group

  // Materials cache for reuse
  private materials: Map<string, THREE.Material> = new Map()

  // Collision meshes for physics
  private collisionMeshes: THREE.Mesh[] = []

  constructor(scene: THREE.Scene) {
    this.scene = scene
    this.buildings = new THREE.Group()
    this.buildings.name = 'buildings'
    this.streets = new THREE.Group()
    this.streets.name = 'streets'
    this.obstacles = new THREE.Group()
    this.obstacles.name = 'obstacles'
    this.decorations = new THREE.Group()
    this.decorations.name = 'decorations'

    this.initMaterials()
  }

  /**
   * Initialize reusable materials
   */
  private initMaterials(): void {
    // Building materials
    this.materials.set('building_concrete', new THREE.MeshStandardMaterial({
      color: 0x555555,
      roughness: 0.9,
      metalness: 0.1,
    }))

    this.materials.set('building_brick', new THREE.MeshStandardMaterial({
      color: 0x8b4513,
      roughness: 0.85,
      metalness: 0.05,
    }))

    this.materials.set('building_damaged', new THREE.MeshStandardMaterial({
      color: 0x3a3a3a,
      roughness: 0.95,
      metalness: 0.05,
    }))

    // Window material (emissive for some lit windows)
    this.materials.set('window_dark', new THREE.MeshStandardMaterial({
      color: 0x111122,
      roughness: 0.1,
      metalness: 0.8,
    }))

    this.materials.set('window_lit', new THREE.MeshStandardMaterial({
      color: 0xffcc66,
      emissive: 0xffcc66,
      emissiveIntensity: 0.3,
      roughness: 0.1,
      metalness: 0.5,
    }))

    // Street materials
    this.materials.set('asphalt', new THREE.MeshStandardMaterial({
      color: 0x222222,
      roughness: 0.95,
      metalness: 0.0,
    }))

    this.materials.set('sidewalk', new THREE.MeshStandardMaterial({
      color: 0x666666,
      roughness: 0.9,
      metalness: 0.0,
    }))

    // Obstacle materials
    this.materials.set('metal_rusty', new THREE.MeshStandardMaterial({
      color: 0x8b4513,
      roughness: 0.8,
      metalness: 0.6,
    }))

    this.materials.set('car_body', new THREE.MeshStandardMaterial({
      color: 0x333344,
      roughness: 0.4,
      metalness: 0.7,
    }))

    this.materials.set('wood', new THREE.MeshStandardMaterial({
      color: 0x654321,
      roughness: 0.9,
      metalness: 0.0,
    }))
  }

  /**
   * Build the complete city scene
   */
  build(): void {
    this.createStreets()
    this.createBuildings()
    this.createObstacles()
    this.createDecorations()

    // Add all groups to scene
    this.scene.add(this.buildings)
    this.scene.add(this.streets)
    this.scene.add(this.obstacles)
    this.scene.add(this.decorations)
  }

  /**
   * Create street network
   */
  private createStreets(): void {
    const streetMaterial = this.materials.get('asphalt')!
    const sidewalkMaterial = this.materials.get('sidewalk')!

    // Main street (north-south)
    const mainStreet = this.createStreet(20, 200, streetMaterial)
    mainStreet.position.set(0, 0.01, 0)
    this.streets.add(mainStreet)

    // Cross streets (east-west)
    for (let z = -80; z <= 80; z += 40) {
      const crossStreet = this.createStreet(15, 100, streetMaterial)
      crossStreet.rotation.y = Math.PI / 2
      crossStreet.position.set(0, 0.01, z)
      this.streets.add(crossStreet)
    }

    // Sidewalks along main street
    const leftSidewalk = this.createSidewalk(4, 200, sidewalkMaterial)
    leftSidewalk.position.set(-12, 0.02, 0)
    this.streets.add(leftSidewalk)

    const rightSidewalk = this.createSidewalk(4, 200, sidewalkMaterial)
    rightSidewalk.position.set(12, 0.02, 0)
    this.streets.add(rightSidewalk)
  }

  /**
   * Create a street segment
   */
  private createStreet(width: number, length: number, material: THREE.Material): THREE.Mesh {
    const geometry = new THREE.PlaneGeometry(width, length)
    const mesh = new THREE.Mesh(geometry, material)
    mesh.rotation.x = -Math.PI / 2
    mesh.receiveShadow = true
    mesh.name = 'street'
    return mesh
  }

  /**
   * Create a sidewalk segment
   */
  private createSidewalk(width: number, length: number, material: THREE.Material): THREE.Mesh {
    const geometry = new THREE.BoxGeometry(width, 0.15, length)
    const mesh = new THREE.Mesh(geometry, material)
    mesh.receiveShadow = true
    mesh.castShadow = true
    mesh.name = 'sidewalk'
    return mesh
  }

  /**
   * Create buildings along the streets
   */
  private createBuildings(): void {
    // Building configurations for left side of main street
    const leftBuildings: BuildingConfig[] = [
      { width: 15, depth: 20, height: 25, floors: 5, hasWindows: true, isDamaged: false, position: new THREE.Vector3(-25, 0, -70) },
      { width: 20, depth: 25, height: 35, floors: 7, hasWindows: true, isDamaged: true, position: new THREE.Vector3(-30, 0, -35) },
      { width: 18, depth: 18, height: 20, floors: 4, hasWindows: true, isDamaged: false, position: new THREE.Vector3(-25, 0, 10) },
      { width: 22, depth: 22, height: 40, floors: 8, hasWindows: true, isDamaged: true, position: new THREE.Vector3(-28, 0, 50) },
      { width: 16, depth: 20, height: 30, floors: 6, hasWindows: true, isDamaged: false, position: new THREE.Vector3(-25, 0, 85) },
    ]

    // Building configurations for right side of main street
    const rightBuildings: BuildingConfig[] = [
      { width: 18, depth: 22, height: 30, floors: 6, hasWindows: true, isDamaged: true, position: new THREE.Vector3(25, 0, -75) },
      { width: 15, depth: 18, height: 22, floors: 4, hasWindows: true, isDamaged: false, position: new THREE.Vector3(22, 0, -40) },
      { width: 25, depth: 25, height: 45, floors: 9, hasWindows: true, isDamaged: false, position: new THREE.Vector3(30, 0, 5) },
      { width: 20, depth: 20, height: 28, floors: 5, hasWindows: true, isDamaged: true, position: new THREE.Vector3(25, 0, 45) },
      { width: 17, depth: 22, height: 32, floors: 6, hasWindows: true, isDamaged: false, position: new THREE.Vector3(24, 0, 80) },
    ]

    // Create all buildings
    const allBuildings = [...leftBuildings, ...rightBuildings]
    allBuildings.forEach((config, index) => {
      const building = this.createBuilding(config)
      building.name = `building_${index}`
      this.buildings.add(building)
    })
  }

  /**
   * Create a single building with windows
   */
  private createBuilding(config: BuildingConfig): THREE.Group {
    const building = new THREE.Group()
    const materialKey = config.isDamaged ? 'building_damaged' : 
      (Math.random() > 0.5 ? 'building_concrete' : 'building_brick')
    const material = this.materials.get(materialKey)!

    // Main building body
    const bodyGeometry = new THREE.BoxGeometry(config.width, config.height, config.depth)
    const body = new THREE.Mesh(bodyGeometry, material)
    body.position.y = config.height / 2
    body.castShadow = true
    body.receiveShadow = true
    body.name = 'building_body'
    building.add(body)

    // Add collision mesh
    this.collisionMeshes.push(body)

    // Add windows if enabled
    if (config.hasWindows) {
      this.addWindowsToBuilding(building, config)
    }

    // Add damage effects if damaged
    if (config.isDamaged) {
      this.addDamageEffects(building, config)
    }

    // Add roof details
    this.addRoofDetails(building, config)

    building.position.copy(config.position)
    return building
  }

  /**
   * Add windows to a building
   */
  private addWindowsToBuilding(building: THREE.Group, config: BuildingConfig): void {
    const windowWidth = 1.5
    const windowHeight = 2
    const windowDepth = 0.1
    const floorHeight = config.height / config.floors

    const windowGeometry = new THREE.BoxGeometry(windowWidth, windowHeight, windowDepth)

    // Add windows to front and back faces
    for (let floor = 0; floor < config.floors; floor++) {
      const windowsPerFloor = Math.floor(config.width / 4)
      const startX = -(windowsPerFloor - 1) * 2

      for (let w = 0; w < windowsPerFloor; w++) {
        const isLit = Math.random() > 0.7
        const material = this.materials.get(isLit ? 'window_lit' : 'window_dark')!

        // Front window
        const frontWindow = new THREE.Mesh(windowGeometry, material)
        frontWindow.position.set(
          startX + w * 4,
          floorHeight * (floor + 0.5),
          config.depth / 2 + 0.05
        )
        building.add(frontWindow)

        // Back window
        const backWindow = new THREE.Mesh(windowGeometry, material)
        backWindow.position.set(
          startX + w * 4,
          floorHeight * (floor + 0.5),
          -config.depth / 2 - 0.05
        )
        building.add(backWindow)
      }
    }
  }

  /**
   * Add damage effects to building (holes, debris)
   */
  private addDamageEffects(building: THREE.Group, config: BuildingConfig): void {
    // Add some "damage holes" using dark boxes
    const holeMaterial = new THREE.MeshBasicMaterial({ color: 0x000000 })
    const numHoles = Math.floor(Math.random() * 3) + 1

    for (let i = 0; i < numHoles; i++) {
      const holeWidth = 2 + Math.random() * 3
      const holeHeight = 2 + Math.random() * 4
      const holeGeometry = new THREE.BoxGeometry(holeWidth, holeHeight, 0.5)
      const hole = new THREE.Mesh(holeGeometry, holeMaterial)

      const side = Math.random() > 0.5 ? 1 : -1
      hole.position.set(
        (Math.random() - 0.5) * config.width * 0.6,
        Math.random() * config.height * 0.7 + config.height * 0.2,
        side * (config.depth / 2 + 0.1)
      )
      building.add(hole)
    }
  }

  /**
   * Add roof details (AC units, water tanks, etc.)
   */
  private addRoofDetails(building: THREE.Group, config: BuildingConfig): void {
    const metalMaterial = this.materials.get('metal_rusty')!

    // AC unit
    if (Math.random() > 0.3) {
      const acGeometry = new THREE.BoxGeometry(3, 1.5, 2)
      const ac = new THREE.Mesh(acGeometry, metalMaterial)
      ac.position.set(
        (Math.random() - 0.5) * config.width * 0.5,
        config.height + 0.75,
        (Math.random() - 0.5) * config.depth * 0.5
      )
      ac.castShadow = true
      building.add(ac)
    }

    // Water tank
    if (Math.random() > 0.5) {
      const tankGeometry = new THREE.CylinderGeometry(1.5, 1.5, 3, 8)
      const tank = new THREE.Mesh(tankGeometry, metalMaterial)
      tank.position.set(
        (Math.random() - 0.5) * config.width * 0.4,
        config.height + 1.5,
        (Math.random() - 0.5) * config.depth * 0.4
      )
      tank.castShadow = true
      building.add(tank)
    }
  }

  /**
   * Create obstacles (cars, barriers, debris)
   */
  private createObstacles(): void {
    // Abandoned cars
    const carPositions = [
      new THREE.Vector3(-5, 0, -50),
      new THREE.Vector3(6, 0, -20),
      new THREE.Vector3(-7, 0, 30),
      new THREE.Vector3(4, 0, 60),
      new THREE.Vector3(-3, 0, -80),
      new THREE.Vector3(8, 0, 90),
    ]

    carPositions.forEach((pos, index) => {
      const car = this.createCar()
      car.position.copy(pos)
      car.rotation.y = Math.random() * Math.PI * 2
      car.name = `car_${index}`
      this.obstacles.add(car)
    })

    // Barriers
    const barrierPositions = [
      new THREE.Vector3(-8, 0, 0),
      new THREE.Vector3(8, 0, 0),
      new THREE.Vector3(0, 0, -60),
    ]

    barrierPositions.forEach((pos, index) => {
      const barrier = this.createBarrier()
      barrier.position.copy(pos)
      barrier.name = `barrier_${index}`
      this.obstacles.add(barrier)
    })

    // Debris piles
    const debrisPositions = [
      new THREE.Vector3(-15, 0, -45),
      new THREE.Vector3(15, 0, 25),
      new THREE.Vector3(-12, 0, 70),
      new THREE.Vector3(18, 0, -70),
    ]

    debrisPositions.forEach((pos, index) => {
      const debris = this.createDebrisPile()
      debris.position.copy(pos)
      debris.name = `debris_${index}`
      this.obstacles.add(debris)
    })

    // Crates
    const cratePositions = [
      new THREE.Vector3(-14, 0, 15),
      new THREE.Vector3(16, 0, -30),
      new THREE.Vector3(-16, 0, 55),
    ]

    cratePositions.forEach((pos, index) => {
      const crateGroup = this.createCrateStack()
      crateGroup.position.copy(pos)
      crateGroup.name = `crates_${index}`
      this.obstacles.add(crateGroup)
    })
  }

  /**
   * Create an abandoned car
   */
  private createCar(): THREE.Group {
    const car = new THREE.Group()
    const bodyMaterial = this.materials.get('car_body')!
    const metalMaterial = this.materials.get('metal_rusty')!

    // Car body
    const bodyGeometry = new THREE.BoxGeometry(4, 1.2, 2)
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
    body.position.y = 0.8
    body.castShadow = true
    body.receiveShadow = true
    car.add(body)
    this.collisionMeshes.push(body)

    // Car roof/cabin
    const cabinGeometry = new THREE.BoxGeometry(2.5, 1, 1.8)
    const cabin = new THREE.Mesh(cabinGeometry, bodyMaterial)
    cabin.position.set(-0.3, 1.9, 0)
    cabin.castShadow = true
    car.add(cabin)

    // Wheels
    const wheelGeometry = new THREE.CylinderGeometry(0.4, 0.4, 0.3, 16)
    const wheelPositions = [
      new THREE.Vector3(1.2, 0.4, 1.1),
      new THREE.Vector3(1.2, 0.4, -1.1),
      new THREE.Vector3(-1.2, 0.4, 1.1),
      new THREE.Vector3(-1.2, 0.4, -1.1),
    ]

    wheelPositions.forEach(pos => {
      const wheel = new THREE.Mesh(wheelGeometry, metalMaterial)
      wheel.position.copy(pos)
      wheel.rotation.x = Math.PI / 2
      wheel.castShadow = true
      car.add(wheel)
    })

    return car
  }

  /**
   * Create a barrier
   */
  private createBarrier(): THREE.Group {
    const barrier = new THREE.Group()
    const metalMaterial = this.materials.get('metal_rusty')!

    // Main barrier body
    const bodyGeometry = new THREE.BoxGeometry(3, 1, 0.5)
    const body = new THREE.Mesh(bodyGeometry, metalMaterial)
    body.position.y = 0.5
    body.castShadow = true
    body.receiveShadow = true
    barrier.add(body)
    this.collisionMeshes.push(body)

    // Support legs
    const legGeometry = new THREE.BoxGeometry(0.2, 1, 0.8)
    const leftLeg = new THREE.Mesh(legGeometry, metalMaterial)
    leftLeg.position.set(-1.2, 0.5, 0)
    leftLeg.castShadow = true
    barrier.add(leftLeg)

    const rightLeg = new THREE.Mesh(legGeometry, metalMaterial)
    rightLeg.position.set(1.2, 0.5, 0)
    rightLeg.castShadow = true
    barrier.add(rightLeg)

    return barrier
  }

  /**
   * Create a debris pile
   */
  private createDebrisPile(): THREE.Group {
    const debris = new THREE.Group()
    const concreteMaterial = this.materials.get('building_damaged')!
    const metalMaterial = this.materials.get('metal_rusty')!

    // Random debris pieces
    const numPieces = 5 + Math.floor(Math.random() * 5)
    for (let i = 0; i < numPieces; i++) {
      const size = 0.3 + Math.random() * 1.5
      const geometry = new THREE.BoxGeometry(size, size * 0.5, size * 0.8)
      const material = Math.random() > 0.3 ? concreteMaterial : metalMaterial
      const piece = new THREE.Mesh(geometry, material)

      piece.position.set(
        (Math.random() - 0.5) * 4,
        size * 0.25,
        (Math.random() - 0.5) * 4
      )
      piece.rotation.set(
        Math.random() * 0.5,
        Math.random() * Math.PI,
        Math.random() * 0.5
      )
      piece.castShadow = true
      piece.receiveShadow = true
      debris.add(piece)
    }

    return debris
  }

  /**
   * Create a stack of crates
   */
  private createCrateStack(): THREE.Group {
    const stack = new THREE.Group()
    const woodMaterial = this.materials.get('wood')!

    const crateSize = 1.2
    const crateGeometry = new THREE.BoxGeometry(crateSize, crateSize, crateSize)

    // Bottom layer (2-3 crates)
    const bottomCount = 2 + Math.floor(Math.random() * 2)
    for (let i = 0; i < bottomCount; i++) {
      const crate = new THREE.Mesh(crateGeometry, woodMaterial)
      crate.position.set(i * crateSize * 1.1 - (bottomCount - 1) * crateSize * 0.55, crateSize / 2, 0)
      crate.castShadow = true
      crate.receiveShadow = true
      stack.add(crate)
      this.collisionMeshes.push(crate)
    }

    // Top layer (1-2 crates)
    if (Math.random() > 0.3) {
      const topCrate = new THREE.Mesh(crateGeometry, woodMaterial)
      topCrate.position.set(0, crateSize * 1.5, 0)
      topCrate.rotation.y = Math.random() * 0.3
      topCrate.castShadow = true
      topCrate.receiveShadow = true
      stack.add(topCrate)
    }

    return stack
  }

  /**
   * Create decorative elements (street lights, signs, etc.)
   */
  private createDecorations(): void {
    // Street lights along main street - reduced count to avoid exceeding texture units
    // Only add lights every 40 units instead of 20, and limit total
    let lightCount = 0
    const maxLights = 4 // Limit to avoid exceeding GPU texture units
    
    for (let z = -80; z <= 80 && lightCount < maxLights; z += 40) {
      // Alternate sides to spread lighting
      if (lightCount % 2 === 0) {
        const leftLight = this.createStreetLight()
        leftLight.position.set(-11, 0, z)
        this.decorations.add(leftLight)
      } else {
        const rightLight = this.createStreetLight()
        rightLight.position.set(11, 0, z)
        rightLight.rotation.y = Math.PI
        this.decorations.add(rightLight)
      }
      lightCount++
    }

    // Fire barrels for atmosphere - reduced to 1 to save texture units
    const barrelPositions = [
      new THREE.Vector3(-14, 0, -25),
    ]

    barrelPositions.forEach((pos, index) => {
      const barrel = this.createFireBarrel()
      barrel.position.copy(pos)
      barrel.name = `fire_barrel_${index}`
      this.decorations.add(barrel)
    })

    // Trash and litter
    this.addTrashDecoration()
  }

  /**
   * Create a street light
   */
  private createStreetLight(): THREE.Group {
    const light = new THREE.Group()
    const metalMaterial = this.materials.get('metal_rusty')!

    // Pole
    const poleGeometry = new THREE.CylinderGeometry(0.1, 0.15, 5, 8)
    const pole = new THREE.Mesh(poleGeometry, metalMaterial)
    pole.position.y = 2.5
    pole.castShadow = true
    light.add(pole)

    // Arm
    const armGeometry = new THREE.BoxGeometry(1.5, 0.1, 0.1)
    const arm = new THREE.Mesh(armGeometry, metalMaterial)
    arm.position.set(0.75, 5, 0)
    arm.castShadow = true
    light.add(arm)

    // Light fixture
    const fixtureGeometry = new THREE.BoxGeometry(0.4, 0.2, 0.3)
    const fixtureMaterial = new THREE.MeshStandardMaterial({
      color: 0x333333,
      roughness: 0.5,
      metalness: 0.8,
    })
    const fixture = new THREE.Mesh(fixtureGeometry, fixtureMaterial)
    fixture.position.set(1.5, 4.9, 0)
    light.add(fixture)

    // Add point light (dim, no shadow to reduce texture unit usage)
    const pointLight = new THREE.PointLight(0xffaa55, 0.5, 15)
    pointLight.position.set(1.5, 4.8, 0)
    pointLight.castShadow = false // Disabled to avoid exceeding MAX_TEXTURE_IMAGE_UNITS
    light.add(pointLight)

    return light
  }

  /**
   * Create a fire barrel
   */
  private createFireBarrel(): THREE.Group {
    const barrel = new THREE.Group()
    const metalMaterial = this.materials.get('metal_rusty')!

    // Barrel body
    const barrelGeometry = new THREE.CylinderGeometry(0.4, 0.35, 1, 12)
    const barrelMesh = new THREE.Mesh(barrelGeometry, metalMaterial)
    barrelMesh.position.y = 0.5
    barrelMesh.castShadow = true
    barrelMesh.receiveShadow = true
    barrel.add(barrelMesh)

    // Fire light
    const fireLight = new THREE.PointLight(0xff6600, 1, 8)
    fireLight.position.y = 1.2
    fireLight.castShadow = false
    barrel.add(fireLight)

    // Fire glow (simple emissive sphere)
    const glowGeometry = new THREE.SphereGeometry(0.3, 8, 8)
    const glowMaterial = new THREE.MeshBasicMaterial({
      color: 0xff4400,
      transparent: true,
      opacity: 0.6,
    })
    const glow = new THREE.Mesh(glowGeometry, glowMaterial)
    glow.position.y = 1
    barrel.add(glow)

    return barrel
  }

  /**
   * Add scattered trash decoration
   */
  private addTrashDecoration(): void {
    const trashMaterial = new THREE.MeshStandardMaterial({
      color: 0x444444,
      roughness: 0.9,
    })

    // Scatter small debris
    for (let i = 0; i < 50; i++) {
      const size = 0.1 + Math.random() * 0.3
      const geometry = new THREE.BoxGeometry(size, size * 0.3, size * 0.8)
      const trash = new THREE.Mesh(geometry, trashMaterial)

      trash.position.set(
        (Math.random() - 0.5) * 180,
        size * 0.15,
        (Math.random() - 0.5) * 180
      )
      trash.rotation.y = Math.random() * Math.PI * 2
      trash.receiveShadow = true
      this.decorations.add(trash)
    }
  }

  /**
   * Get all collision meshes for physics
   */
  getCollisionMeshes(): THREE.Mesh[] {
    return this.collisionMeshes
  }

  /**
   * Get spawn points for zombies (positions away from player start)
   */
  getZombieSpawnPoints(): THREE.Vector3[] {
    const spawnPoints: THREE.Vector3[] = []

    // Spawn points along the streets, away from center
    const distances = [40, 60, 80]
    const angles = [0, Math.PI / 4, Math.PI / 2, (3 * Math.PI) / 4, Math.PI, 
                   (5 * Math.PI) / 4, (3 * Math.PI) / 2, (7 * Math.PI) / 4]

    distances.forEach(dist => {
      angles.forEach(angle => {
        spawnPoints.push(new THREE.Vector3(
          Math.cos(angle) * dist,
          0,
          Math.sin(angle) * dist
        ))
      })
    })

    return spawnPoints
  }

  /**
   * Dispose of all resources
   */
  dispose(): void {
    // Dispose materials
    this.materials.forEach(material => material.dispose())
    this.materials.clear()

    // Dispose geometries in all groups
    const disposeGroup = (group: THREE.Group) => {
      group.traverse((object) => {
        if (object instanceof THREE.Mesh) {
          object.geometry.dispose()
        }
      })
    }

    disposeGroup(this.buildings)
    disposeGroup(this.streets)
    disposeGroup(this.obstacles)
    disposeGroup(this.decorations)

    // Clear collision meshes
    this.collisionMeshes = []
  }
}
