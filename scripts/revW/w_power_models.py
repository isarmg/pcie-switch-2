"""Repair Rev W regulator ERC models from manufacturer pin tables.

No nets, NC markers, geometry, UUIDs, or ERC exclusions are changed. Run after
schematic generation. The original layout pipeline still requires KiCad 10 and
its historical work inputs; this repair itself uses only the Python stdlib.
"""
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / 'outputs/PCIe_E1S_96x45_USB12mm_RevW/Main_12E1S'


def models():
    a = {}
    def add(pins, name, kind):
        for pin in pins:
            a[str(pin)] = (name, kind)
    add([1, 2, 3], 'NU', 'no_connect')
    add([4], 'EN_UVLO', 'input')
    add([5], 'BOOT', 'passive')  # Floating gate-driver supply, not a DC rail.
    add(range(6, 13), 'SW', 'power_out')
    add(range(13, 21), 'PGND', 'power_in')
    add(range(21, 27), 'PVIN', 'power_in')
    add([27], 'NC', 'no_connect')
    add([28], 'VDD', 'power_in')
    add([29], 'DRGND', 'power_in')
    add([30], 'AGND', 'power_in')
    add([31], 'BP', 'power_out')
    for pin, name in [(32, 'FSEL'), (33, 'VSEL'), (34, 'MODE'), (36, 'ILIM'),
                      (38, 'RSN'), (39, 'RSP'), (40, 'VOSNS')]:
        add([pin], name, 'input')
    add([35], 'PGOOD', 'open_collector')
    add([37], 'RESV_TRK', 'no_connect')
    add([41], 'THERMAL_PAD_PGND', 'power_in')
    b = {str(pin): (name, kind) for pin, name, kind in [
        (1, 'VIN1', 'power_in'), (2, 'RBOOT', 'passive'),
        (3, 'CBOOT', 'passive'), (4, 'SW', 'output'),
        (5, 'VLDOIN', 'power_in'), (6, 'VCC', 'power_out'),
        (7, 'AGND', 'power_in'), (8, 'FB', 'input'),
        (9, 'VOUT1', 'power_out'), (10, 'VOUT2', 'power_out'),
        (11, 'AGND', 'power_in'), (12, 'RT', 'input'),
        (13, 'PG', 'open_collector'), (14, 'SPSP', 'input'),
        (15, 'SYNC_MODE', 'input'), (16, 'NC', 'no_connect'),
        (17, 'EN', 'input'), (18, 'VIN2', 'power_in'),
        (19, 'PGND', 'power_in'), (20, 'PGND', 'power_in'),
        (21, 'AGND', 'power_in'), (22, 'AGND', 'power_in')]}
    # Paralleled terminals of a single device must not create false output
    # conflicts. One terminal carries the driver type; peers remain passive.
    for pin in range(7, 13):
        a[str(pin)] = ('SW', 'passive')
    b['10'] = ('VOUT2', 'passive')
    c = {'1': ('RESET', 'open_collector'), '2': ('GND', 'power_in'),
         '3': ('MR', 'input'), '4': ('CT', 'passive'),
         '5': ('SENSE', 'input'), '6': ('VDD', 'power_in')}
    d={'1':('VCCA','power_in'),'2':('GND','power_in'),'3':('A','input'),
       '4':('B','output'),'5':('DIR','input'),'6':('VCCB','power_in')}
    e={**d,'3':('A','output'),'4':('B','input')}
    return {'U901': a, 'U902': b, 'U605': c, 'U511': d, 'U512': e}


def update_metadata(folder=DESIGN):
    path = folder / 'COMPONENTS.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    by_ref = {c['ref']: c for c in data}
    for ref, pins in models().items():
        c = by_ref[ref]
        assert set(c['pinmap']) == set(pins), (ref, 'unexpected pin map')
        if ref in ['U511','U512']:
            assert c['pinmap']['5']==('/CPU_VCCPRIM_1P8' if ref=='U511' else '/GND'), 'Recheck translator direction before applying this configured model'
            c['datasheet']='https://www.ti.com/lit/ds/symlink/sn74axc1t45.pdf'
        c['pin_names'] = {p: n for p, (n, _) in pins.items()}
        c['pin_types'] = {p: t for p, (_, t) in pins.items()}
        c['erc_model_source'] = c.get('datasheet', '')
        c['erc_model_note'] = ('Manufacturer pin functions; analog bootstrap terminals are passive. '
                               'Paralleled output terminals have one power_out driver. '
                               'ERC does not validate startup, power sequencing or current capacity.')
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def patch_symbols(text):
    current = None
    found = set()
    lines = []
    for line in text.splitlines(keepends=True):
        match = re.search(r'\(symbol "(?:Local:)?PART_(U\d+)(?:_\d+_\d+)?"', line)
        if match:
            current = match.group(1)
        if current in models() and line.startswith('(pin '):
            pin = re.search(r'\(number "([^"]+)"', line).group(1)
            name, kind = models()[current][pin]
            line = re.sub(r'^\(pin \S+ line', f'(pin {kind} line', line)
            line = re.sub(r'\(name "[^"]*"', f'(name "{name}"', line, count=1)
            found.add((current, pin))
        lines.append(line)
    return ''.join(lines), found


def apply(folder=DESIGN):
    update_metadata(folder)
    changed = []
    found = set()
    for path in [folder/'Local.kicad_sym', *folder.glob('*.kicad_sch')]:
        # Preserve CRLF as well as all UUIDs and net labels.
        raw = path.read_bytes().decode('utf-8')
        new, pins = patch_symbols(raw)
        found |= pins
        if new != raw:
            path.write_bytes(new.encode('utf-8'))
            changed.append(path.name)
    expected = {(r, p) for r, pins in models().items() for p in pins}
    assert found == expected, (expected-found, found-expected)
    return changed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--design', type=Path, default=DESIGN)
    args = parser.parse_args()
    print(json.dumps({'updated_files': apply(args.design), 'nets_changed': False}, indent=2))
