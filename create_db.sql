-- Create database
CREATE DATABASE IF NOT EXISTS sres_db;
USE sres_db;

-- Create table
CREATE TABLE IF NOT EXISTS restriction_enzymes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    enzyme_name VARCHAR(50),
    recognition_seq VARCHAR(20),
    cut_position INT,
    overhang_type VARCHAR(10),   -- e.g., "5'", "3'", "blunt"
    buffer_1 BOOLEAN,
    buffer_2 BOOLEAN,
    buffer_3 BOOLEAN,
    cutsmart BOOLEAN,
    supplier_url TEXT
);

-- Insert starter data
INSERT INTO restriction_enzymes (enzyme_name, recognition_seq, cut_position, overhang_type, buffer_1, buffer_2, buffer_3, cutsmart, supplier_url) VALUES
('EcoRI', 'GAATTC', 1, '5\'', TRUE, TRUE, FALSE, TRUE, 'https://www.neb.com/products/r0101-ecori'),
('BamHI', 'GGATCC', 1, '5\'', FALSE, TRUE, TRUE, TRUE, 'https://www.neb.com/products/r0136-bamhi'),
('HindIII', 'AAGCTT', 1, '5\'', TRUE, FALSE, TRUE, TRUE, 'https://www.neb.com/products/r0104-hindiii'),
('XhoI', 'CTCGAG', 1, '5\'', TRUE, TRUE, TRUE, TRUE, 'https://www.neb.com/products/r0146-xhoi'),
('PstI', 'CTGCAG', 5, '3\'', TRUE, FALSE, TRUE, TRUE, 'https://www.neb.com/products/r0140-psti'),
('SmaI', 'CCCGGG', 3, 'blunt', TRUE, FALSE, TRUE, TRUE, 'https://www.neb.com/products/r0141-smai'),
('KpnI', 'GGTACC', 5, '3\'', TRUE, TRUE, FALSE, TRUE, 'https://www.neb.com/products/r0142-kpni'),
('SalI', 'GTCGAC', 1, '5\'', FALSE, TRUE, TRUE, TRUE, 'https://www.neb.com/products/r0138-sali'),
('NotI', 'GCGGCCGC', 2, '5\'', TRUE, TRUE, TRUE, TRUE, 'https://www.neb.com/products/r0189-noti'),
('NcoI', 'CCATGG', 1, '5\'', FALSE, TRUE, TRUE, TRUE, 'https://www.neb.com/products/r0193-ncoi');
