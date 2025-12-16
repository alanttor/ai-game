/**
 * ScoreCalculator - Handles all score calculations for the game
 * Requirements: 4.4
 */

/**
 * Score configuration
 */
export const ScoreConfig = {
  // Base score per zombie kill
  SCORE_PER_KILL: 100,
  
  // Wave completion bonus base
  WAVE_COMPLETION_BONUS: 500,
  
  // Bonus multipliers
  HEADSHOT_MULTIPLIER: 1.5,
  MELEE_KILL_MULTIPLIER: 1.25,
}

/**
 * Calculate score for killing zombies in a wave
 * Formula: zombies * 100 * wave
 * Requirements: 4.4
 * 
 * @param zombiesKilled - Number of zombies killed
 * @param waveNumber - Current wave number
 * @returns Calculated score
 */
export function calculateKillScore(zombiesKilled: number, waveNumber: number): number {
  if (zombiesKilled < 0 || waveNumber < 1) {
    return 0
  }
  return zombiesKilled * ScoreConfig.SCORE_PER_KILL * waveNumber
}

/**
 * Calculate wave completion bonus
 * 
 * @param waveNumber - Completed wave number
 * @returns Bonus score
 */
export function calculateWaveBonus(waveNumber: number): number {
  if (waveNumber < 1) {
    return 0
  }
  return waveNumber * ScoreConfig.WAVE_COMPLETION_BONUS
}

/**
 * Calculate total score for completing a wave
 * 
 * @param zombiesKilled - Number of zombies killed in the wave
 * @param waveNumber - Wave number
 * @param includeBonus - Whether to include wave completion bonus
 * @returns Total score
 */
export function calculateWaveScore(
  zombiesKilled: number,
  waveNumber: number,
  includeBonus: boolean = true
): number {
  const killScore = calculateKillScore(zombiesKilled, waveNumber)
  const bonus = includeBonus ? calculateWaveBonus(waveNumber) : 0
  return killScore + bonus
}

/**
 * ScoreCalculator class for stateful score tracking
 */
export class ScoreCalculator {
  private _totalScore: number = 0
  private _waveScore: number = 0
  private _currentWave: number = 1
  private _zombiesKilledThisWave: number = 0

  /**
   * Reset the calculator
   */
  reset(): void {
    this._totalScore = 0
    this._waveScore = 0
    this._currentWave = 1
    this._zombiesKilledThisWave = 0
  }

  /**
   * Set current wave
   */
  setWave(wave: number): void {
    this._currentWave = Math.max(1, wave)
    this._waveScore = 0
    this._zombiesKilledThisWave = 0
  }

  /**
   * Record a zombie kill and return the score earned
   */
  recordKill(): number {
    this._zombiesKilledThisWave++
    const killScore = calculateKillScore(1, this._currentWave)
    this._waveScore += killScore
    this._totalScore += killScore
    return killScore
  }

  /**
   * Complete the current wave and return the bonus earned
   */
  completeWave(): number {
    const bonus = calculateWaveBonus(this._currentWave)
    this._totalScore += bonus
    return bonus
  }

  /**
   * Get total score
   */
  get totalScore(): number {
    return this._totalScore
  }

  /**
   * Get current wave score
   */
  get waveScore(): number {
    return this._waveScore
  }

  /**
   * Get zombies killed this wave
   */
  get zombiesKilledThisWave(): number {
    return this._zombiesKilledThisWave
  }

  /**
   * Get current wave
   */
  get currentWave(): number {
    return this._currentWave
  }
}
