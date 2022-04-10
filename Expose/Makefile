all: ausarb.pdf 

ausarb.pdf: ausarb.tex
	pdflatex -interaction=nonstopmode ausarb.tex
	bibtex ausarb
	pdflatex -interaction=nonstopmode ausarb.tex # texen mit neuen Referenzen
	pdflatex -interaction=nonstopmode ausarb.tex # Jetzt spätestens sollte alles stimmen

.PHONY: clean

clean:
	-/bin/rm -f ausarb.pdf *.lof *.log *.lot *.aux *.bbl *.toc *.blg
