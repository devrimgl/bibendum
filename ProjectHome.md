The project is at a very early development stage. The aim is to make an application similar to Bibus or Zotero, but with extra features. Main features are:
  * Import/export citations automatically from Bibtex, Endnote, Pubmed, ISI...
  * Create, modify, delete references.
  * Search the reference database using human format (e.g. "Smith et al., 2005, JASA"). Possibly, make and interface with Pubmed, ISI...
  * Find citations in plain text (in a document your working on) and convert them into fields (so that the rendering becomes style dependent and can be updated).
  * The field format must not be dependent upon the software (i.e. MS Word vs. OpenOffice Writer) so that if you open or save a Word document in Writer, the fields are maintained and compatible.
  * Use a field system so enable collaborators to see the formatted citation without having the software installed, but in the original document so that if they modify it you don't have to rebuild the bibliography (as opposed to sending a frozen pure text version).
  * Have a wide variety of citation methods as in the LaTeX/BibTeX package "natbib".
  * Make journal format (long, ISO, Pubmed) part of the style.
  * Separate citation style and reference-list style.
  * Make the reference database accessible from everywhere and with a web interface.
  * Make the database format open and evolutive.

The project will be written in Python and the GUI will be Qt4. The initial version will be based on the MySQL database, but the database access type will be modular so that SQLite or PostgreSQL modules can be developed later. The connexion with OpenOffice.org will be made via PyUNO.