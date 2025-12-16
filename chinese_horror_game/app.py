"""
《纸人归魂》- 中式恐怖文字冒险游戏
后端主程序
"""
from flask import Flask, render_template, jsonify, request, session
from flask_cors import CORS
import json
import random
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'paper_ghost_secret_key_2024'
CORS(app)

# 游戏状态管理
class GameState:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.current_scene = 'prologue'
        self.sanity = 100  # 理智值
        self.items = []
        self.flags = {}
        self.death_count = 0
        self.discovered_secrets = []
        self.time_in_mansion = 0
        
    def to_dict(self):
        return {
            'current_scene': self.current_scene,
            'sanity': self.sanity,
            'items': self.items,
            'flags': self.flags,
            'death_count': self.death_count,
            'discovered_secrets': self.discovered_secrets,
            'time_in_mansion': self.time_in_mansion
        }
    
    def from_dict(self, data):
        self.current_scene = data.get('current_scene', 'prologue')
        self.sanity = data.get('sanity', 100)
        self.items = data.get('items', [])
        self.flags = data.get('flags', {})
        self.death_count = data.get('death_count', 0)
        self.discovered_secrets = data.get('discovered_secrets', [])
        self.time_in_mansion = data.get('time_in_mansion', 0)


# 游戏场景数据
SCENES = {
    'prologue': {
        'title': '序章 · 归乡',
        'text': '''
        <p class="narration">民国二十三年，深秋。</p>
        <p class="narration">你收到一封来自故乡的信，信封上沾着暗红色的污渍，字迹潦草而颤抖：</p>
        <p class="letter">"吾儿速归，老宅有异，纸人...纸人活了..."</p>
        <p class="narration">这是父亲的笔迹。你已三年未归故里。</p>
        <p class="narration">当你踏上归途时，天色已晚。马车夫在距离陈家老宅三里处便不肯再走，只留下一句：</p>
        <p class="dialogue">"那地方...不干净。"</p>
        <p class="narration">你独自走在泥泞的小路上，远处，陈家老宅的轮廓在浓雾中若隐若现...</p>
        ''',
        'background': 'fog_path',
        'ambience': 'wind_howling',
        'choices': [
            {'text': '加快脚步，尽快赶到老宅', 'next': 'mansion_gate', 'sanity_change': 0},
            {'text': '点燃火折子，小心前行', 'next': 'mansion_gate_light', 'sanity_change': 5, 'add_item': '火折子'},
            {'text': '回头看看身后', 'next': 'look_back', 'sanity_change': -10}
        ]
    },
    
    'look_back': {
        'title': '回首',
        'text': '''
        <p class="narration">你下意识回头望去。</p>
        <p class="narration">浓雾中，一个模糊的人影站在你来时的路上。</p>
        <p class="narration">那身影穿着红色的嫁衣，长发遮面，一动不动。</p>
        <p class="narration">你眨了眨眼，那身影消失了。</p>
        <p class="narration">但你分明听到身后传来细碎的脚步声...</p>
        <p class="horror">越来越近...</p>
        <p class="narration">你不敢再回头，拼命向前跑去。</p>
        ''',
        'background': 'red_bride',
        'ambience': 'footsteps',
        'sanity_effect': -10,
        'choices': [
            {'text': '继续向老宅跑去', 'next': 'mansion_gate_panic', 'sanity_change': -5}
        ]
    },
    
    'mansion_gate': {
        'title': '陈家老宅',
        'text': '''
        <p class="narration">老宅的大门在你面前缓缓显现。</p>
        <p class="narration">朱红色的大门已经斑驳，门上的铜环锈迹斑斑。门楣上挂着的灯笼散发着诡异的红光。</p>
        <p class="narration">门是虚掩着的。</p>
        <p class="narration">你注意到门槛上撒着一层厚厚的纸钱灰烬，门框两侧贴着倒置的对联。</p>
        <p class="detail">对联上写着：</p>
        <p class="couplet">"生人勿近阴阳隔"</p>
        <p class="couplet">"死者长眠莫惊扰"</p>
        <p class="narration">一阵阴风吹过，门发出"吱呀"的声响，像是在邀请你进入...</p>
        ''',
        'background': 'mansion_gate',
        'ambience': 'door_creak',
        'choices': [
            {'text': '推门进入', 'next': 'main_hall', 'sanity_change': 0},
            {'text': '绕到侧门查看', 'next': 'side_door', 'sanity_change': 0},
            {'text': '大声呼喊父亲的名字', 'next': 'call_father', 'sanity_change': -15}
        ]
    },
    
    'mansion_gate_light': {
        'title': '陈家老宅',
        'text': '''
        <p class="narration">火折子的微光驱散了些许黑暗，你感到稍微安心了一些。</p>
        <p class="narration">老宅的大门在火光中显现。朱红色的漆面已经剥落，露出下面腐朽的木头。</p>
        <p class="narration">借着火光，你看到门上刻着奇怪的符文，像是某种封印。</p>
        <p class="detail">符文中央，有一个被划破的"镇"字。</p>
        <p class="narration">门是虚掩着的，从门缝中透出一丝微弱的烛光。</p>
        ''',
        'background': 'mansion_gate_lit',
        'ambience': 'fire_crackle',
        'choices': [
            {'text': '推门进入', 'next': 'main_hall', 'sanity_change': 0},
            {'text': '仔细查看符文', 'next': 'examine_seal', 'sanity_change': 0, 'add_flag': 'know_seal'},
            {'text': '绕到侧门查看', 'next': 'side_door', 'sanity_change': 0}
        ]
    },
    
    'mansion_gate_panic': {
        'title': '陈家老宅',
        'text': '''
        <p class="narration">你气喘吁吁地跑到老宅门前，身后的脚步声在你停下的瞬间消失了。</p>
        <p class="narration">你不敢回头，只是死死盯着面前的大门。</p>
        <p class="narration">门是开着的。</p>
        <p class="horror">里面一片漆黑，像是一张等待吞噬猎物的巨口。</p>
        <p class="narration">你别无选择...</p>
        ''',
        'background': 'mansion_gate_dark',
        'ambience': 'heartbeat',
        'choices': [
            {'text': '冲进老宅', 'next': 'main_hall_dark', 'sanity_change': -5}
        ]
    },
    
    'call_father': {
        'title': '回响',
        'text': '''
        <p class="narration">"父亲！父亲！"</p>
        <p class="narration">你的声音在夜色中回荡。</p>
        <p class="narration">片刻的寂静后，老宅深处传来回应：</p>
        <p class="dialogue">"...儿啊...进来..."</p>
        <p class="narration">那声音沙哑而空洞，像是从很远的地方传来。</p>
        <p class="narration">但你分明记得，父亲的声音不是这样的。</p>
        <p class="horror">那声音...太冷了。</p>
        <p class="narration">大门突然自己打开了。</p>
        ''',
        'background': 'door_open',
        'ambience': 'whisper',
        'sanity_effect': -15,
        'choices': [
            {'text': '硬着头皮进入', 'next': 'main_hall_dark', 'sanity_change': -10},
            {'text': '转身逃跑', 'next': 'escape_attempt', 'sanity_change': -20}
        ]
    },
    
    'escape_attempt': {
        'title': '无路可逃',
        'text': '''
        <p class="narration">你转身想要逃跑，却发现来时的路已经消失在浓雾中。</p>
        <p class="narration">四周只剩下无尽的黑暗和雾气。</p>
        <p class="narration">你拼命奔跑，却始终跑不出这片迷雾。</p>
        <p class="narration">不知过了多久，当你精疲力竭地停下时...</p>
        <p class="horror">你发现自己又站在了老宅门前。</p>
        <p class="narration">门开着，像是在嘲笑你的徒劳。</p>
        <p class="detail">你听到身后传来轻轻的笑声...</p>
        ''',
        'background': 'fog_loop',
        'ambience': 'laughter',
        'sanity_effect': -20,
        'choices': [
            {'text': '认命进入老宅', 'next': 'main_hall_dark', 'sanity_change': -10}
        ]
    }
}


# 继续添加更多场景
SCENES.update({
    'examine_seal': {
        'title': '封印',
        'text': '''
        <p class="narration">你凑近查看那些符文。</p>
        <p class="narration">这是道家的镇魂符，用于封印不洁之物。但符文已经被人为破坏，"镇"字被利器划破。</p>
        <p class="detail">你注意到划痕是从里面划出来的。</p>
        <p class="narration">符文周围还有一些暗红色的痕迹，像是干涸的血迹。</p>
        <p class="narration">你想起父亲信中的话："纸人活了..."</p>
        <p class="horror">这封印...是用来封住什么的？</p>
        ''',
        'background': 'seal_closeup',
        'ambience': 'wind',
        'add_secret': '破损的封印',
        'choices': [
            {'text': '推门进入', 'next': 'main_hall', 'sanity_change': 0},
            {'text': '绕到侧门', 'next': 'side_door', 'sanity_change': 0}
        ]
    },
    
    'side_door': {
        'title': '侧门',
        'text': '''
        <p class="narration">你绕到老宅侧面，找到了一扇小门。</p>
        <p class="narration">门上贴着一张泛黄的符纸，符纸上画着一个诡异的图案——一个没有五官的人形。</p>
        <p class="narration">门缝中飘出一股腐朽的气息，混合着檀香和纸钱燃烧的味道。</p>
        <p class="detail">你听到门内传来轻微的"沙沙"声，像是有什么东西在移动...</p>
        ''',
        'background': 'side_door',
        'ambience': 'rustling',
        'choices': [
            {'text': '撕掉符纸，推门进入', 'next': 'side_room_danger', 'sanity_change': -20, 'add_flag': 'broke_talisman'},
            {'text': '从符纸旁边的缝隙窥视', 'next': 'peek_side_door', 'sanity_change': -10},
            {'text': '返回正门', 'next': 'mansion_gate', 'sanity_change': 0}
        ]
    },
    
    'peek_side_door': {
        'title': '窥视',
        'text': '''
        <p class="narration">你将眼睛凑近门缝，试图看清里面的情况。</p>
        <p class="narration">昏暗的房间里，你看到一排排纸人整齐地站立着。</p>
        <p class="narration">它们都穿着白色的寿衣，面朝着门的方向。</p>
        <p class="horror">突然，最前面那个纸人的头缓缓转动...</p>
        <p class="horror">一只眼睛从门缝那边看向你！</p>
        <p class="narration">你惊恐地后退，撞倒了身后的杂物。</p>
        <p class="detail">门内传来"咯咯"的笑声...</p>
        ''',
        'background': 'paper_eye',
        'ambience': 'giggle',
        'sanity_effect': -10,
        'choices': [
            {'text': '逃向正门', 'next': 'main_hall_panic', 'sanity_change': -5},
            {'text': '强行推开侧门', 'next': 'side_room_danger', 'sanity_change': -15}
        ]
    },
    
    'main_hall': {
        'title': '正厅',
        'text': '''
        <p class="narration">你推开大门，走进了陈家老宅的正厅。</p>
        <p class="narration">厅内点着几盏油灯，昏黄的光线在墙上投下摇曳的影子。</p>
        <p class="narration">正中央供奉着祖先牌位，香炉中的香还在燃烧，青烟袅袅。</p>
        <p class="detail">奇怪的是，牌位上的名字都被黑墨涂掉了。</p>
        <p class="narration">厅堂两侧各站着一个真人大小的纸人，它们穿着喜庆的红衣，脸上画着诡异的笑容。</p>
        <p class="narration">你注意到地上有一串脚印，从大门延伸向后院...</p>
        ''',
        'background': 'main_hall',
        'ambience': 'incense',
        'choices': [
            {'text': '查看祖先牌位', 'next': 'examine_tablets', 'sanity_change': -5},
            {'text': '仔细观察纸人', 'next': 'examine_paper_figures', 'sanity_change': -10},
            {'text': '跟随脚印去后院', 'next': 'backyard_path', 'sanity_change': 0},
            {'text': '去东厢房', 'next': 'east_wing', 'sanity_change': 0},
            {'text': '去西厢房', 'next': 'west_wing', 'sanity_change': 0}
        ]
    },
    
    'main_hall_dark': {
        'title': '正厅',
        'text': '''
        <p class="narration">你踏入漆黑的正厅，身后的门"砰"地一声关上了。</p>
        <p class="narration">黑暗中，你什么也看不见。</p>
        <p class="narration">但你能感觉到...这里不止你一个人。</p>
        <p class="horror">有什么东西在黑暗中注视着你。</p>
        <p class="narration">突然，一盏油灯自己亮了起来。</p>
        <p class="narration">昏黄的光线中，你看到两个纸人站在你面前，距离你不到三尺。</p>
        <p class="horror">它们的眼睛...在动。</p>
        ''',
        'background': 'dark_hall_figures',
        'ambience': 'breathing',
        'sanity_effect': -15,
        'choices': [
            {'text': '保持冷静，慢慢后退', 'next': 'main_hall_retreat', 'sanity_change': -5},
            {'text': '大声呵斥', 'next': 'shout_at_figures', 'sanity_change': -20},
            {'text': '闭上眼睛', 'next': 'close_eyes', 'sanity_change': 0, 'require_item': '火折子'}
        ]
    },
    
    'main_hall_panic': {
        'title': '正厅',
        'text': '''
        <p class="narration">你慌忙冲进正厅，重重地关上身后的门。</p>
        <p class="narration">喘息间，你环顾四周。</p>
        <p class="narration">厅内的油灯忽明忽暗，两侧的纸人在光影中显得格外诡异。</p>
        <p class="detail">你总觉得它们的位置和刚才不太一样...</p>
        <p class="narration">地上有一串脚印，从大门延伸向后院。</p>
        ''',
        'background': 'main_hall_dim',
        'ambience': 'heartbeat',
        'choices': [
            {'text': '跟随脚印去后院', 'next': 'backyard_path', 'sanity_change': 0},
            {'text': '去东厢房', 'next': 'east_wing', 'sanity_change': 0},
            {'text': '去西厢房', 'next': 'west_wing', 'sanity_change': 0}
        ]
    },
    
    'examine_tablets': {
        'title': '祖先牌位',
        'text': '''
        <p class="narration">你走近供桌，仔细查看那些牌位。</p>
        <p class="narration">牌位上的名字确实被黑墨涂掉了，但你用手指轻轻刮了刮，露出下面的字迹。</p>
        <p class="detail">"陈氏先祖...陈守义...陈守信..."</p>
        <p class="narration">这些都是你的祖辈。但最后一块牌位让你心头一紧：</p>
        <p class="horror">"陈守仁"——这是你父亲的名字。</p>
        <p class="narration">父亲的牌位怎么会在这里？他...他不是还活着吗？</p>
        <p class="narration">你注意到牌位后面刻着一行小字：</p>
        <p class="detail">"民国二十三年九月初七，殁"</p>
        <p class="horror">那是...三天前。</p>
        ''',
        'background': 'tablets',
        'ambience': 'whisper',
        'sanity_effect': -5,
        'add_secret': '父亲的牌位',
        'add_flag': 'know_father_dead',
        'choices': [
            {'text': '去后院寻找真相', 'next': 'backyard_path', 'sanity_change': -5},
            {'text': '去东厢房（父亲的书房）', 'next': 'east_wing', 'sanity_change': 0},
            {'text': '检查香炉', 'next': 'examine_incense', 'sanity_change': 0}
        ]
    },
    
    'examine_incense': {
        'title': '香炉',
        'text': '''
        <p class="narration">你查看香炉，发现里面除了香灰，还有一些烧焦的纸片。</p>
        <p class="narration">你小心翼翼地捡起一片，上面残留着几个字：</p>
        <p class="detail">"...封印已破...她回来了...救救..."</p>
        <p class="narration">这是父亲的笔迹。</p>
        <p class="narration">香炉底部，你发现了一把生锈的钥匙。</p>
        <p class="detail">钥匙上刻着"西"字。</p>
        ''',
        'background': 'incense_burner',
        'ambience': 'wind',
        'add_item': '西厢房钥匙',
        'add_secret': '父亲的遗言',
        'choices': [
            {'text': '去西厢房', 'next': 'west_wing_key', 'sanity_change': 0},
            {'text': '去东厢房', 'next': 'east_wing', 'sanity_change': 0},
            {'text': '去后院', 'next': 'backyard_path', 'sanity_change': 0}
        ]
    }
})


# 更多场景 - 纸人相关
SCENES.update({
    'examine_paper_figures': {
        'title': '纸人',
        'text': '''
        <p class="narration">你走近其中一个纸人，仔细端详。</p>
        <p class="narration">这纸人做工精细得可怕，每一个细节都栩栩如生。</p>
        <p class="narration">它的眼睛是用黑色的玻璃珠做的，在烛光下闪烁着诡异的光芒。</p>
        <p class="detail">你注意到纸人的嘴角似乎在微微上扬...</p>
        <p class="narration">突然，你感到一阵寒意——</p>
        <p class="horror">另一个纸人不见了。</p>
        <p class="narration">你猛地转身，却什么也没看到。</p>
        <p class="narration">当你再次转回来时...</p>
        <p class="horror">面前的纸人离你更近了。</p>
        ''',
        'background': 'paper_figure_close',
        'ambience': 'static',
        'sanity_effect': -10,
        'add_flag': 'paper_figure_moved',
        'choices': [
            {'text': '快速离开正厅', 'next': 'backyard_path', 'sanity_change': -5},
            {'text': '推倒纸人', 'next': 'push_figure', 'sanity_change': -15},
            {'text': '对纸人说话', 'next': 'talk_to_figure', 'sanity_change': -10}
        ]
    },
    
    'push_figure': {
        'title': '推倒',
        'text': '''
        <p class="narration">你伸手推向纸人。</p>
        <p class="narration">纸人倒下的瞬间，你听到一声尖锐的惨叫。</p>
        <p class="horror">那声音...像是从纸人体内发出的。</p>
        <p class="narration">纸人躺在地上，它的头缓缓转向你。</p>
        <p class="narration">那张画着笑容的脸上，两行血泪从眼眶中流出。</p>
        <p class="horror">"你...不该...碰我..."</p>
        <p class="narration">声音沙哑而怨毒，像是从地狱深处传来。</p>
        <p class="narration">所有的油灯同时熄灭了。</p>
        <p class="narration">黑暗中，你感到有什么东西抓住了你的脚踝...</p>
        ''',
        'background': 'darkness',
        'ambience': 'scream',
        'sanity_effect': -15,
        'add_flag': 'angered_paper_figure',
        'choices': [
            {'text': '挣脱逃跑', 'next': 'escape_hall', 'sanity_change': -10},
            {'text': '点燃火折子', 'next': 'light_fire_hall', 'sanity_change': 0, 'require_item': '火折子'}
        ]
    },
    
    'talk_to_figure': {
        'title': '对话',
        'text': '''
        <p class="narration">"你...是什么？"你颤抖着问道。</p>
        <p class="narration">纸人没有回答，但你感到一阵寒风拂过耳畔。</p>
        <p class="narration">风中夹杂着细碎的低语：</p>
        <p class="whisper">"我们...等了很久..."</p>
        <p class="whisper">"她...回来了..."</p>
        <p class="whisper">"你...也会...留下..."</p>
        <p class="narration">低语声越来越多，像是有无数个声音在同时说话。</p>
        <p class="horror">你意识到，这些声音来自老宅的每一个角落...</p>
        ''',
        'background': 'whispers',
        'ambience': 'many_whispers',
        'sanity_effect': -10,
        'add_secret': '纸人的低语',
        'choices': [
            {'text': '"她是谁？"', 'next': 'ask_who', 'sanity_change': -5},
            {'text': '不再理会，去后院', 'next': 'backyard_path', 'sanity_change': 0},
            {'text': '去东厢房', 'next': 'east_wing', 'sanity_change': 0}
        ]
    },
    
    'ask_who': {
        'title': '她',
        'text': '''
        <p class="narration">"她是谁？"你追问道。</p>
        <p class="narration">低语声突然停止了。</p>
        <p class="narration">死一般的寂静。</p>
        <p class="narration">然后，所有的声音汇聚成一个：</p>
        <p class="horror">"新...娘..."</p>
        <p class="narration">话音刚落，你听到后院传来一阵凄厉的哭声。</p>
        <p class="narration">那哭声悲切而怨恨，像是受尽委屈的女子在诉说冤情。</p>
        <p class="detail">哭声中，你隐约听到一个名字："陈...守...仁..."</p>
        <p class="narration">那是你父亲的名字。</p>
        ''',
        'background': 'crying',
        'ambience': 'woman_crying',
        'sanity_effect': -5,
        'add_flag': 'know_bride',
        'add_secret': '新娘的哭声',
        'choices': [
            {'text': '去后院查看', 'next': 'backyard_path', 'sanity_change': -5},
            {'text': '去东厢房寻找线索', 'next': 'east_wing', 'sanity_change': 0}
        ]
    },
    
    'escape_hall': {
        'title': '逃离',
        'text': '''
        <p class="narration">你拼命挣脱那冰冷的触感，跌跌撞撞地向前跑去。</p>
        <p class="narration">黑暗中，你撞翻了什么东西，听到瓷器碎裂的声音。</p>
        <p class="narration">你不敢停下，凭着记忆向后院的方向跑去。</p>
        <p class="narration">身后传来"沙沙"的声音，像是有什么东西在地上爬行...</p>
        <p class="horror">越来越近...</p>
        <p class="narration">终于，你冲出了正厅，来到后院的走廊。</p>
        <p class="narration">月光洒下，你回头望去——</p>
        <p class="narration">正厅的门口，站着三个纸人。</p>
        <p class="horror">它们的头都歪向一边，用那空洞的眼睛注视着你。</p>
        ''',
        'background': 'corridor_figures',
        'ambience': 'crawling',
        'sanity_effect': -10,
        'choices': [
            {'text': '继续向后院跑', 'next': 'backyard_path', 'sanity_change': -5},
            {'text': '躲进东厢房', 'next': 'east_wing_hide', 'sanity_change': 0}
        ]
    },
    
    'light_fire_hall': {
        'title': '火光',
        'text': '''
        <p class="narration">你颤抖着点燃火折子。</p>
        <p class="narration">火光驱散了黑暗，你看到——</p>
        <p class="narration">抓住你脚踝的是一只纸做的手，从倒下的纸人身上伸出。</p>
        <p class="narration">火光靠近的瞬间，那只手像是被烫到一般缩了回去。</p>
        <p class="narration">纸人发出一声尖叫，整个身体开始扭曲。</p>
        <p class="detail">你注意到纸人的胸口有一张符纸，符纸上写着一个名字。</p>
        <p class="narration">趁着纸人退缩，你快步离开了正厅。</p>
        ''',
        'background': 'fire_paper',
        'ambience': 'burning',
        'add_secret': '纸人怕火',
        'add_flag': 'know_fire_weakness',
        'choices': [
            {'text': '去后院', 'next': 'backyard_path', 'sanity_change': 0},
            {'text': '去东厢房', 'next': 'east_wing', 'sanity_change': 0}
        ]
    }
})


# 东厢房和西厢房场景
SCENES.update({
    'east_wing': {
        'title': '东厢房 · 书房',
        'text': '''
        <p class="narration">你推开东厢房的门，这里是父亲的书房。</p>
        <p class="narration">书架上的书籍凌乱地散落着，桌上的砚台还有未干的墨迹。</p>
        <p class="narration">墙上挂着一幅画像，画中是一个穿着红色嫁衣的女子。</p>
        <p class="detail">女子的面容被人用刀划破了。</p>
        <p class="narration">桌上放着一本翻开的日记，旁边是一封未寄出的信。</p>
        <p class="narration">角落里，你看到一个上锁的木箱。</p>
        ''',
        'background': 'study_room',
        'ambience': 'clock_ticking',
        'choices': [
            {'text': '阅读日记', 'next': 'read_diary', 'sanity_change': -5},
            {'text': '查看那封信', 'next': 'read_letter', 'sanity_change': 0},
            {'text': '仔细看画像', 'next': 'examine_portrait', 'sanity_change': -10},
            {'text': '尝试打开木箱', 'next': 'try_open_box', 'sanity_change': 0},
            {'text': '返回正厅', 'next': 'main_hall', 'sanity_change': 0}
        ]
    },
    
    'east_wing_hide': {
        'title': '东厢房 · 躲藏',
        'text': '''
        <p class="narration">你冲进东厢房，反手关上门。</p>
        <p class="narration">门外传来"沙沙"的脚步声，在门前停了下来。</p>
        <p class="narration">你屏住呼吸，不敢发出一点声音。</p>
        <p class="narration">"咚...咚...咚..."</p>
        <p class="horror">有什么东西在敲门。</p>
        <p class="narration">敲门声持续了很久，然后渐渐远去。</p>
        <p class="narration">你松了一口气，环顾四周——这是父亲的书房。</p>
        <p class="narration">桌上放着一本翻开的日记，墙上挂着一幅被划破的画像。</p>
        ''',
        'background': 'study_room_dark',
        'ambience': 'knocking',
        'choices': [
            {'text': '阅读日记', 'next': 'read_diary', 'sanity_change': -5},
            {'text': '查看画像', 'next': 'examine_portrait', 'sanity_change': -10},
            {'text': '等一会再出去', 'next': 'wait_in_study', 'sanity_change': 5}
        ]
    },
    
    'read_diary': {
        'title': '父亲的日记',
        'text': '''
        <p class="narration">你翻开日记，上面记录着父亲最后几天的经历：</p>
        <p class="diary">九月初三</p>
        <p class="diary">老宅地下室的封印出现裂痕，我请了道士来加固。道士说，这封印已有六十年，里面封的是一个冤魂——我祖父的童养媳，在新婚之夜被活活烧死。</p>
        <p class="diary">九月初五</p>
        <p class="diary">封印破了。半夜听到女人的哭声，纸人的眼睛会动了。我必须找到重新封印的方法。</p>
        <p class="diary">九月初六</p>
        <p class="diary">她来找我了。她说要我偿命，说陈家欠她一条命。我把重新封印的方法藏在了西厢房的神龛里，如果我出事，希望有人能完成封印。</p>
        <p class="diary">九月初七</p>
        <p class="diary">今晚就是她的忌日。她越来越强了。我给儿子写了信，希望他能...</p>
        <p class="narration">日记到这里就断了，后面的页面被撕掉了。</p>
        ''',
        'background': 'diary',
        'ambience': 'writing',
        'sanity_effect': -5,
        'add_secret': '父亲的日记',
        'add_flag': 'know_truth',
        'choices': [
            {'text': '去西厢房找封印方法', 'next': 'west_wing', 'sanity_change': 0},
            {'text': '查看画像', 'next': 'examine_portrait', 'sanity_change': -10},
            {'text': '去后院', 'next': 'backyard_path', 'sanity_change': 0}
        ]
    },
    
    'read_letter': {
        'title': '未寄出的信',
        'text': '''
        <p class="narration">你拿起那封信，信封上写着你的名字。</p>
        <p class="letter">吾儿：</p>
        <p class="letter">当你看到这封信时，为父恐怕已经不在人世。</p>
        <p class="letter">陈家有一个六十年的秘密。你曾祖父年轻时，家中为他娶了一个童养媳，名叫阿绣。阿绣生得美貌，却命运多舛。新婚之夜，你曾祖父嫌她出身卑微，竟将她活活烧死在新房中。</p>
        <p class="letter">阿绣死后，怨气不散，化为厉鬼。你曾祖父请高人将她封印在地下室，并立下规矩：陈家子孙不得打开封印，每年忌日需焚香祭拜。</p>
        <p class="letter">然而，封印已破。阿绣回来复仇了。</p>
        <p class="letter">为父已将重新封印的方法藏在西厢房神龛之后。你需要找到阿绣的骨灰，用朱砂和黑狗血画出镇魂符，在她的忌日子时之前完成封印。</p>
        <p class="letter">切记：不要直视她的眼睛，不要回应她的呼唤。</p>
        <p class="letter">父 绝笔</p>
        ''',
        'background': 'letter',
        'ambience': 'wind',
        'add_secret': '父亲的遗书',
        'add_flag': 'know_seal_method',
        'choices': [
            {'text': '去西厢房', 'next': 'west_wing', 'sanity_change': 0},
            {'text': '去后院寻找骨灰', 'next': 'backyard_path', 'sanity_change': 0},
            {'text': '查看画像', 'next': 'examine_portrait', 'sanity_change': -10}
        ]
    },
    
    'examine_portrait': {
        'title': '画像',
        'text': '''
        <p class="narration">你走近那幅画像。</p>
        <p class="narration">尽管面容被划破，你仍能看出画中女子的轮廓——她很年轻，也很美丽。</p>
        <p class="narration">她穿着红色的嫁衣，头戴凤冠，嘴角带着一丝微笑。</p>
        <p class="detail">画像下方写着：阿绣，民国二十三年。</p>
        <p class="narration">等等...民国二十三年？那不是今年吗？</p>
        <p class="narration">你再仔细看那画像，突然发现——</p>
        <p class="horror">画中女子的眼睛在动。</p>
        <p class="narration">她的嘴角慢慢上扬，露出一个诡异的笑容。</p>
        <p class="horror">"你...来了..."</p>
        <p class="narration">声音从画像中传出，阴冷而怨毒。</p>
        <p class="narration">你惊恐地后退，撞翻了身后的椅子。</p>
        ''',
        'background': 'portrait_alive',
        'ambience': 'ghost_voice',
        'sanity_effect': -10,
        'add_flag': 'seen_axiu',
        'choices': [
            {'text': '逃出书房', 'next': 'escape_study', 'sanity_change': -5},
            {'text': '质问她', 'next': 'confront_portrait', 'sanity_change': -15},
            {'text': '烧掉画像', 'next': 'burn_portrait', 'sanity_change': -10, 'require_item': '火折子'}
        ]
    },
    
    'burn_portrait': {
        'title': '焚烧',
        'text': '''
        <p class="narration">你举起火折子，将火焰凑近画像。</p>
        <p class="narration">画中的女子发出一声尖叫，画像开始燃烧。</p>
        <p class="narration">火焰中，你看到她的脸扭曲变形，变得狰狞可怖。</p>
        <p class="horror">"你...也想...烧死我？"</p>
        <p class="narration">她的声音充满怨恨。</p>
        <p class="horror">"陈家人...都该死！"</p>
        <p class="narration">画像化为灰烬，但你知道，这并没有消灭她。</p>
        <p class="narration">一阵阴风吹过，你感到后背一阵发凉。</p>
        <p class="detail">她...就在你身后。</p>
        ''',
        'background': 'burning_portrait',
        'ambience': 'fire_scream',
        'sanity_effect': -10,
        'add_flag': 'burned_portrait',
        'choices': [
            {'text': '慢慢转身', 'next': 'turn_around', 'sanity_change': -20},
            {'text': '不回头，直接跑', 'next': 'run_without_looking', 'sanity_change': -5}
        ]
    },
    
    'west_wing': {
        'title': '西厢房',
        'text': '''
        <p class="narration">你来到西厢房门前。</p>
        <p class="narration">门上贴着一张符纸，门是锁着的。</p>
        <p class="narration">透过门缝，你看到里面漆黑一片，隐约能闻到一股腐朽的气息。</p>
        <p class="detail">门缝下方，有什么东西在动...</p>
        ''',
        'background': 'west_wing_door',
        'ambience': 'scratching',
        'choices': [
            {'text': '用钥匙开门', 'next': 'west_wing_enter', 'sanity_change': 0, 'require_item': '西厢房钥匙'},
            {'text': '撕掉符纸强行开门', 'next': 'west_wing_force', 'sanity_change': -20},
            {'text': '返回正厅', 'next': 'main_hall', 'sanity_change': 0},
            {'text': '去后院', 'next': 'backyard_path', 'sanity_change': 0}
        ]
    },
    
    'west_wing_key': {
        'title': '西厢房',
        'text': '''
        <p class="narration">你用钥匙打开了西厢房的门。</p>
        <p class="narration">门"吱呀"一声打开，一股陈腐的气息扑面而来。</p>
        <p class="narration">房间里摆满了纸扎的物品——纸人、纸马、纸房子...</p>
        <p class="narration">正中央是一个神龛，神龛上供奉着一个牌位。</p>
        <p class="detail">牌位上写着：亡妻阿绣之灵位。</p>
        <p class="narration">神龛前的香炉里，三炷香还在燃烧。</p>
        <p class="horror">是谁点的香？</p>
        ''',
        'background': 'west_wing_inside',
        'ambience': 'incense_burning',
        'choices': [
            {'text': '查看神龛后面', 'next': 'behind_shrine', 'sanity_change': 0},
            {'text': '检查那些纸扎', 'next': 'examine_paper_offerings', 'sanity_change': -10},
            {'text': '离开这里', 'next': 'main_hall', 'sanity_change': 0}
        ]
    },
    
    'west_wing_enter': {
        'title': '西厢房',
        'text': '''
        <p class="narration">你用钥匙打开了西厢房的门。</p>
        <p class="narration">门"吱呀"一声打开，一股陈腐的气息扑面而来。</p>
        <p class="narration">房间里摆满了纸扎的物品——纸人、纸马、纸房子...</p>
        <p class="narration">正中央是一个神龛，神龛上供奉着一个牌位。</p>
        <p class="detail">牌位上写着：亡妻阿绣之灵位。</p>
        <p class="narration">神龛前的香炉里，三炷香还在燃烧。</p>
        <p class="horror">是谁点的香？</p>
        ''',
        'background': 'west_wing_inside',
        'ambience': 'incense_burning',
        'choices': [
            {'text': '查看神龛后面', 'next': 'behind_shrine', 'sanity_change': 0},
            {'text': '检查那些纸扎', 'next': 'examine_paper_offerings', 'sanity_change': -10},
            {'text': '离开这里', 'next': 'main_hall', 'sanity_change': 0}
        ]
    },
    
    'behind_shrine': {
        'title': '神龛之后',
        'text': '''
        <p class="narration">你小心翼翼地移开神龛，发现后面的墙上有一个暗格。</p>
        <p class="narration">暗格里放着一个布包，里面是：</p>
        <p class="detail">一瓶朱砂、一张画着符文的黄纸、一本泛黄的手札。</p>
        <p class="narration">手札上记载着封印的方法：</p>
        <p class="diary">"以朱砂画镇魂符于骨灰坛上，念诵镇魂咒三遍，在子时之前完成，可封印怨灵六十年。"</p>
        <p class="diary">"若怨灵已出，需先找到其执念之物，将其焚毁，方可削弱怨灵之力。"</p>
        <p class="narration">手札最后写着：</p>
        <p class="detail">"阿绣的执念是那件嫁衣，嫁衣藏在地下室的棺材中。"</p>
        ''',
        'background': 'secret_compartment',
        'ambience': 'revelation',
        'add_item': '朱砂',
        'add_item2': '镇魂符',
        'add_secret': '封印方法',
        'add_flag': 'have_seal_items',
        'choices': [
            {'text': '去地下室', 'next': 'basement_entrance', 'sanity_change': -5},
            {'text': '去后院找骨灰', 'next': 'backyard_path', 'sanity_change': 0},
            {'text': '检查纸扎', 'next': 'examine_paper_offerings', 'sanity_change': -10}
        ]
    }
})


# 后院和地下室场景
SCENES.update({
    'backyard_path': {
        'title': '后院',
        'text': '''
        <p class="narration">你沿着走廊来到后院。</p>
        <p class="narration">月光下，后院显得格外阴森。枯萎的树木像是伸出的鬼爪，在风中摇曳。</p>
        <p class="narration">院子中央有一口古井，井口用石板盖着，上面压着一块刻有符文的石碑。</p>
        <p class="narration">井边种着一棵老槐树，树下有一座小小的坟茔。</p>
        <p class="detail">坟前的墓碑上刻着：爱妻阿绣之墓。</p>
        <p class="narration">后院的角落里，有一扇通往地下室的门。</p>
        <p class="narration">你注意到坟茔周围的泥土是新翻过的...</p>
        ''',
        'background': 'backyard',
        'ambience': 'night_wind',
        'choices': [
            {'text': '查看坟茔', 'next': 'examine_grave', 'sanity_change': -5},
            {'text': '查看古井', 'next': 'examine_well', 'sanity_change': -10},
            {'text': '去地下室', 'next': 'basement_entrance', 'sanity_change': -5},
            {'text': '返回正厅', 'next': 'main_hall', 'sanity_change': 0}
        ]
    },
    
    'examine_grave': {
        'title': '坟茔',
        'text': '''
        <p class="narration">你走近那座坟茔。</p>
        <p class="narration">墓碑上的字迹已经模糊，但你仍能辨认出：</p>
        <p class="detail">"爱妻阿绣之墓，民国二十三年立"</p>
        <p class="narration">等等...这墓碑是今年立的？</p>
        <p class="narration">你注意到坟茔周围的泥土确实是新翻过的，像是有人刚刚挖掘过。</p>
        <p class="narration">坟前放着一束枯萎的红花，花瓣上沾着暗红色的液体。</p>
        <p class="horror">那不是露水...是血。</p>
        <p class="narration">你蹲下身，发现坟茔旁边有一个被挖开的洞。洞里空空如也。</p>
        <p class="detail">骨灰坛...不见了。</p>
        ''',
        'background': 'grave',
        'ambience': 'digging',
        'sanity_effect': -5,
        'add_flag': 'know_grave_empty',
        'choices': [
            {'text': '去地下室寻找', 'next': 'basement_entrance', 'sanity_change': -5},
            {'text': '查看古井', 'next': 'examine_well', 'sanity_change': -10},
            {'text': '返回正厅', 'next': 'main_hall', 'sanity_change': 0}
        ]
    },
    
    'examine_well': {
        'title': '古井',
        'text': '''
        <p class="narration">你走近那口古井。</p>
        <p class="narration">井口的石板上刻满了符文，石碑上写着"镇"字。</p>
        <p class="narration">你注意到石板有被移动过的痕迹，符文也有些模糊了。</p>
        <p class="narration">你将耳朵贴近石板，听到井下传来微弱的声音...</p>
        <p class="horror">"救...救我..."</p>
        <p class="narration">那声音沙哑而虚弱，像是一个垂死之人的呼救。</p>
        <p class="narration">你犹豫着要不要移开石板。</p>
        ''',
        'background': 'well',
        'ambience': 'well_echo',
        'sanity_effect': -10,
        'choices': [
            {'text': '移开石板', 'next': 'open_well', 'sanity_change': -20},
            {'text': '不理会，去地下室', 'next': 'basement_entrance', 'sanity_change': 0},
            {'text': '返回正厅', 'next': 'main_hall', 'sanity_change': 0}
        ]
    },
    
    'open_well': {
        'title': '井中',
        'text': '''
        <p class="narration">你费力地移开石板，一股腐臭的气息扑面而来。</p>
        <p class="narration">你捂住口鼻，借着月光向井下望去。</p>
        <p class="narration">井水漆黑如墨，水面上漂浮着什么东西...</p>
        <p class="horror">是一具尸体。</p>
        <p class="narration">尸体穿着你熟悉的衣服——那是父亲的长衫。</p>
        <p class="narration">你惊恐地后退，却听到身后传来一个声音：</p>
        <p class="horror">"找到了吗...你父亲？"</p>
        <p class="narration">你猛地转身，看到一个红衣女子站在你身后。</p>
        <p class="narration">她的脸苍白如纸，眼眶深陷，嘴角挂着诡异的笑容。</p>
        <p class="horror">"他...已经陪我了..."</p>
        ''',
        'background': 'well_body',
        'ambience': 'ghost_laugh',
        'sanity_effect': -20,
        'add_flag': 'found_father_body',
        'add_flag2': 'met_axiu',
        'choices': [
            {'text': '逃跑', 'next': 'escape_from_axiu', 'sanity_change': -10},
            {'text': '质问她', 'next': 'confront_axiu', 'sanity_change': -15},
            {'text': '用火折子', 'next': 'fire_at_axiu', 'sanity_change': 0, 'require_item': '火折子'}
        ]
    },
    
    'basement_entrance': {
        'title': '地下室入口',
        'text': '''
        <p class="narration">你来到地下室的入口。</p>
        <p class="narration">一扇沉重的铁门挡在你面前，门上的锁已经被打开。</p>
        <p class="narration">门缝中透出一丝微弱的红光，像是有什么东西在燃烧。</p>
        <p class="narration">一股阴冷的气息从门缝中涌出，让你不寒而栗。</p>
        <p class="detail">你听到门内传来轻微的歌声，像是一首古老的童谣...</p>
        <p class="whisper">"红嫁衣，红盖头，新娘子，莫回头..."</p>
        ''',
        'background': 'basement_door',
        'ambience': 'nursery_rhyme',
        'choices': [
            {'text': '推门进入', 'next': 'basement', 'sanity_change': -10},
            {'text': '返回后院', 'next': 'backyard_path', 'sanity_change': 0}
        ]
    },
    
    'basement': {
        'title': '地下室',
        'text': '''
        <p class="narration">你推开铁门，走进地下室。</p>
        <p class="narration">地下室比你想象的要大得多，四周的墙壁上画满了符文。</p>
        <p class="narration">正中央放着一口黑色的棺材，棺材上缠绕着铁链，贴满了符纸。</p>
        <p class="horror">棺材是打开的。</p>
        <p class="narration">棺材旁边的地上，放着一件红色的嫁衣。嫁衣上沾满了暗红色的污渍。</p>
        <p class="narration">角落里，你看到一个骨灰坛。</p>
        <p class="detail">骨灰坛上刻着"阿绣"二字。</p>
        <p class="narration">红光是从棺材里发出的，像是有什么东西在里面燃烧。</p>
        ''',
        'background': 'basement',
        'ambience': 'chains',
        'choices': [
            {'text': '查看棺材', 'next': 'examine_coffin', 'sanity_change': -15},
            {'text': '拿起嫁衣', 'next': 'take_dress', 'sanity_change': -10},
            {'text': '拿起骨灰坛', 'next': 'take_urn', 'sanity_change': -5, 'add_item': '骨灰坛'},
            {'text': '立即进行封印', 'next': 'try_seal', 'sanity_change': 0, 'require_flag': 'have_seal_items'}
        ]
    },
    
    'examine_coffin': {
        'title': '棺材',
        'text': '''
        <p class="narration">你走近棺材，向里面望去。</p>
        <p class="narration">棺材里铺着红色的绸缎，绸缎上躺着一具干枯的尸体。</p>
        <p class="narration">尸体穿着新娘的服饰，头戴凤冠，脸上蒙着红盖头。</p>
        <p class="horror">尸体的手中握着一张照片——那是你父亲年轻时的照片。</p>
        <p class="narration">红光是从尸体胸口的一颗红色宝石中发出的。</p>
        <p class="narration">突然，尸体的手动了。</p>
        <p class="horror">她缓缓坐起身来，红盖头下传出沙哑的声音：</p>
        <p class="horror">"你...来送我出嫁吗？"</p>
        ''',
        'background': 'coffin_bride',
        'ambience': 'rising',
        'sanity_effect': -15,
        'add_flag': 'awakened_axiu',
        'choices': [
            {'text': '后退', 'next': 'retreat_from_coffin', 'sanity_change': -10},
            {'text': '揭开红盖头', 'next': 'lift_veil', 'sanity_change': -25},
            {'text': '用火折子点燃棺材', 'next': 'burn_coffin', 'sanity_change': -5, 'require_item': '火折子'}
        ]
    },
    
    'take_dress': {
        'title': '嫁衣',
        'text': '''
        <p class="narration">你弯腰拿起那件嫁衣。</p>
        <p class="narration">嫁衣入手冰凉，像是刚从冰窖里取出来的。</p>
        <p class="narration">你注意到嫁衣上的污渍不是血，而是烧焦的痕迹。</p>
        <p class="detail">这件嫁衣...曾经被火烧过。</p>
        <p class="narration">突然，嫁衣开始剧烈抖动，像是有什么东西想要挣脱。</p>
        <p class="horror">嫁衣从你手中飞起，在空中展开，像是有人穿着它。</p>
        <p class="narration">一个女人的轮廓在嫁衣中显现...</p>
        <p class="horror">"这是...我的...嫁衣..."</p>
        ''',
        'background': 'floating_dress',
        'ambience': 'ghost_wail',
        'sanity_effect': -10,
        'add_flag': 'touched_dress',
        'choices': [
            {'text': '扔掉嫁衣逃跑', 'next': 'drop_dress_run', 'sanity_change': -5},
            {'text': '用火折子烧掉嫁衣', 'next': 'burn_dress', 'sanity_change': 0, 'require_item': '火折子'},
            {'text': '抓住嫁衣不放', 'next': 'hold_dress', 'sanity_change': -20}
        ]
    },
    
    'burn_dress': {
        'title': '焚烧嫁衣',
        'text': '''
        <p class="narration">你举起火折子，将火焰凑近嫁衣。</p>
        <p class="narration">嫁衣瞬间燃烧起来，发出刺耳的尖叫声。</p>
        <p class="horror">"不！不要！"</p>
        <p class="narration">火焰中，你看到一个女人的身影在挣扎、扭曲。</p>
        <p class="narration">她的脸在火光中显现——那是一张美丽却扭曲的脸，充满了怨恨和痛苦。</p>
        <p class="horror">"你们...都要...陪葬！"</p>
        <p class="narration">嫁衣化为灰烬，女人的身影也消散了。</p>
        <p class="narration">但你知道，这只是削弱了她的力量，并没有彻底消灭她。</p>
        <p class="detail">你需要找到骨灰坛，完成封印。</p>
        ''',
        'background': 'burning_dress',
        'ambience': 'fire_scream',
        'add_flag': 'burned_dress',
        'add_secret': '焚烧嫁衣',
        'choices': [
            {'text': '拿起骨灰坛', 'next': 'take_urn_after_burn', 'sanity_change': 0},
            {'text': '查看棺材', 'next': 'examine_coffin_after_burn', 'sanity_change': -5}
        ]
    },
    
    'take_urn': {
        'title': '骨灰坛',
        'text': '''
        <p class="narration">你拿起骨灰坛。</p>
        <p class="narration">坛子冰凉沉重，上面刻着"阿绣"二字和一些符文。</p>
        <p class="narration">你注意到坛子上的封印已经被打破，盖子是松的。</p>
        <p class="detail">里面的骨灰还在，但似乎少了一些。</p>
        <p class="narration">突然，你感到一阵寒意袭来。</p>
        <p class="narration">身后传来轻轻的脚步声...</p>
        ''',
        'background': 'urn',
        'ambience': 'footsteps_behind',
        'sanity_effect': -5,
        'choices': [
            {'text': '转身查看', 'next': 'turn_to_axiu', 'sanity_change': -15},
            {'text': '不回头，立即进行封印', 'next': 'seal_ritual', 'sanity_change': 0, 'require_flag': 'have_seal_items'},
            {'text': '拿着骨灰坛逃跑', 'next': 'escape_with_urn', 'sanity_change': -10}
        ]
    },
    
    'take_urn_after_burn': {
        'title': '骨灰坛',
        'text': '''
        <p class="narration">你拿起骨灰坛。</p>
        <p class="narration">焚烧嫁衣后，地下室安静了许多，但空气中仍弥漫着不祥的气息。</p>
        <p class="narration">你知道，阿绣只是暂时被削弱了，你必须尽快完成封印。</p>
        ''',
        'background': 'urn_quiet',
        'ambience': 'silence',
        'add_item': '骨灰坛',
        'choices': [
            {'text': '进行封印仪式', 'next': 'seal_ritual', 'sanity_change': 0, 'require_flag': 'have_seal_items'},
            {'text': '离开地下室', 'next': 'backyard_path', 'sanity_change': 0}
        ]
    }
})


# 结局场景
SCENES.update({
    'seal_ritual': {
        'title': '封印仪式',
        'text': '''
        <p class="narration">你将骨灰坛放在地上，取出朱砂和镇魂符。</p>
        <p class="narration">按照手札上的记载，你开始在骨灰坛上画符。</p>
        <p class="narration">朱砂在你手中发出微弱的光芒，符文渐渐成形。</p>
        <p class="narration">突然，地下室的温度骤降，你的呼吸化作白雾。</p>
        <p class="horror">"你...想封印我？"</p>
        <p class="narration">阿绣的声音从四面八方传来。</p>
        <p class="narration">她的身影在你面前凝聚，红衣飘飘，长发遮面。</p>
        <p class="horror">"六十年...我等了六十年..."</p>
        <p class="narration">她缓缓抬起头，露出那张苍白扭曲的脸。</p>
        <p class="horror">"没有人...能再封印我！"</p>
        ''',
        'background': 'seal_confrontation',
        'ambience': 'ritual',
        'choices': [
            {'text': '继续画符，念诵咒语', 'next': 'continue_seal', 'sanity_change': -20},
            {'text': '与她对话，试图安抚', 'next': 'talk_to_axiu_final', 'sanity_change': -10},
            {'text': '放弃封印，逃跑', 'next': 'abandon_seal', 'sanity_change': -30}
        ]
    },
    
    'continue_seal': {
        'title': '封印',
        'text': '''
        <p class="narration">你咬紧牙关，继续画符。</p>
        <p class="narration">"太上老君急急如律令，镇魂安魄，永世不出..."</p>
        <p class="narration">阿绣发出尖锐的惨叫，向你扑来。</p>
        <p class="narration">她的手穿过你的身体，带来刺骨的寒冷。</p>
        <p class="horror">你感到生命力在流失...</p>
        <p class="narration">但你没有停下，继续念诵咒语。</p>
        <p class="narration">符文开始发光，骨灰坛上升起一道金色的光芒。</p>
        <p class="narration">阿绣的身影开始扭曲、消散。</p>
        <p class="horror">"不...不要...我不想...再被关起来..."</p>
        <p class="narration">她的声音中带着哭腔，不再是怨恨，而是恐惧和悲伤。</p>
        ''',
        'background': 'sealing',
        'ambience': 'chanting',
        'sanity_effect': -20,
        'choices': [
            {'text': '完成封印', 'next': 'ending_seal', 'sanity_change': -10},
            {'text': '停下来，听她说', 'next': 'listen_to_axiu', 'sanity_change': 0}
        ]
    },
    
    'talk_to_axiu_final': {
        'title': '对话',
        'text': '''
        <p class="narration">"阿绣...我知道你受了委屈。"你颤抖着说。</p>
        <p class="narration">阿绣停下了脚步，那双空洞的眼睛注视着你。</p>
        <p class="horror">"委屈？你知道什么是委屈？"</p>
        <p class="narration">"新婚之夜，被活活烧死...六十年，困在黑暗中..."</p>
        <p class="narration">她的声音颤抖着，泪水从那苍白的脸上流下。</p>
        <p class="horror">"我只是想...有人记得我...有人为我报仇..."</p>
        <p class="narration">"你父亲...他答应帮我...但他骗了我..."</p>
        <p class="narration">你想起父亲日记中的内容，心中涌起复杂的情绪。</p>
        ''',
        'background': 'axiu_crying',
        'ambience': 'sobbing',
        'sanity_effect': -10,
        'choices': [
            {'text': '"我可以帮你超度，让你安息"', 'next': 'offer_peace', 'sanity_change': 0},
            {'text': '"对不起，但我必须封印你"', 'next': 'apologize_seal', 'sanity_change': -10},
            {'text': '"你杀了我父亲，我不会原谅你"', 'next': 'refuse_forgive', 'sanity_change': -15}
        ]
    },
    
    'offer_peace': {
        'title': '超度',
        'text': '''
        <p class="narration">"阿绣，我可以帮你超度。"你说，"让你不再受苦，让你安息。"</p>
        <p class="narration">阿绣愣住了，那双空洞的眼睛中闪过一丝光芒。</p>
        <p class="horror">"你...愿意帮我？"</p>
        <p class="narration">"陈家欠你的，我来还。"你说，"但你也要放下怨恨。"</p>
        <p class="narration">阿绣沉默了很久，最后缓缓点头。</p>
        <p class="narration">"好...我累了...我想休息了..."</p>
        <p class="narration">你拿起朱砂，在骨灰坛上画下不同的符文——这是超度的符文。</p>
        <p class="narration">金色的光芒笼罩了阿绣，她的身影渐渐变得柔和。</p>
        <p class="narration">她最后看了你一眼，嘴角露出一丝微笑。</p>
        <p class="detail">"谢谢你..."</p>
        <p class="narration">然后，她化作点点光芒，消散在空气中。</p>
        ''',
        'background': 'transcendence',
        'ambience': 'peace',
        'choices': [
            {'text': '继续', 'next': 'ending_peace', 'sanity_change': 20}
        ]
    },
    
    'ending_peace': {
        'title': '结局 · 往生',
        'text': '''
        <p class="narration">阿绣走了，带着六十年的怨恨和悲伤。</p>
        <p class="narration">地下室恢复了平静，那股阴冷的气息也消散了。</p>
        <p class="narration">你走出老宅，天边已经泛起鱼肚白。</p>
        <p class="narration">回头望去，陈家老宅在晨光中显得格外沧桑。</p>
        <p class="narration">你知道，父亲已经不在了，但至少，阿绣得到了安息。</p>
        <p class="narration">也许，这就是最好的结局。</p>
        <p class="ending">【往生结局】</p>
        <p class="ending">你选择了宽恕与救赎，让怨灵得到超度。</p>
        <p class="ending">陈家的罪孽，终于画上了句号。</p>
        ''',
        'background': 'sunrise',
        'ambience': 'morning',
        'is_ending': True,
        'ending_type': 'peace',
        'choices': [
            {'text': '重新开始', 'next': 'prologue', 'sanity_change': 0, 'reset': True}
        ]
    },
    
    'ending_seal': {
        'title': '结局 · 封印',
        'text': '''
        <p class="narration">你完成了最后一笔符文，大声念出咒语的最后一句。</p>
        <p class="narration">金色的光芒将阿绣笼罩，她发出最后一声惨叫。</p>
        <p class="horror">"我会回来的...六十年后...我会回来..."</p>
        <p class="narration">她的身影被吸入骨灰坛中，符文闪烁着封住了坛口。</p>
        <p class="narration">一切归于平静。</p>
        <p class="narration">你瘫坐在地上，浑身冰冷，精疲力竭。</p>
        <p class="narration">封印完成了，但你知道，这只是暂时的。</p>
        <p class="narration">六十年后，阿绣还会回来。届时，又会是谁来面对她？</p>
        <p class="ending">【封印结局】</p>
        <p class="ending">你成功封印了怨灵，但这只是将问题推迟。</p>
        <p class="ending">陈家的诅咒，将继续延续...</p>
        ''',
        'background': 'sealed',
        'ambience': 'silence',
        'is_ending': True,
        'ending_type': 'seal',
        'choices': [
            {'text': '重新开始', 'next': 'prologue', 'sanity_change': 0, 'reset': True}
        ]
    },
    
    'listen_to_axiu': {
        'title': '倾听',
        'text': '''
        <p class="narration">你停下了手中的动作，看着阿绣。</p>
        <p class="narration">"告诉我，发生了什么。"</p>
        <p class="narration">阿绣的身影颤抖着，泪水从那苍白的脸上流下。</p>
        <p class="horror">"我...我只是一个童养媳..."</p>
        <p class="narration">"新婚之夜，他嫌我出身卑微，说我配不上陈家..."</p>
        <p class="narration">"他...他放火烧了新房...我被活活烧死..."</p>
        <p class="narration">"我的尸体被扔进井里，没有人为我收尸，没有人为我哭泣..."</p>
        <p class="narration">她的声音越来越悲切，整个地下室都在颤抖。</p>
        <p class="horror">"六十年...我在黑暗中等了六十年..."</p>
        ''',
        'background': 'axiu_story',
        'ambience': 'tragic',
        'choices': [
            {'text': '"我帮你超度"', 'next': 'offer_peace', 'sanity_change': 0},
            {'text': '"对不起，但我必须封印你"', 'next': 'apologize_seal', 'sanity_change': -10}
        ]
    },
    
    'apologize_seal': {
        'title': '抱歉',
        'text': '''
        <p class="narration">"对不起，阿绣。"你说，"但我必须封印你。"</p>
        <p class="narration">"你已经杀了太多人，我不能让你继续伤害无辜。"</p>
        <p class="narration">阿绣的脸扭曲了，怨恨重新涌上她的眼眶。</p>
        <p class="horror">"无辜？陈家人...有谁是无辜的？"</p>
        <p class="narration">她向你扑来，但你已经完成了符文。</p>
        <p class="narration">金色的光芒将她笼罩，她发出凄厉的惨叫。</p>
        <p class="horror">"我恨你们...我恨你们所有人！"</p>
        <p class="narration">她的身影被吸入骨灰坛中，封印完成。</p>
        ''',
        'background': 'forced_seal',
        'ambience': 'screaming',
        'sanity_effect': -10,
        'choices': [
            {'text': '继续', 'next': 'ending_seal', 'sanity_change': 0}
        ]
    },
    
    'refuse_forgive': {
        'title': '拒绝',
        'text': '''
        <p class="narration">"你杀了我父亲！"你怒吼道，"我不会原谅你！"</p>
        <p class="narration">阿绣的脸扭曲成狰狞的模样。</p>
        <p class="horror">"原谅？我从来没有要求你的原谅！"</p>
        <p class="narration">"陈家欠我一条命，你父亲已经还了..."</p>
        <p class="horror">"现在，轮到你了！"</p>
        <p class="narration">她向你扑来，冰冷的手掐住你的脖子。</p>
        <p class="narration">你感到生命在流失，眼前一片黑暗...</p>
        ''',
        'background': 'attack',
        'ambience': 'choking',
        'sanity_effect': -15,
        'choices': [
            {'text': '挣扎着完成封印', 'next': 'desperate_seal', 'sanity_change': -20},
            {'text': '放弃抵抗', 'next': 'ending_death', 'sanity_change': -50}
        ]
    },
    
    'desperate_seal': {
        'title': '绝境',
        'text': '''
        <p class="narration">你用尽最后的力气，将朱砂涂在骨灰坛上。</p>
        <p class="narration">符文在你模糊的视线中发出光芒。</p>
        <p class="narration">"太上老君...急急如律令..."你艰难地念出咒语。</p>
        <p class="narration">阿绣惨叫着松开了手，被金光吸入骨灰坛中。</p>
        <p class="narration">你瘫倒在地，大口喘息着。</p>
        <p class="narration">封印完成了，但你也付出了惨重的代价。</p>
        ''',
        'background': 'desperate',
        'ambience': 'heavy_breathing',
        'sanity_effect': -20,
        'choices': [
            {'text': '继续', 'next': 'ending_pyrrhic', 'sanity_change': 0}
        ]
    },
    
    'ending_pyrrhic': {
        'title': '结局 · 惨胜',
        'text': '''
        <p class="narration">你艰难地爬出地下室，天已经亮了。</p>
        <p class="narration">你的身体虚弱不堪，头发在一夜之间变得花白。</p>
        <p class="narration">你知道，阿绣带走了你的一部分生命力。</p>
        <p class="narration">你活了下来，但你再也不是从前的你了。</p>
        <p class="narration">每到深夜，你都会听到那个声音在耳边低语：</p>
        <p class="horror">"六十年后...我会回来找你..."</p>
        <p class="ending">【惨胜结局】</p>
        <p class="ending">你封印了怨灵，但付出了惨重的代价。</p>
        <p class="ending">余生，你将活在恐惧的阴影中...</p>
        ''',
        'background': 'pyrrhic',
        'ambience': 'haunted',
        'is_ending': True,
        'ending_type': 'pyrrhic',
        'choices': [
            {'text': '重新开始', 'next': 'prologue', 'sanity_change': 0, 'reset': True}
        ]
    },
    
    'ending_death': {
        'title': '结局 · 死亡',
        'text': '''
        <p class="narration">你放弃了抵抗，任由黑暗将你吞噬。</p>
        <p class="narration">最后一刻，你看到阿绣的脸近在咫尺。</p>
        <p class="narration">她的嘴角挂着诡异的笑容。</p>
        <p class="horror">"欢迎...加入我们..."</p>
        <p class="narration">你的意识渐渐消散，化作老宅中的又一个亡魂。</p>
        <p class="narration">从此，陈家老宅又多了一个纸人...</p>
        <p class="ending">【死亡结局】</p>
        <p class="ending">你成为了老宅的一部分，永远困在这里。</p>
        <p class="ending">也许有一天，会有人来救你...</p>
        <p class="ending">也许不会。</p>
        ''',
        'background': 'death',
        'ambience': 'flatline',
        'is_ending': True,
        'ending_type': 'death',
        'choices': [
            {'text': '重新开始', 'next': 'prologue', 'sanity_change': 0, 'reset': True}
        ]
    },
    
    'abandon_seal': {
        'title': '逃跑',
        'text': '''
        <p class="narration">你扔下朱砂，转身就跑。</p>
        <p class="narration">阿绣的笑声在身后响起。</p>
        <p class="horror">"跑？你能跑到哪里去？"</p>
        <p class="narration">你冲出地下室，穿过后院，向大门跑去。</p>
        <p class="narration">但无论你怎么跑，老宅的大门始终在你面前。</p>
        <p class="narration">你被困在这里了。</p>
        <p class="narration">阿绣的身影在你身后显现。</p>
        <p class="horror">"你逃不掉的...没有人能逃出这里..."</p>
        ''',
        'background': 'trapped',
        'ambience': 'laughter',
        'sanity_effect': -30,
        'choices': [
            {'text': '继续挣扎', 'next': 'ending_trapped', 'sanity_change': -20},
            {'text': '回去完成封印', 'next': 'return_to_seal', 'sanity_change': -10}
        ]
    },
    
    'ending_trapped': {
        'title': '结局 · 困囚',
        'text': '''
        <p class="narration">你不知道跑了多久，最终精疲力竭地倒在地上。</p>
        <p class="narration">阿绣站在你面前，俯视着你。</p>
        <p class="horror">"你会留在这里...永远陪着我..."</p>
        <p class="narration">你的意识渐渐模糊，身体变得僵硬。</p>
        <p class="narration">当你再次睁开眼睛时，你发现自己站在正厅里。</p>
        <p class="narration">你想动，却发现自己动不了。</p>
        <p class="horror">你低头看去——你的身体已经变成了纸...</p>
        <p class="ending">【困囚结局】</p>
        <p class="ending">你变成了老宅中的一个纸人，永远困在这里。</p>
        <p class="ending">也许有一天，会有人来到这里...</p>
        <p class="ending">届时，你会对他说什么呢？</p>
        ''',
        'background': 'paper_person',
        'ambience': 'eternal_silence',
        'is_ending': True,
        'ending_type': 'trapped',
        'choices': [
            {'text': '重新开始', 'next': 'prologue', 'sanity_change': 0, 'reset': True}
        ]
    },
    
    'return_to_seal': {
        'title': '回头',
        'text': '''
        <p class="narration">你停下脚步，深吸一口气。</p>
        <p class="narration">"我不能逃。"你对自己说，"我必须结束这一切。"</p>
        <p class="narration">你转身走回地下室，阿绣的身影在你身后飘荡。</p>
        <p class="horror">"你...要回去？"她的声音中带着一丝惊讶。</p>
        <p class="narration">"是的。"你说，"我要结束这一切。"</p>
        <p class="narration">你重新拿起朱砂，开始画符。</p>
        ''',
        'background': 'return',
        'ambience': 'determination',
        'sanity_effect': -10,
        'choices': [
            {'text': '完成封印', 'next': 'continue_seal', 'sanity_change': -10},
            {'text': '尝试与她对话', 'next': 'talk_to_axiu_final', 'sanity_change': 0}
        ]
    }
})


# 随机恐怖事件 - 增强版
RANDOM_EVENTS = [
    {
        'text': '<p class="horror">你感到有什么东西在注视着你...</p>',
        'sanity_change': -5,
        'effect': 'watching'
    },
    {
        'text': '<p class="horror">身后传来轻微的脚步声，但当你回头时，什么也没有。</p>',
        'sanity_change': -3,
        'effect': 'footsteps'
    },
    {
        'text': '<p class="horror">一阵阴风吹过，你听到有人在耳边低语你的名字...</p>',
        'sanity_change': -5,
        'effect': 'whisper'
    },
    {
        'text': '<p class="horror">墙上的影子似乎动了一下...</p>',
        'sanity_change': -3,
        'effect': 'shadow'
    },
    {
        'text': '<p class="horror">你闻到一股焦糊的气味，像是有什么东西在燃烧...</p>',
        'sanity_change': -5,
        'effect': 'burning'
    },
    {
        'text': '<p class="horror">远处传来女人的哭声，凄厉而悲切...</p>',
        'sanity_change': -5,
        'effect': 'crying'
    },
    {
        'text': '<p class="horror">你的影子...似乎比你慢了一拍...</p>',
        'sanity_change': -8,
        'effect': 'shadow_delay'
    },
    {
        'text': '<p class="horror">镜子里的你...在笑，但你没有笑...</p>',
        'sanity_change': -10,
        'effect': 'mirror'
    },
    {
        'text': '<p class="horror">你看到窗外有一张苍白的脸一闪而过...</p>',
        'sanity_change': -8,
        'effect': 'face_flash'
    },
    {
        'text': '<p class="horror">天花板上传来"咚咚"的脚步声，像是有人在上面走动...</p>',
        'sanity_change': -6,
        'effect': 'ceiling_steps'
    },
    {
        'text': '<p class="horror">你感到有冰冷的手指轻轻划过你的后颈...</p>',
        'sanity_change': -10,
        'effect': 'cold_touch'
    },
    {
        'text': '<p class="horror">角落里的纸人...它的头转向了你...</p>',
        'sanity_change': -12,
        'effect': 'paper_turn'
    },
    {
        'text': '<p class="horror">"回来..."一个声音在你脑海中回响...</p>',
        'sanity_change': -7,
        'effect': 'voice_inside'
    },
    {
        'text': '<p class="horror">你的手表停了，指针定格在子时...</p>',
        'sanity_change': -5,
        'effect': 'time_stop'
    },
    {
        'text': '<p class="horror">地上出现了一串湿漉漉的脚印，从门外延伸到你身后...</p>',
        'sanity_change': -10,
        'effect': 'wet_footprints'
    },
    {
        'text': '<p class="horror">你听到有人在唱那首童谣..."红嫁衣，红盖头..."</p>',
        'sanity_change': -8,
        'effect': 'nursery_rhyme'
    }
]

# 跳吓事件 - 特定场景触发
JUMPSCARE_EVENTS = {
    'look_back': {
        'type': 'ghost_bride',
        'text': '红衣女子的脸突然出现在你面前！',
        'sound': 'scream'
    },
    'peek_side_door': {
        'type': 'paper_eye',
        'text': '一只眼睛从门缝中直直地盯着你！',
        'sound': 'jumpscare'
    },
    'push_figure': {
        'type': 'paper_face',
        'text': '纸人的脸扭曲着向你逼近！',
        'sound': 'scream'
    },
    'examine_portrait': {
        'type': 'portrait_alive',
        'text': '画中的女子睁开了眼睛！',
        'sound': 'ghost'
    },
    'open_well': {
        'type': 'corpse',
        'text': '井中的尸体突然睁开了眼！',
        'sound': 'jumpscare'
    },
    'lift_veil': {
        'type': 'black_eyes',
        'text': '红盖头下是一张没有眼睛的脸！',
        'sound': 'scream'
    },
    'call_father': {
        'type': 'fake_father',
        'text': '那不是你父亲的声音...',
        'sound': 'ghost'
    }
}

# 危险选项标记
DANGEROUS_CHOICES = [
    '回头', '窥视', '推倒', '撕掉', '呵斥', '质问',
    '揭开', '强行', '移开石板', '直视', '抓住', '放弃'
]

# 理智值过低时的效果
INSANITY_EFFECTS = {
    70: '你开始感到不安，总觉得有什么东西在暗处窥视。',
    50: '你的手开始颤抖，眼角似乎看到了什么东西在移动。',
    30: '你听到了不存在的声音，看到了不存在的影子。现实与幻觉开始模糊。',
    10: '你几乎无法分辨什么是真实的。也许...你已经疯了？'
}

# 恐怖氛围等级
def get_horror_level(state):
    """根据游戏状态计算恐怖等级"""
    level = 0
    level += (100 - state.get('sanity', 100)) // 10
    level += state.get('time_in_mansion', 0) // 3
    level += len(state.get('discovered_secrets', [])) * 2
    
    # 特定标记增加恐怖等级
    flags = state.get('flags', {})
    if flags.get('angered_paper_figure'):
        level += 5
    if flags.get('burned_portrait'):
        level += 3
    if flags.get('met_axiu'):
        level += 10
    if flags.get('awakened_axiu'):
        level += 15
        
    return min(level, 100)

# Flask路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_game():
    """开始新游戏"""
    session['game_state'] = GameState().to_dict()
    return jsonify({
        'success': True,
        'scene': SCENES['prologue'],
        'state': session['game_state']
    })

@app.route('/api/choice', methods=['POST'])
def make_choice():
    """处理玩家选择"""
    data = request.json
    choice_index = data.get('choice_index', 0)
    
    if 'game_state' not in session:
        session['game_state'] = GameState().to_dict()
    
    state = session['game_state']
    current_scene = SCENES.get(state['current_scene'], SCENES['prologue'])
    
    if choice_index >= len(current_scene.get('choices', [])):
        return jsonify({'success': False, 'error': '无效的选择'})
    
    choice = current_scene['choices'][choice_index]
    
    # 检查是否需要特定物品
    if 'require_item' in choice and choice['require_item'] not in state['items']:
        return jsonify({
            'success': False, 
            'error': f'你需要 {choice["require_item"]} 才能这样做'
        })
    
    # 检查是否需要特定标记
    if 'require_flag' in choice and not state['flags'].get(choice['require_flag']):
        return jsonify({
            'success': False,
            'error': '你还没有准备好这样做'
        })
    
    # 重置游戏
    if choice.get('reset'):
        session['game_state'] = GameState().to_dict()
        return jsonify({
            'success': True,
            'scene': SCENES['prologue'],
            'state': session['game_state']
        })
    
    # 更新游戏状态
    next_scene_id = choice['next']
    state['current_scene'] = next_scene_id
    state['sanity'] += choice.get('sanity_change', 0)
    state['time_in_mansion'] += 1
    
    # 添加物品
    if 'add_item' in choice and choice['add_item'] not in state['items']:
        state['items'].append(choice['add_item'])
    if 'add_item2' in choice and choice['add_item2'] not in state['items']:
        state['items'].append(choice['add_item2'])
    
    # 添加标记
    if 'add_flag' in choice:
        state['flags'][choice['add_flag']] = True
    if 'add_flag2' in choice:
        state['flags'][choice['add_flag2']] = True
    
    next_scene = SCENES.get(next_scene_id, SCENES['prologue'])
    
    # 场景效果
    if 'sanity_effect' in next_scene:
        state['sanity'] += next_scene['sanity_effect']
    if 'add_item' in next_scene and next_scene['add_item'] not in state['items']:
        state['items'].append(next_scene['add_item'])
    if 'add_flag' in next_scene:
        state['flags'][next_scene['add_flag']] = True
    if 'add_secret' in next_scene and next_scene['add_secret'] not in state['discovered_secrets']:
        state['discovered_secrets'].append(next_scene['add_secret'])
    
    # 检查是否是危险选项
    choice_text = choice.get('text', '')
    is_dangerous = any(keyword in choice_text for keyword in DANGEROUS_CHOICES)
    
    # 检查是否触发跳吓
    jumpscare = None
    if next_scene_id in JUMPSCARE_EVENTS and random.random() < 0.6:
        jumpscare = JUMPSCARE_EVENTS[next_scene_id]
    
    # 随机恐怖事件 - 概率随恐怖等级增加
    horror_level = get_horror_level(state)
    event_chance = 0.15 + (horror_level / 200)  # 基础15%，最高65%
    
    random_event = None
    if random.random() < event_chance and not next_scene.get('is_ending'):
        random_event = random.choice(RANDOM_EVENTS)
        state['sanity'] += random_event['sanity_change']
    
    # 理智值边界
    state['sanity'] = max(0, min(100, state['sanity']))
    
    # 理智值过低效果
    insanity_message = None
    for threshold, message in sorted(INSANITY_EFFECTS.items(), reverse=True):
        if state['sanity'] <= threshold:
            insanity_message = message
            break
    
    # 计算恐怖效果
    horror_effects = {
        'level': horror_level,
        'is_dangerous': is_dangerous,
        'should_shake': is_dangerous or state['sanity'] < 30,
        'should_flash': state['sanity'] < 50 and random.random() < 0.3,
        'ghost_chance': min(0.5, horror_level / 100),
        'ambient_horror': state['sanity'] < 40
    }
    
    # 理智值归零 - 死亡
    if state['sanity'] <= 0:
        state['death_count'] += 1
        return jsonify({
            'success': True,
            'scene': {
                'title': '结局 · 疯狂',
                'text': '''
                <p class="narration">你的理智已经完全崩溃。</p>
                <p class="narration">你分不清什么是真实，什么是幻觉。</p>
                <p class="narration">你开始大笑，笑声在空荡的老宅中回响。</p>
                <p class="horror">也许...你已经成为了这里的一部分...</p>
                <p class="ending">【疯狂结局】</p>
                <p class="ending">你的理智归零，永远迷失在恐惧中。</p>
                ''',
                'background': 'insanity',
                'ambience': 'madness',
                'is_ending': True,
                'ending_type': 'insanity',
                'choices': [
                    {'text': '重新开始', 'next': 'prologue', 'reset': True}
                ]
            },
            'state': state,
            'random_event': random_event,
            'insanity_message': insanity_message,
            'jumpscare': {'type': 'insanity_face', 'text': '你疯了...'},
            'horror_effects': horror_effects
        })
    
    session['game_state'] = state
    
    return jsonify({
        'success': True,
        'scene': next_scene,
        'state': state,
        'random_event': random_event,
        'insanity_message': insanity_message,
        'jumpscare': jumpscare,
        'horror_effects': horror_effects
    })

@app.route('/api/state', methods=['GET'])
def get_state():
    """获取当前游戏状态"""
    if 'game_state' not in session:
        session['game_state'] = GameState().to_dict()
    
    state = session['game_state']
    current_scene = SCENES.get(state['current_scene'], SCENES['prologue'])
    
    return jsonify({
        'success': True,
        'scene': current_scene,
        'state': state
    })

# 导入额外场景
try:
    from scenes_extra import EXTRA_SCENES
    SCENES.update(EXTRA_SCENES)
except ImportError:
    pass

if __name__ == '__main__':
    app.run(debug=True, port=5008, host='0.0.0.0')
