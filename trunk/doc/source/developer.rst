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

.. automodule:: bBase
   :members:

.. automodule:: bBibFormat
   :members:

.. automodule:: bDatabase
   :members:

.. automodule:: bStyle
   :members:

:mod:`bTextProcessor` -- Interaction with text processors
=========================================================

:class:`bTextProcessor._generic` -- Abstract class
--------------------------------------------------

.. automodule:: bTextProcessor._generic
   :members:

:class:`bTextProcessor.openoffice` -- Specific implementation for OpenOffice.org
--------------------------------------------------------------------------------

.. automodule:: bTextProcessor.openoffice
   :members:

:mod:`bCitationFinder` -- Methods to find in-text citations
===========================================================

:class:`bCitationFinder._generic` -- Abstract class
---------------------------------------------------

.. automodule:: bCitationFinder._generic
   :members:

:class:`bCitationFinder.natbib` -- Emulating LaTeX/BibTeX's natbib behaviour
----------------------------------------------------------------------------

.. automodule:: bCitationFinder.natbib
   :members:

:class:`bCitationFinder.plaintext` -- Find citations in plain text
------------------------------------------------------------------

.. automodule:: bCitationFinder.plaintext
   :members:

