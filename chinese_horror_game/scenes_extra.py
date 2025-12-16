"""
额外场景 - 更多恐怖内容
"""

EXTRA_SCENES = {
    'side_room_danger': {
        'title': '危险',
        'text': '''
        <p class="narration">你撕掉符纸，推开侧门。</p>
        <p class="narration">门内一片漆黑，但你能感觉到有什么东西在注视着你。</p>
        <p class="narration">突然，无数双手从黑暗中伸出，抓住了你！</p>
        <p class="horror">冰冷的触感让你浑身发抖...</p>
        <p class="narration">你拼命挣扎，终于挣脱了那些手，跌跌撞撞地逃了出来。</p>
        <p class="narration">回头望去，门内站满了纸人，它们的眼睛都在看着你...</p>
        ''',
        'background': 'paper_army',
        'ambience': 'grabbing',
        'sanity_effect': -20,
        'add_flag': 'broke_talisman',
        'choices': [
            {'text': '逃向正厅', 'next': 'main_hall_panic', 'sanity_change': -10}
        ]
    },
    
    'wait_in_study': {
        'title': '等待',
        'text': '''
        <p class="narration">你决定在书房里等一会儿。</p>
        <p class="narration">你靠在墙边，努力平复自己的呼吸。</p>
        <p class="narration">书房里很安静，只有老旧时钟的滴答声。</p>
        <p class="narration">渐渐地，你的心情平静了下来。</p>
        <p class="detail">也许...这里是安全的。</p>
        <p class="narration">你注意到桌上的日记和墙上的画像。</p>
        ''',
        'background': 'study_calm',
        'ambience': 'clock',
        'choices': [
            {'text': '阅读日记', 'next': 'read_diary', 'sanity_change': -5},
            {'text': '查看画像', 'next': 'examine_portrait', 'sanity_change': -10},
            {'text': '小心地出去', 'next': 'main_hall', 'sanity_change': 0}
        ]
    }
}


EXTRA_SCENES.update({
    'main_hall_retreat': {
        'title': '后退',
        'text': '''
        <p class="narration">你慢慢后退，不敢发出一点声音。</p>
        <p class="narration">那两个纸人一动不动，但你总觉得它们在跟着你移动。</p>
        <p class="narration">你的后背撞到了什么东西——</p>
        <p class="horror">是第三个纸人。</p>
        <p class="narration">你惊叫一声，向旁边闪去。</p>
        <p class="narration">借着微弱的光线，你看到通往后院的走廊。</p>
        ''',
        'background': 'three_figures',
        'ambience': 'static',
        'sanity_effect': -5,
        'choices': [
            {'text': '冲向后院', 'next': 'backyard_path', 'sanity_change': -5},
            {'text': '躲进东厢房', 'next': 'east_wing_hide', 'sanity_change': 0}
        ]
    },
    
    'shout_at_figures': {
        'title': '呵斥',
        'text': '''
        <p class="narration">"滚开！"你大声呵斥。</p>
        <p class="narration">你的声音在空荡的正厅中回响。</p>
        <p class="narration">纸人没有动，但你听到了回应——</p>
        <p class="horror">是你自己的声音，从四面八方传来。</p>
        <p class="whisper">"滚开...滚开...滚开..."</p>
        <p class="narration">声音越来越多，越来越尖锐，像是无数个你在同时说话。</p>
        <p class="horror">然后，所有的声音突然停止。</p>
        <p class="narration">死一般的寂静中，你听到纸人发出"咯咯"的笑声...</p>
        ''',
        'background': 'echo',
        'ambience': 'echo_voices',
        'sanity_effect': -20,
        'choices': [
            {'text': '逃跑', 'next': 'escape_hall', 'sanity_change': -10}
        ]
    },
    
    'close_eyes': {
        'title': '闭眼',
        'text': '''
        <p class="narration">你闭上眼睛，在心中默念。</p>
        <p class="narration">"它们不是真的...它们不是真的..."</p>
        <p class="narration">你感到有什么东西在你面前移动，冰冷的气息拂过你的脸。</p>
        <p class="horror">有什么东西...在闻你的味道。</p>
        <p class="narration">你屏住呼吸，一动不动。</p>
        <p class="narration">过了很久，那股气息消失了。</p>
        <p class="narration">你睁开眼睛——纸人不见了。</p>
        <p class="detail">但你知道，它们还在这里，在某个你看不到的地方...</p>
        ''',
        'background': 'empty_hall',
        'ambience': 'breathing',
        'add_secret': '纸人的习性',
        'choices': [
            {'text': '去后院', 'next': 'backyard_path', 'sanity_change': 0},
            {'text': '去东厢房', 'next': 'east_wing', 'sanity_change': 0}
        ]
    },
    
    'escape_study': {
        'title': '逃离书房',
        'text': '''
        <p class="narration">你转身冲出书房，身后传来画像中女子的笑声。</p>
        <p class="horror">"跑吧...跑吧...你跑不掉的..."</p>
        <p class="narration">你冲进走廊，大口喘着气。</p>
        <p class="narration">回头望去，书房的门自己关上了。</p>
        <p class="narration">你听到门内传来轻轻的歌声...</p>
        <p class="whisper">"红嫁衣，红盖头，新娘子，莫回头..."</p>
        ''',
        'background': 'corridor',
        'ambience': 'singing',
        'sanity_effect': -5,
        'choices': [
            {'text': '去后院', 'next': 'backyard_path', 'sanity_change': 0},
            {'text': '去西厢房', 'next': 'west_wing', 'sanity_change': 0},
            {'text': '返回正厅', 'next': 'main_hall', 'sanity_change': 0}
        ]
    },
    
    'confront_portrait': {
        'title': '质问',
        'text': '''
        <p class="narration">"你是谁？你想要什么？"你颤抖着问道。</p>
        <p class="narration">画中的女子歪着头，露出诡异的笑容。</p>
        <p class="horror">"我？我是这里的新娘..."</p>
        <p class="narration">"六十年前，我本该嫁入陈家..."</p>
        <p class="narration">"但他们...他们烧死了我..."</p>
        <p class="horror">她的脸突然扭曲，变得狰狞可怖。</p>
        <p class="horror">"现在...我要他们偿命！"</p>
        <p class="narration">画像中伸出一只苍白的手，向你抓来！</p>
        ''',
        'background': 'portrait_attack',
        'ambience': 'scream',
        'sanity_effect': -15,
        'choices': [
            {'text': '躲开', 'next': 'dodge_portrait', 'sanity_change': -10},
            {'text': '用火折子', 'next': 'burn_portrait', 'sanity_change': -10, 'require_item': '火折子'}
        ]
    },
    
    'dodge_portrait': {
        'title': '躲避',
        'text': '''
        <p class="narration">你向旁边一闪，那只手擦着你的脸颊划过。</p>
        <p class="horror">冰冷刺骨的触感让你打了个寒颤。</p>
        <p class="narration">你跌跌撞撞地后退，撞翻了书桌上的东西。</p>
        <p class="narration">画中的女子发出尖锐的笑声，然后渐渐消失。</p>
        <p class="narration">画像恢复了原状，但那张被划破的脸似乎在嘲笑你。</p>
        <p class="detail">你注意到地上掉落了一把钥匙...</p>
        ''',
        'background': 'study_mess',
        'ambience': 'laughter',
        'sanity_effect': -10,
        'add_item': '西厢房钥匙',
        'choices': [
            {'text': '捡起钥匙，去西厢房', 'next': 'west_wing_key', 'sanity_change': 0},
            {'text': '离开书房', 'next': 'escape_study', 'sanity_change': 0}
        ]
    }
})


EXTRA_SCENES.update({
    'turn_around': {
        'title': '转身',
        'text': '''
        <p class="narration">你慢慢转过身去。</p>
        <p class="narration">她就站在你身后，近在咫尺。</p>
        <p class="narration">红色的嫁衣，苍白的脸，空洞的眼眶。</p>
        <p class="horror">她的嘴角挂着诡异的笑容，露出一口黑色的牙齿。</p>
        <p class="horror">"找到你了..."</p>
        <p class="narration">她伸出手，冰冷的手指触碰你的脸。</p>
        <p class="narration">你感到一阵眩晕，眼前一黑...</p>
        ''',
        'background': 'axiu_close',
        'ambience': 'heartbeat',
        'sanity_effect': -20,
        'choices': [
            {'text': '挣扎', 'next': 'struggle_axiu', 'sanity_change': -15},
            {'text': '闭上眼睛', 'next': 'close_eyes_axiu', 'sanity_change': -10}
        ]
    },
    
    'run_without_looking': {
        'title': '逃跑',
        'text': '''
        <p class="narration">你不敢回头，拔腿就跑。</p>
        <p class="narration">身后传来轻轻的笑声，像是在嘲笑你的徒劳。</p>
        <p class="narration">你冲出书房，沿着走廊狂奔。</p>
        <p class="narration">不知跑了多久，你终于停下来，大口喘着气。</p>
        <p class="narration">回头望去，走廊空无一人。</p>
        <p class="detail">但你知道，她还在某处看着你...</p>
        ''',
        'background': 'corridor_dark',
        'ambience': 'running',
        'sanity_effect': -5,
        'choices': [
            {'text': '去后院', 'next': 'backyard_path', 'sanity_change': 0},
            {'text': '去西厢房', 'next': 'west_wing', 'sanity_change': 0}
        ]
    },
    
    'struggle_axiu': {
        'title': '挣扎',
        'text': '''
        <p class="narration">你拼命挣扎，试图挣脱她的控制。</p>
        <p class="narration">但她的力量大得惊人，你根本无法动弹。</p>
        <p class="horror">"别挣扎了...你逃不掉的..."</p>
        <p class="narration">她的脸凑近你，你能闻到一股腐朽的气息。</p>
        <p class="horror">"陈家的人...都要陪我..."</p>
        <p class="narration">就在你以为一切都完了的时候，远处传来鸡鸣声。</p>
        <p class="narration">阿绣的身影突然变得虚幻，她发出一声尖叫，消失在空气中。</p>
        <p class="detail">天...快亮了。</p>
        ''',
        'background': 'dawn',
        'ambience': 'rooster',
        'sanity_effect': -15,
        'add_flag': 'survived_axiu',
        'choices': [
            {'text': '趁天亮去地下室', 'next': 'basement_entrance', 'sanity_change': 0},
            {'text': '趁天亮逃离老宅', 'next': 'try_escape_dawn', 'sanity_change': 0}
        ]
    },
    
    'close_eyes_axiu': {
        'title': '闭眼',
        'text': '''
        <p class="narration">你闭上眼睛，不敢看她。</p>
        <p class="narration">你感到她的手在你脸上游走，冰冷刺骨。</p>
        <p class="horror">"你...不敢看我？"</p>
        <p class="narration">她的声音中带着一丝悲伤。</p>
        <p class="horror">"六十年了...没有人敢看我..."</p>
        <p class="narration">她的手停了下来，你感到她在颤抖。</p>
        <p class="narration">"我...我只是想...有人记得我..."</p>
        <p class="narration">当你再次睁开眼睛时，她已经消失了。</p>
        <p class="detail">地上留下一滴血泪...</p>
        ''',
        'background': 'blood_tear',
        'ambience': 'crying',
        'sanity_effect': -10,
        'add_secret': '阿绣的悲伤',
        'choices': [
            {'text': '去地下室', 'next': 'basement_entrance', 'sanity_change': 0},
            {'text': '去后院', 'next': 'backyard_path', 'sanity_change': 0}
        ]
    },
    
    'try_escape_dawn': {
        'title': '逃离',
        'text': '''
        <p class="narration">你趁着天亮，向老宅大门跑去。</p>
        <p class="narration">大门就在眼前，你伸手去推——</p>
        <p class="narration">门纹丝不动。</p>
        <p class="narration">你用尽全力，门依然不动。</p>
        <p class="detail">门上的符文闪烁着微弱的光芒...</p>
        <p class="narration">你意识到，在完成封印之前，你无法离开这里。</p>
        <p class="horror">这座老宅...不会让你离开。</p>
        ''',
        'background': 'locked_gate',
        'ambience': 'wind',
        'choices': [
            {'text': '去地下室完成封印', 'next': 'basement_entrance', 'sanity_change': -5},
            {'text': '去西厢房找封印方法', 'next': 'west_wing', 'sanity_change': 0}
        ]
    },
    
    'examine_paper_offerings': {
        'title': '纸扎',
        'text': '''
        <p class="narration">你查看那些纸扎物品。</p>
        <p class="narration">纸人、纸马、纸房子...还有一顶纸做的花轿。</p>
        <p class="narration">这些都是给死人的陪葬品。</p>
        <p class="detail">你注意到每个纸人的胸口都贴着一张符纸，上面写着名字。</p>
        <p class="narration">你凑近看了看那些名字——</p>
        <p class="horror">都是陈家的人。</p>
        <p class="narration">你的名字...也在其中。</p>
        ''',
        'background': 'paper_offerings',
        'ambience': 'whisper',
        'sanity_effect': -10,
        'add_secret': '纸人的秘密',
        'choices': [
            {'text': '撕掉写着你名字的符纸', 'next': 'tear_talisman', 'sanity_change': -5},
            {'text': '查看神龛后面', 'next': 'behind_shrine', 'sanity_change': 0},
            {'text': '离开这里', 'next': 'main_hall', 'sanity_change': 0}
        ]
    },
    
    'tear_talisman': {
        'title': '撕符',
        'text': '''
        <p class="narration">你伸手撕下那张写着你名字的符纸。</p>
        <p class="narration">符纸在你手中化为灰烬。</p>
        <p class="narration">那个纸人突然倒下，像是失去了生命。</p>
        <p class="detail">你松了一口气。</p>
        <p class="narration">但就在这时，你听到身后传来声音：</p>
        <p class="horror">"你...撕了我的符..."</p>
        <p class="narration">你猛地转身，看到阿绣站在门口。</p>
        <p class="horror">"那是...我为你准备的..."</p>
        ''',
        'background': 'axiu_door',
        'ambience': 'ghost_voice',
        'sanity_effect': -5,
        'add_flag': 'tore_talisman',
        'choices': [
            {'text': '与她对话', 'next': 'talk_to_axiu_final', 'sanity_change': -10},
            {'text': '拿起骨灰坛进行封印', 'next': 'seal_ritual', 'sanity_change': 0, 'require_flag': 'have_seal_items'}
        ]
    },
    
    'west_wing_force': {
        'title': '强行进入',
        'text': '''
        <p class="narration">你撕掉符纸，用力推开门。</p>
        <p class="narration">门"砰"地一声打开，一股阴冷的气息扑面而来。</p>
        <p class="narration">房间里漆黑一片，你什么也看不见。</p>
        <p class="narration">突然，无数双眼睛在黑暗中亮起，都在看着你。</p>
        <p class="horror">那是纸人的眼睛。</p>
        <p class="narration">它们开始向你移动...</p>
        ''',
        'background': 'paper_eyes',
        'ambience': 'rustling',
        'sanity_effect': -20,
        'choices': [
            {'text': '逃跑', 'next': 'escape_west_wing', 'sanity_change': -10},
            {'text': '用火折子', 'next': 'fire_west_wing', 'sanity_change': 0, 'require_item': '火折子'}
        ]
    },
    
    'escape_west_wing': {
        'title': '逃离西厢房',
        'text': '''
        <p class="narration">你转身就跑，身后传来"沙沙"的声音。</p>
        <p class="narration">那些纸人在追你。</p>
        <p class="narration">你冲出西厢房，重重地关上门。</p>
        <p class="narration">门内传来"咚咚"的撞击声，但门没有被撞开。</p>
        <p class="detail">符纸虽然被撕掉了，但门上的封印似乎还有残余的力量...</p>
        ''',
        'background': 'corridor_escape',
        'ambience': 'banging',
        'sanity_effect': -10,
        'choices': [
            {'text': '去后院', 'next': 'backyard_path', 'sanity_change': 0},
            {'text': '去东厢房', 'next': 'east_wing', 'sanity_change': 0}
        ]
    },
    
    'fire_west_wing': {
        'title': '火光',
        'text': '''
        <p class="narration">你点燃火折子，火光照亮了房间。</p>
        <p class="narration">那些纸人发出尖叫，纷纷后退。</p>
        <p class="narration">借着火光，你看到房间里摆满了纸扎物品，正中央是一个神龛。</p>
        <p class="detail">神龛上供奉着一个牌位：亡妻阿绣之灵位。</p>
        <p class="narration">纸人们退到墙角，用那空洞的眼睛注视着你。</p>
        <p class="narration">它们不敢靠近火光。</p>
        ''',
        'background': 'west_wing_lit',
        'ambience': 'fire',
        'add_secret': '纸人怕火',
        'add_flag': 'know_fire_weakness',
        'choices': [
            {'text': '查看神龛后面', 'next': 'behind_shrine', 'sanity_change': 0},
            {'text': '烧掉这些纸人', 'next': 'burn_paper_army', 'sanity_change': -10}
        ]
    },
    
    'burn_paper_army': {
        'title': '焚烧',
        'text': '''
        <p class="narration">你将火折子凑近那些纸人。</p>
        <p class="narration">它们发出凄厉的惨叫，像是真的有生命一样。</p>
        <p class="narration">火焰迅速蔓延，整个房间都燃烧起来。</p>
        <p class="horror">在火光中，你看到那些纸人扭曲、挣扎、化为灰烬。</p>
        <p class="narration">突然，一个声音在你耳边响起：</p>
        <p class="horror">"你...烧了我的仆人..."</p>
        <p class="narration">阿绣的身影在火焰中显现，她的脸扭曲着愤怒。</p>
        <p class="horror">"你会后悔的..."</p>
        ''',
        'background': 'burning_room',
        'ambience': 'fire_scream',
        'sanity_effect': -10,
        'add_flag': 'burned_paper_army',
        'choices': [
            {'text': '趁乱拿走神龛后的东西', 'next': 'grab_seal_items', 'sanity_change': -5},
            {'text': '逃出房间', 'next': 'escape_burning_room', 'sanity_change': 0}
        ]
    }
})


EXTRA_SCENES.update({
    'grab_seal_items': {
        'title': '夺取',
        'text': '''
        <p class="narration">你冲向神龛，在火焰中摸索。</p>
        <p class="narration">你的手被烫伤了，但你不顾疼痛，抓住了神龛后的布包。</p>
        <p class="narration">阿绣向你扑来，但火焰阻挡了她。</p>
        <p class="horror">"不！那是我的！"</p>
        <p class="narration">你抱着布包冲出房间，身后传来她愤怒的尖叫。</p>
        <p class="detail">布包里是朱砂和镇魂符。</p>
        ''',
        'background': 'escape_fire',
        'ambience': 'fire_escape',
        'add_item': '朱砂',
        'add_item2': '镇魂符',
        'add_flag': 'have_seal_items',
        'choices': [
            {'text': '去地下室完成封印', 'next': 'basement_entrance', 'sanity_change': -5}
        ]
    },
    
    'escape_burning_room': {
        'title': '逃离',
        'text': '''
        <p class="narration">你冲出燃烧的房间，火焰在你身后蔓延。</p>
        <p class="narration">阿绣的尖叫声在火焰中回荡。</p>
        <p class="narration">你跑到走廊，回头望去，西厢房已经被火焰吞噬。</p>
        <p class="detail">但你知道，这火烧不死她。</p>
        <p class="narration">你需要找到其他方法来封印她。</p>
        ''',
        'background': 'corridor_fire',
        'ambience': 'fire_distant',
        'choices': [
            {'text': '去地下室', 'next': 'basement_entrance', 'sanity_change': 0},
            {'text': '去东厢房找线索', 'next': 'east_wing', 'sanity_change': 0}
        ]
    },
    
    'escape_from_axiu': {
        'title': '逃离',
        'text': '''
        <p class="narration">你转身就跑，不敢回头。</p>
        <p class="narration">阿绣的笑声在身后响起，像是在嘲笑你的徒劳。</p>
        <p class="horror">"跑吧...跑吧...你跑不出这里的..."</p>
        <p class="narration">你拼命奔跑，穿过后院，冲进走廊。</p>
        <p class="narration">当你停下来喘息时，发现自己来到了地下室入口。</p>
        <p class="detail">也许...答案就在地下室里。</p>
        ''',
        'background': 'basement_entrance',
        'ambience': 'running',
        'sanity_effect': -10,
        'choices': [
            {'text': '进入地下室', 'next': 'basement', 'sanity_change': -10}
        ]
    },
    
    'confront_axiu': {
        'title': '质问',
        'text': '''
        <p class="narration">"你为什么要杀我父亲？"你颤抖着问道。</p>
        <p class="narration">阿绣歪着头，露出诡异的笑容。</p>
        <p class="horror">"杀？我没有杀他..."</p>
        <p class="narration">"他是自己跳下去的..."</p>
        <p class="narration">"他说...他要陪我..."</p>
        <p class="horror">她的笑容变得更加诡异。</p>
        <p class="horror">"就像你...也会陪我一样..."</p>
        <p class="narration">她向你伸出手，冰冷的气息扑面而来。</p>
        ''',
        'background': 'axiu_reaching',
        'ambience': 'ghost_voice',
        'sanity_effect': -15,
        'choices': [
            {'text': '后退', 'next': 'retreat_from_axiu', 'sanity_change': -10},
            {'text': '用火折子', 'next': 'fire_at_axiu', 'sanity_change': 0, 'require_item': '火折子'}
        ]
    },
    
    'fire_at_axiu': {
        'title': '火焰',
        'text': '''
        <p class="narration">你举起火折子，火焰在你手中跳动。</p>
        <p class="narration">阿绣看到火焰，脸上露出恐惧的表情。</p>
        <p class="horror">"不...不要...火..."</p>
        <p class="narration">她后退了几步，身影变得虚幻。</p>
        <p class="narration">"你...你想再烧死我一次吗？"</p>
        <p class="narration">她的声音中带着恐惧和愤怒。</p>
        <p class="horror">"我不会让你得逞的！"</p>
        <p class="narration">她消失在空气中，但你知道她还会回来。</p>
        ''',
        'background': 'fire_ghost',
        'ambience': 'ghost_scream',
        'add_secret': '阿绣怕火',
        'choices': [
            {'text': '趁机去地下室', 'next': 'basement', 'sanity_change': 0},
            {'text': '去后院找骨灰坛', 'next': 'backyard_path', 'sanity_change': 0}
        ]
    },
    
    'retreat_from_axiu': {
        'title': '后退',
        'text': '''
        <p class="narration">你慢慢后退，不敢转身。</p>
        <p class="narration">阿绣一步步向你逼近，她的脚不着地，像是飘浮着。</p>
        <p class="horror">"别怕...我不会伤害你..."</p>
        <p class="narration">她的声音像是在哄骗孩子。</p>
        <p class="horror">"我只是...想要一个伴..."</p>
        <p class="narration">你的后背撞到了墙，无路可退。</p>
        <p class="narration">就在她即将触碰到你的时候，远处传来鸡鸣声。</p>
        <p class="narration">阿绣的身影瞬间消散，像是被阳光驱散的阴影。</p>
        ''',
        'background': 'dawn_light',
        'ambience': 'rooster',
        'sanity_effect': -10,
        'choices': [
            {'text': '趁天亮去地下室', 'next': 'basement_entrance', 'sanity_change': 0}
        ]
    },
    
    'retreat_from_coffin': {
        'title': '后退',
        'text': '''
        <p class="narration">你惊恐地后退，撞翻了身后的东西。</p>
        <p class="narration">棺材中的尸体缓缓站起，红盖头下传出沙哑的声音：</p>
        <p class="horror">"别走...陪我..."</p>
        <p class="narration">她向你伸出干枯的手，指甲又长又黑。</p>
        <p class="narration">你转身就跑，冲向地下室的出口。</p>
        <p class="narration">身后传来"沙沙"的脚步声，越来越近...</p>
        ''',
        'background': 'chase',
        'ambience': 'chase_music',
        'sanity_effect': -10,
        'choices': [
            {'text': '继续跑', 'next': 'escape_basement', 'sanity_change': -5},
            {'text': '转身用火折子', 'next': 'fire_at_corpse', 'sanity_change': 0, 'require_item': '火折子'}
        ]
    },
    
    'lift_veil': {
        'title': '揭开',
        'text': '''
        <p class="narration">你伸手揭开红盖头。</p>
        <p class="narration">盖头下是一张美丽却苍白的脸，眼睛紧闭。</p>
        <p class="narration">就在你以为她只是一具尸体时——</p>
        <p class="horror">她的眼睛突然睁开！</p>
        <p class="narration">那是一双漆黑的眼睛，没有眼白，像是两个深渊。</p>
        <p class="horror">"你...看到我了..."</p>
        <p class="narration">她的嘴角上扬，露出诡异的笑容。</p>
        <p class="horror">"现在...你是我的了..."</p>
        <p class="narration">你感到一阵剧烈的眩晕，眼前一黑...</p>
        ''',
        'background': 'black_eyes',
        'ambience': 'possession',
        'sanity_effect': -25,
        'choices': [
            {'text': '挣扎', 'next': 'struggle_possession', 'sanity_change': -20},
            {'text': '放弃抵抗', 'next': 'ending_possessed', 'sanity_change': -50}
        ]
    },
    
    'struggle_possession': {
        'title': '挣扎',
        'text': '''
        <p class="narration">你拼命挣扎，试图摆脱她的控制。</p>
        <p class="narration">你的意识在黑暗中漂浮，像是溺水一般。</p>
        <p class="narration">你想起父亲的话："不要直视她的眼睛..."</p>
        <p class="narration">你闭上眼睛，在心中默念。</p>
        <p class="narration">"我不属于这里...我不属于这里..."</p>
        <p class="narration">渐渐地，黑暗开始消退，你感到自己的意识在回归。</p>
        <p class="narration">当你再次睁开眼睛时，你躺在地下室的地上，浑身冰冷。</p>
        <p class="detail">阿绣不见了，但你知道她还在这里。</p>
        ''',
        'background': 'basement_floor',
        'ambience': 'heavy_breathing',
        'sanity_effect': -20,
        'choices': [
            {'text': '拿起骨灰坛进行封印', 'next': 'take_urn_after_burn', 'sanity_change': 0}
        ]
    },
    
    'ending_possessed': {
        'title': '结局 · 附身',
        'text': '''
        <p class="narration">你放弃了抵抗，任由黑暗将你吞噬。</p>
        <p class="narration">你感到自己的意识在消散，被另一个存在取代。</p>
        <p class="narration">当你再次"醒来"时，你发现自己站在镜子前。</p>
        <p class="narration">镜中的你穿着红色的嫁衣，脸上带着诡异的笑容。</p>
        <p class="horror">那不是你的笑容。</p>
        <p class="narration">阿绣的声音在你脑海中响起：</p>
        <p class="horror">"谢谢你...给了我一个新的身体..."</p>
        <p class="ending">【附身结局】</p>
        <p class="ending">你的身体被阿绣占据，你的灵魂被困在黑暗中。</p>
        <p class="ending">也许有一天，会有人来救你...</p>
        <p class="ending">但那一天，可能永远不会到来。</p>
        ''',
        'background': 'mirror_bride',
        'ambience': 'possession_complete',
        'is_ending': True,
        'ending_type': 'possessed',
        'choices': [
            {'text': '重新开始', 'next': 'prologue', 'sanity_change': 0, 'reset': True}
        ]
    },
    
    'burn_coffin': {
        'title': '焚烧棺材',
        'text': '''
        <p class="narration">你将火折子凑近棺材，火焰舔上干燥的木头。</p>
        <p class="narration">棺材开始燃烧，里面的尸体发出凄厉的惨叫。</p>
        <p class="horror">"不！不要！"</p>
        <p class="narration">阿绣的身影从火焰中冲出，向你扑来。</p>
        <p class="narration">但火焰阻挡了她，她只能在火焰外徘徊。</p>
        <p class="horror">"你...你会后悔的！"</p>
        <p class="narration">棺材化为灰烬，阿绣的力量明显减弱了。</p>
        <p class="detail">现在是完成封印的最好时机。</p>
        ''',
        'background': 'burning_coffin',
        'ambience': 'fire_scream',
        'add_flag': 'burned_coffin',
        'add_secret': '焚烧棺材',
        'choices': [
            {'text': '拿起骨灰坛进行封印', 'next': 'seal_ritual', 'sanity_change': 0, 'require_flag': 'have_seal_items'},
            {'text': '先拿骨灰坛', 'next': 'take_urn_after_burn', 'sanity_change': 0}
        ]
    },
    
    'examine_coffin_after_burn': {
        'title': '棺材',
        'text': '''
        <p class="narration">焚烧嫁衣后，你走近棺材查看。</p>
        <p class="narration">棺材里的尸体一动不动，似乎失去了生命力。</p>
        <p class="narration">阿绣的力量被削弱了，但她还没有被消灭。</p>
        <p class="detail">你需要完成封印才能彻底解决问题。</p>
        ''',
        'background': 'coffin_quiet',
        'ambience': 'silence',
        'choices': [
            {'text': '拿起骨灰坛进行封印', 'next': 'seal_ritual', 'sanity_change': 0, 'require_flag': 'have_seal_items'},
            {'text': '先拿骨灰坛', 'next': 'take_urn_after_burn', 'sanity_change': 0}
        ]
    },
    
    'turn_to_axiu': {
        'title': '转身',
        'text': '''
        <p class="narration">你慢慢转过身去。</p>
        <p class="narration">阿绣就站在你身后，红衣飘飘，长发遮面。</p>
        <p class="horror">"你...拿了我的骨灰..."</p>
        <p class="narration">她的声音低沉而怨毒。</p>
        <p class="horror">"你想...封印我？"</p>
        <p class="narration">她向你伸出手，冰冷的气息扑面而来。</p>
        ''',
        'background': 'axiu_basement',
        'ambience': 'ghost_voice',
        'sanity_effect': -15,
        'choices': [
            {'text': '立即进行封印', 'next': 'seal_ritual', 'sanity_change': -10, 'require_flag': 'have_seal_items'},
            {'text': '与她对话', 'next': 'talk_to_axiu_final', 'sanity_change': -5}
        ]
    },
    
    'escape_with_urn': {
        'title': '逃跑',
        'text': '''
        <p class="narration">你抱着骨灰坛，转身就跑。</p>
        <p class="narration">阿绣的尖叫声在身后响起：</p>
        <p class="horror">"把它还给我！"</p>
        <p class="narration">你冲出地下室，跑进后院。</p>
        <p class="narration">月光下，你看到阿绣的身影在你身后飘荡。</p>
        <p class="narration">你无处可逃，只能在这里完成封印。</p>
        ''',
        'background': 'backyard_chase',
        'ambience': 'chase_music',
        'sanity_effect': -10,
        'choices': [
            {'text': '进行封印', 'next': 'seal_ritual', 'sanity_change': -5, 'require_flag': 'have_seal_items'},
            {'text': '继续跑', 'next': 'endless_chase', 'sanity_change': -15}
        ]
    },
    
    'endless_chase': {
        'title': '无尽追逐',
        'text': '''
        <p class="narration">你继续跑，但无论你跑到哪里，阿绣都在你身后。</p>
        <p class="narration">你跑过正厅，跑过走廊，跑过后院...</p>
        <p class="narration">但你始终无法摆脱她。</p>
        <p class="horror">"你跑不掉的..."</p>
        <p class="narration">她的声音像是从四面八方传来。</p>
        <p class="narration">你精疲力竭地停下，大口喘着气。</p>
        <p class="detail">你必须面对她。</p>
        ''',
        'background': 'exhausted',
        'ambience': 'heavy_breathing',
        'sanity_effect': -15,
        'choices': [
            {'text': '进行封印', 'next': 'seal_ritual', 'sanity_change': -10, 'require_flag': 'have_seal_items'},
            {'text': '与她对话', 'next': 'talk_to_axiu_final', 'sanity_change': -5}
        ]
    },
    
    'escape_basement': {
        'title': '逃离地下室',
        'text': '''
        <p class="narration">你冲上楼梯，身后的脚步声越来越近。</p>
        <p class="narration">你用尽全力推开铁门，冲进后院。</p>
        <p class="narration">月光洒下，你回头望去——</p>
        <p class="narration">地下室的门口空无一人。</p>
        <p class="narration">但你知道，她还在那里，等待着你回去。</p>
        <p class="detail">你必须找到封印她的方法。</p>
        ''',
        'background': 'backyard_night',
        'ambience': 'night_wind',
        'sanity_effect': -5,
        'choices': [
            {'text': '去西厢房找封印方法', 'next': 'west_wing', 'sanity_change': 0},
            {'text': '去东厢房找线索', 'next': 'east_wing', 'sanity_change': 0}
        ]
    },
    
    'fire_at_corpse': {
        'title': '火焰',
        'text': '''
        <p class="narration">你转身举起火折子，火焰照亮了追来的身影。</p>
        <p class="narration">阿绣看到火焰，发出一声尖叫，后退了几步。</p>
        <p class="horror">"火...不要..."</p>
        <p class="narration">她的身影在火光中变得虚幻，像是随时会消散。</p>
        <p class="narration">你趁机后退，保持火焰在你和她之间。</p>
        <p class="detail">火是她的弱点。</p>
        ''',
        'background': 'fire_standoff',
        'ambience': 'fire_crackle',
        'add_secret': '阿绣怕火',
        'add_flag': 'know_fire_weakness',
        'choices': [
            {'text': '趁机拿骨灰坛', 'next': 'take_urn_after_burn', 'sanity_change': 0},
            {'text': '烧掉棺材', 'next': 'burn_coffin', 'sanity_change': -5}
        ]
    },
    
    'drop_dress_run': {
        'title': '丢弃',
        'text': '''
        <p class="narration">你扔掉嫁衣，转身就跑。</p>
        <p class="narration">身后传来阿绣愤怒的尖叫：</p>
        <p class="horror">"你敢扔掉我的嫁衣！"</p>
        <p class="narration">你冲出地下室，不敢回头。</p>
        <p class="narration">当你停下来喘息时，发现自己来到了后院。</p>
        <p class="detail">你需要找到其他方法来削弱她。</p>
        ''',
        'background': 'backyard_escape',
        'ambience': 'running',
        'sanity_effect': -5,
        'choices': [
            {'text': '去西厢房', 'next': 'west_wing', 'sanity_change': 0},
            {'text': '返回地下室', 'next': 'basement', 'sanity_change': -5}
        ]
    },
    
    'hold_dress': {
        'title': '抓住',
        'text': '''
        <p class="narration">你死死抓住嫁衣不放。</p>
        <p class="narration">阿绣的身影在嫁衣中挣扎，发出凄厉的惨叫。</p>
        <p class="horror">"放开！放开我！"</p>
        <p class="narration">你感到一股强大的力量在拉扯你，像是要把你拖入深渊。</p>
        <p class="narration">你的手开始发麻，意识开始模糊...</p>
        <p class="horror">她在吸取你的生命力！</p>
        ''',
        'background': 'struggle_dress',
        'ambience': 'draining',
        'sanity_effect': -20,
        'choices': [
            {'text': '放手', 'next': 'release_dress', 'sanity_change': -10},
            {'text': '用火折子烧掉', 'next': 'burn_dress', 'sanity_change': 0, 'require_item': '火折子'}
        ]
    },
    
    'release_dress': {
        'title': '放手',
        'text': '''
        <p class="narration">你松开手，嫁衣飘落在地。</p>
        <p class="narration">阿绣的身影从嫁衣中浮现，她的脸上带着得意的笑容。</p>
        <p class="horror">"你...太弱了..."</p>
        <p class="narration">她消失在空气中，留下一阵阴冷的笑声。</p>
        <p class="narration">你瘫坐在地上，浑身无力。</p>
        <p class="detail">你失去了一部分生命力，但你还活着。</p>
        ''',
        'background': 'weakened',
        'ambience': 'laughter',
        'sanity_effect': -10,
        'choices': [
            {'text': '拿起骨灰坛', 'next': 'take_urn', 'sanity_change': 0},
            {'text': '休息一下', 'next': 'rest_basement', 'sanity_change': 5}
        ]
    },
    
    'rest_basement': {
        'title': '休息',
        'text': '''
        <p class="narration">你靠在墙边，闭上眼睛休息。</p>
        <p class="narration">地下室很安静，只有你自己的呼吸声。</p>
        <p class="narration">渐渐地，你的体力恢复了一些。</p>
        <p class="narration">当你睁开眼睛时，你注意到角落里的骨灰坛。</p>
        <p class="detail">是时候完成你来这里的目的了。</p>
        ''',
        'background': 'basement_rest',
        'ambience': 'silence',
        'choices': [
            {'text': '拿起骨灰坛', 'next': 'take_urn', 'sanity_change': 0}
        ]
    },
    
    'try_seal': {
        'title': '封印',
        'text': '''
        <p class="narration">你拿出朱砂和镇魂符，准备进行封印。</p>
        <p class="narration">但你意识到，你还没有骨灰坛。</p>
        <p class="detail">你需要先拿到骨灰坛才能完成封印。</p>
        ''',
        'background': 'basement',
        'ambience': 'wind',
        'choices': [
            {'text': '拿起骨灰坛', 'next': 'take_urn', 'sanity_change': 0}
        ]
    }
})
