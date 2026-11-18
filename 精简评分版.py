from pathlib import Path
import json, re, subprocess

ROOT = Path(__file__).resolve().parent
raw = json.loads((ROOT/'地方风土资料.json').read_text(encoding='utf-8'))
old = (ROOT/'北京铁路旅行清单-线路版.html').read_text(encoding='utf-8')
prefix = re.search(r'<script>([\s\S]*?)</script>', old)[1].split('const $=')[0]
code = 'const vm=require("vm");const c={};vm.createContext(c);vm.runInContext('+json.dumps(prefix)+'+";globalThis.out={routes,sources,stationGuide};",c);console.log(JSON.stringify(c.out));'
base = json.loads(subprocess.run(['node'],input=code,capture_output=True,text=True,encoding='utf-8',check=True).stdout)

# 主观评分：只评价列出景点的不可替代性；同类资源越普遍，分数越低。
SCORES = '''八达岭|8|明长城关沟段，山地防御体系完整；长城沿线仍有多处替代。
延庆|6.5|山水与园林以近郊休闲为主，龙庆峡有辨识度。
怀来|6.5|鸡鸣驿保留驿城格局；水库与葡萄酒体验同类较多。
张家口|7.5|大境门的边贸门户形象突出，堡子里补充城镇历史。
崇礼|6.5|冬奥场馆组合鲜明，滑雪本身可被其他雪场替代。
乌兰察布|8.5|乌兰哈达火山与高原草甸组合突出。
呼和浩特|8|召庙群、土默川与塞上老街形成鲜明地域组合。
包头|7|五当召的藏传佛教建筑是核心差异，其他休闲景观较常见。
大同|9.5|云冈北魏石窟，叠加华严寺、善化寺辽金古建。
浑源|9|悬空寺崖壁木构极有辨识度，恒山补充山岳景观。
应县|9.5|辽代木塔的年代、体量与木结构稀缺性极高。
朔州|8|崇福寺金代建筑与彩塑，是高于普通古城游的核心。
忻州|9|五台山寺院群与佛光寺唐代木构；主资源在远郊县域。
太原|9|晋祠宋代木构与彩塑，叠加山西博物院文物体系。
晋中、太谷、祁县|8|晋商宅院群有整体价值，单座大院之间存在替代。
平遥|9|城墙、街巷、票号与双林寺彩塑构成完整历史组合。
介休|8|张壁古堡的堡寨与宗教建筑组合鲜明。
灵石|8|王家大院规模与雕饰突出，同类晋商大院可部分替代。
临汾、洪洞|9|广胜寺建筑壁画与隰县小西天悬塑，稀缺资源分散。
运城|9|永乐宫元代壁画、解州关帝庙与盐湖叠加。
涿州|5.5|地方古迹有历史线索，但现有景点组合的全国稀缺性有限。
保定|7.5|直隶总督署的官署属性突出，莲池补充省城历史。
定州|8|开元寺塔与地方出土文物辨识度高，行程紧凑。
石家庄、正定|8.5|隆兴寺造像与正定多时期寺塔，古建密度高。
邢台|6.5|古寺与太行山水有价值，同类资源替代较多。
邯郸|8.5|响堂山北朝石窟与赵文化、磁州窑形成多层组合。
安阳、林州|9.5|殷墟甲骨与商代遗存不可替代；红旗渠另有现代史价值。
鹤壁|8|大伾山石佛、浚县古城与运河遗产组合独特。
新乡|7.5|郭亮挂壁公路与南太行崖壁村落突出，峡谷同类较多。
郑州、登封|8.5|嵩山古建群、少林文化与河南博物院，核心多在登封。
洛阳|9.5|龙门北魏至唐代造像，叠加多时期都城遗址与文物。
开封|8|铁塔与宋都历史价值高；复建街区、主题演艺替代性较强。
许昌|6|曹魏文化有明确关联，现有旅游呈现较依赖纪念与复建。
漯河|6|许慎文字学主题鲜明，景观与原址遗存的稀缺性有限。
驻马店|7|嵖岈山花岗岩地貌有辨识度，同类山岳可部分替代。
雄安|6.5|白洋淀芦苇湿地与新城建设有组合差异，湖区同类较多。
任丘、河间|6|河间府署与地方城镇史有特色，景点组合较薄。
深州|4.5|果园与乡村体验为主，专程旅游的稀缺景点较少。
衡水|6.5|内画工艺与衡水湖有地方辨识度，湖景本身常见。
临清|8|钞关、舍利塔与运河商镇遗存，漕运主题集中。
聊城|7.5|东昌湖环城格局与光岳楼、会馆组合鲜明。
梁山|5.5|水浒文学关联明确，山水与主题演艺替代性较强。
郓城|5|文化主题明确，核心旅游呈现以当代仿古景区为主。
菏泽|7|牡丹种植与地方戏曲辨识度高，花期之外优势下降。
商丘|7.5|古城空间与应天书院历史线索突出，建筑呈现需区分复建。
廊坊|6|戏剧幻城有当代创作特色，其他景点的地域稀缺性较低。
沧州|7.5|铁狮子、吴桥杂技与运河构成特色组合，分布较散。
德州|5.5|运河历史有价值，现有主景点较难形成稀缺组合。
济南|8.5|泉群与老城日常水系交织，区别于普通湖泊公园。
泰安|9|泰山碑刻、封禅传统与岱庙，把山岳与历史景观结合。
曲阜|9.5|三孔与孔氏家族延续的礼制空间，文化原点难替代。
滕州|6.5|墨学与地方文博主题明确，湿地休闲同类较多。
枣庄|6.5|运河、矿业和铁路主题有组合性；台儿庄以复建游览为主。
徐州|8.5|汉墓、汉画像石与汉代出土文物形成强主题。
宿州、萧县|6|皇藏峪与地方文博有特色，同类山林较多。
蚌埠|6.5|淮河与花鼓灯有地域辨识度，常设景点稀缺性一般。
滁州|7.5|醉翁亭与琅琊山的文学地景关系鲜明。
合肥|7|安徽博物院与庐州文化有内容，公园古镇同类较多。
淄博|8|临淄齐文化、周村商埠与博山陶琉构成多中心组合。
青州|8.5|龙兴寺出土佛教造像是核心稀缺资源。
潍坊|7.5|风筝、杨家埠年画与十笏园形成地域工艺主题。
青岛|8.5|丘陵海港老城、近代建筑与崂山组合鲜明。
泗水、蒙山区域|7|蒙山山地与儒文化周边资源有特色，整体可替代性仍较高。
临沂|8|银雀山汉简与琅琊文脉是差异，普通山水不单独加分。
日照|6.5|沙滩、松林和渔家体验舒适，同类海岸替代较多。
济宁|7|太白楼与运河商贸遗存有特色，核心景观规模有限。
天津市区|8|海河、近代街区、曲艺与民间工艺构成完整城市体验。
武清|4.5|商业小镇与休闲购物为主，地域性历史景点组合较弱。
天津滨海|7.5|海洋博物馆、海防与港口工业组合突出。
香河|4.5|地方手艺和饮食有特色，主景点稀缺性有限。
宝坻、北辰|5|地方非遗有价值，现有旅游景点缺少强稀缺核心。
唐山|8|早期煤矿铁路工业遗产与皮影、评剧组合鲜明。
北戴河、昌黎|6.5|海滨度假与葡萄产区有组合，沙滩、商业社区替代较多。
秦皇岛、山海关|8.5|山海关与老龙头把长城、关城和海岸连接起来。
怀柔、密云|7.5|慕田峪、司马台等长城段有特色，水库与度假项目较常见。
古北口|8|潮河关口与长城、村落格局相互解释。
兴隆|7|雾灵山山地森林有价值，同类山岳森林较多。
承德|9|避暑山庄与周围寺庙群，清代园林和多种建筑语汇并存。
平泉|6.5|契丹记忆与辽河源生态有地方特色，常设景点组合较薄。
凌源、建平|8.5|牛河梁红山文化遗址具有显著考古稀缺性。
辽宁朝阳|8.5|三燕佛教遗存与热河生物群化石形成跨时段组合。
北票|8|古生物化石资源突出，山林景观本身替代性较强。
阜新|7.5|海棠山摩崖造像与工业遗存组合有辨识度。
沈阳|8.5|清代宫殿陵寝与工业城市遗产形成强历史叠层。
铁岭|6|银冈书院与曲艺有地方性，景点组合稀缺性有限。
四平|6.5|战史主题明确，主要优势集中在特定历史兴趣。
长春|8.5|伪满宫廷遗址、长影与汽车工业史组合鲜明。
赤峰|9|红山考古、契丹辽遗存与草原沙地组合强，远县资源需另程。
克什克腾、乌兰布统|8.5|石阵、草原湖泊与火山地貌组合突出。
通辽|7|科尔沁文化和沙地景观有特色，市区常设景点较薄。
科左后旗、库伦|7.5|大青沟沙地沟谷林与库伦文化有辨识度。
葫芦岛、兴城|7.5|兴城古城格局与海岸、温泉形成组合。
锦州、义县|8.5|奉国寺辽代大殿与塑像稀缺，叠加锦州战史。
盘锦|8|辽河口红海滩、湿地与稻田组合突出，明显依赖季节。
营口、鲅鱼圈|6.5|开埠老街与港湾有特色，海滨休闲同类较多。
大连|8.5|半岛岩岸、近代港城与旅顺海防遗址组合鲜明。
本溪|7.5|水洞与辽东山林有辨识度，溶洞和秋色同类较多。
凤城|7|凤凰山险峻花岗岩地形突出，其他山岳可部分替代。
丹东|8|鸭绿江断桥与边境江城空间，历史和地理关联鲜明。
十渡|6|拒马河岩溶峡谷有辨识度，同类山水较多。
涞源|7.5|白石山峰林和高差突出，山岳景观仍有替代。
灵丘|7.5|觉山寺与平型关历史形成组合，需有对应兴趣。'''
ratings = {}
for row in SCORES.splitlines():
    name, score, reason = row.split('|')
    ratings[name] = {'score':float(score),'reason':reason.rstrip('。')}

def concise(text):
    """删去提示、泛化与阅读指导，保留地点、对象和关系。"""
    kept=[]
    for sentence in re.split('[。；]',text):
        s=sentence.strip()
        if not s: continue
        if any(k in s for k in ['待核','待专题','待县域','待再','需查','需核','须查','须核','另查','另核','不保证','按当年','要按','需要','适合','可以','可作','可找','可关注','可继续','暂不','以现场','作区域','区域选择','区域口味','区域风味','区域背景','具体活动','具体场次','具体北票','具体县级','具体村镇','核心区','不把','别把','不可直接','不能','不等于','不等同','避免','尊重','遵循','遵守','应查','需预约']): continue
        s=re.sub('，?(具体|各县|项目|场次|活动日期|演出时间|体验点).*?(需|待|另查|确认).*$', '', s)
        s=re.sub('是(理解|观察|阅读).*?(入口|线索|主线|对象)', '', s)
        s=s.replace('是两条重要线索','').replace('是两条不同线索','').replace('可作专题','').replace('构成阅读线索','').replace('值得连着看','')
        if s: kept.append(s.rstrip('，'))
    return '；'.join(kept)

FOOD = {
'八达岭':'','延庆':'','怀来':'怀涿葡萄酒','张家口':'莜面、羊肉','崇礼':'','乌兰察布':'莜面、丰镇月饼、卓资熏鸡','呼和浩特':'烧麦、羊杂、焙子、奶茶','包头':'老茶汤、莜面','大同':'刀削面、什锦火锅、盐煎羊肉','浑源':'浑源凉粉','应县':'','朔州':'莜面','忻州':'','太原':'头脑、老鼠窟元宵、蒸饺','晋中、太谷、祁县':'太谷饼','平遥':'平遥牛肉、碗托','介休':'贯馅糖','灵石':'','临汾、洪洞':'晋南年馍','运城':'','涿州':'','保定':'驴肉火烧、槐茂酱菜','定州':'定州马肉','石家庄、正定':'金凤扒鸡、正定八大碗、马家卤鸡','邢台':'','邯郸':'','安阳、林州':'扁粉菜、皮渣；道口烧鸡在滑县','鹤壁':'浚县子馍、王桥豆腐皮、淇县懒渣','新乡':'红焖羊肉、原阳烩面','郑州、登封':'烩面、胡辣汤','洛阳':'水席、牛肉汤、浆面条','开封':'灌汤包、桶子鸡、鲤鱼焙面','许昌':'','漯河':'','驻马店':'','雄安':'','任丘、河间':'河间驴肉火烧','深州':'深州蜜桃','衡水':'','临清':'什香面','聊城':'呱嗒、八批果子','梁山':'','郓城':'','菏泽':'单县羊汤、曹县烧牛肉、成武酱菜','商丘':'剁子羊肉、水激馍','廊坊':'','沧州':'火锅鸡','德州':'德州扒鸡','济南':'把子肉、鲁式糕点','泰安':'泰山豆腐宴、煎饼','曲阜':'孔府菜','滕州':'菜煎饼','枣庄':'菜煎饼','徐州':'烙馍卷馓子、地锅、辣汤','宿州、萧县':'符离集烧鸡','蚌埠':'烧饼夹里脊、小龙虾、冰酒酿','滁州':'','合肥':'庐州烤鸭、鸭油烧饼、吴山贡鹅','淄博':'周村烧饼、博山菜、烧烤','青州':'隆盛糕点','潍坊':'朝天锅、鸡鸭和乐、肉火烧','青岛':'鲅鱼饺子、啤酒','泗水、蒙山区域':'','临沂':'煎饼；沂水丰糕在沂水县','日照':'日照绿茶','济宁':'甏肉干饭','天津市区':'煎饼馃子、锅巴菜、炸糕','武清':'杨村糕干','天津滨海':'','香河':'香河肉饼','宝坻、北辰':'','唐山':'棋子烧饼、饹馇','北戴河、昌黎':'昌黎饺子、葡萄酒','秦皇岛、山海关':'','怀柔、密云':'怀柔板栗、密云鱼肴','古北口':'小锅饽饽、驴打滚','兴隆':'山楂','承德':'满族八大碗、饸饹、杏仁饮品','平泉':'改刀肉、羊汤','凌源、建平':'','辽宁朝阳':'','北票':'','阜新':'','沈阳':'鸡架、饺子、抻面、西塔冷面','铁岭':'','四平':'','长春':'白肉血肠、炒肉拉皮','赤峰':'对夹','克什克腾、乌兰布统':'奶茶、奶食、牛羊肉','通辽':'科尔沁馅饼','科左后旗、库伦':'科尔沁馅饼','葫芦岛、兴城':'酸菜锅','锦州、义县':'锦州烧烤','盘锦':'河蟹、稻米、辽河口渔家菜','营口、鲅鱼圈':'','大连':'焖子、海鲜','本溪':'烤豆皮、羊汤','凤城':'','丹东':'朝鲜族泡菜','十渡':'','涞源':'','灵丘':'黄烧饼'}

EXTRA_REFS = {
'应县':['应县木塔结构 · 中科院力学所','https://imech.cas.cn/science/lxyd/syjh/202505/t20250519_7689883.html'],
'平遥':['平遥古城 · UNESCO','https://whc.unesco.org/en/list/812/'],
'安阳、林州':['殷墟 · UNESCO','https://whc.unesco.org/en/list/1114/'],
'郑州、登封':['登封天地之中古迹 · UNESCO','https://whc.unesco.org/en/list/1305/'],
'泰安':['泰山 · UNESCO','https://whc.unesco.org/en/list/437/']}

CUSTOM = {'张家口':'蔚县剪纸、打树花（蔚县）','乌兰察布':'莜面制作','呼和浩特':'烧麦早餐、奶茶食俗','包头':'老茶汤制作','忻州':'五台山朝山传统','太原':'元宵灯会','晋中、太谷、祁县':'太谷饼制作、晋中花馍','平遥':'推光漆器','介休':'寒食节与介子推传说','临汾、洪洞':'洪洞大槐树祭祖','运城':'关帝文化、河东制盐','定州':'缂丝','石家庄、正定':'正定中幡；藁城宫灯在藁城','邢台':'隆尧抬阁、广宗柳编','邯郸':'磁州窑、武安戏曲','鹤壁':'浚县泥咕咕、古庙会','郑州、登封':'少林功夫、豫剧','洛阳':'牡丹花会','开封':'朱仙镇木版年画、盘鼓','雄安':'芦苇画、苇编','深州':'形意拳','衡水':'内画；武强年画在武强县','临清':'什香面食俗','菏泽':'牡丹花会、地方戏曲','廊坊':'安次传统音乐会','沧州':'孟村八极拳、吴桥杂技','济南':'皮影、趵突泉灯会','泰安':'泰山祈福、登山传统','曲阜':'祭孔、孔府食礼','徐州':'烙馍制作','宿州、萧县':'埇桥马戏','蚌埠':'花鼓灯','滁州':'琅琊山庙会；走太平在全椒','合肥':'庐剧、巢湖民歌','淄博':'陶瓷、琉璃制作','青州':'隆盛糕点制作','潍坊':'风筝、杨家埠木版年画','临沂':'柳琴戏','日照':'传统渔船制作','天津市区':'相声、杨柳青年画、泥人张彩塑','武清':'杨村剪纸','天津滨海':'汉沽飞镲、大港剪纸','香河':'安头屯中幡、大河各庄竹马会','宝坻、北辰':'宝坻皮影（宝坻）','唐山':'评剧、皮影、乐亭大鼓','北戴河、昌黎':'昌黎民歌、吹歌','古北口':'节令饽饽','兴隆':'雾灵山传说、砂画','平泉':'契丹始祖传说','凌源、建平':'凌源皮影','辽宁朝阳':'皮影、绒绣','阜新':'蒙古勒津传统艺术','沈阳':'东北大鼓、秧歌','铁岭':'二人转','通辽':'安代舞','科左后旗、库伦':'库伦安代舞','锦州、义县':'锦州高跷秧歌','盘锦':'辽河口渔家菜、传统排船','大连':'贝雕','本溪':'南芬剪纸、草编','丹东':'朝鲜族泡菜食俗','灵丘':'黄烧饼制作'}
CULTURE = {'崇礼':'冬奥场馆、山地运动','呼和浩特':'召庙文化与农牧交往','包头':'黄河商贸与工业城市','大同':'北朝佛教造像、辽金寺院艺术','太原':'宋塑、山西出土文物','平遥':'票号金融、彩塑、漆艺','运城':'道教壁画与盐业','安阳、林州':'甲骨文字与商代青铜','洛阳':'北魏至唐代佛教艺术','曲阜':'儒家礼制与孔氏家族','徐州':'汉墓、汉画像石','青州':'龙兴寺佛教造像','唐山':'煤矿铁路工业遗产','长春':'长影与汽车工业','赤峰':'红山文化与契丹辽文化','辽宁朝阳':'三燕佛教与古生物化石','沈阳':'清代宫廷与近现代工业','天津市区':'漕运、近代开埠、曲艺','承德':'清代园林与多民族寺院建筑'}

entries=[]
for p in raw['profiles']:
    name=p['names'][0]
    if name not in ratings: raise ValueError('缺少评分：'+name)
    matches=[]
    for i,r in enumerate(base['routes']):
        for row in r['rows'].split('\n'):
            parts=row.split('|')
            if parts[0] in p['names']:
                matches.append((i,r,parts))
    assert matches, name
    sights=list(dict.fromkeys(t[2][2] for t in matches))
    station=list(dict.fromkeys(s for _,r,_ in matches for s in r['stations']))
    route_ids=list(dict.fromkeys(i for i,_,_ in matches))
    notes=[]
    for _,r,t in matches:
        n=t[4]
        if any(k in n for k in ['较远','远郊','分散','跨县','进山','不在','市外','位于','数小时','汽车','开行','乘降','边界','千公里','约 893','995','1000','不同']):
            notes.append(n.replace('适合汽车串联。','').replace('适合周末城市游，',''))
    fields={k:concise(p[k]) for k in ['geo','history','culture','custom']}
    fields['geo']=p['geo'].split('。')[0].split('，')[0]
    fields['history']=p['history'].split('。')[0].split('，')[0].replace('为主要历史线索','').replace('形成新旧叠层','').replace('是两条重要线索','').replace('构成城市历史层次','').removeprefix('以')
    fields['culture']=CULTURE.get(name,'')
    fields['custom']=CUSTOM.get(name,'')
    if name in ['邢台','驻马店','深州','香河','宝坻、北辰','铁岭','十渡','涞源']:
        fields['history']=''
    fields['food']=FOOD.get(name,'')
    refs=[raw['refs'][k] for k in p['refs']]
    if name in EXTRA_REFS:refs.insert(0,EXTRA_REFS[name])
    entries.append(dict(id=name,name=name,aliases=p['names'],**ratings[name],sights='；'.join(sights),
                        stations=station,routes=route_ids,stops=list(dict.fromkeys(t[2][1] for t in matches)),
                        tags=list(dict.fromkeys(tag for _,_,t in matches for tag in t[3].split(' '))),
                        note=' '.join(dict.fromkeys(notes)),edge=next((t[2][5] for t in matches if len(t[2])>5),''),
                        months=sorted(p['months']),zone=p['zone'],fields=fields,refs=refs))

assert len(entries)==102
dataset={'updated':'2026-11-18','entries':entries,'routes':[{'name':r['name'],'line':r['line'],'path':r['path'],'stations':r['stations']} for r in base['routes']],'climate':raw['climate'],'stationGuide':base['stationGuide']}
(ROOT/'城市独特性评分.json').write_text(json.dumps(dataset,ensure_ascii=False,indent=2),encoding='utf-8')

HTML = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>北京周边逃逸行动 · 景点评分</title><style>
:root{--paper:#f6f4ee;--ink:#22352f;--muted:#57665d;--line:#d6ddd2;--green:#245c49}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:14px/1.65 "Microsoft YaHei","PingFang SC",sans-serif}::selection{background:#c7dfb9}a{color:var(--green);text-underline-offset:3px}button,input,select{font:inherit;color:inherit}button{cursor:pointer}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:2px solid #995024;outline-offset:3px}main{max-width:1160px;padding:32px 30px 60px;margin:auto}header{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:20px}h1{font-size:24px;line-height:1.4;margin:0;font-weight:600}header p{color:var(--muted);font-size:12px;margin:0;white-space:nowrap}.filters{display:grid;grid-template-columns:minmax(180px,1fr) 155px 140px 135px 130px;gap:8px}input,select{width:100%;min-width:0;height:40px;border:1px solid #b7c3b8;border-radius:3px;padding:0 10px;background:#fffdf8}input::placeholder{color:var(--muted)}.bar{display:flex;gap:16px;align-items:center;justify-content:space-between;margin:12px 0 6px;color:var(--muted);font-size:12px}.actions{display:flex;align-items:center;gap:16px;flex-wrap:wrap}.actions button{background:none;border:0;padding:4px 0;color:var(--green)}.actions label{display:flex;align-items:center;gap:5px}.actions input{width:14px;height:14px;accent-color:var(--green)}.method{margin:0 0 20px;color:var(--muted);font-size:12px}.method summary{cursor:pointer;width:fit-content}.method p{max-width:80ch;margin:10px 0}.results{border-top:1px solid var(--line)}.place{display:grid;grid-template-columns:64px minmax(0,1fr) 28px;gap:16px;padding:18px 0;border-bottom:1px solid var(--line)}.score{font-size:27px;line-height:1.25;font-variant-numeric:tabular-nums;letter-spacing:-.03em;color:var(--green)}.score small{display:block;font-size:11px;color:var(--muted);letter-spacing:0}.heading{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap}.heading h2{font-size:17px;margin:0;font-weight:600}.heading span{font-size:11px;color:var(--muted)}.reason{margin:5px 0;color:var(--ink)}.sights{font-size:12px;color:var(--muted);margin:4px 0}.star{border:0;background:none;color:var(--muted);width:28px;height:32px;padding:4px}.star svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.6}.star[aria-pressed=true]{color:var(--green)}.star[aria-pressed=true] svg{fill:currentColor}.detail{margin-top:7px;font-size:12px}.detail>summary{color:var(--green);cursor:pointer;width:fit-content}.facts{display:grid;grid-template-columns:1fr 1fr;gap:12px 24px;margin:14px 0}.facts div{min-width:0}.facts dt{color:var(--muted);margin-bottom:3px;font-size:11px}.facts dd{margin:0}.transport{padding:10px 0;border-top:1px solid var(--line);color:var(--muted)}.transport p{margin:4px 0}.refs{margin:10px 0 0;color:var(--muted)}.refs a{margin-right:12px;display:inline-block}.edge{color:#874b26}.empty{padding:40px 0;text-align:center;color:var(--muted)}footer{font-size:12px;color:var(--muted);margin-top:25px}footer details{margin-top:12px}footer summary{cursor:pointer;width:fit-content}.station-list{display:grid;grid-template-columns:1fr 1fr;gap:10px 24px;margin:15px 0}footer p{max-width:85ch}.route-line{margin:10px 0}.route-line strong{display:block}button,summary{touch-action:manipulation}[hidden]{display:none!important}
@media(max-width:850px){.filters{grid-template-columns:repeat(2,minmax(0,1fr))}.filters input{grid-column:1/-1}.filters select:last-child{grid-column:1/-1}.bar{align-items:start}.actions{gap:10px}main{padding:24px 20px 40px}}
@media(max-width:520px){main{padding:20px 16px 35px}header{display:block}h1{font-size:21px}header p{margin-top:5px}.place{grid-template-columns:45px minmax(0,1fr) 24px;gap:10px;padding:16px 0}.score{font-size:24px}.heading h2{font-size:16px}.heading{gap:4px 10px}.reason{font-size:13px}.facts,.station-list{grid-template-columns:1fr}.bar{gap:8px;flex-wrap:wrap}.actions{gap:12px}.sights{line-height:1.8}}
@media print{main{padding:0}.filters,.bar,.star,.method{display:none}.place{break-inside:avoid}.score{font-size:22px}.detail{font-size:11px}footer{font-size:10px}body{background:#fff}}
</style></head><body><main><header><h1>北京周边逃逸行动</h1><p>约 1000 km · 景点独特性 / 10</p></header>
<div class="filters"><input id="q" type="search" aria-label="搜索城市、景点、美食" placeholder="城市、景点、美食"><select id="route" aria-label="线路"><option value="">全部线路</option></select><select id="station" aria-label="北京出发站"><option value="">全部出发站</option></select><select id="month" aria-label="建议出游月份"><option value="">全部月份</option></select><select id="sort" aria-label="排序"><option value="score">独特性从高到低</option><option value="route">按线路排列</option><option value="name">按城市名称</option></select></div>
<div class="bar"><span id="count" role="status" aria-live="polite" tabindex="-1"></span><div class="actions"><label><input id="saved" type="checkbox">收藏</label><button id="reset">重置</button><button id="print">打印</button></div></div>
<details class="method"><summary>评分标准</summary><p>主观评分：看景点稀缺性、原真性与地域辨识度。9—10：很难替代；7—8.5：特色鲜明；5—6.5：同类较多；低于 5：以通用休闲为主。评价范围为本条所列景点，含注明的远郊县域。</p></details>
<div class="results" id="results"></div>
<footer><p>铁路约千公里，边界另标。月份为季节建议；班次查 <a href="https://www.12306.cn/" target="_blank" rel="noopener">12306</a>。评分为编者判断，来源支持景点事实。更新：2026-11-18。</p><details><summary>线路与车站</summary><div id="route-guide"></div><div class="station-list" id="station-guide"></div></details></footer></main>
<script>
const DATA=__DATA__;
const $=s=>document.querySelector(s),esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let favorites=new Set(),favoritesStored=false;try{const stored=localStorage.getItem('rail-city-favs-v2');favoritesStored=stored!==null;favorites=new Set(JSON.parse(stored||'[]'))}catch(e){}
// 迁移上一版收藏到去重后的目的地。
try{if(!favoritesStored){const old=new Set(JSON.parse(localStorage.getItem('beijing-rail-favs')||'[]'));const rows=__OLDROWS__;DATA.entries.forEach(x=>{if(rows.some(r=>old.has(r.id)&&x.aliases.includes(r.city)))favorites.add(x.id)});localStorage.setItem('rail-city-favs-v2',JSON.stringify([...favorites]))}}catch(e){}
const labels={geo:'地理',history:'历史',culture:'人文',food:'吃什么',custom:'风俗'};
$('#route').innerHTML+=DATA.routes.map((r,i)=>'<option value="'+i+'">'+esc(r.name)+'</option>').join('');$('#station').innerHTML+=Object.keys(DATA.stationGuide).map(s=>'<option>'+esc(s)+'</option>').join('');$('#month').innerHTML+=Array.from({length:12},(_,i)=>'<option value="'+(i+1)+'">'+(i+1)+' 月</option>').join('');
$('#route-guide').innerHTML=DATA.routes.map(r=>'<div class="route-line"><strong>'+esc(r.name)+'</strong>'+esc(r.line)+'<br>'+esc(r.path.replaceAll('/',' → '))+'</div>').join('');$('#station-guide').innerHTML=Object.entries(DATA.stationGuide).map(([k,v])=>'<div><strong>'+esc(k)+'</strong><br>'+esc(v)+'</div>').join('');
function details(x){const c=DATA.climate[x.zone];return '<details class="detail"><summary>风土与交通</summary><dl class="facts">'+Object.entries(x.fields).filter(([k,v])=>v).map(([k,v])=>'<div><dt>'+labels[k]+'</dt><dd>'+esc(v)+'</dd></div>').join('')+'<div><dt>气候 · '+esc(c[0])+'</dt><dd>'+esc(c[1])+'</dd></div><div><dt>建议月份</dt><dd>'+x.months.join('、')+' 月</dd></div></dl><div class="transport"><p>下车：'+x.stops.map(esc).join(' / ')+'</p><p>出发：'+x.stations.map(esc).join(' / ')+'</p>'+(x.note?'<p>'+esc(x.note)+'</p>':'')+(x.edge?'<p class="edge">'+esc(x.edge)+'</p>':'')+'</div><details class="refs"><summary>来源</summary>'+x.refs.map(([t,u])=>'<a href="'+esc(u)+'" target="_blank" rel="noopener">'+esc(t)+'</a>').join('')+'<a href="'+esc(c[2])+'" target="_blank" rel="noopener">区域气候依据</a></details></details>'}
const star='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 2.8 5.7 6.3.9-4.5 4.4 1.1 6.2-5.7-3-5.7 3 1.1-6.2-4.5-4.4 6.3-.9Z"/></svg>';
function getResults(){const q=$('#q').value.trim().toLowerCase(),r=$('#route').value,s=$('#station').value,m=Number($('#month').value);let list=DATA.entries.filter(x=>(r===''||x.routes.includes(Number(r)))&&(!s||x.stations.includes(s))&&(!m||x.months.includes(m))&&(!$('#saved').checked||favorites.has(x.id))&&(!q||[x.name,x.sights,x.reason,...Object.values(x.fields)].join(' ').toLowerCase().includes(q)));const sort=$('#sort').value;list.sort((a,b)=>sort==='route'?(a.routes[0]-b.routes[0]||b.score-a.score):sort==='name'?a.name.localeCompare(b.name,'zh'):b.score-a.score||a.name.localeCompare(b.name,'zh'));return list}
function render(){const list=getResults();$('#count').textContent=list.length+' 个城市 / 地区';$('#results').innerHTML=list.map(x=>'<article class="place"><div class="score">'+x.score.toFixed(1)+'<small>/ 10</small></div><div><div class="heading"><h2>'+esc(x.name)+'</h2><span>'+x.routes.map(i=>esc(DATA.routes[i].name.split(' · ')[0])).join(' / ')+'</span></div><p class="reason">'+esc(x.reason)+'</p><p class="sights">'+esc(x.sights)+'</p>'+details(x)+'</div><button class="star" data-save="'+esc(x.id)+'" aria-pressed="'+favorites.has(x.id)+'" aria-label="'+(favorites.has(x.id)?'取消收藏':'收藏')+esc(x.name)+'">'+star+'</button></article>').join('')||'<div class="empty">没有匹配结果。<button id="empty-reset">重置筛选</button></div>'}
function reset(){['q','route','station','month'].forEach(id=>$('#'+id).value='');$('#saved').checked=false;$('#sort').value='score';render()}
['q','route','station','month','sort','saved'].forEach(id=>$('#'+id).addEventListener(id==='q'?'input':'change',render));$('#reset').onclick=reset;
$('#results').addEventListener('click',e=>{if(e.target.closest('#empty-reset'))return reset();const b=e.target.closest('[data-save]');if(!b)return;const id=b.dataset.save;favorites.has(id)?favorites.delete(id):favorites.add(id);try{localStorage.setItem('rail-city-favs-v2',JSON.stringify([...favorites]))}catch(e){}if($('#saved').checked){render();$('#count').focus({preventScroll:true})}else{b.setAttribute('aria-pressed',String(favorites.has(id)));b.setAttribute('aria-label',(favorites.has(id)?'取消收藏':'收藏')+id)}});
let printState=[];window.addEventListener('beforeprint',()=>{printState=[...document.querySelectorAll('.detail')].map(d=>[d,d.open]);printState.forEach(([d])=>d.open=true)});window.addEventListener('afterprint',()=>printState.forEach(([d,o])=>d.open=o));$('#print').onclick=()=>window.print();render();
</script></body></html>'''
old_rows=[{'id':f'{i}-{j}','city':row.split('|')[0]} for i,r in enumerate(base['routes']) for j,row in enumerate(r['rows'].split('\n'))]
html=HTML.replace('__DATA__',json.dumps(dataset,ensure_ascii=False,separators=(',',':'))).replace('__OLDROWS__',json.dumps(old_rows,ensure_ascii=False,separators=(',',':')))
(ROOT/'北京铁路旅行清单.html').write_text(html,encoding='utf-8')
(ROOT/'index.html').write_text(html,encoding='utf-8')
md=['# 城市景点独特性评分','', '主观评分，只衡量所列景点的稀缺性、原真性、地域辨识度。范围含该条明确列出的远郊县域。','', '| 城市 / 地区 | 分数 | 理由 |','|---|---:|---|']
for e in sorted(entries,key=lambda x:(-x['score'],x['name'])):md.append(f"| {e['name']} | {e['score']:.1f} | {e['reason']} |")
ranking_md=md.copy()
md+=['','## 风土','']
for e in sorted(entries,key=lambda x:(-x['score'],x['name'])):
    md+=['### '+e['name'],'',e['sights'],'']
    for key,label in [('geo','地理'),('history','历史'),('culture','人文'),('food','吃什么'),('custom','风俗')]:
        if e['fields'][key]:md.append(f"- {label}：{e['fields'][key]}")
    md.append('- 气候：'+raw['climate'][e['zone']][1])
    md+=['- 建议月份：'+'、'.join(str(m) for m in e['months'])+' 月','', '来源：'+'；'.join(f'[{t}]({u})' for t,u in e['refs'])+'。','']
(ROOT/'各地风土调研.md').write_text('\n'.join(md),encoding='utf-8')
(ROOT/'城市景点独特性评分.md').write_text('\n'.join(ranking_md),encoding='utf-8')
print(f'已精简并评分 {len(entries)} 个城市/地区。')
