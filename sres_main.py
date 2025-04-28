#!/usr/bin/env python3

import cgi
import cgitb
import mysql.connector
import re

# Enable debugging in browser
cgitb.enable()

# --- Configuration ---
DB_HOST = 'localhost'
DB_USER = 'rray16'
DB_PASSWORD = 'DBPStrongmonkey71!'
DB_NAME = 'sres_db'

# --- Helper Functions ---

def connect_db():
    """Connect to the MySQL database."""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def get_enzymes(conn):
    """Retrieve all enzymes from the database."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM restriction_enzymes;")
    enzymes = cursor.fetchall()
    cursor.close()
    return enzymes

def find_internal_cutters(sequence, enzymes):
    """Find enzymes that cut inside the sequence."""
    cutters = []
    for enzyme in enzymes:
        pattern = enzyme['recognition_seq']
        if re.search(pattern, sequence):
            cutters.append(enzyme['enzyme_name'])
    return cutters

def filter_enzymes(enzymes, internal_cutters, preference):
    """Filter usable enzymes based on internal cuts and end preference."""
    usable = []
    for enzyme in enzymes:
        if enzyme['enzyme_name'] in internal_cutters:
            continue
        if preference == 'sticky' and enzyme['overhang_type'] == 'blunt':
            continue
        if preference == 'blunt' and enzyme['overhang_type'] != 'blunt':
            continue
        usable.append(enzyme)
    return usable

def find_compatible_pairs(usable_enzymes):
    """Find enzyme pairs that share at least one compatible buffer."""
    pairs = []
    for i in range(len(usable_enzymes)):
        for j in range(i + 1, len(usable_enzymes)):
            e1 = usable_enzymes[i]
            e2 = usable_enzymes[j]
            # Check if they share any buffer
            shared_buffer = (
                (e1['buffer_1'] and e2['buffer_1']) or
                (e1['buffer_2'] and e2['buffer_2']) or
                (e1['buffer_3'] and e2['buffer_3']) or
                (e1['cutsmart'] and e2['cutsmart'])
            )
            pairs.append({
                'enzyme1': e1['enzyme_name'],
                'enzyme2': e2['enzyme_name'],
                'overhang1': e1['overhang_type'],
                'overhang2': e2['overhang_type'],
                'buffer_compatible': shared_buffer,
                'supplier1': e1['supplier_url'],
                'supplier2': e2['supplier_url']
            })
    return pairs

def highlight_sequence(sequence, enzymes):
    """Highlight all recognition sites inside the sequence."""
    highlighted = sequence
    for enzyme in enzymes:
        pattern = enzyme['recognition_seq']
        highlighted = re.sub(
            pattern,
            lambda m: f"<span class='cut-site'>{m.group(0)}</span>",
            highlighted
        )
    return highlighted

def generate_html_output(pairs, highlighted_sequence):
    """Generate and print the full HTML output page."""
    print("Content-Type: text/html\n")
    print("<html><head><title>Restriction Enzyme Results</title>")
    print("<link rel='stylesheet' href='../css/style.css'>")
    print("</head><body>")

    print("<h1>Smart Restriction Enzyme Selector Results</h1>")

    print("<h2>Your Input Sequence:</h2>")
    print(f"<div class='sequence-display'>{highlighted_sequence}</div>")

    print("<h2>Recommended Enzyme Pairs:</h2>")
    print("<table border='1'>")
    print("<tr><th>5' Enzyme</th><th>3' Enzyme</th><th>Buffer Compatible?</th><th>Overhang Types</th><th>Supplier Links</th></tr>")

    for pair in pairs:
        buffer_color = 'compatible' if pair['buffer_compatible'] else 'incompatible'
        print(f"<tr>")
        print(f"<td>{pair['enzyme1']}</td>")
        print(f"<td>{pair['enzyme2']}</td>")
        print(f"<td><span class='{buffer_color}'>{'Yes' if pair['buffer_compatible'] else 'No'}</span></td>")
        print(f"<td>{pair['overhang1']} / {pair['overhang2']}</td>")
        print(f"<td><a href='{pair['supplier1']}' target='_blank'>E1</a> | <a href='{pair['supplier2']}' target='_blank'>E2</a></td>")
        print(f"</tr>")

    print("</table>")
    print("<br><a href='../templates/index.html'>Back to Home</a>")

    print("</body></html>")

# --- Main Execution ---

def main():
    # Get form data
    form = cgi.FieldStorage()
    sequence_input = form.getfirst('sequence', '').upper().strip()
    preference = form.getfirst('end_type', 'any')

    # Clean FASTA input if needed
    if sequence_input.startswith('>'):
        sequence_input = ''.join(sequence_input.split('\n')[1:])

    # Connect to database
    conn = connect_db()
    enzymes = get_enzymes(conn)
    conn.close()

    # Analyze sequence
    internal_cutters = find_internal_cutters(sequence_input, enzymes)
    usable_enzymes = filter_enzymes(enzymes, internal_cutters, preference)
    enzyme_pairs = find_compatible_pairs(usable_enzymes)

    # Highlight sequence
    highlighted_seq = highlight_sequence(sequence_input, usable_enzymes)

    # Output results
    generate_html_output(enzyme_pairs, highlighted_seq)

if __name__ == "__main__":
    main()
