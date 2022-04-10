# Makefile für thesis. Mit pdflatex, bevorzugt auf 
# Linux Rechnern und libreoffice installiert
PDFLATEX=pdflatex -interaction=nonstopmode
BIBTEX=bibtex
SOFFICE=soffice
ZIP=zip
RM=rm
MKDIR=mkdir

STYLES=hsmalogo.sty hsmalogosw.pdf blindtext.sty
DRAWINGS=zeichnung.odg templateprozess.odg
INCLUDE_DRAWINGS=zeichnung.pdf templateprozess.pdf
IMAGES=zeichnungjpg.jpg zeichnungpng.png zeichnungdraft.jpg gnu.png automata.pdf
SOURCES=gcd.cpp
MAIN=thesis
TEXFILES=$(MAIN).tex preamble.tex vorspann.tex hyphenations.tex
BIB=thesis.bib online.bib
INCLUDE_BIB=$(MAIN)1.bbl $(MAIN)2.bbl # Achtung spaeter nochmal manuell
TOPACK= $(STYLES) $(BIB) $(DRAWINGS) $(IMAGES) $(SOURCES) $(TEXFILES) Makefile thesis.pdf HinweiseKolloquium.pdf

$(MAIN): $(MAIN).pdf HinweiseKolloquium.pdf

# bewusst nicht erstes Ziel
all: bib $(MAIN).pdf LaTeXThesis.zip

LaTeXThesis.zip: $(TOPACK) 
	-$(RM) -rf LaTeXThesis
	$(MKDIR) LaTeXThesis
	cp $(TOPACK) LaTeXThesis
	$(ZIP) -r LaTeXThesis.zip LaTeXThesis
	$(RM) -rf LaTeXThesis

$(MAIN).pdf: $(TEXFILES) $(STYLES) $(INCLUDE_DRAWINGS) $(INCLUDE_BIB)

# für das convert braucht man ImageMagick
zeichnungjpg.jpg: zeichnung.pdf
	convert zeichnung.pdf zeichnungjpg.jpg
zeichnungpng.png: zeichnung.pdf
	convert zeichnung.pdf zeichnungpng.png

bib: $(MAIN)1.bbl $(MAIN)2.bbl
# Bibliography geht nur manuell wegen bibtopic
# Nachteil: make erstellt bei jedem Durchlauf das PDF neu. 
# Vorteil: Es geht auch von Anfang an, für Leute (die Mehrheit),
#          die nicht schauen. 
bib: $(MAIN)1.bbl $(MAIN)2.bbl
$(MAIN)1.bbl: thesis.bib $(MAIN)1.aux
	-$(BIBTEX) $(MAIN)1
$(MAIN)2.bbl: online.bib $(MAIN)2.aux
	-$(BIBTEX) $(MAIN)2

# Das erste Mal TeXen wegen Bibliographie
# Das allererste Mal ist die Bibliographie noch nicht drin.
$(MAIN)1.aux: 
	$(PDFLATEX) $(MAIN).tex
$(MAIN)2.aux: 
	$(PDFLATEX) $(MAIN).tex

.PHONY: clean

RERUN = "(There were undefined |Rerun to get (cross-references|the bars))"

.SUFFIXES: .odg .tex .pdf

.tex.pdf: bib
	$(PDFLATEX) $*.tex
    # nochmal wenn notwendig
	egrep $(RERUN) $*.log && ($(PDFLATEX) $*.tex) ; true
    # und nochmal wenn notwendig
	egrep $(RERUN) $*.log && ($(PDFLATEX) $*.tex) ; true

.odg.pdf:
	$(SOFFICE) --headless --convert-to pdf $*.odg

clean:
	-$(RM) $(MAIN).pdf *.lof *.log *.lot *.aux *.toc *.blg
	-$(RM) $(INCLUDE_DRAWINGS) $(INCLUDE_BIB)

TOPUB=LaTeXThesis.zip thesis.pdf
pub: $(TOPUB)
	chmod a+r $(TOPUB)
	scp -rp $(TOPUB) peter@www.pbma.de:/var/www/html/latex
