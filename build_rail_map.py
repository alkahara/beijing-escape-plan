"""Local OSM rail geometry (ODbL). Run --download to refresh. No invented joins."""
import argparse
import json
import math
import gzip
import base64
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parent
QUERY = '''[out:json][timeout:180];(
way[railway=rail][!service](around:1000000,39.9042,116.4074);
node[railway=station][station!=subway][subway!=yes](around:1000000,39.9042,116.4074);
);out geom;'''

def distance(point):
    lon, lat = map(math.radians, point)
    a, b = map(math.radians, [116.4074, 39.9042])
    v = math.sin((lat-b)/2)**2 + math.cos(b)*math.cos(lat)*math.sin((lon-a)/2)**2
    return 12742 * math.asin(min(1, math.sqrt(v)))

def build():
    parser = argparse.ArgumentParser()
    parser.add_argument('--download', action='store_true')
    opt = parser.parse_args()
    source = ROOT / 'rail-osm-source.json'
    if opt.download:
        import requests
        # A planet-wide around query can exceed Overpass memory limits. Query indexed
        # bounding boxes first and apply the spherical radius filter locally below.
        parts = []
        session = requests.Session()
        session.trust_env = False
        session.headers['User-Agent'] = 'BeijingEscapePlan/1.0 (https://github.com/alkahara/beijing-escape-plan)'
        for box in [(31,104,40,116.5),(31,116.5,40,129),(40,104,49,116.5),(40,116.5,49,129)]:
            bounds = ','.join(map(str, box))
            query = f'[out:json][timeout:180];(way[railway=rail][!service]({bounds});node[railway=station][station!=subway][subway!=yes]({bounds}););out geom;'
            response = session.get('https://overpass-api.de/api/interpreter', params={'data': query}, timeout=210)
            response.raise_for_status()
            part = response.json()
            if part.get('remark'):
                raise RuntimeError(part['remark'])
            parts.append(part)
        elements = {(e['type'],e['id']):e for part in parts for e in part['elements']}
        raw = {'osm3s':parts[0]['osm3s'], 'elements':list(elements.values())}
        source.write_text(json.dumps(raw, ensure_ascii=False), encoding='utf-8')
    raw = json.loads(source.read_text(encoding='utf-8'))
    if raw.get('remark'):
        raise RuntimeError(raw['remark'])
    rails, stations = [], []
    for e in raw['elements']:
        tags = e.get('tags', {})
        name = tags.get('name:zh-Hans') or tags.get('name:zh') or tags.get('name', '')
        if e['type'] == 'way':
            points = [[round(p['lon'], 6), round(p['lat'], 6)] for p in e.get('geometry', []) if p]
            if len(points) < 2:
                continue
            if not any(distance(p) <= 1000 for p in points):
                continue
            try:
                speed = int(tags.get('maxspeed', '0'))
            except ValueError:
                speed = 0
            properties = {'name': name, 'ref': tags.get('ref', ''),
                'highspeed': tags.get('highspeed') == 'yes' or speed >= 200,
                'speed': speed, 'usage': tags.get('usage', ''),
                'structure': tags.get('bridge') == 'yes' and '桥梁' or tags.get('tunnel') == 'yes' and '隧道' or ''}
            rails.append({'type': 'Feature', 'id': e['id'], 'properties': properties,
                'geometry': {'type': 'LineString', 'coordinates': points}})
        elif e['type'] == 'node' and name and tags.get('train') != 'no' and tags.get('station') not in ('subway', 'light_rail') and tags.get('passenger') != 'no':
            point = [e['lon'], e['lat']]
            if distance(point) > 1000:
                continue
            stations.append({'id': str(e['id']), 'name': name, 'coords': point, 'distance': round(distance(point))})
    stations.sort(key=lambda s: (s['distance'], s['name']))
    meta = {'source': 'OpenStreetMap', 'license': 'ODbL 1.0',
        'osmDate': raw.get('osm3s', {}).get('timestamp_osm_base', ''),
        'built': datetime.now(timezone.utc).isoformat(), 'center': [116.4074, 39.9042],
        'radiusKm': 1000, 'query': QUERY, 'wayCount': len(rails),
        'stationCount': len(stations), 'vertices': sum(len(f['geometry']['coordinates']) for f in rails)}
    data = {'meta': meta, 'rails': {'type': 'FeatureCollection', 'features': rails}, 'stations': stations}
    if not rails or not stations:
        raise RuntimeError('Incomplete snapshot: expected rail geometry and stations')
    assets = ROOT / 'assets'
    assets.mkdir(exist_ok=True)
    packed = base64.b64encode(gzip.compress(json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), mtime=0)).decode('ascii')
    (assets / 'rail-data.js').write_text('window.RAIL_DATA_PACKED="' + packed + '";', encoding='utf-8')
    style = json.loads((ROOT / 'rail-basemap-style.json').read_text(encoding='utf-8'))
    style['layers'] = [l for l in style['layers'] if not l['id'].startswith('railway')]
    for layer in style['layers']:
        if layer['type'] == 'symbol' and 'text-field' in layer.get('layout', {}):
            layer['layout']['text-field'] = ['coalesce', ['get', 'name:zh-Hans'], ['get', 'name:zh'], ['get', 'name']]
    (assets / 'rail-basemap.js').write_text('window.RAIL_BASEMAP=' + json.dumps(style, ensure_ascii=False, separators=(',', ':')) + ';', encoding='utf-8')
    (assets / 'rail-data-metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(meta, ensure_ascii=True))

if __name__ == '__main__':
    build()
