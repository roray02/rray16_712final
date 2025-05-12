
# Smart Restriction Enzyme Selector (SRES)

## Overview

The Smart Restriction Enzyme Selector (SRES) is a web-based tool designed to help molecular biologists identify pairs of restriction enzymes suitable for cloning. Given a user-input DNA sequence, it returns enzyme pairs that:

- Cut near the 5′ and 3′ ends of the sequence (within a user-defined window),
- Do not cut internally,
- Have compatible overhangs,
- Are available from commercial sources (if selected).

The tool uses a parsed and filtered REBASE database and presents results through an interactive web interface with sequence visualization.

## Project Directory

This project is hosted at: `/var/www/html/rray16/final` on our class server.

### Key Files and Directories:

- `allenz.txt` – Raw REBASE enzyme data (version 505)
- `index.html` – Web form for user input (sequence, enzyme preferences)
- `insert_rebase_enzymes.py` – Script to parse and populate REBASE data into MySQL
- `sres_main.cgi` – Main backend CGI script handling logic and rendering results
- `templates/` – Jinja2 template directory containing `results.html` layout

---

## Usage

To use the Smart Restriction Enzyme Selector, simply visit the following URL in your browser:

http://bfx3.aap.jhu.edu/rray16/final/index.html

### Steps

1. **Paste your DNA sequence (FASTA format or plain string).**

2. **Set preferences for overhang type, enzyme source (commercial/all), and cut site window size.**
3. **Submit the form.**
4. **View the results, which show enzyme pairs, compatibility info, and highlights of the cut sites on your sequence.**
   
---

## Notes

- The recognition sequences and overhang compatibility are parsed from REBASE, including caret-based and offset-based notation.
- JavaScript enables hover-based highlighting and interaction with enzyme pair rows.


---

## Acknowledgments

REBASE – The Restriction Enzyme Database (Dr. Richard J. Roberts)

Developed as part of a final project for AS.410.712 Advanced Computer Concepts for Bioinformatics at Johns Hopkins University.
