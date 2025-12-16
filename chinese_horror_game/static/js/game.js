/**
 * 纸人归魂 - 游戏主逻辑
 * 增强版 - 包含跳吓、鬼影、诡异效果
 */

class HorrorGame {
    constructor() {
        this.state = null;
        this.currentScene = null;
        this.isTransitioning = false;
        this.audioEnabled = true;
        this.horrorLevel = 0; // 恐怖等级累积
        this.lastJumpscare = 0; // 上次跳吓时间
        this.ghostAppearances = 0; // 鬼影出现次数
        this.audioContext = null;
        
        // DOM元素
        this.screens = {
            intro: document.getElementById('intro-screen'),
            game: document.getElementById('game-screen'),
            ending: document.getElementById('ending-screen')
        };
        
        this.elements = {
            backgroundLayer: document.getElementById('background-layer'),
            horrorEffects: document.getElementById('horror-effects'),
            sceneTitle: document.getElementById('scene-title'),
            sceneText: document.getElementById('scene-text'),
            choicesContainer: document.getElementById('choices-container'),
            sanityFill: document.getElementById('sanity-fill'),
            sanityValue: document.getElementById('sanity-value'),
            itemsList: document.getElementById('items-list'),
            randomEvent: document.getElementById('random-event'),
            insanityWarning: document.getElementById('insanity-warning'),
            secretsPanel: document.getElementById('secrets-panel'),
            secretsList: document.getElementById('secrets-list'),
            jumpscare: document.getElementById('jumpscare'),
            jumpscareImg: document.getElementById('jumpscare-img')
        };
        
        // 危险选项关键词 - 选择这些会触发恐怖效果
        this.dangerousKeywords = [
            '回头', '窥视', '推倒', '撕掉', '呵斥', '质问', 
            '揭开', '强行', '打开井', '直视', '抓住', '放弃'
        ];
        
        // 跳吓场景
        this.jumpscareScenes = [
            'look_back', 'peek_side_door', 'push_figure', 'examine_portrait',
            'open_well', 'lift_veil', 'turn_around', 'call_father'
        ];
        
        this.init();
    }
    
    init() {
        // 绑定事件
        document.getElementById('start-btn').addEventListener('click', () => this.startGame());
        document.getElementById('secrets-btn').addEventListener('click', () => this.toggleSecrets());
        document.getElementById('close-secrets').addEventListener('click', () => this.toggleSecrets());
        document.getElementById('restart-btn').addEventListener('click', () => this.restartGame());
        document.getElementById('replay-btn').addEventListener('click', () => this.restartGame());
        
        // 添加键盘支持
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
        
        // 预加载音效
        this.preloadAudio();
        
        // 添加打字机效果的CSS
        this.addTypewriterStyles();
    }
    
    addTypewriterStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .typewriter {
                overflow: hidden;
                white-space: nowrap;
                animation: typing 2s steps(40, end);
            }
            @keyframes typing {
                from { width: 0; }
                to { width: 100%; }
            }
            
            /* 鬼影效果 */
            .ghost-flash {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(139, 0, 0, 0.3);
                z-index: 500;
                pointer-events: none;
                animation: ghostFlash 0.1s ease;
            }
            
            @keyframes ghostFlash {
                0%, 100% { opacity: 0; }
                50% { opacity: 1; }
            }
            
            /* 鬼脸闪现 */
            .ghost-face {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 300px;
                color: #8B0000;
                text-shadow: 0 0 50px #8B0000;
                z-index: 600;
                animation: ghostFaceAppear 0.3s ease;
                pointer-events: none;
            }
            
            @keyframes ghostFaceAppear {
                0% { opacity: 0; transform: translate(-50%, -50%) scale(0.5); }
                50% { opacity: 1; transform: translate(-50%, -50%) scale(1.2); }
                100% { opacity: 0; transform: translate(-50%, -50%) scale(1); }
            }
            
            /* 屏幕扭曲 */
            .screen-distort {
                animation: distort 0.5s ease;
            }
            
            @keyframes distort {
                0%, 100% { filter: none; }
                25% { filter: blur(2px) hue-rotate(90deg); }
                50% { filter: blur(0) hue-rotate(180deg) invert(0.1); }
                75% { filter: blur(3px) hue-rotate(270deg); }
            }
            
            /* 血滴效果 */
            .blood-drop {
                position: fixed;
                width: 10px;
                height: 20px;
                background: linear-gradient(180deg, #8B0000 0%, #4a0000 100%);
                border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
                z-index: 400;
                animation: bloodFall 2s ease-in forwards;
            }
            
            @keyframes bloodFall {
                0% { transform: translateY(-100px); opacity: 1; }
                100% { transform: translateY(100vh); opacity: 0; }
            }
            
            /* 眼睛注视效果 */
            .watching-eyes {
                position: fixed;
                font-size: 60px;
                color: #ff0000;
                text-shadow: 0 0 20px #ff0000;
                z-index: 300;
                animation: eyesBlink 3s ease infinite;
                pointer-events: none;
            }
            
            @keyframes eyesBlink {
                0%, 45%, 55%, 100% { opacity: 0.8; }
                50% { opacity: 0; }
            }
            
            /* 文字抖动 */
            .text-shake {
                animation: textShake 0.1s ease infinite;
            }
            
            @keyframes textShake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-2px); }
                75% { transform: translateX(2px); }
            }
            
            /* 诡异微笑 */
            .creepy-smile {
                position: fixed;
                bottom: 20%;
                right: 10%;
                font-size: 100px;
                opacity: 0;
                animation: creepySmile 5s ease-in-out;
                z-index: 200;
                pointer-events: none;
            }
            
            @keyframes creepySmile {
                0%, 80%, 100% { opacity: 0; }
                85%, 95% { opacity: 0.3; }
            }
            
            /* 纸人移动 */
            .paper-figure-shadow {
                position: fixed;
                width: 100px;
                height: 200px;
                background: linear-gradient(180deg, #1a1a1a 0%, transparent 100%);
                z-index: 150;
                animation: paperMove 8s ease-in-out;
                pointer-events: none;
            }
            
            @keyframes paperMove {
                0% { left: -100px; opacity: 0; }
                10% { opacity: 0.5; }
                90% { opacity: 0.5; }
                100% { left: calc(100% + 100px); opacity: 0; }
            }
            

        `;
        document.head.appendChild(style);
    }
    
    preloadAudio() {
        // 音效映射 - 增强版
        this.sounds = {
            click: { frequency: 200, duration: 0.1, type: 'sine' },
            horror: { frequency: 80, duration: 0.8, type: 'sawtooth' },
            whisper: { frequency: 150, duration: 0.5, type: 'sine' },
            heartbeat: { frequency: 60, duration: 0.3, type: 'sine' },
            scream: { frequency: 800, duration: 0.5, type: 'sawtooth' },
            jumpscare: { frequency: 1200, duration: 0.3, type: 'square' },
            ghost: { frequency: 100, duration: 1, type: 'triangle' },
            door: { frequency: 50, duration: 0.5, type: 'sawtooth' },
            footsteps: { frequency: 120, duration: 0.2, type: 'square' },
            laugh: { frequency: 300, duration: 0.8, type: 'sawtooth' }
        };
    }
    
    createOscillatorSound(frequency, duration) {
        return { frequency, duration };
    }
    
    getAudioContext() {
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        return this.audioContext;
    }
    
    playSound(type, volume = 0.15) {
        if (!this.audioEnabled) return;
        
        try {
            const audioContext = this.getAudioContext();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            const sound = this.sounds[type];
            if (sound) {
                oscillator.frequency.value = sound.frequency;
                oscillator.type = sound.type || 'sine';
                gainNode.gain.setValueAtTime(volume, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + sound.duration);
                
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + sound.duration);
            }
        } catch (e) {
            console.log('Audio not supported');
        }
    }
    
    // 播放恐怖音效序列
    playHorrorSequence() {
        this.playSound('horror', 0.2);
        setTimeout(() => this.playSound('ghost', 0.1), 200);
        setTimeout(() => this.playSound('whisper', 0.15), 500);
    }
    
    // 播放跳吓音效
    playJumpscareSound() {
        this.playSound('jumpscare', 0.3);
        setTimeout(() => this.playSound('scream', 0.25), 100);
    }
    
    // 播放心跳加速
    playHeartbeat(times = 5) {
        let count = 0;
        const interval = setInterval(() => {
            this.playSound('heartbeat', 0.2);
            count++;
            if (count >= times) clearInterval(interval);
        }, 500 - count * 50);
    }
    
    async startGame() {
        this.playSound('click');
        
        try {
            const response = await fetch('/api/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.state = data.state;
                this.currentScene = data.scene;
                this.switchScreen('game');
                this.renderScene();
            }
        } catch (error) {
            console.error('Failed to start game:', error);
            // 离线模式 - 使用本地数据
            this.startOfflineGame();
        }
    }
    
    startOfflineGame() {
        this.state = {
            current_scene: 'prologue',
            sanity: 100,
            items: [],
            flags: {},
            death_count: 0,
            discovered_secrets: [],
            time_in_mansion: 0
        };
        this.switchScreen('game');
        this.showOfflineMessage();
    }
    
    showOfflineMessage() {
        this.elements.sceneTitle.textContent = '连接失败';
        this.elements.sceneText.innerHTML = `
            <p class="narration">无法连接到服务器。</p>
            <p class="detail">请确保后端服务正在运行：python app.py</p>
        `;
        this.elements.choicesContainer.innerHTML = `
            <button class="choice-btn" onclick="location.reload()">重试</button>
        `;
    }
    
    async makeChoice(choiceIndex) {
        if (this.isTransitioning) return;
        
        this.isTransitioning = true;
        this.playSound('click');
        
        // 获取选择的文本
        const choices = this.currentScene.choices || [];
        const choiceText = choices[choiceIndex]?.text || '';
        
        // 检查是否是危险选项
        const isDangerous = this.dangerousKeywords.some(keyword => choiceText.includes(keyword));
        
        if (isDangerous) {
            this.horrorLevel += 10;
            // 危险选项触发恐怖效果
            this.triggerDangerousChoiceEffect();
        }
        
        // 添加过渡效果
        this.elements.sceneText.style.opacity = '0';
        
        try {
            const response = await fetch('/api/choice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ choice_index: choiceIndex })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.state = data.state;
                this.currentScene = data.scene;
                
                // 处理跳吓事件
                if (data.jumpscare) {
                    this.handleJumpscare(data.jumpscare);
                }
                
                // 处理恐怖效果
                if (data.horror_effects) {
                    this.applyHorrorEffects(data.horror_effects);
                }
                
                // 处理随机事件
                if (data.random_event) {
                    this.showRandomEvent(data.random_event);
                }
                
                // 处理理智警告
                if (data.insanity_message) {
                    this.showInsanityWarning(data.insanity_message);
                }
                
                // 检查是否是跳吓场景
                const nextSceneId = this.state.current_scene;
                if (this.jumpscareScenes.includes(nextSceneId)) {
                    this.triggerJumpscare(nextSceneId);
                }
                
                // 检查是否是结局
                if (this.currentScene.is_ending) {
                    setTimeout(() => {
                        this.showEnding();
                    }, 500);
                } else {
                    setTimeout(() => {
                        this.renderScene();
                        this.elements.sceneText.style.opacity = '1';
                        
                        // 场景渲染后的恐怖效果
                        this.triggerSceneHorrorEffects();
                    }, 300);
                }
                
                // 更新理智效果
                this.updateSanityEffects();
                
                // 随机鬼影效果
                this.maybeShowGhostEffect();
                
            } else {
                // 显示错误信息
                this.showError(data.error);
                this.elements.sceneText.style.opacity = '1';
            }
        } catch (error) {
            console.error('Failed to make choice:', error);
            this.elements.sceneText.style.opacity = '1';
        }
        
        this.isTransitioning = false;
    }
    
    renderScene() {
        if (!this.currentScene) return;
        
        // 更新标题
        this.elements.sceneTitle.textContent = this.currentScene.title || '';
        
        // 低理智时标题添加恐怖效果
        if (this.state.sanity < 40) {
            this.elements.sceneTitle.classList.add('horror-title');
        } else {
            this.elements.sceneTitle.classList.remove('horror-title');
        }
        
        // 更新文本（带打字效果）
        this.elements.sceneText.innerHTML = this.currentScene.text || '';
        
        // 更新选项
        this.renderChoices();
        
        // 更新状态栏
        this.updateStatusBar();
        
        // 更新背景
        this.updateBackground();
        
        // 触发恐怖效果
        if (this.currentScene.text && this.currentScene.text.includes('class="horror"')) {
            this.triggerHorrorEffect();
        }
        
        // 增强的场景效果
        this.enhancedSceneEffects();
    }
    
    renderChoices() {
        const choices = this.currentScene.choices || [];
        this.elements.choicesContainer.innerHTML = '';
        
        // 低理智时选项容器添加恐怖效果
        if (this.state.sanity < 50) {
            this.elements.choicesContainer.classList.add('horror-mode');
        } else {
            this.elements.choicesContainer.classList.remove('horror-mode');
        }
        
        choices.forEach((choice, index) => {
            const btn = document.createElement('button');
            btn.className = 'choice-btn';
            btn.textContent = choice.text;
            
            // 检查是否是危险选项
            const isDangerous = this.dangerousKeywords.some(keyword => choice.text.includes(keyword));
            if (isDangerous) {
                btn.classList.add('dangerous');
                btn.title = '这个选择可能很危险...';
            }
            
            // 检查是否需要物品
            if (choice.require_item && !this.state.items.includes(choice.require_item)) {
                btn.classList.add('disabled');
                btn.title = `需要: ${choice.require_item}`;
            }
            
            // 检查是否需要标记
            if (choice.require_flag && !this.state.flags[choice.require_flag]) {
                btn.classList.add('disabled');
                btn.title = '条件未满足';
            }
            
            // 危险选项悬停效果
            if (isDangerous) {
                btn.addEventListener('mouseenter', () => {
                    this.playSound('whisper', 0.05);
                    if (Math.random() < 0.3) {
                        this.flashScreen('rgba(139, 0, 0, 0.1)', 50);
                    }
                });
            }
            
            btn.addEventListener('click', () => {
                if (!btn.classList.contains('disabled')) {
                    // 危险选项点击时的额外效果
                    if (isDangerous) {
                        this.playSound('door', 0.15);
                        this.screens.game.classList.add('screen-distort');
                        setTimeout(() => this.screens.game.classList.remove('screen-distort'), 300);
                    }
                    this.makeChoice(index);
                }
            });
            
            // 延迟显示选项
            btn.style.opacity = '0';
            btn.style.transform = 'translateX(-20px)';
            setTimeout(() => {
                btn.style.transition = 'all 0.3s ease';
                btn.style.opacity = '1';
                btn.style.transform = 'translateX(0)';
            }, 1500 + index * 200);
            
            this.elements.choicesContainer.appendChild(btn);
        });
        
        // 低理智时随机打乱选项顺序的视觉效果
        if (this.state.sanity < 20 && Math.random() < 0.3) {
            setTimeout(() => {
                const buttons = this.elements.choicesContainer.querySelectorAll('.choice-btn');
                buttons.forEach(btn => {
                    btn.style.transform = `translateX(${(Math.random() - 0.5) * 10}px)`;
                });
                setTimeout(() => {
                    buttons.forEach(btn => btn.style.transform = '');
                }, 500);
            }, 2000);
        }
    }
    
    updateStatusBar() {
        // 更新理智值
        const sanity = this.state.sanity;
        this.elements.sanityFill.style.width = `${sanity}%`;
        this.elements.sanityValue.textContent = sanity;
        
        // 理智值颜色变化
        if (sanity <= 30) {
            this.elements.sanityFill.style.background = 'linear-gradient(90deg, #8B0000 0%, #4a0000 100%)';
        } else if (sanity <= 50) {
            this.elements.sanityFill.style.background = 'linear-gradient(90deg, #8B4500 0%, #8B0000 100%)';
        } else {
            this.elements.sanityFill.style.background = 'linear-gradient(90deg, #8B0000 0%, #4a6fa5 100%)';
        }
        
        // 更新物品列表
        this.elements.itemsList.innerHTML = '';
        this.state.items.forEach(item => {
            const tag = document.createElement('span');
            tag.className = 'item-tag';
            tag.textContent = item;
            this.elements.itemsList.appendChild(tag);
        });
    }
    
    updateBackground() {
        const bg = this.currentScene.background;
        if (bg) {
            // 使用CSS渐变作为背景
            const backgrounds = {
                'fog_path': 'linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f0f0f 100%)',
                'red_bride': 'linear-gradient(180deg, #2d0a0a 0%, #1a0505 100%)',
                'mansion_gate': 'linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%)',
                'main_hall': 'linear-gradient(180deg, #2a1a0a 0%, #1a0f05 100%)',
                'darkness': 'linear-gradient(180deg, #000000 0%, #0a0a0a 100%)',
                'basement': 'linear-gradient(180deg, #0a0a1a 0%, #050510 100%)',
                'default': 'linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%)'
            };
            
            this.elements.backgroundLayer.style.background = backgrounds[bg] || backgrounds['default'];
        }
    }
    
    updateSanityEffects() {
        const sanity = this.state.sanity;
        const gameScreen = this.screens.game;
        
        gameScreen.classList.remove('low-sanity', 'critical-sanity');
        
        if (sanity <= 30) {
            gameScreen.classList.add('critical-sanity');
            this.triggerHorrorEffect();
            // 低理智时更频繁的恐怖效果
            this.startLowSanityEffects();
        } else if (sanity <= 50) {
            gameScreen.classList.add('low-sanity');
            // 中等理智时偶尔出现效果
            if (Math.random() < 0.3) {
                this.showWatchingEyes();
            }
        }
    }
    
    triggerHorrorEffect() {
        // 屏幕闪烁
        this.elements.horrorEffects.style.opacity = '1';
        
        // 播放恐怖音效
        this.playHorrorSequence();
        
        // 短暂的屏幕抖动
        this.screens.game.style.animation = 'screenShake 0.3s ease';
        setTimeout(() => {
            this.screens.game.style.animation = '';
        }, 300);
        
        // 添加红色闪烁
        this.flashScreen('#8B0000', 100);
    }
    
    // 危险选项效果
    triggerDangerousChoiceEffect() {
        // 屏幕扭曲
        this.screens.game.classList.add('screen-distort');
        setTimeout(() => {
            this.screens.game.classList.remove('screen-distort');
        }, 500);
        
        // 播放不祥音效
        this.playSound('door', 0.2);
        
        // 血滴效果
        if (Math.random() < 0.5) {
            this.createBloodDrops(3);
        }
    }
    
    // 跳吓效果
    triggerJumpscare(sceneId) {
        const now = Date.now();
        // 防止跳吓过于频繁
        if (now - this.lastJumpscare < 30000) return;
        
        // 根据场景决定跳吓类型
        const jumpscareTypes = {
            'look_back': 'ghost_bride',
            'peek_side_door': 'paper_eye',
            'push_figure': 'paper_face',
            'examine_portrait': 'portrait_alive',
            'open_well': 'corpse',
            'lift_veil': 'black_eyes',
            'turn_around': 'ghost_close',
            'call_father': 'fake_father'
        };
        
        const type = jumpscareTypes[sceneId] || 'ghost';
        
        // 50%概率触发跳吓
        if (Math.random() < 0.5) {
            this.lastJumpscare = now;
            this.showJumpscare(type);
        }
    }
    
    // 显示跳吓
    showJumpscare(type) {
        // 创建跳吓元素
        const jumpscare = document.createElement('div');
        jumpscare.className = 'jumpscare-overlay';
        jumpscare.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #000;
            z-index: 1000;
            display: flex;
            justify-content: center;
            align-items: center;
            animation: jumpscareFlash 0.5s ease;
        `;
        
        // 根据类型显示不同的恐怖图像（使用文字符号）
        const faces = {
            'ghost_bride': '👰',
            'paper_eye': '👁️',
            'paper_face': '🎭',
            'portrait_alive': '😱',
            'corpse': '💀',
            'black_eyes': '👻',
            'ghost_close': '😈',
            'fake_father': '🧟',
            'ghost': '👹'
        };
        
        const face = document.createElement('div');
        face.style.cssText = `
            font-size: 250px;
            animation: jumpscareZoom 0.4s ease;
            filter: drop-shadow(0 0 50px #8B0000);
        `;
        face.textContent = faces[type] || '👻';
        
        jumpscare.appendChild(face);
        document.body.appendChild(jumpscare);
        
        // 播放跳吓音效
        this.playJumpscareSound();
        
        // 屏幕抖动
        document.body.style.animation = 'screenShake 0.3s ease';
        
        // 移除跳吓
        setTimeout(() => {
            jumpscare.style.opacity = '0';
            jumpscare.style.transition = 'opacity 0.3s';
            setTimeout(() => {
                jumpscare.remove();
                document.body.style.animation = '';
            }, 300);
        }, 400);
    }
    
    // 场景恐怖效果
    triggerSceneHorrorEffects() {
        const sceneText = this.currentScene.text || '';
        
        // 如果场景包含恐怖内容
        if (sceneText.includes('class="horror"')) {
            // 文字抖动效果
            const horrorElements = document.querySelectorAll('.horror');
            horrorElements.forEach(el => {
                el.classList.add('text-shake');
                setTimeout(() => el.classList.remove('text-shake'), 2000);
            });
            
            // 播放恐怖音效
            this.playSound('ghost', 0.1);
        }
        
        // 随机诡异微笑
        if (Math.random() < 0.1 && this.state.sanity < 70) {
            this.showCreepySmile();
        }
    }
    
    // 可能显示鬼影
    maybeShowGhostEffect() {
        const chance = (100 - this.state.sanity) / 200; // 理智越低概率越高
        
        if (Math.random() < chance) {
            this.ghostAppearances++;
            
            const effects = [
                () => this.showGhostFlash(),
                () => this.showPaperFigureShadow(),
                () => this.showWatchingEyes(),
                () => this.flashScreen('#8B0000', 50),
                () => this.showCreepySmile()
            ];
            
            const effect = effects[Math.floor(Math.random() * effects.length)];
            effect();
        }
    }
    
    // 鬼影闪现
    showGhostFlash() {
        const flash = document.createElement('div');
        flash.className = 'ghost-flash';
        document.body.appendChild(flash);
        
        this.playSound('ghost', 0.1);
        
        setTimeout(() => flash.remove(), 100);
    }
    
    // 鬼脸闪现
    showGhostFace() {
        const face = document.createElement('div');
        face.className = 'ghost-face';
        face.textContent = '👻';
        document.body.appendChild(face);
        
        this.playSound('scream', 0.2);
        
        setTimeout(() => face.remove(), 300);
    }
    
    // 纸人影子移动
    showPaperFigureShadow() {
        const shadow = document.createElement('div');
        shadow.className = 'paper-figure-shadow';
        shadow.style.top = Math.random() * 50 + 25 + '%';
        document.body.appendChild(shadow);
        
        this.playSound('footsteps', 0.1);
        
        setTimeout(() => shadow.remove(), 8000);
    }
    
    // 注视的眼睛
    showWatchingEyes() {
        const eyes = document.createElement('div');
        eyes.className = 'watching-eyes';
        eyes.textContent = '👁️ 👁️';
        eyes.style.top = Math.random() * 30 + 10 + '%';
        eyes.style.left = Math.random() * 60 + 20 + '%';
        document.body.appendChild(eyes);
        
        setTimeout(() => eyes.remove(), 3000);
    }
    
    // 诡异微笑
    showCreepySmile() {
        const smile = document.createElement('div');
        smile.className = 'creepy-smile';
        smile.textContent = '😈';
        document.body.appendChild(smile);
        
        this.playSound('laugh', 0.05);
        
        setTimeout(() => smile.remove(), 5008);
    }
    
    // 血滴效果
    createBloodDrops(count) {
        for (let i = 0; i < count; i++) {
            setTimeout(() => {
                const drop = document.createElement('div');
                drop.className = 'blood-drop';
                drop.style.left = Math.random() * 100 + '%';
                drop.style.top = '-20px';
                document.body.appendChild(drop);
                
                setTimeout(() => drop.remove(), 2000);
            }, i * 300);
        }
    }
    
    // 屏幕闪烁
    flashScreen(color, duration) {
        const flash = document.createElement('div');
        flash.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: ${color};
            opacity: 0.3;
            z-index: 400;
            pointer-events: none;
        `;
        document.body.appendChild(flash);
        
        setTimeout(() => flash.remove(), duration);
    }
    
    // 低理智持续效果
    startLowSanityEffects() {
        // 持续的心跳
        this.playHeartbeat(3);
        
        // 随机闪烁
        if (Math.random() < 0.3) {
            this.flashScreen('rgba(139, 0, 0, 0.2)', 100);
        }
        
        // 文字扭曲
        this.elements.sceneText.style.filter = 'blur(0.5px)';
        setTimeout(() => {
            this.elements.sceneText.style.filter = '';
        }, 1000);
    }
    
    showRandomEvent(event) {
        this.elements.randomEvent.innerHTML = event.text;
        this.elements.randomEvent.classList.remove('hidden');
        
        // 根据事件类型播放不同效果
        const effectType = event.effect || 'whisper';
        this.triggerEventEffect(effectType);
        
        setTimeout(() => {
            this.elements.randomEvent.classList.add('hidden');
        }, 3000);
    }
    
    // 根据事件类型触发效果
    triggerEventEffect(effectType) {
        switch(effectType) {
            case 'watching':
                this.showWatchingEyes();
                this.playSound('ghost', 0.1);
                break;
            case 'footsteps':
                this.playSound('footsteps', 0.15);
                this.showPaperFigureShadow();
                break;
            case 'whisper':
                this.playSound('whisper', 0.1);
                break;
            case 'shadow':
            case 'shadow_delay':
                this.showGhostFlash();
                this.playSound('ghost', 0.08);
                break;
            case 'burning':
                this.flashScreen('rgba(255, 100, 0, 0.2)', 200);
                this.playSound('horror', 0.1);
                break;
            case 'crying':
                this.playSound('ghost', 0.15);
                this.showCreepySmile();
                break;
            case 'mirror':
                this.showGhostFace();
                this.playSound('scream', 0.15);
                break;
            case 'face_flash':
                this.showJumpscare('ghost_close');
                break;
            case 'cold_touch':
                this.flashScreen('rgba(100, 150, 255, 0.3)', 300);
                this.playSound('ghost', 0.2);
                this.screens.game.style.animation = 'screenShake 0.5s ease';
                setTimeout(() => this.screens.game.style.animation = '', 500);
                break;
            case 'paper_turn':
                this.showPaperFigureShadow();
                this.playSound('door', 0.15);
                break;
            case 'voice_inside':
                this.playSound('whisper', 0.2);
                this.elements.sceneText.classList.add('text-shake');
                setTimeout(() => this.elements.sceneText.classList.remove('text-shake'), 1000);
                break;
            case 'wet_footprints':
                this.createBloodDrops(5);
                this.playSound('footsteps', 0.1);
                break;
            case 'nursery_rhyme':
                this.playHorrorSequence();
                break;
            default:
                this.playSound('whisper', 0.1);
        }
    }
    
    // 处理服务器返回的跳吓
    handleJumpscare(jumpscare) {
        if (!jumpscare) return;
        
        // 延迟一点显示，增加惊吓效果
        setTimeout(() => {
            this.showJumpscare(jumpscare.type);
            
            // 显示跳吓文字
            this.showHorrorMessage(jumpscare.text);
        }, 500 + Math.random() * 1000);
    }
    
    // 显示恐怖消息
    showHorrorMessage(text) {
        const msgEl = document.getElementById('horror-message');
        const textEl = document.getElementById('horror-message-text');
        
        if (msgEl && textEl) {
            textEl.textContent = text;
            msgEl.classList.remove('hidden');
            
            this.playSound('horror', 0.15);
            
            setTimeout(() => {
                msgEl.classList.add('hidden');
            }, 2000);
        }
    }
    
    // 应用恐怖效果
    applyHorrorEffects(effects) {
        if (!effects) return;
        
        // 屏幕抖动
        if (effects.should_shake) {
            this.screens.game.style.animation = 'screenShake 0.3s ease';
            setTimeout(() => this.screens.game.style.animation = '', 300);
        }
        
        // 屏幕闪烁
        if (effects.should_flash) {
            this.flashScreen('rgba(139, 0, 0, 0.3)', 100);
        }
        
        // 随机鬼影
        if (Math.random() < effects.ghost_chance) {
            const ghostEffects = [
                () => this.showGhostFlash(),
                () => this.showWatchingEyes(),
                () => this.showPaperFigureShadow(),
                () => this.showCreepySmile()
            ];
            const effect = ghostEffects[Math.floor(Math.random() * ghostEffects.length)];
            setTimeout(effect, Math.random() * 2000);
        }
        
        // 持续恐怖氛围
        if (effects.ambient_horror) {
            this.startAmbientHorror();
        }
        
        // 危险选项额外效果
        if (effects.is_dangerous) {
            this.playSound('door', 0.1);
            this.screens.game.classList.add('screen-distort');
            setTimeout(() => this.screens.game.classList.remove('screen-distort'), 500);
        }
    }
    
    // 持续恐怖氛围
    startAmbientHorror() {
        // 随机时间后触发效果
        const delay = 3000 + Math.random() * 5008;
        
        setTimeout(() => {
            if (this.state && this.state.sanity < 40) {
                const effects = [
                    () => this.playSound('whisper', 0.05),
                    () => this.flashScreen('rgba(139, 0, 0, 0.1)', 50),
                    () => {
                        this.elements.sceneText.style.filter = 'blur(1px)';
                        setTimeout(() => this.elements.sceneText.style.filter = '', 500);
                    }
                ];
                const effect = effects[Math.floor(Math.random() * effects.length)];
                effect();
            }
        }, delay);
    }
    
    showInsanityWarning(message) {
        this.elements.insanityWarning.textContent = message;
        this.elements.insanityWarning.classList.remove('hidden');
        
        setTimeout(() => {
            this.elements.insanityWarning.classList.add('hidden');
        }, 4000);
    }
    
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'random-event';
        errorDiv.innerHTML = `<p class="detail">${message}</p>`;
        this.elements.choicesContainer.insertBefore(errorDiv, this.elements.choicesContainer.firstChild);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 2000);
    }
    
    showEnding() {
        document.getElementById('ending-title').textContent = this.currentScene.title;
        document.getElementById('ending-text').innerHTML = this.currentScene.text;
        document.getElementById('final-sanity').textContent = this.state.sanity;
        document.getElementById('final-secrets').textContent = this.state.discovered_secrets.length;
        document.getElementById('final-deaths').textContent = this.state.death_count;
        
        this.switchScreen('ending');
    }
    
    toggleSecrets() {
        const panel = this.elements.secretsPanel;
        panel.classList.toggle('hidden');
        
        if (!panel.classList.contains('hidden')) {
            this.elements.secretsList.innerHTML = '';
            
            if (this.state.discovered_secrets.length === 0) {
                const li = document.createElement('li');
                li.textContent = '尚未发现任何秘密';
                li.style.color = 'rgba(240, 230, 211, 0.5)';
                this.elements.secretsList.appendChild(li);
            } else {
                this.state.discovered_secrets.forEach(secret => {
                    const li = document.createElement('li');
                    li.textContent = secret;
                    this.elements.secretsList.appendChild(li);
                });
            }
        }
    }
    
    async restartGame() {
        this.playSound('click');
        await this.startGame();
    }
    
    switchScreen(screenName) {
        Object.values(this.screens).forEach(screen => {
            screen.classList.remove('active');
        });
        
        setTimeout(() => {
            this.screens[screenName].classList.add('active');
        }, 100);
    }
    
    handleKeyPress(e) {
        // 数字键选择选项
        if (e.key >= '1' && e.key <= '9') {
            const index = parseInt(e.key) - 1;
            const choices = this.elements.choicesContainer.querySelectorAll('.choice-btn:not(.disabled)');
            if (choices[index]) {
                choices[index].click();
            }
        }
        
        // ESC关闭秘密面板
        if (e.key === 'Escape') {
            if (!this.elements.secretsPanel.classList.contains('hidden')) {
                this.toggleSecrets();
            }
        }
    }
    
    // 鼠标跟踪的诡异眼睛
    startCreepyMouseTracking() {
        if (this.mouseTrackingActive) return;
        this.mouseTrackingActive = true;
        
        const eyes = document.createElement('div');
        eyes.id = 'tracking-eyes';
        eyes.innerHTML = '👁️';
        eyes.style.cssText = `
            position: fixed;
            font-size: 30px;
            opacity: 0;
            z-index: 250;
            pointer-events: none;
            transition: opacity 2s ease;
            filter: drop-shadow(0 0 10px #ff0000);
        `;
        document.body.appendChild(eyes);
        
        // 随机出现并跟踪鼠标
        const showEyes = () => {
            if (this.state && this.state.sanity < 50 && Math.random() < 0.1) {
                eyes.style.opacity = '0.5';
                
                const moveHandler = (e) => {
                    const offsetX = (Math.random() - 0.5) * 200;
                    const offsetY = (Math.random() - 0.5) * 200;
                    eyes.style.left = (e.clientX + offsetX) + 'px';
                    eyes.style.top = (e.clientY + offsetY) + 'px';
                };
                
                document.addEventListener('mousemove', moveHandler);
                
                setTimeout(() => {
                    eyes.style.opacity = '0';
                    document.removeEventListener('mousemove', moveHandler);
                }, 3000);
            }
        };
        
        setInterval(showEyes, 10000);
    }
    
    // 随机恐怖弹窗
    showRandomHorrorPopup() {
        const messages = [
            '她在看着你...',
            '回头...',
            '你听到了吗？',
            '别回头...',
            '她来了...',
            '纸人...在动...',
            '子时将至...'
        ];
        
        const popup = document.createElement('div');
        popup.style.cssText = `
            position: fixed;
            top: ${Math.random() * 60 + 20}%;
            left: ${Math.random() * 60 + 20}%;
            background: rgba(0, 0, 0, 0.9);
            border: 1px solid #8B0000;
            padding: 20px 30px;
            color: #8B0000;
            font-family: 'Ma Shan Zheng', cursive;
            font-size: 1.5rem;
            z-index: 600;
            animation: popupAppear 0.3s ease;
            pointer-events: none;
        `;
        popup.textContent = messages[Math.floor(Math.random() * messages.length)];
        
        const style = document.createElement('style');
        style.textContent = `
            @keyframes popupAppear {
                0% { opacity: 0; transform: scale(0.5); }
                50% { opacity: 1; transform: scale(1.1); }
                100% { opacity: 1; transform: scale(1); }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(popup);
        this.playSound('whisper', 0.1);
        
        setTimeout(() => {
            popup.style.opacity = '0';
            popup.style.transition = 'opacity 0.5s';
            setTimeout(() => popup.remove(), 500);
        }, 1500);
    }
    
    // 屏幕边缘的鬼手
    showGhostHand() {
        const hand = document.createElement('div');
        const side = Math.random() < 0.5 ? 'left' : 'right';
        hand.style.cssText = `
            position: fixed;
            ${side}: -50px;
            top: ${Math.random() * 60 + 20}%;
            font-size: 80px;
            z-index: 300;
            animation: ghostHandReach 3s ease;
            pointer-events: none;
            transform: ${side === 'right' ? 'scaleX(-1)' : ''};
        `;
        hand.textContent = '🖐️';
        
        const style = document.createElement('style');
        style.textContent = `
            @keyframes ghostHandReach {
                0% { ${side}: -100px; opacity: 0; }
                30% { ${side}: 20px; opacity: 0.7; }
                70% { ${side}: 20px; opacity: 0.7; }
                100% { ${side}: -100px; opacity: 0; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(hand);
        this.playSound('ghost', 0.1);
        
        setTimeout(() => hand.remove(), 3000);
    }
    
    // 文字逐渐变红效果
    startBleedingTextEffect() {
        const horrorTexts = document.querySelectorAll('.horror');
        horrorTexts.forEach(text => {
            if (Math.random() < 0.3) {
                text.classList.add('bleeding-text');
            }
        });
    }
    
    // 增强的场景渲染后效果
    enhancedSceneEffects() {
        // 低理智时的额外效果
        if (this.state.sanity < 40) {
            // 随机显示恐怖弹窗
            if (Math.random() < 0.15) {
                setTimeout(() => this.showRandomHorrorPopup(), 2000 + Math.random() * 3000);
            }
            
            // 随机显示鬼手
            if (Math.random() < 0.1) {
                setTimeout(() => this.showGhostHand(), 3000 + Math.random() * 5008);
            }
            
            // 文字出血效果
            this.startBleedingTextEffect();
        }
        
        // 极低理智时
        if (this.state.sanity < 20) {
            // 屏幕持续轻微抖动
            this.screens.game.style.animation = 'textWobble 2s ease-in-out infinite';
            
            // 更频繁的恐怖效果
            this.startCreepyMouseTracking();
        } else {
            this.screens.game.style.animation = '';
        }
    }
}

// 初始化游戏
document.addEventListener('DOMContentLoaded', () => {
    window.game = new HorrorGame();
    
    // 创建沉浸式环境效果
    createImmersiveEffects();
    
    // 添加页面可见性变化时的恐怖效果
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden && window.game.state && window.game.state.sanity < 60) {
            if (Math.random() < 0.3) {
                setTimeout(() => {
                    window.game.showGhostFlash();
                    window.game.playSound('ghost', 0.15);
                }, 500);
            }
        }
    });
    
    // 鼠标长时间不动时的效果
    let idleTimer;
    document.addEventListener('mousemove', () => {
        clearTimeout(idleTimer);
        idleTimer = setTimeout(() => {
            if (window.game.state && window.game.state.sanity < 50) {
                window.game.showWatchingEyes();
            }
        }, 15008);
    });
});

// 创建沉浸式环境效果
function createImmersiveEffects() {
    // 创建灰尘粒子
    createDustParticles();
    
    // 创建烛光闪烁效果
    createCandleLightEffect();
    
    // 创建环境音效指示器
    createAmbienceIndicator();
    
    // 创建血手光标
    createBloodHandCursor();
}

// 灰尘粒子效果
function createDustParticles() {
    const container = document.createElement('div');
    container.id = 'dust-container';
    container.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 15;
        overflow: hidden;
    `;
    document.body.appendChild(container);
    
    // 创建多个灰尘粒子
    for (let i = 0; i < 20; i++) {
        createSingleDust(container, i);
    }
}

function createSingleDust(container, index) {
    const dust = document.createElement('div');
    const size = Math.random() * 3 + 1;
    const startX = Math.random() * 100;
    const duration = Math.random() * 15 + 10;
    const delay = Math.random() * 10;
    
    dust.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        background: rgba(255, 255, 255, ${Math.random() * 0.2 + 0.1});
        border-radius: 50%;
        left: ${startX}%;
        bottom: -10px;
        animation: dustFloat${index} ${duration}s linear ${delay}s infinite;
    `;
    
    // 创建独特的动画
    const style = document.createElement('style');
    const swayAmount = Math.random() * 100 - 50;
    style.textContent = `
        @keyframes dustFloat${index} {
            0% { 
                transform: translateY(0) translateX(0); 
                opacity: 0; 
            }
            10% { opacity: ${Math.random() * 0.3 + 0.1}; }
            90% { opacity: ${Math.random() * 0.3 + 0.1}; }
            100% { 
                transform: translateY(-100vh) translateX(${swayAmount}px); 
                opacity: 0; 
            }
        }
    `;
    document.head.appendChild(style);
    container.appendChild(dust);
}

// 烛光闪烁效果
function createCandleLightEffect() {
    const light = document.createElement('div');
    light.id = 'candle-light-effect';
    light.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 3;
        background: radial-gradient(ellipse at 50% 20%, rgba(255, 180, 100, 0.03) 0%, transparent 60%);
        animation: candleAmbient 3s ease-in-out infinite;
    `;
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes candleAmbient {
            0%, 100% { opacity: 0.6; transform: scale(1); }
            25% { opacity: 0.8; transform: scale(1.02); }
            50% { opacity: 0.5; transform: scale(0.98); }
            75% { opacity: 0.9; transform: scale(1.01); }
        }
    `;
    document.head.appendChild(style);
    document.body.appendChild(light);
}

// 环境音效指示器
function createAmbienceIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'ambience-text';
    indicator.style.cssText = `
        position: fixed;
        bottom: 15px;
        left: 15px;
        font-size: 0.75rem;
        color: rgba(196, 30, 58, 0.4);
        font-style: italic;
        z-index: 50;
        pointer-events: none;
    `;
    document.body.appendChild(indicator);
    
    // 随机更新环境描述
    const ambiences = [
        '风声呜咽...',
        '远处传来哭声...',
        '木板吱呀作响...',
        '有什么在移动...',
        '寂静...',
        '心跳加速...',
        '阴风阵阵...'
    ];
    
    setInterval(() => {
        if (window.game && window.game.state && window.game.screens.game.classList.contains('active')) {
            if (Math.random() < 0.3) {
                indicator.textContent = ambiences[Math.floor(Math.random() * ambiences.length)];
                indicator.style.opacity = '1';
                setTimeout(() => {
                    indicator.style.opacity = '0';
                    indicator.style.transition = 'opacity 2s';
                }, 3000);
            }
        }
    }, 8000);
}


// ========== 血手光标系统 ==========
function createBloodHandCursor() {
    // 隐藏默认光标
    const cursorStyle = document.createElement('style');
    cursorStyle.id = 'cursor-style';
    cursorStyle.textContent = `
        * { cursor: none !important; }
    `;
    document.head.appendChild(cursorStyle);
    
    // 创建血手光标元素
    const cursor = document.createElement('div');
    cursor.id = 'blood-hand-cursor';
    cursor.innerHTML = createBloodHandSVG(100); // 初始理智100
    cursor.style.cssText = `
        position: fixed;
        pointer-events: none;
        z-index: 10000;
        transform: translate(-50%, -50%);
        transition: filter 0.3s ease;
        will-change: left, top;
    `;
    document.body.appendChild(cursor);
    
    // 创建血迹拖尾容器
    const trailContainer = document.createElement('div');
    trailContainer.id = 'blood-trail-container';
    trailContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9999;
        overflow: hidden;
    `;
    document.body.appendChild(trailContainer);
    
    let lastX = 0, lastY = 0;
    let trailTimer = 0;
    
    // 鼠标移动跟踪
    document.addEventListener('mousemove', (e) => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
        
        // 低理智时留下血迹
        if (window.game && window.game.state) {
            const sanity = window.game.state.sanity;
            
            // 理智越低，血迹越多
            if (sanity < 50 && Date.now() - trailTimer > (sanity * 5 + 100)) {
                const distance = Math.sqrt(Math.pow(e.clientX - lastX, 2) + Math.pow(e.clientY - lastY, 2));
                if (distance > 30) {
                    createBloodTrail(e.clientX, e.clientY, sanity, trailContainer);
                    lastX = e.clientX;
                    lastY = e.clientY;
                    trailTimer = Date.now();
                }
            }
        }
    });
    
    // 点击时的血溅效果
    document.addEventListener('mousedown', (e) => {
        if (window.game && window.game.state && window.game.state.sanity < 60) {
            createBloodSplash(e.clientX, e.clientY, window.game.state.sanity);
        }
        cursor.style.transform = 'translate(-50%, -50%) scale(0.9)';
    });
    
    document.addEventListener('mouseup', () => {
        cursor.style.transform = 'translate(-50%, -50%) scale(1)';
    });
    
    // 定期更新光标外观
    setInterval(() => {
        if (window.game && window.game.state) {
            updateBloodHandCursor(window.game.state.sanity);
        }
    }, 500);
}

// 创建血手SVG
function createBloodHandSVG(sanity) {
    // 根据理智计算颜色和效果
    const bloodIntensity = Math.max(0, (100 - sanity) / 100);
    const baseColor = interpolateColor('#f5deb3', '#8B0000', bloodIntensity);
    const bloodColor = `rgba(139, 0, 0, ${0.3 + bloodIntensity * 0.7})`;
    const glowIntensity = bloodIntensity * 20;
    
    // 手指抖动程度
    const shake = sanity < 30 ? 2 : (sanity < 50 ? 1 : 0);
    
    return `
        <svg width="40" height="50" viewBox="0 0 40 50" xmlns="http://www.w3.org/2000/svg" 
             style="filter: drop-shadow(0 0 ${glowIntensity}px ${bloodColor});">
            <!-- 手掌 -->
            <path d="M12 45 Q8 35 10 25 L12 15 Q13 12 15 15 L16 22 
                     L17 10 Q18 7 20 10 L21 22
                     L22 8 Q23 5 25 8 L26 22
                     L27 10 Q28 7 30 10 L30 22
                     L32 18 Q34 15 35 18 L33 28 Q35 35 30 45 Z" 
                  fill="${baseColor}" 
                  stroke="#4a3728" 
                  stroke-width="0.5"
                  transform="rotate(${shake * (Math.random() - 0.5)}, 20, 25)"/>
            
            <!-- 血迹 - 根据理智显示 -->
            ${sanity < 80 ? `<ellipse cx="18" cy="30" rx="${3 + bloodIntensity * 3}" ry="${4 + bloodIntensity * 4}" fill="${bloodColor}" opacity="${0.5 + bloodIntensity * 0.5}"/>` : ''}
            ${sanity < 60 ? `<ellipse cx="25" cy="35" rx="${2 + bloodIntensity * 2}" ry="${3 + bloodIntensity * 3}" fill="${bloodColor}" opacity="${0.6 + bloodIntensity * 0.4}"/>` : ''}
            ${sanity < 40 ? `<path d="M15 25 Q14 30 16 38 Q15 42 14 45" stroke="${bloodColor}" stroke-width="${1 + bloodIntensity * 2}" fill="none" opacity="0.8"/>` : ''}
            ${sanity < 30 ? `<path d="M28 22 Q30 28 28 35 Q29 40 27 45" stroke="${bloodColor}" stroke-width="${1 + bloodIntensity * 2}" fill="none" opacity="0.7"/>` : ''}
            ${sanity < 20 ? `
                <ellipse cx="20" cy="20" rx="4" ry="5" fill="${bloodColor}" opacity="0.9"/>
                <ellipse cx="30" cy="25" rx="3" ry="4" fill="${bloodColor}" opacity="0.8"/>
                <path d="M10 30 L8 45" stroke="${bloodColor}" stroke-width="3" opacity="0.9"/>
            ` : ''}
            
            <!-- 指甲 - 低理智时变黑 -->
            ${sanity < 50 ? `
                <ellipse cx="15" cy="14" rx="2" ry="1.5" fill="${interpolateColor('#d4a574', '#1a0505', bloodIntensity)}"/>
                <ellipse cx="20" cy="9" rx="2" ry="1.5" fill="${interpolateColor('#d4a574', '#1a0505', bloodIntensity)}"/>
                <ellipse cx="25" cy="7" rx="2" ry="1.5" fill="${interpolateColor('#d4a574', '#1a0505', bloodIntensity)}"/>
                <ellipse cx="30" cy="9" rx="2" ry="1.5" fill="${interpolateColor('#d4a574', '#1a0505', bloodIntensity)}"/>
                <ellipse cx="34" cy="17" rx="2" ry="1.5" fill="${interpolateColor('#d4a574', '#1a0505', bloodIntensity)}"/>
            ` : ''}
        </svg>
    `;
}

// 颜色插值
function interpolateColor(color1, color2, factor) {
    const c1 = hexToRgb(color1);
    const c2 = hexToRgb(color2);
    const r = Math.round(c1.r + (c2.r - c1.r) * factor);
    const g = Math.round(c1.g + (c2.g - c1.g) * factor);
    const b = Math.round(c1.b + (c2.b - c1.b) * factor);
    return `rgb(${r}, ${g}, ${b})`;
}

function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : { r: 0, g: 0, b: 0 };
}

// 更新血手光标
function updateBloodHandCursor(sanity) {
    const cursor = document.getElementById('blood-hand-cursor');
    if (cursor) {
        cursor.innerHTML = createBloodHandSVG(sanity);
        
        // 低理智时光标抖动
        if (sanity < 30) {
            cursor.style.animation = 'cursorShake 0.1s infinite';
        } else if (sanity < 50) {
            cursor.style.animation = 'cursorShake 0.3s infinite';
        } else {
            cursor.style.animation = 'none';
        }
    }
}

// 创建血迹拖尾
function createBloodTrail(x, y, sanity, container) {
    const trail = document.createElement('div');
    const size = Math.random() * 8 + 4;
    const opacity = (100 - sanity) / 150;
    
    trail.style.cssText = `
        position: fixed;
        left: ${x}px;
        top: ${y}px;
        width: ${size}px;
        height: ${size}px;
        background: radial-gradient(ellipse, rgba(139, 0, 0, ${opacity}) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
        animation: bloodTrailFade 3s ease forwards;
    `;
    
    container.appendChild(trail);
    setTimeout(() => trail.remove(), 3000);
}

// 创建血溅效果
function createBloodSplash(x, y, sanity) {
    const splashCount = Math.floor((100 - sanity) / 20) + 1;
    
    for (let i = 0; i < splashCount; i++) {
        const splash = document.createElement('div');
        const size = Math.random() * 10 + 5;
        const angle = Math.random() * Math.PI * 2;
        const distance = Math.random() * 30 + 10;
        const endX = x + Math.cos(angle) * distance;
        const endY = y + Math.sin(angle) * distance;
        
        splash.style.cssText = `
            position: fixed;
            left: ${x}px;
            top: ${y}px;
            width: ${size}px;
            height: ${size}px;
            background: rgba(139, 0, 0, ${0.6 + Math.random() * 0.4});
            border-radius: 50%;
            pointer-events: none;
            z-index: 9998;
            animation: bloodSplash${i} 0.5s ease forwards;
        `;
        
        const style = document.createElement('style');
        style.textContent = `
            @keyframes bloodSplash${i} {
                0% { transform: translate(0, 0) scale(1); opacity: 1; }
                100% { transform: translate(${endX - x}px, ${endY - y}px) scale(0.3); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(splash);
        setTimeout(() => splash.remove(), 500);
    }
}

// 添加光标动画样式
const cursorAnimStyle = document.createElement('style');
cursorAnimStyle.textContent = `
    @keyframes cursorShake {
        0%, 100% { transform: translate(-50%, -50%) rotate(0deg); }
        25% { transform: translate(-48%, -52%) rotate(-2deg); }
        50% { transform: translate(-52%, -48%) rotate(2deg); }
        75% { transform: translate(-50%, -50%) rotate(-1deg); }
    }
    
    @keyframes bloodTrailFade {
        0% { opacity: 1; transform: scale(1); }
        100% { opacity: 0; transform: scale(0.5); }
    }
`;
document.head.appendChild(cursorAnimStyle);
