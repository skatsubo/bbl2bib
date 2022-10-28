# Bibitem to bib converter

It extracts fields from unstructured `\bibitem` content by pattern matching (based on GROK regex library) and then saves them in `bibtex` format.

Use it when a document has citations without using BibTex but just old style `thebibliography` environment and `\bibitem`'s. The script translates `\bibitem` entries and puts them into BibTex format.


# Installation
Install dependencies with

```sh
pip install -r requirements.txt
```

or

```sh
pip3 install pygrok
```


# How to run

Run it and save its output to a file:
```sh
python3 bbl2bib.py samples/bibitem-medium.tex > bibitem.bib
```

Run with verbose debug output:
```sh
python3 bbl2bib.py samples/bibitem.tex -d
```


# How to develop
You can test your grok patterns at https://grokdebug.herokuapp.com/.

See the list of available default grok patterns: https://grokdebug.herokuapp.com/patterns or https://github.com/garyelephant/pygrok/tree/master/pygrok/patterns.

Sources and documentation for pygrok: https://github.com/garyelephant/pygrok.


# Issues
Both pygrok and py3grok have their limitations.


# Alternatives

## convertbiblio
- http://materia.fisica.unimi.it/manini/scripts/convertbiblio.py
- http://materia.fisica.unimi.it/manini/scripts/convertbiblio

Run as
```sh
python3 convertbiblio.py ref.tex
```


## https://github.com/borisveytsman/crossrefware
Uses online database.
```sh
curl -L -o bbl2bib.pl https://raw.githubusercontent.com/borisveytsman/crossrefware/master/bbl2bib.pl
sudo cpan install BibTeX::Parser
perl bbl2bib.pl bibitem.tex
```


## text2bib
```sh
docker run -it --rm -v $(pwd):/srv --entrypoint sh php:5.6-alpine
cd /srv
php -f convert.php bibitem2.tex
#docker run -it --rm -v $(pwd):/srv php:5.6-alpine -f /srv/convert.php /srv/bbl.tex
```

Remove square brackets `[]`
```sh
gsed -E 's \[\{ { ; s \}\] } ' bibitem.tex > bibitem2.tex
```



## perl
https://ctan.org/tex-archive/biblio/bibtex/utils/tex2bib
https://sites.ualberta.ca/afs/ualberta.ca/sunsite/ftp/pub/Mirror/CTAN/help/Catalogue/entries/tex2bib.html

/CTAN/biblio/bibtex/utils/tex2bib/

sudo cpan
notest install Perl4::CoreLibs

perl tex2bib.pl -i bibitem.tex
