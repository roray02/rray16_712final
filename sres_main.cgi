#!/usr/local/bin/python3

import cgi
import cgitb
import mysql.connector
import re
from jinja2 import Environment, FileSystemLoader

cgitb.enable()

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('results.html')

# --- Configuration ---
DB_HOST = 'localhost'
DB_USER = 'rray16'
DB_PASSWORD = 'DBPStrongmonkey71!'
DB_NAME = 'rray16'

def connect_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def get_enzymes(conn, table_name):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {table_name} WHERE recognition_seq IS NOT NULL AND recognition_seq != '';")
    enzymes = cursor.fetchall()
    cursor.close()
    return enzymes

def find_internal_cutters(sequence, enzymes, window_size):
    internal = []
    seq_len = len(sequence)

    for enzyme in enzymes:
        try:
            pattern = enzyme['recognition_seq']
            matches = list(re.finditer(pattern, sequence))
            for match in matches:
                start = match.start()
                end = match.end()
                # keep if within window from either end
                if start <= window_size or end >= seq_len - window_size:
                    internal.append(enzyme['enzyme_name'])
                    print("Content-Type: text/html\n")
                    print(f"<p style='color:red;'>DEBUG: Internal cut by {enzyme['enzyme_name']} at position {start}-{end}</p>")
                    break  # only need one hit to flag it
        except re.error:
            continue
    return internal

def find_end_cutters(sequence, enzymes, window_size):
    """
    Return a list of enzymes that cut within window_size of either sequence end.
    """
    end_cutters = []
    seq_len = len(sequence)

    for enzyme in enzymes:
        try:
            pattern = enzyme['recognition_seq']
            for match in re.finditer(pattern, sequence):
                start = match.start()
                end = match.end()
                if start <= window_size or end >= seq_len - window_size:
                    end_cutters.append(enzyme)
                    break
        except re.error:
            continue
    return end_cutters


def filter_enzymes(enzymes, internal_cutters, preference):
    filtered = []
    for e in enzymes:
        if e['enzyme_name'] in internal_cutters:
            continue # excluding the internal cutters
        if preference == 'sticky' and e['overhang_type'] == 'blunt':
            continue
        if preference == 'blunt' and e['overhang_type'] != 'blunt':
            continue
        filtered.append(e)
    return filtered

def find_compatible_pairs(sequence, matched_enzymes, window_size):
    pairs = []
    seq_len = len(sequence)

    five_prime = []
    three_prime = []

    for enzyme in matched_enzymes:
        try:
            pattern = enzyme['recognition_seq']
            for match in re.finditer(pattern, sequence):
                start = match.start()
                end = match.end()
                if start <= window_size:
                    five_prime.append(enzyme)
                    break
                elif end >= seq_len - window_size:
                    three_prime.append(enzyme)
                    break
        except re.error:
            continue

    # Build only valid 5'/3' pairs
    for e5 in five_prime:
        for e3 in three_prime:
            if e5['enzyme_name'] == e3['enzyme_name']:
                continue  # skip self-pairs
            buffer_compatible = bool(set(e5['commercial_sources']) & set(e3['commercial_sources']))
            pairs.append({
                'enzyme1': e5['enzyme_name'],
                'enzyme2': e3['enzyme_name'],
                'overhang1': e5['overhang_type'],
                'overhang2': e3['overhang_type'],
                'buffer_compatible': buffer_compatible,
                'recog1': e5['recognition_seq'],
                'recog2': e3['recognition_seq'],
                'source1': e5['commercial_sources'],
                'source2': e3['commercial_sources'],
            })

    return pairs


def highlight_sequence(sequence, enzymes):
    highlighted = sequence
    for e in enzymes:
        try:
            highlighted = re.sub(
                e['recognition_seq'],
                lambda m: f"<span class='cut-site'>{m.group(0)}</span>",
                highlighted
            )
        except re.error:
            continue
    return highlighted

def main():
    form = cgi.FieldStorage()
    sequence = form.getfirst('sequence', '').upper().strip()
    preference = form.getfirst('end_type', 'any')
    source_option = form.getfirst('source_option', 'commercial')
    window_size = int(form.getfirst('window_size', '50'))

    if sequence.startswith(">"):
        sequence = ''.join(sequence.splitlines()[1:])

    table_name = 'restriction_enzymes_rebase_commercialsources' if source_option == 'commercial' else 'restriction_enzymes_rebase'

    conn = connect_db()
    enzymes = get_enzymes(conn, table_name)
    conn.close()

    #internal_cutters = find_internal_cutters(sequence, enzymes, window_size)
    end_cutters = find_end_cutters(sequence, enzymes, window_size)
    usable = filter_enzymes(end_cutters, [], preference)
    pairs = find_compatible_pairs(sequence, usable, window_size)
    highlighted = highlight_sequence(sequence, usable)

    template_pairs = []
    cut_counter = 1
    for p in pairs:
        overhang1 = p['overhang1']
        overhang2 = p['overhang2']
        
        ligation_compatible = (
            (overhang1 == overhang2) or
            (overhang1 == 'blunt' and overhang2 == 'blunt')
        )

        template_pairs.append({
            'enzyme_5': p['enzyme1'],
            'enzyme_3': p['enzyme2'],
            'overhangs': f"{overhang1} / {overhang2}",
            'ligation_compatible': ligation_compatible,
            'sources': f"{p['source1']} / {p['source2']}",
            'cut_ids': [f"cut{cut_counter}", f"cut{cut_counter+1}"],
            'site1': p['recog1'],  # <-- Add this
            'site2': p['recog2'],  # <-- And this
        })
        cut_counter += 2

    print("Content-Type: text/html\n")
    print(template.render(
        enzyme_pairs=template_pairs,
        sequence=highlighted
    ))
    #generate_html_output(pairs, highlighted, table_name, window_size)


if __name__ == "__main__":
    main()