import * as THREE from 'three'
import { ZombieVariant, ZombieStateType } from '../types'

/**
 * Animation state for zombies
 */
export enum ZombieAnimation {
  IDLE = 'idle',
  WALK = 'walk',
  RUN = 'run',
  ATTACK = 'attack',
  HIT = 'hit',
  DEATH = 'death',
}

/**
 * Zombie visual configuration per variant
 */
interface ZombieVisualConfig {
  bodyColor: number
  skinColor: number
  eyeColor: number
  height: number
  width: number
  walkSpeed: number  // Animation speed multiplier
}

/**
 * Visual configs by variant
 */
const ZOMBIE_VISUAL_CONFIGS: Record<ZombieVariant, ZombieVisualConfig> = {
  [ZombieVariant.WALKER]: {
    bodyColor: 0x4a7c4e,
    skinColor: 0x8b7355,
    eyeColor: 0xff0000,
    height: 1.8,
    width: 0.5,
    walkSpeed: 1.0,
  },
  [ZombieVariant.RUNNER]: {
    bodyColor: 0x7c4a4a,
    skinColor: 0x9b8365,
    eyeColor: 0xff3300,
    height: 1.7,
    width: 0.4,
    walkSpeed: 2.0,
  },
  [ZombieVariant.BRUTE]: {
    bodyColor: 0x4a4a7c,
    skinColor: 0x7b6345,
    eyeColor: 0xff0066,
    height: 2.2,
    width: 0.8,
    walkSpeed: 0.7,
  },
  [ZombieVariant.CRAWLER]: {
    bodyColor: 0x7c7c4a,
    skinColor: 0x6b5335,
    eyeColor: 0xffff00,
    height: 0.8,
    width: 0.6,
    walkSpeed: 1.5,
  },
}


/**
 * ZombieVisuals - Handles zombie 3D models and animations
 * Requirements: 3.1
 */
export class ZombieVisuals {
  private mesh: THREE.Group
  private _variant: ZombieVariant
  private config: ZombieVisualConfig
  
  // Animation state
  private currentAnimation: ZombieAnimation = ZombieAnimation.IDLE
  private animationTime: number = 0
  private animationSpeed: number = 1.0
  
  // Body parts for animation
  private body: THREE.Mesh | null = null
  private head: THREE.Mesh | null = null
  private leftArm: THREE.Group | null = null
  private rightArm: THREE.Group | null = null
  private leftLeg: THREE.Group | null = null
  private rightLeg: THREE.Group | null = null
  
  // Death animation state
  private deathProgress: number = 0
  private isDeathComplete: boolean = false

  constructor(variant: ZombieVariant) {
    this._variant = variant
    this.config = ZOMBIE_VISUAL_CONFIGS[variant]
    this.mesh = this.createZombieMesh()
  }

  /**
   * Get the zombie variant
   */
  get variant(): ZombieVariant {
    return this._variant
  }

  /**
   * Create the zombie 3D mesh with articulated parts
   */
  private createZombieMesh(): THREE.Group {
    const group = new THREE.Group()
    const { bodyColor, skinColor, eyeColor, height, width } = this.config
    
    // Materials
    const bodyMaterial = new THREE.MeshStandardMaterial({ 
      color: bodyColor, 
      roughness: 0.8,
      metalness: 0.1,
    })
    const skinMaterial = new THREE.MeshStandardMaterial({ 
      color: skinColor, 
      roughness: 0.7,
      metalness: 0.0,
    })
    const eyeMaterial = new THREE.MeshBasicMaterial({ 
      color: eyeColor,
    })
    
    // Torso
    const torsoHeight = height * 0.35
    const torsoGeometry = new THREE.CylinderGeometry(width * 0.45, width * 0.5, torsoHeight, 8)
    this.body = new THREE.Mesh(torsoGeometry, bodyMaterial)
    this.body.position.y = height * 0.5
    this.body.castShadow = true
    this.body.receiveShadow = true
    group.add(this.body)
    
    // Head
    const headRadius = width * 0.35
    const headGeometry = new THREE.SphereGeometry(headRadius, 12, 12)
    this.head = new THREE.Mesh(headGeometry, skinMaterial)
    this.head.position.y = height * 0.75
    this.head.castShadow = true
    group.add(this.head)
    
    // Eyes
    const eyeGeometry = new THREE.SphereGeometry(0.04, 6, 6)
    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
    leftEye.position.set(-0.07, height * 0.78, headRadius * 0.8)
    group.add(leftEye)
    
    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
    rightEye.position.set(0.07, height * 0.78, headRadius * 0.8)
    group.add(rightEye)
    
    // Arms
    this.leftArm = this.createArm(skinMaterial, height, width)
    this.leftArm.position.set(-width * 0.55, height * 0.6, 0)
    group.add(this.leftArm)
    
    this.rightArm = this.createArm(skinMaterial, height, width)
    this.rightArm.position.set(width * 0.55, height * 0.6, 0)
    group.add(this.rightArm)
    
    // Legs
    this.leftLeg = this.createLeg(bodyMaterial, height, width)
    this.leftLeg.position.set(-width * 0.2, height * 0.25, 0)
    group.add(this.leftLeg)
    
    this.rightLeg = this.createLeg(bodyMaterial, height, width)
    this.rightLeg.position.set(width * 0.2, height * 0.25, 0)
    group.add(this.rightLeg)
    
    return group
  }

  /**
   * Create an arm group
   */
  private createArm(material: THREE.Material, height: number, width: number): THREE.Group {
    const arm = new THREE.Group()
    
    const armLength = height * 0.25
    const armGeometry = new THREE.CylinderGeometry(width * 0.1, width * 0.08, armLength, 6)
    const armMesh = new THREE.Mesh(armGeometry, material)
    armMesh.position.y = -armLength / 2
    armMesh.castShadow = true
    arm.add(armMesh)
    
    // Hand
    const handGeometry = new THREE.SphereGeometry(width * 0.1, 6, 6)
    const hand = new THREE.Mesh(handGeometry, material)
    hand.position.y = -armLength
    hand.castShadow = true
    arm.add(hand)
    
    return arm
  }

  /**
   * Create a leg group
   */
  private createLeg(material: THREE.Material, height: number, width: number): THREE.Group {
    const leg = new THREE.Group()
    
    const legLength = height * 0.3
    const legGeometry = new THREE.CylinderGeometry(width * 0.12, width * 0.1, legLength, 6)
    const legMesh = new THREE.Mesh(legGeometry, material)
    legMesh.position.y = -legLength / 2
    legMesh.castShadow = true
    leg.add(legMesh)
    
    // Foot
    const footGeometry = new THREE.BoxGeometry(width * 0.15, width * 0.08, width * 0.25)
    const foot = new THREE.Mesh(footGeometry, material)
    foot.position.set(0, -legLength, width * 0.05)
    foot.castShadow = true
    leg.add(foot)
    
    return leg
  }


  /**
   * Update animation based on zombie state
   */
  update(deltaTime: number, state: ZombieStateType, speed: number): void {
    this.animationTime += deltaTime * this.config.walkSpeed * this.animationSpeed
    
    // Determine animation from state
    const newAnimation = this.getAnimationForState(state, speed)
    if (newAnimation !== this.currentAnimation) {
      this.currentAnimation = newAnimation
      this.animationTime = 0
    }
    
    // Apply animation
    switch (this.currentAnimation) {
      case ZombieAnimation.IDLE:
        this.animateIdle()
        break
      case ZombieAnimation.WALK:
        this.animateWalk()
        break
      case ZombieAnimation.RUN:
        this.animateRun()
        break
      case ZombieAnimation.ATTACK:
        this.animateAttack()
        break
      case ZombieAnimation.DEATH:
        this.animateDeath(deltaTime)
        break
    }
  }

  /**
   * Get animation type from zombie state
   */
  private getAnimationForState(state: ZombieStateType, speed: number): ZombieAnimation {
    switch (state) {
      case ZombieStateType.IDLE:
        return ZombieAnimation.IDLE
      case ZombieStateType.WANDERING:
        return ZombieAnimation.WALK
      case ZombieStateType.CHASING:
        return speed > 3 ? ZombieAnimation.RUN : ZombieAnimation.WALK
      case ZombieStateType.ATTACKING:
        return ZombieAnimation.ATTACK
      case ZombieStateType.DYING:
        return ZombieAnimation.DEATH
      default:
        return ZombieAnimation.IDLE
    }
  }

  /**
   * Idle animation - subtle breathing/swaying
   */
  private animateIdle(): void {
    const sway = Math.sin(this.animationTime * 2) * 0.02
    
    if (this.body) {
      this.body.rotation.z = sway
    }
    if (this.head) {
      this.head.rotation.z = sway * 0.5
      this.head.rotation.y = Math.sin(this.animationTime * 0.5) * 0.1
    }
    
    // Reset limbs
    this.resetLimbs()
  }

  /**
   * Walking animation
   */
  private animateWalk(): void {
    const walkCycle = this.animationTime * 4
    const armSwing = Math.sin(walkCycle) * 0.5
    const legSwing = Math.sin(walkCycle) * 0.4
    
    // Arms swing opposite to legs
    if (this.leftArm) {
      this.leftArm.rotation.x = armSwing
      this.leftArm.rotation.z = 0.3 // Zombie arms forward
    }
    if (this.rightArm) {
      this.rightArm.rotation.x = -armSwing
      this.rightArm.rotation.z = -0.3
    }
    
    // Legs
    if (this.leftLeg) {
      this.leftLeg.rotation.x = legSwing
    }
    if (this.rightLeg) {
      this.rightLeg.rotation.x = -legSwing
    }
    
    // Body bob
    if (this.body) {
      this.body.position.y = this.config.height * 0.5 + Math.abs(Math.sin(walkCycle * 2)) * 0.02
    }
    
    // Head sway
    if (this.head) {
      this.head.rotation.z = Math.sin(walkCycle) * 0.05
    }
  }

  /**
   * Running animation - faster and more exaggerated
   */
  private animateRun(): void {
    const runCycle = this.animationTime * 8
    const armSwing = Math.sin(runCycle) * 0.8
    const legSwing = Math.sin(runCycle) * 0.6
    
    if (this.leftArm) {
      this.leftArm.rotation.x = armSwing
      this.leftArm.rotation.z = 0.4
    }
    if (this.rightArm) {
      this.rightArm.rotation.x = -armSwing
      this.rightArm.rotation.z = -0.4
    }
    
    if (this.leftLeg) {
      this.leftLeg.rotation.x = legSwing
    }
    if (this.rightLeg) {
      this.rightLeg.rotation.x = -legSwing
    }
    
    // More pronounced body movement
    if (this.body) {
      this.body.position.y = this.config.height * 0.5 + Math.abs(Math.sin(runCycle * 2)) * 0.04
      this.body.rotation.x = 0.1 // Lean forward
    }
  }

  /**
   * Attack animation
   */
  private animateAttack(): void {
    const attackPhase = (this.animationTime % 1.5) / 1.5 // 1.5 second attack cycle
    
    if (attackPhase < 0.3) {
      // Wind up
      const windUp = attackPhase / 0.3
      if (this.leftArm) this.leftArm.rotation.x = -windUp * 1.5
      if (this.rightArm) this.rightArm.rotation.x = -windUp * 1.5
    } else if (attackPhase < 0.5) {
      // Strike
      const strike = (attackPhase - 0.3) / 0.2
      if (this.leftArm) this.leftArm.rotation.x = -1.5 + strike * 2.5
      if (this.rightArm) this.rightArm.rotation.x = -1.5 + strike * 2.5
    } else {
      // Recovery
      const recovery = (attackPhase - 0.5) / 0.5
      if (this.leftArm) this.leftArm.rotation.x = 1.0 - recovery * 1.0
      if (this.rightArm) this.rightArm.rotation.x = 1.0 - recovery * 1.0
    }
    
    // Body lunge
    if (this.body && attackPhase < 0.5) {
      this.body.rotation.x = Math.sin(attackPhase * Math.PI * 2) * 0.2
    }
  }

  /**
   * Death animation
   */
  private animateDeath(deltaTime: number): void {
    if (this.isDeathComplete) return
    
    this.deathProgress += deltaTime * 0.5 // 2 seconds to fall
    
    if (this.deathProgress >= 1) {
      this.deathProgress = 1
      this.isDeathComplete = true
    }
    
    // Fall backwards
    this.mesh.rotation.x = this.deathProgress * (Math.PI / 2)
    
    // Sink into ground slightly
    this.mesh.position.y = -this.deathProgress * 0.3
    
    // Arms flail
    if (this.leftArm) {
      this.leftArm.rotation.x = -this.deathProgress * 1.5
      this.leftArm.rotation.z = this.deathProgress * 0.5
    }
    if (this.rightArm) {
      this.rightArm.rotation.x = -this.deathProgress * 1.5
      this.rightArm.rotation.z = -this.deathProgress * 0.5
    }
  }

  /**
   * Reset limbs to default position
   */
  private resetLimbs(): void {
    if (this.leftArm) {
      this.leftArm.rotation.x = 0.3
      this.leftArm.rotation.z = 0.2
    }
    if (this.rightArm) {
      this.rightArm.rotation.x = 0.3
      this.rightArm.rotation.z = -0.2
    }
    if (this.leftLeg) {
      this.leftLeg.rotation.x = 0
    }
    if (this.rightLeg) {
      this.rightLeg.rotation.x = 0
    }
  }

  /**
   * Play hit reaction
   */
  playHitReaction(): void {
    // Flash red briefly
    if (this.body) {
      const material = this.body.material as THREE.MeshStandardMaterial
      const originalColor = material.color.getHex()
      material.color.setHex(0xff0000)
      
      setTimeout(() => {
        material.color.setHex(originalColor)
      }, 100)
    }
  }

  /**
   * Get the mesh group
   */
  getMesh(): THREE.Group {
    return this.mesh
  }

  /**
   * Check if death animation is complete
   */
  isDeathAnimationComplete(): boolean {
    return this.isDeathComplete
  }

  /**
   * Set animation speed multiplier
   */
  setAnimationSpeed(speed: number): void {
    this.animationSpeed = speed
  }

  /**
   * Cleanup resources
   */
  dispose(): void {
    this.mesh.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.geometry.dispose()
        if (Array.isArray(child.material)) {
          child.material.forEach((m) => m.dispose())
        } else {
          child.material.dispose()
        }
      }
    })
  }
}
