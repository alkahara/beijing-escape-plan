/* Railway geometry: OpenStreetMap (ODbL). Travel times: user records only. */
(async () => {
  'use strict';
  const $ = id => document.getElementById(id);
  const tell = (message, error = false) => { $('status').textContent = message; $('status').classList.toggle('error', error); };
  if (!window.RAIL_DATA_PACKED || !window.maplibregl) {
    tell('地图文件不完整，请重新下载 assets 文件夹。', true); return;
  }
  let DATA;
  try {
    const bytes = Uint8Array.from(atob(window.RAIL_DATA_PACKED), c => c.charCodeAt(0));
    const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
    DATA = JSON.parse(await new Response(stream).text());
    delete window.RAIL_DATA_PACKED;
  } catch (_) { tell('轨道数据解压失败，请使用新版 Edge / Chrome / Firefox。', true); return; }
  const stations = DATA.stations;
  const byId = new Map(stations.map(s => [s.id, s]));
  const key = 'beijing-escape-rail-times-v1';
  const origins = ['北京', '北京南', '北京西', '北京北', '北京朝阳', '北京丰台', '清河', '北京通州', '北京大兴', '大兴机场'];
  let records = [], selected = null, ready = false, map, selectedMarker;
  let timeMarkers = [];
  const option = (value, text = value) => { const el = document.createElement('option'); el.value = value; el.textContent = text; return el; };
  const stationLabel = s => `${s.name} · ${s.distance} km · ${s.id}`;
  const normalize = name => name.trim().replace(/站$/, '');
  const formatTime = n => n < 60 ? `${n} 分` : `${Math.floor(n / 60)} 时${n % 60 ? ` ${n % 60} 分` : ''}`;
  const validRecord = r => r && typeof r.id === 'string' && r.id.length <= 100 && byId.has(r.stationId) && origins.includes(r.origin) && Number.isInteger(r.minutes) && r.minutes > 0 && r.minutes <= 10080 && ['train','date','note'].every(k => typeof r[k] === 'string' && r[k].length <= 200) && (!r.date || /^\d{4}-\d{2}-\d{2}$/.test(r.date));
  try {
    const saved = JSON.parse(localStorage.getItem(key) || '[]');
    if (!Array.isArray(saved) || !saved.every(validRecord)) throw Error('invalid');
    records = saved;
  } catch (_) { tell('本地记录无法读取；可导入备份恢复。', true); }
  stations.forEach(s => $('station-options').append(option(stationLabel(s))));
  origins.forEach(name => { $('origin').append(option(name)); $('time-origin').append(option(name)); });
  $('data-meta').textContent = `OSM 快照 ${DATA.meta.osmDate.slice(0,10)} · ${DATA.meta.wayCount.toLocaleString()} 段轨道 · ${DATA.meta.stationCount.toLocaleString()} 个站点。轨道未做手工简化；数据可能缺漏。`;

  function save(next) {
    try { localStorage.setItem(key, JSON.stringify(next)); records = next; return true; }
    catch (_) { tell('浏览器未能保存记录，请导出备份后重试。', true); return false; }
  }
  function currentRecords() { return records.filter(r => !$('time-origin').value || r.origin === $('time-origin').value); }
  function feature(s, properties = {}) { return { type: 'Feature', geometry: { type: 'Point', coordinates: s.coords }, properties: { id: s.id, name: s.name, ...properties } }; }
  function collection(features) { return { type: 'FeatureCollection', features }; }
  function renderRecords() {
    const visible = currentRecords().slice().sort((a,b) => a.minutes-b.minutes);
    $('record-count').textContent = String(visible.length);
    $('empty-records').hidden = visible.length > 0;
    $('empty-records').textContent = records.length ? '此出发站没有记录。' : '点击车站记录时长，保存后直接显示在地图上。';
    $('record-list').replaceChildren();
    visible.forEach(r => {
      const s = byId.get(r.stationId), row = document.createElement('div'), button = document.createElement('button');
      row.className = 'record'; button.type = 'button';
      const body = document.createElement('span'), name = document.createElement('span'), meta = document.createElement('span'), time = document.createElement('span');
      body.className = 'record-body'; name.className = 'record-name'; meta.className = 'record-meta'; time.className = 'record-time';
      name.textContent = `${r.origin} → ${s.name}`;
      meta.textContent = [r.train, r.date, r.note].filter(Boolean).join(' · ') || '未填车次、日期';
      time.textContent = formatTime(r.minutes); body.append(name,meta); button.append(body,time); row.append(button);
      button.addEventListener('click', () => selectStation(s, r)); $('record-list').append(row);
    });
    if (ready) {
      const fastest = new Map();
      visible.forEach(r => { if (!fastest.has(r.stationId)) fastest.set(r.stationId,r); });
      map.getSource('times').setData(collection([...fastest.values()].map(r => feature(byId.get(r.stationId), { label: `${byId.get(r.stationId).name} ${formatTime(r.minutes)}`, minutes:r.minutes }))));
      timeMarkers.forEach(marker => marker.remove());
      timeMarkers = [...fastest.values()].map(r => {
        const station = byId.get(r.stationId), button = document.createElement('button');
        button.type = 'button'; button.className = 'map-time';
        button.textContent = `${station.name} ${formatTime(r.minutes)}`;
        button.title = `${r.origin} → ${station.name} · ${r.train || '未填车次'} · ${r.date || '未填日期'}`;
        button.addEventListener('click', () => selectStation(station, r));
        return new maplibregl.Marker({element:button,anchor:'bottom',offset:[0,-8]}).setLngLat(station.coords).addTo(map);
      });
    }
  }
  function resetRecord() {
    $('time-form').reset(); $('record-id').value = '';
    $('origin').value = $('time-origin').value || '北京南';
    $('new-record').hidden = true; $('delete-record').hidden = true;
  }
  function selectStation(s, record) {
    selected = s; resetRecord();
    $('editor').hidden = false; $('station-title').textContent = s.name;
    $('station-note').textContent = `距北京中心直线约 ${s.distance} km · 车站是否办客请查 12306`;
    if (record) {
      $('record-id').value = record.id; $('origin').value = record.origin; $('duration').value = record.minutes;
      $('train').value = record.train; $('travel-date').value = record.date; $('note').value = record.note;
      $('new-record').hidden = false; $('delete-record').hidden = false;
    }
    document.body.classList.remove('panel-hidden'); updatePanel();
    if (map) {
      const mobile = window.innerWidth <= 700;
      map.easeTo({ center: s.coords, zoom: Math.max(map.getZoom(), 10), padding: mobile ? {bottom:Math.min(innerHeight*.45,360),top:20,left:20,right:20} : {left:340,right:30,top:30,bottom:30}, duration: matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 450 });
      if (selectedMarker) selectedMarker.remove();
      selectedMarker = new maplibregl.Marker({color:'#995024'}).setLngLat(s.coords).addTo(map);
    }
    $('editor').scrollIntoView({block:'nearest'});
  }
  function updatePanel() {
    const hidden = document.body.classList.contains('panel-hidden');
    $('panel-toggle').setAttribute('aria-expanded', String(!hidden));
    $('panel-toggle').textContent = hidden ? '车站与时长' : '收起面板';
  }
  $('panel-toggle').addEventListener('click', () => { document.body.classList.toggle('panel-hidden'); updatePanel(); });
  $('close-editor').addEventListener('click', () => { $('editor').hidden = true; selected = null; selectedMarker?.remove(); $('station-search').focus(); });
  $('search-form').addEventListener('submit', e => {
    e.preventDefault();
    const q = $('station-search').value.trim();
    const s = stations.find(s => stationLabel(s) === q) || stations.find(s => normalize(s.name) === normalize(q));
    if (!s) { tell('未找到车站，请从搜索建议中选择完整站名。', true); return; }
    selectStation(s); tell(`已定位 ${s.name}`);
  });
  $('time-form').addEventListener('submit', e => {
    e.preventDefault(); if (!selected) return;
    const id = $('record-id').value || (globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(36).slice(2)}`);
    const r = { id, stationId:selected.id, origin:$('origin').value, minutes:Number($('duration').value), train:$('train').value.trim(), date:$('travel-date').value, note:$('note').value.trim() };
    if (!validRecord(r)) { tell('请检查车站和时长（1—10080 分钟）。', true); return; }
    const next = records.filter(item => item.id !== id).concat(r);
    if (save(next)) { $('record-id').value=id; $('new-record').hidden=false; $('delete-record').hidden=false; renderRecords(); tell(`已保存 ${selected.name} · ${formatTime(r.minutes)}`); }
  });
  $('new-record').addEventListener('click', () => { resetRecord(); $('duration').focus(); });
  $('delete-record').addEventListener('click', () => {
    const id = $('record-id').value;
    if (save(records.filter(r => r.id !== id))) { resetRecord(); renderRecords(); tell('已删除此条记录。'); }
  });
  $('time-origin').addEventListener('change', renderRecords);
  $('export').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify({version:1,records},null,2)], {type:'application/json'});
    const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = '北京铁路时长.json'; link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  });
  $('import').addEventListener('click', () => $('import-file').click());
  $('import-file').addEventListener('change', async e => {
    try {
      const file = e.target.files[0]; if (!file) return;
      if (file.size > 5000000) throw Error('文件过大');
      const data = JSON.parse(await file.text());
      if (data.version !== 1 || !Array.isArray(data.records) || !data.records.every(validRecord)) throw Error('记录格式或站点不匹配');
      const merged = new Map(records.map(r => [r.id,r]));
      // Reimporting a backup never overwrites edits already stored in this browser.
      data.records.forEach(r => { if (!merged.has(r.id)) merged.set(r.id,r); });
      if (save([...merged.values()])) { renderRecords(); tell(`已合并导入 ${data.records.length} 条记录。`); }
    } catch (err) { tell(`导入失败：${err.message}`, true); }
    e.target.value='';
  });
  renderRecords();

  // A local style starts immediately, even if online basemap requests fail.
  const base = window.RAIL_BASEMAP;
  const initial = {version:8, glyphs:base?.glyphs, sources:{}, layers:[{id:'paper',type:'background',paint:{'background-color':'#f0f0e8'}}]};
  try {
    map = new maplibregl.Map({container:'map',style:initial,center:[116.5,39.5],zoom:6.2,minZoom:4,maxZoom:18,attributionControl:false});
  } catch (_) { tell('浏览器无法启动 WebGL 地图，请启用硬件加速或换用 Edge / Chrome。',true); return; }
  map.addControl(new maplibregl.NavigationControl(),'top-right');
  map.addControl(new maplibregl.ScaleControl({maxWidth:100,unit:'metric'}),'bottom-left');
  map.addControl(new maplibregl.AttributionControl({compact:true,customAttribution:'<a href="https://www.openstreetmap.org/copyright">© OpenStreetMap contributors</a> · <a href="https://openfreemap.org/">OpenFreeMap</a>'}),'bottom-right');
  const stationGeo = collection(stations.map(s => feature(s)));
  const color = ['case',['==',['get','highspeed'],true],'#995024','#245c49'];
  function addLayers() {
    map.addSource('rails',{type:'geojson',data:DATA.rails,tolerance:0,maxzoom:16});
    map.addSource('stations',{type:'geojson',data:stationGeo});
    map.addSource('times',{type:'geojson',data:collection([])});
    const coords=[];
    for(let i=0;i<=180;i++) {
      const bearing=i*Math.PI/90, angular=1000/6371, lat=39.9042*Math.PI/180, lon=116.4074*Math.PI/180;
      const p=Math.asin(Math.sin(lat)*Math.cos(angular)+Math.cos(lat)*Math.sin(angular)*Math.cos(bearing));
      const l=lon+Math.atan2(Math.sin(bearing)*Math.sin(angular)*Math.cos(lat),Math.cos(angular)-Math.sin(lat)*Math.sin(p));
      coords.push([l*180/Math.PI,p*180/Math.PI]);
    }
    map.addSource('radius',{type:'geojson',data:{type:'Feature',properties:{},geometry:{type:'LineString',coordinates:coords}}});
    map.addLayer({id:'radius',type:'line',source:'radius',paint:{'line-color':'#788176','line-width':1,'line-dasharray':[4,4]}});
    map.addLayer({id:'rail-casing',type:'line',source:'rails',layout:{'line-join':'round','line-cap':'round'},paint:{'line-color':'#fffdf7','line-width':['interpolate',['linear'],['zoom'],4,1.8,8,3.3,14,5]}});
    map.addLayer({id:'rail-lines',type:'line',source:'rails',layout:{'line-join':'round','line-cap':'round'},paint:{'line-color':color,'line-width':['interpolate',['linear'],['zoom'],4,.8,8,1.6,14,3]}});
    map.addLayer({id:'rail-hit',type:'line',source:'rails',paint:{'line-color':'#000','line-opacity':0,'line-width':12}});
    map.addLayer({id:'station-dots',type:'circle',source:'stations',minzoom:6.5,paint:{'circle-color':'#fffdf7','circle-radius':['interpolate',['linear'],['zoom'],6,1.5,11,3,16,4],'circle-stroke-width':1,'circle-stroke-color':'#245c49'}});
    map.addLayer({id:'station-names',type:'symbol',source:'stations',minzoom:8,layout:{'text-field':['get','name'],'text-font':['Noto Sans Regular'],'text-size':12,'text-anchor':'top','text-offset':[0,.6]},paint:{'text-color':'#22352f','text-halo-color':'#fffdf7','text-halo-width':2}});
    map.addLayer({id:'time-dots',type:'circle',source:'times',paint:{'circle-radius':5,'circle-color':'#995024','circle-stroke-width':2,'circle-stroke-color':'#fffdf7'}});
    ready=true; $('rail-kind').disabled=false; renderRecords();
    tell(`${DATA.meta.wayCount.toLocaleString()} 段真实轨道 · 点击车站记录时长`);
  }
  map.on('load', () => {
    // Insert base layers below our local railway data. Never wait for external tiles to draw tracks.
    if (base) {
      for (const [id,source] of Object.entries(base.sources)) map.addSource(id,source);
      for (const layer of base.layers) map.addLayer(layer);
    }
    addLayers();
    ['station-dots','station-names','time-dots'].forEach(layer => {
      map.on('click',layer,e => { const s=byId.get(e.features[0].properties.id); if(s) selectStation(s); });
      map.on('mouseenter',layer,() => map.getCanvas().style.cursor='pointer');
      map.on('mouseleave',layer,() => map.getCanvas().style.cursor='');
    });
    map.on('click','rail-hit',e => {
      if (map.queryRenderedFeatures(e.point,{layers:['station-dots','station-names','time-dots']}).length) return;
      const f=e.features[0],p=f.properties, box=document.createElement('div'), title=document.createElement('h3'),desc=document.createElement('p'),link=document.createElement('a');
      title.textContent=p.name || '未命名铁路';
      desc.textContent=[p.highspeed?'高速铁路':'其他铁路',p.structure,p.speed?`OSM 标注限速 ${p.speed} km/h`:'',p.ref?`线路编号 ${p.ref}`:''].filter(Boolean).join(' · ');
      link.textContent='查看 OSM 原始轨道';link.href=`https://www.openstreetmap.org/way/${f.id}`;link.target='_blank';link.rel='noopener';box.append(title,desc,link);
      new maplibregl.Popup().setLngLat(e.lngLat).setDOMContent(box).addTo(map);
    });
  });
  $('rail-kind').addEventListener('change', () => {
    if (!ready) return;
    const mode=$('rail-kind').value,filter=mode==='all'?null:['==',['get','highspeed'],mode==='fast'];
    ['rail-lines','rail-casing','rail-hit'].forEach(id => map.setFilter(id,filter));
  });
  $('overview').addEventListener('click', () => map.fitBounds([[104,30.8],[128.5,49]],{padding:innerWidth<=700?{top:50,bottom:innerHeight*.45,left:20,right:20}:{top:40,bottom:40,left:340,right:40},duration:0}));
  let baseError=false;
  map.on('error', e => {
    console.warn('Map resource:',e.error?.message || e.error);
    if (!baseError) { baseError=true; tell('部分底图未加载；本地铁路与站点仍可用。',true); }
  });
})();
