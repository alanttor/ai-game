import type { EventCallback } from './types'

/**
 * Input key codes for game controls
 */
export enum InputKey {
  // Movement
  FORWARD = 'KeyW',
  LEFT = 'KeyA',
  BACKWARD = 'KeyS',
  RIGHT = 'KeyD',
  JUMP = 'Space',
  SPRINT = 'ShiftLeft',
  
  // Weapons
  RELOAD = 'KeyR',
  WEAPON_1 = 'Digit1',
  WEAPON_2 = 'Digit2',
  WEAPON_3 = 'Digit3',
  WEAPON_4 = 'Digit4',
  
  // Game controls
  PAUSE = 'Escape',
  INVENTORY = 'Tab',
}

/**
 * Mouse button codes
 */
export enum MouseButton {
  LEFT = 0,
  MIDDLE = 1,
  RIGHT = 2,
}

/**
 * Input events emitted by InputManager
 */
export enum InputEvent {
  KEY_DOWN = 'input:keydown',
  KEY_UP = 'input:keyup',
  MOUSE_DOWN = 'input:mousedown',
  MOUSE_UP = 'input:mouseup',
  MOUSE_MOVE = 'input:mousemove',
  MOUSE_WHEEL = 'input:mousewheel',
  POINTER_LOCK_CHANGE = 'input:pointerlockchange',
}

/**
 * Mouse movement data
 */
export interface MouseMovement {
  movementX: number
  movementY: number
  clientX: number
  clientY: number
}

/**
 * Mouse wheel data
 */
export interface MouseWheelData {
  deltaY: number
  direction: 'up' | 'down'
}

/**
 * InputManager - Handles all keyboard and mouse input for the game
 * Requirements: 1.1, 1.2, 2.1, 2.3, 2.4
 */
export class InputManager {
  // Key states
  private keysPressed: Set<string> = new Set()
  private keysJustPressed: Set<string> = new Set()
  private keysJustReleased: Set<string> = new Set()
  
  // Mouse states
  private mouseButtonsPressed: Set<number> = new Set()
  private mouseButtonsJustPressed: Set<number> = new Set()
  private mouseButtonsJustReleased: Set<number> = new Set()
  private mouseMovement: MouseMovement = { movementX: 0, movementY: 0, clientX: 0, clientY: 0 }
  private mouseWheelDelta: number = 0
  
  // Pointer lock state
  private isPointerLocked: boolean = false
  private targetElement: HTMLElement | null = null
  
  // Mouse sensitivity
  private mouseSensitivity: number = 0.002
  
  // Event listeners
  private eventListeners: Map<string, Set<EventCallback>> = new Map()
  
  // Bound event handlers (for cleanup)
  private boundKeyDown: (e: KeyboardEvent) => void
  private boundKeyUp: (e: KeyboardEvent) => void
  private boundMouseDown: (e: MouseEvent) => void
  private boundMouseUp: (e: MouseEvent) => void
  private boundMouseMove: (e: MouseEvent) => void
  private boundMouseWheel: (e: WheelEvent) => void
  private boundPointerLockChange: () => void
  private boundContextMenu: (e: Event) => void

  constructor() {
    // Bind event handlers
    this.boundKeyDown = this.handleKeyDown.bind(this)
    this.boundKeyUp = this.handleKeyUp.bind(this)
    this.boundMouseDown = this.handleMouseDown.bind(this)
    this.boundMouseUp = this.handleMouseUp.bind(this)
    this.boundMouseMove = this.handleMouseMove.bind(this)
    this.boundMouseWheel = this.handleMouseWheel.bind(this)
    this.boundPointerLockChange = this.handlePointerLockChange.bind(this)
    this.boundContextMenu = (e: Event) => e.preventDefault()
  }

  /**
   * Initialize input listeners
   * @param element Target element for pointer lock
   */
  init(element: HTMLElement): void {
    this.targetElement = element
    
    // Keyboard events
    window.addEventListener('keydown', this.boundKeyDown)
    window.addEventListener('keyup', this.boundKeyUp)
    
    // Mouse events
    element.addEventListener('mousedown', this.boundMouseDown)
    window.addEventListener('mouseup', this.boundMouseUp)
    window.addEventListener('mousemove', this.boundMouseMove)
    element.addEventListener('wheel', this.boundMouseWheel, { passive: false })
    
    // Pointer lock events
    document.addEventListener('pointerlockchange', this.boundPointerLockChange)
    
    // Prevent context menu on right click
    element.addEventListener('contextmenu', this.boundContextMenu)
  }

  /**
   * Cleanup input listeners
   */
  dispose(): void {
    window.removeEventListener('keydown', this.boundKeyDown)
    window.removeEventListener('keyup', this.boundKeyUp)
    
    if (this.targetElement) {
      this.targetElement.removeEventListener('mousedown', this.boundMouseDown)
      this.targetElement.removeEventListener('wheel', this.boundMouseWheel)
      this.targetElement.removeEventListener('contextmenu', this.boundContextMenu)
    }
    
    window.removeEventListener('mouseup', this.boundMouseUp)
    window.removeEventListener('mousemove', this.boundMouseMove)
    document.removeEventListener('pointerlockchange', this.boundPointerLockChange)
    
    this.exitPointerLock()
    this.clearState()
  }


  /**
   * Clear all input state
   */
  private clearState(): void {
    this.keysPressed.clear()
    this.keysJustPressed.clear()
    this.keysJustReleased.clear()
    this.mouseButtonsPressed.clear()
    this.mouseButtonsJustPressed.clear()
    this.mouseButtonsJustReleased.clear()
    this.mouseMovement = { movementX: 0, movementY: 0, clientX: 0, clientY: 0 }
    this.mouseWheelDelta = 0
  }

  /**
   * Update input state - call at end of each frame
   */
  update(): void {
    // Clear "just" states
    this.keysJustPressed.clear()
    this.keysJustReleased.clear()
    this.mouseButtonsJustPressed.clear()
    this.mouseButtonsJustReleased.clear()
    
    // Reset mouse movement accumulator
    this.mouseMovement.movementX = 0
    this.mouseMovement.movementY = 0
    this.mouseWheelDelta = 0
  }

  // ==================== Keyboard Input ====================

  private handleKeyDown(event: KeyboardEvent): void {
    // Prevent default for game keys
    if (this.isGameKey(event.code)) {
      event.preventDefault()
    }
    
    if (!this.keysPressed.has(event.code)) {
      this.keysPressed.add(event.code)
      this.keysJustPressed.add(event.code)
      this.emit(InputEvent.KEY_DOWN, { code: event.code, key: event.key })
    }
  }

  private handleKeyUp(event: KeyboardEvent): void {
    if (this.keysPressed.has(event.code)) {
      this.keysPressed.delete(event.code)
      this.keysJustReleased.add(event.code)
      this.emit(InputEvent.KEY_UP, { code: event.code, key: event.key })
    }
  }

  /**
   * Check if a key is currently pressed
   */
  isKeyPressed(key: string | InputKey): boolean {
    return this.keysPressed.has(key)
  }

  /**
   * Check if a key was just pressed this frame
   */
  isKeyJustPressed(key: string | InputKey): boolean {
    return this.keysJustPressed.has(key)
  }

  /**
   * Check if a key was just released this frame
   */
  isKeyJustReleased(key: string | InputKey): boolean {
    return this.keysJustReleased.has(key)
  }

  /**
   * Check if key is a game control key
   */
  private isGameKey(code: string): boolean {
    return Object.values(InputKey).includes(code as InputKey)
  }

  // ==================== Mouse Input ====================

  private handleMouseDown(event: MouseEvent): void {
    if (!this.mouseButtonsPressed.has(event.button)) {
      this.mouseButtonsPressed.add(event.button)
      this.mouseButtonsJustPressed.add(event.button)
      this.emit(InputEvent.MOUSE_DOWN, { button: event.button })
    }
    
    // Request pointer lock on left click if not already locked
    if (event.button === MouseButton.LEFT && !this.isPointerLocked) {
      this.requestPointerLock()
    }
  }

  private handleMouseUp(event: MouseEvent): void {
    if (this.mouseButtonsPressed.has(event.button)) {
      this.mouseButtonsPressed.delete(event.button)
      this.mouseButtonsJustReleased.add(event.button)
      this.emit(InputEvent.MOUSE_UP, { button: event.button })
    }
  }

  private handleMouseMove(event: MouseEvent): void {
    if (this.isPointerLocked) {
      // Accumulate movement for this frame
      this.mouseMovement.movementX += event.movementX
      this.mouseMovement.movementY += event.movementY
    }
    
    this.mouseMovement.clientX = event.clientX
    this.mouseMovement.clientY = event.clientY
    
    this.emit(InputEvent.MOUSE_MOVE, {
      movementX: event.movementX * this.mouseSensitivity,
      movementY: event.movementY * this.mouseSensitivity,
      clientX: event.clientX,
      clientY: event.clientY,
    })
  }

  private handleMouseWheel(event: WheelEvent): void {
    event.preventDefault()
    this.mouseWheelDelta = event.deltaY
    
    const direction = event.deltaY > 0 ? 'down' : 'up'
    this.emit(InputEvent.MOUSE_WHEEL, { deltaY: event.deltaY, direction })
  }

  /**
   * Check if a mouse button is currently pressed
   */
  isMouseButtonPressed(button: MouseButton): boolean {
    return this.mouseButtonsPressed.has(button)
  }

  /**
   * Check if a mouse button was just pressed this frame
   */
  isMouseButtonJustPressed(button: MouseButton): boolean {
    return this.mouseButtonsJustPressed.has(button)
  }

  /**
   * Check if a mouse button was just released this frame
   */
  isMouseButtonJustReleased(button: MouseButton): boolean {
    return this.mouseButtonsJustReleased.has(button)
  }

  /**
   * Get accumulated mouse movement for this frame
   */
  getMouseMovement(): MouseMovement {
    return {
      movementX: this.mouseMovement.movementX * this.mouseSensitivity,
      movementY: this.mouseMovement.movementY * this.mouseSensitivity,
      clientX: this.mouseMovement.clientX,
      clientY: this.mouseMovement.clientY,
    }
  }

  /**
   * Get mouse wheel delta for this frame
   */
  getMouseWheelDelta(): number {
    return this.mouseWheelDelta
  }

  /**
   * Get mouse wheel direction (-1 for up, 1 for down, 0 for none)
   */
  getMouseWheelDirection(): number {
    if (this.mouseWheelDelta === 0) return 0
    return this.mouseWheelDelta > 0 ? 1 : -1
  }

  // ==================== Pointer Lock ====================

  private handlePointerLockChange(): void {
    this.isPointerLocked = document.pointerLockElement === this.targetElement
    this.emit(InputEvent.POINTER_LOCK_CHANGE, { locked: this.isPointerLocked })
  }

  /**
   * Request pointer lock on target element
   */
  requestPointerLock(): void {
    if (this.targetElement && !this.isPointerLocked) {
      this.targetElement.requestPointerLock()
    }
  }

  /**
   * Exit pointer lock
   */
  exitPointerLock(): void {
    if (this.isPointerLocked) {
      document.exitPointerLock()
    }
  }

  /**
   * Check if pointer is locked
   */
  hasPointerLock(): boolean {
    return this.isPointerLocked
  }

  // ==================== Settings ====================

  /**
   * Set mouse sensitivity
   */
  setMouseSensitivity(sensitivity: number): void {
    this.mouseSensitivity = Math.max(0.0001, Math.min(0.01, sensitivity))
  }

  /**
   * Get mouse sensitivity
   */
  getMouseSensitivity(): number {
    return this.mouseSensitivity
  }

  // ==================== Event System ====================

  /**
   * Subscribe to input events
   */
  on(event: string, callback: EventCallback): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set())
    }
    this.eventListeners.get(event)!.add(callback)
  }

  /**
   * Unsubscribe from input events
   */
  off(event: string, callback: EventCallback): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.delete(callback)
    }
  }

  /**
   * Emit an input event
   */
  private emit(event: string, data?: unknown): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.forEach((callback) => callback(data))
    }
  }

  // ==================== Helper Methods ====================

  /**
   * Get movement input as a normalized vector
   * Returns { x, z } where x is left/right and z is forward/backward
   */
  getMovementInput(): { x: number; z: number } {
    let x = 0
    let z = 0
    
    if (this.isKeyPressed(InputKey.FORWARD)) z -= 1
    if (this.isKeyPressed(InputKey.BACKWARD)) z += 1
    if (this.isKeyPressed(InputKey.LEFT)) x -= 1
    if (this.isKeyPressed(InputKey.RIGHT)) x += 1
    
    // Normalize diagonal movement
    const length = Math.sqrt(x * x + z * z)
    if (length > 0) {
      x /= length
      z /= length
    }
    
    return { x, z }
  }

  /**
   * Check if player wants to jump
   */
  wantsToJump(): boolean {
    return this.isKeyJustPressed(InputKey.JUMP)
  }

  /**
   * Check if player wants to sprint
   */
  wantsToSprint(): boolean {
    return this.isKeyPressed(InputKey.SPRINT)
  }

  /**
   * Check if player wants to reload
   */
  wantsToReload(): boolean {
    return this.isKeyJustPressed(InputKey.RELOAD)
  }

  /**
   * Check if player wants to fire
   */
  wantsToFire(): boolean {
    return this.isMouseButtonPressed(MouseButton.LEFT)
  }

  /**
   * Get weapon slot from number key press (1-4)
   * Returns -1 if no weapon key pressed
   */
  getWeaponSlotPressed(): number {
    if (this.isKeyJustPressed(InputKey.WEAPON_1)) return 0
    if (this.isKeyJustPressed(InputKey.WEAPON_2)) return 1
    if (this.isKeyJustPressed(InputKey.WEAPON_3)) return 2
    if (this.isKeyJustPressed(InputKey.WEAPON_4)) return 3
    return -1
  }
}
