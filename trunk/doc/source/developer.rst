.. coding: utf-8

.. bibendum developer documentation.
   
   Etienne Gaudrain <egaudrain@gmail.com>, 2009-10-23
   
   Copyright 2009 Etienne Gaudrain
   
   This file, developer.rst, is part of the Bibendum Reference Manager project.
   
   Bibendum Reference Manager is a free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, version 3 of the License.
   
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   
   You should have received a copy of the GNU General Public License
   along with this program. If not, see <http://www.gnu.org/licenses/>.


Bibendum's developer documentation
##################################

This part of the documentation explains the architecture of the Bibendum Reference Manager source code. The code is organized is different submodules.

.. contents:: :depth: 3




:mod:`bBase` -- Base and utility classes
========================================

.. contents:: :depth: 1
   :local:

:class:`bBase.citation`
-----------------------

.. autoclass:: bBase.citation
   :members:

:class:`bBase.text` -- Formatted text
-------------------------------------

.. autoclass:: bBase.text
   :members:




:mod:`bBibFormat` -- Bibliography import/export
===============================================

.. automodule:: bBibFormat
   :members:




:mod:`bDatabase` -- Database access
===================================

.. automodule:: bDatabase
   :members:




:mod:`bStyle` -- Citation and reference list styles
===================================================

.. automodule:: bStyle
   :members:




:mod:`bTextProcessor` -- Interaction with text processors
=========================================================

.. contents:: :depth: 1
   :local:

:mod:`bTextProcessor._generic` -- Abstract class
------------------------------------------------

.. automodule:: bTextProcessor._generic
   :members:

:mod:`bTextProcessor.openoffice` -- Specific implementation for OpenOffice.org
------------------------------------------------------------------------------

.. automodule:: bTextProcessor.openoffice
   :members:





:mod:`bCitationFinder` -- Methods to find in-text citations
===========================================================

The implementations of this module define a class :class:`finder` that implements
methods to search citations in the text. Typically, citations can be searched for
in :mod:`natbib`\ -like format or in :mod:`plaintext`. Additionally, methods can be implemented
to find a marker defining the name of the Bibendum style and the position of the reference list.

Those class can also implement the reverse mechanism, i.e. transform fields into
textual representations.

.. contents:: :depth: 1
   :local:

:mod:`bCitationFinder._generic` -- Abstract class
---------------------------------------------------

.. automodule:: bCitationFinder._generic
   :members:

:mod:`bCitationFinder.natbib` -- Emulate LaTeX/BibTeX's natbib behaviour
--------------------------------------------------------------------------

.. automodule:: bCitationFinder.natbib
   :members:

:mod:`bCitationFinder.plaintext` -- Find citations in plain text
----------------------------------------------------------------

.. automodule:: bCitationFinder.plaintext
   :members:

