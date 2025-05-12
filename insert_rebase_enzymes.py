import mysql.connector
import re

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="rray16",
    password="DBPStrongmonkey71!",
    database="rray16"
)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS restriction_enzymes_rebase_commercialsources")

cursor.execute("""
CREATE TABLE restriction_enzymes_rebase_commercialsources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    enzyme_name VARCHAR(50),
    recognition_seq TEXT,
    overhang_type VARCHAR(10),
    commercial_sources TEXT,
    reference_id TEXT
);
""")

def parse_recognition_site(raw_seq):
    """
    Parses a REBASE recognition sequence.
    Returns: (cleaned_sequence, inferred_overhang_type)
    """
    # Case 1: Cut site using caret ^
    if "^" in raw_seq:
        cleaned = raw_seq.replace("^", "")
        pos = raw_seq.find("^")
        if pos == 0 or pos == len(raw_seq) - 1:
            overhang = "blunt"
        elif pos < len(raw_seq) // 2:
            overhang = "5'"
        else:
            overhang = "3'"
        return cleaned, overhang

    # Case 2: Cut site using offset notation (n/m)
    match = re.search(r"\(([-\d]+)/([-\d]+)\)", raw_seq)
    if match:
        top_cut = int(match.group(1))
        bottom_cut = int(match.group(2))
        cleaned = re.sub(r"\(([-\d]+)/([-\d]+)\)", "", raw_seq)
        if top_cut == bottom_cut:
            overhang = "blunt"
        elif top_cut < bottom_cut:
            overhang = "5'"
        else:
            overhang = "3'"
        return cleaned, overhang

    # Fallback: no recognizable cut site info
    return raw_seq.strip(), "unknown"


# Load REBASE-parsed file
with open("allenz.txt", "r") as f:
    content = f.read()

# Parse entries using REBASE tags
pattern = re.compile(
    r"<1>(.*?)\n<2>(.*?)\n<3>(.*?)\n<4>(.*?)\n<5>(.*?)\n<6>(.*?)\n<7>(.*?)\n<8>(.*?)\n",
    re.DOTALL
)
entries = pattern.findall(content)

inserted = 0
for entry in entries:
    enzyme_name = entry[0].strip()
    recog_seq = entry[4].strip()
    sources = entry[6].strip()
    ref_id = entry[7].strip()

    if not recog_seq or recog_seq == '?' or sources.strip() == '':
        continue

    recog_seq_clean, overhang = parse_recognition_site(recog_seq)

    cursor.execute("""
        INSERT INTO restriction_enzymes_rebase (enzyme_name, recognition_seq, overhang_type, commercial_sources, reference_id)
        VALUES (%s, %s, %s, %s, %s);
    """, (enzyme_name, recog_seq_clean, overhang, sources, ref_id))
    inserted += 1

conn.commit()
cursor.close()
conn.close()

print(f"Inserted {inserted} enzymes.")