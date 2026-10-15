#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trích xuất từ vựng từ "Thaolejp_BJT_Chinh phuc tu vung (kem dich nghia).pdf"
(45 bài, ~2200 từ) → vocab_thaole.js  (var THAOLE_VOCAB = [...])

Chạy:  python3 extract_thaole_vocab.py
Yêu cầu: poppler `pdftotext` (brew install poppler)
Sửa tay: thêm vào OVERRIDES[(lesson, pdfNo)] = {field: value}
"""
import json, re, subprocess, sys, os, datetime
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, "Thaolejp_BJT_Chinh phuc tu vung (kem dich nghia).pdf")
OUT = os.path.join(HERE, "vocab_thaole.js")
PDFTOTEXT = "/opt/homebrew/bin/pdftotext" if os.path.exists("/opt/homebrew/bin/pdftotext") else "pdftotext"

# ---- sửa tay (key: (lesson, pdfNo)) ---------------------------------------
OVERRIDES = {
    (6, 291):  {'word': '括弧', 'en': 'parentheses, brackets', 'meaning': 'Dấu ngoặc'},
    (11, 537): {'meaning': 'Trường hợp, tình huống; vỏ/hộp đựng'},
    (12, 574): {'meaning': 'Kiểm tra, kiểm định, thanh tra'},
    (14, 666): {'meaning': 'Bán lẻ'},
    (17, 811): {'meaning': 'CC (gửi bản sao email cho người khác cùng xem)'},
    (22, 1055): {'meaning': 'Khuyến khích, khích lệ'},
    (10, 480): {'word': '～口', 'tag': 'quán ngữ'},
    (33, 1638): {'word': '拝見', 'tag': 'kính ngữ'},
    (30, 1464): {'meaning': 'Video, hình ảnh động'},
}

# ---- regex / helpers --------------------------------------------------------
RE_LESSON  = re.compile(r'^\s*BÀI\s+(\d+)\s*$')
RE_HEADER  = re.compile(r'^\s*(\d{1,4})．(.*)$')
RE_ARROW   = re.compile(r'^\s*→\s*(.*)$')
RE_EXAMPLE = re.compile(r'^\s*・\s*(.*)$')
RE_NOTE    = re.compile(r'^\s*❖\s*(.*)$')
RE_SURU    = re.compile(r'^\s*～する\s*$')
RE_SKIP    = [
    re.compile(r'^\s*$'),
    re.compile(r'^\s*Thaolejp_BJT_Chinh'),
    re.compile(r'^\s*\d{1,3}\s*$'),
    re.compile(r'^\s*Link làm bài'),
    re.compile(r'^\s*MỤC LỤC'),
    re.compile(r'^\s*BÀI \d+\s*·'),
    re.compile(r'^\s*○\s*$'),
    re.compile(r'^[\u3040-\u309f\s]{1,14}$'),   # furigana lạc dòng (không có 。、)
]
RE_SANKO   = re.compile(r'^\s*参\s*(.*)$')
RE_POS     = re.compile(r'～(?:する|な|に|の|と|的)')
VI_CHARS = set("ăâđêôơưàảãáạầấậắằặẩẫèéẻẽẹếềểễệìíỉĩịòóỏõọốồổỗộớờởỡợùúủũụứừửữựỳýỵỷỹ"
               "ĂÂĐÊÔƠƯÀẢÃÁẠẦẤẬẮẰẶẨẪÈÉẺẼẸẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌỐỒỔỖỘỚỜỞỠỢÙÚỦŨỤỨỪỬỮỰỲÝỴỶỸ")
# từ tiếng Việt không dấu hay gặp ở đầu nghĩa inline
VI_PLAIN = {"an","ninh","kinh","chi","phi","sai","nam","ban","con","dong","lam","trong","cho","toan","ty"}
RE_JA = re.compile(r'[぀-ヿ一-鿿]')
RE_HIRA = re.compile(r'[぀-ゟ]')

def is_vi(s): return any(c in VI_CHARS for c in s)
def is_ja(s): return bool(RE_JA.search(s))
def skip(s):  return any(r.match(s) for r in RE_SKIP)

def make_short(m, limit=40):
    s = m.strip()
    for sep in (':', ' ('):
        i = s.find(sep)
        if i > 0: s = s[:i]
    s = s.strip(' .;,-–')
    if len(s) > limit:
        cut = -1
        for sep in (',', '/', ';'):
            i = s.find(sep)
            if i >= 5 and (cut == -1 or i < cut): cut = i
        if cut != -1: s = s[:cut].strip(' .;,-–')
        if len(s) > limit: s = s[:limit - 2].rstrip() + '…'
    return s

RE_ALT = re.compile(r'（([^）]*)）')

def split_inline_vi(rest):
    """rest = phần sau 「reading」. Trả về (en, vi_inline)."""
    toks = rest.split()
    k = next((i for i, t in enumerate(toks) if is_vi(t)), None)
    if k is None:
        return rest.strip(' ,;'), ''
    while k > 0 and (toks[k-1].lower() in VI_PLAIN or (toks[k-1][:1].isupper() and toks[k-1][1:].islower() and len(toks[k-1]) > 1)):
        k -= 1
    en = ' '.join(toks[:k]).strip(' ,;')
    vi = ' '.join(t for t in toks[k:] if not re.fullmatch(r'[\u3040-\u309f]+', t)).strip()
    return en, vi

def parse_header(text, e):
    t = text
    if '→' in t:                       # nghĩa dính ngay trên dòng header
        t, after = t.split('→', 1)
        e['meanings'].insert(0, after.strip())
    pos = RE_POS.findall(t)
    if '～する' in pos: e['suru'] = True
    e['pos'] = '、'.join(dict.fromkeys(p for p in pos if p != '～する'))
    t = RE_POS.sub(' ', t).replace('○', ' ').replace('、', ' ')
    t = re.sub(r'\s+', ' ', t).strip()
    reading = ''
    if '「' in t:
        left, _, rest = t.partition('「')
        reading, _, rest = rest.partition('」')
    else:
        m = re.match(r'^(\S+?（[^）]*）|\S+)\s*(.*)$', t, re.S)
        left, rest = (m.group(1), m.group(2)) if m else (t, '')
    alt = ''
    m = RE_ALT.search(left)
    if m:
        alt = m.group(1).strip(); left = RE_ALT.sub('', left)
    word = re.sub(r'\s+', '', left.strip())
    # marker cuối từ trong sách: 慣 quán ngữ, 敬 kính ngữ, 接 tiếp vĩ ngữ, 略 viết tắt, パ thuật ngữ máy tính
    tag = ''
    if word.endswith(('慣', '敬')) and RE_HIRA.search(word[:-1]): tag, word = word[-1], word[:-1]
    elif word.endswith('接') and '～' in word: tag, word = '接', word[:-1]
    elif word.endswith('略') and alt: tag, word = '略', word[:-1]
    elif word.endswith('パ') and len(word) >= 3: tag, word = 'パ', word[:-1]
    e['tag'] = {'慣': 'quán ngữ', '敬': 'kính ngữ', '接': 'tiếp vĩ ngữ', '略': 'viết tắt', 'パ': 'thuật ngữ PC'}.get(tag, '')
    e['word'] = word; e['alt'] = alt; e['reading'] = reading.strip()
    en, vi = split_inline_vi(rest.strip())
    e['en'] = en
    if vi: e['inline_vi'] = vi

def new_entry(pdf_no, lesson, n, head):
    return {'pdfNo': pdf_no, 'lesson': lesson, 'n': n, 'head': head,
            'meanings': [], 'examples': [], 'notes': [], 'suru': False}

def main():
    txt = subprocess.run([PDFTOTEXT, PDF, '-'], capture_output=True, text=True, check=True).stdout
    lines = [l.rstrip() for l in txt.split('\n')]

    entries, cur, state, lesson, n = [], None, None, 0, 0
    started = False
    for raw in lines:
        if skip(raw): continue
        m = RE_LESSON.match(raw)
        if m:
            lesson = int(m.group(1)); n = 0; started = True; state = None; cur = None
            continue
        if not started: continue
        s = raw.strip()
        m = RE_HEADER.match(s)
        if m:
            n += 1
            cur = new_entry(int(m.group(1)), lesson, n, m.group(2).strip())
            entries.append(cur); state = 'HEADER'; continue
        if cur is None: continue
        if RE_SURU.match(s): cur['suru'] = True; continue
        m = RE_ARROW.match(s)
        if m: cur['meanings'].append(m.group(1).strip()); state = 'MEANING'; continue
        m = RE_EXAMPLE.match(s)
        if m:
            body = m.group(1).strip()
            if is_vi(body) and not is_ja(body) and not cur['meanings']:
                cur['meanings'].append(body); state = 'MEANING'
            else:
                cur['examples'].append({'ja': body, 'vi': ''}); state = 'EX_JA'
            continue
        m = RE_NOTE.match(s) or RE_SANKO.match(s)
        if m: cur['notes'].append(m.group(1).strip()); state = 'NOTE'; continue
        # dòng thường
        if state == 'HEADER':
            cur['head'] += ' ' + s
        elif state == 'MEANING':
            if is_ja(s) and not is_vi(s) and len(s) > 6:      # ví dụ thiếu dấu ・
                cur['examples'].append({'ja': s, 'vi': ''}); state = 'EX_JA'
            elif cur['meanings']: cur['meanings'][-1] += ' ' + s
        elif state in ('EX_JA', 'EX_VI'):
            ex = cur['examples'][-1]
            if state == 'EX_JA' and is_ja(s) and not is_vi(s):
                ex['ja'] += s
            else:
                ex['vi'] = (ex['vi'] + ' ' + s).strip(); state = 'EX_VI'
        elif state == 'NOTE':
            if cur['notes'] and cur['notes'][-1] == '': cur['notes'][-1] = s
            else: cur['notes'][-1] += ' ' + s

    # ---- hậu xử lý ---------------------------------------------------------
    out, report = [], {'no_meaning': [], 'no_reading': [], 'inline_vi': [], 'residue': [], 'truncated': []}
    for i, e in enumerate(entries, 1):
        parse_header(e['head'], e)
        meanings = list(e['meanings'])
        if e.get('inline_vi'):
            meanings.insert(0, e['inline_vi'])
            report['inline_vi'].append((e['lesson'], e['pdfNo'], e['head']))
        rec = {
            'id': i, 'n': e['n'], 'lesson': e['lesson'], 'pdfNo': e['pdfNo'],
            'word': e.get('word', ''), 'alt': e.get('alt', ''), 'reading': e.get('reading', ''),
            'en': e.get('en', ''), 'meaning': '; '.join(m.strip() for m in meanings if m.strip()),
            'short': '', 'suru': e['suru'], 'pos': e.get('pos', ''), 'tag': e.get('tag', ''),
            'examples': [x for x in e['examples'] if x['ja']],
            'note': ' | '.join(x for x in e['notes'] if x),
        }
        ov = OVERRIDES.get((rec['lesson'], rec['pdfNo']))
        if ov: rec.update(ov)
        if not rec['short']:
            rec['short'] = make_short(meanings[0]) if meanings else ''
        if ov and 'meaning' in ov and 'short' not in ov:
            rec['short'] = make_short(rec['meaning'].split(';')[0])
        out.append(rec)
        # báo cáo
        if not rec['meaning']: report['no_meaning'].append((rec['lesson'], rec['pdfNo'], e['head']))
        if re.search(r'[一-鿿]', rec['word']) and not rec['reading']:
            report['no_reading'].append((rec['lesson'], rec['pdfNo'], e['head']))
        blob = json.dumps(rec, ensure_ascii=False)
        if re.search(r'Thaolejp|forms\.gle|❖|○|→', blob) or rec['word'].endswith(('慣', 'パ')):
            report['residue'].append((rec['lesson'], rec['pdfNo'], rec['word'], blob[:120]))
        if rec['short'].endswith('…'): report['truncated'].append((rec['lesson'], rec['pdfNo'], rec['word'], rec['short']))

    meta = {'count': len(out), 'lessons': max(r['lesson'] for r in out),
            'generated': datetime.date.today().isoformat(),
            'source': os.path.basename(PDF)}
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('// Sinh tự động bởi extract_thaole_vocab.py — KHÔNG sửa tay, dùng OVERRIDES trong script.\n')
        f.write('var THAOLE_META = ' + json.dumps(meta, ensure_ascii=False) + ';\n')
        f.write('var THAOLE_VOCAB = [\n')
        f.write(',\n'.join(json.dumps(r, ensure_ascii=False) for r in out))
        f.write('\n];\n')

    # ---- in báo cáo --------------------------------------------------------
    cnt = Counter(r['lesson'] for r in out)
    print(f"Tổng: {len(out)} entry, {len(cnt)} bài → {OUT}")
    print("Bài ≠ 50:", {k: v for k, v in sorted(cnt.items()) if v != 50})
    for k, v in report.items():
        print(f"\n== {k}: {len(v)}")
        for row in v[:60]: print("  ", row)
    return 0

if __name__ == '__main__':
    sys.exit(main())
