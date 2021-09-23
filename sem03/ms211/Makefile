.PHONY : clean cleanall

PDFS = $(wildcard lista*_resolucao.pdf)

NBFLAGS = --TagRemovePreprocessor.remove_cell_tags="remove_cell" \
	--TemplateExporter.extra_template_basedirs="." \
	--template template --no-prompt --to pdf

all : $(PDFS)

clean :
	rm -r *_files

cleanall : clean
	rm -r $(PDFS)

lista%_resolucao.pdf : lista%_resolucao.ipynb
	jupyter nbconvert $(NBFLAGS) $<
