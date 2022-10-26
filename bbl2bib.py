#!/usr/bin/env python3

import sys
import logging
import argparse
import re
from pygrok import Grok



def prepare_grok():
	# configure patterns that will be used for parsing bbl entries
	bbl_elements={
		"REF_INFO": r"\[\{[^\]]+\}\]",
		"REF_LABEL": r"[\w ]+",
		"YEAR_EXT": r"\d\d\d\d[a-z]?",
		"BIBITEM": r"\\bibitem%{DATA:data}%{YEAR:year}"
	}
	# line example for pattern matching:
	# [{Alveen et~al.(2014)Alveen, McNamara, Carolan, Murphy, and Ivankovi{\'{c}}}]{Alveen2014} Alveen, P., McNamara, D., Carolan, D., Murphy, N., and Ivankovi{\'{c}}, A., \titlecap{Analysis of two-phase ceramic composites using micromechanical models}, {\em Comput. Mater. Sci.}, vol.~{\bf 92}, pp.~318--324, 2014.
	bbl_pattern = r'%{REF_INFO}{%{WORD:ref_label}}%{DATA:authors}\\titlecap.+%{YEAR_EXT:year}\.'

	return Grok(bbl_pattern, custom_patterns=bbl_elements)



def parse_bbl(text):
	# Extract each bibitem entry - between two `\bibitem` or between `\bibitem` and `\end{thebibliography}`. Example:
	#
	# \bibitem[{Zeng and Qin(2018)}]{ZENG2018269}
	# Zeng, Q. and Qin, Y., Multiscale Modeling of Hybrid Machining Processes, in \textit{Hybrid Machining}, X. Luo and Y. Qin, Eds., New York: Academic Press, pp. 269--298, 2018.
	#
	# \bibitem[{Allaire, 2002}]{Allaire2002}
	# Allaire, G., {\em Shape optimization by the homogenization method},
	#  New York: Springer, 2002.
	#
	# \end{thebibliography}

	# strip text starting from `\end{thebibliography}`
	without_end = text.split(r'\end{thebibliography}')[0]
	# strip text before the first `bibitem` and split them to separate bibitem entities
	bibitem_entries = without_end.split(r'\bibitem')[1:]
	logging.debug(f'bibitem_entries={bibitem_entries}')

	# iterate through each bibitem entry, parse it, add the result (parsed fields) to biblio list
	biblio = []
	for bi in bibitem_entries:
		fields = parse_bibitem(bi)
		biblio.append(fields)

	return biblio



def parse_bibitem(bibitem):
	# normalize the entry (whitespaces, tabs, line breaks) and make it a single line
	line = ' '.join(bibitem.split())
	logging.debug(f'bibitem line:\n{line}')

	# extract fields: authors, year, and so on
	fields = grok.match(line)
	logging.debug(f'fields:\n{fields}')

	# add custom metadata
	fields.update({ 
		'bibitem_line': line,
		'type': 'article'
	})

	# normalize values: strip whitespaces and commas
	clean_fields = { k : v.strip(' ,') for k, v in fields.items()}

	return clean_fields



def biblio_to_bibtex(biblio):
	# Bibtex format examples:
	#
	# @ARTICLE{ar2016,
	#     author = {AminPour, H. and Rizzi, N.},
	#     title = {A one-dimensional continuum with microstructure for single-wall carbon nanotubes bifurcation analysis},
	#     journal = {Math. Mech. Solids},
	#     fjournal = {Mathematics and Mechanics of Solids},
	#     volume = {21},
	#     year = {2016},
	#     number = {2},
	#     pages = {168--181},
	#     issn = {1081-2865},
	#     mrclass = {74A60},
	#     mrnumber = {3437815},
	#     doi = {10.1177/1081286515577037},
	#     url = {https://doi.org/10.1177/1081286515577037},
	# }
	#
	# @INCOLLECTION{ar2015,
	#     author = {Aminpour, Hossein and Rizzi, Nicola},
	#     title = {On the modelling of carbon nano tubes as generalized continua},
	#     booktitle = {Generalized continua as models for classical and advanced materials},
	#     series = {Adv. Struct. Mater.},
	#     volume = {42},
	#     pages = {15--35},
	#     publisher = {Springer, [Cham]},
	#     year = {2016},
	#     mrclass = {74K10},
	#     mrnumber = {3774228},
	#     doi = {10.1007/978-3-319-31721-2\_2},
	#     url = {https://doi.org/10.1007/978-3-319-31721-2_2},
	# }
	#
	# @BOOK{AntmanBook,
	#     author = {Antman, Stuart S.},
	#     title = {Nonlinear problems of elasticity},
	#     series = {Applied Mathematical Sciences},
	#     volume = {107},
	#     edition = {Second},
	#     publisher = {Springer, New York},
	#     year = {2005},
	#     pages = {xviii+831},
	#     isbn = {0-387-20880-1},
	#     mrclass = {74-02 (35Q72 58E20 74B20 74G65 74Kxx)},
	#     mrnumber = {2132247},
	#     mrreviewer = {Massimo Lanza de Cristoforis},
	#}
	bibtex = ''
	for b in biblio:
		logging.debug(f'biblio_entry:\n{b}')

		type    = b["type"]
		ref     = b["ref_label"]
		authors = b["authors"]
		year    = b["year"]
		line    = b["bibitem_line"]

		bibtex_entry = (
			f'@{type}{{{ref},\n'
			f'    author = {{{authors}}},\n'
			f'    year = {{{year}}},\n'
			f'    note = {{{line}}}\n'
			'}\n'
		)

		bibtex += bibtex_entry

	return bibtex



#--------------------------------------------------------------------------
# main
#--------------------------------------------------------------------------

# parse command line arguments
p = argparse.ArgumentParser(description='Bibitem to bib converter. Input: path to a tex file (if provided) or standard input if file is not specified. Output: parsed bibitem content in .bib format on standard output.')
p.add_argument("-d", "--debug", action="store_true", help="enable debug output")
p.add_argument("-t", "--test", action="store_true", help="run embedded tests")
p.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="path to a file (optional); stdin if not specified")
args = p.parse_args()

# debug mode
if args.debug:
	debug = True
	logging.root.setLevel(logging.DEBUG)

# prepare global pattern matcher
grok = prepare_grok()

# read bbl (tex) file
bbl_text = args.infile.read()
logging.debug('bbl_text:\n' + bbl_text)

# parse bbl data into internal `biblio` list of entries
biblio = parse_bbl(bbl_text)

# convert internal `biblio` to bibtex format
bibtex = biblio_to_bibtex(biblio)

print(bibtex)
