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

:class:`bBase.author` -- Author's name
--------------------------------------

.. autoclass:: bBase.author
   :members:

:class:`bBase.authorlist` -- List of author's names
---------------------------------------------------

.. autoclass:: bBase.authorlist
   :members:

:class:`bBase.entry` -- A bibliography entry
--------------------------------------------

.. autoclass:: bBase.entry
   :members:



:mod:`bBibFormat` -- Bibliography import/export
===============================================

.. automodule:: bBibFormat
   :members:




:mod:`bDatabase` -- Database access
===================================

Data model
----------

Access to the data is expected to be in UTF-8. Text searches are expected to be operated case insensitive.

:obj:`Entries` -- The information that any reference will have
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   +-----------------+--------------------------------+
   | Field           | Type and details               |
   +=================+================================+
   | `id_entry`      | ``int``, auto increment, index |
   +-----------------+--------------------------------+
   | `cite_ref`      | ``char[256]``, unique, index   |
   +-----------------+--------------------------------+
   | `type`          | ``char[256]``                  |
   +-----------------+--------------------------------+
   | `title`         | ``text``                       |
   +-----------------+--------------------------------+
   | `author`        | ``text``                       |
   +-----------------+--------------------------------+
   | `year`          | ``int``                        |
   +-----------------+--------------------------------+
   | `creation_date` | ``datetime``                   |
   +-----------------+--------------------------------+


:obj:`Fields` -- The information that depends on the reference type, or custom data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   +-----------------+--------------------------------+
   | Field           | Type and details               |
   +=================+================================+
   | `id_field`      | ``int``, auto increment, index |
   +-----------------+--------------------------------+
   | `id_entry`      | ``int``                        |
   +-----------------+--------------------------------+
   | `field_name`    | ``text``                       |
   +-----------------+--------------------------------+
   | `field_value`   | ``text``                       |
   +-----------------+--------------------------------+


:obj:`Backup` -- Where any entry is saved when modified or deleted
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   +-----------------+--------------------------------+
   | Field           | Type and details               |
   +=================+================================+
   | `id_backup`     | ``int``, auto increment, index |
   +-----------------+--------------------------------+
   | `entry_data`    | ``text``                       |
   +-----------------+--------------------------------+
   | `field_data`    | ``text``                       |
   +-----------------+--------------------------------+
   | `backup_date`   | ``datetime``                   |
   +-----------------+--------------------------------+
   | `reason`        | ``char[16]``                   |
   +-----------------+--------------------------------+


:obj:`Journals` -- Contains a list of journals in various formats
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   +-----------------+--------------------------------+
   | Field           | Type and details               |
   +=================+================================+
   | `id_journal`    | ``int``, auto increment, index |
   +-----------------+--------------------------------+
   | `iso`           | ``text``, index                |
   +-----------------+--------------------------------+
   | `long`          | ``text``                       |
   +-----------------+--------------------------------+
   | `pubmed`        | ``text``                       |
   +-----------------+--------------------------------+
   | `short`         | ``text``                       |
   +-----------------+--------------------------------+

:obj:`Search` -- Contains representation of the entries compatible with natural search
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   +-----------------+--------------------------------+
   | Field           | Type and details               |
   +=================+================================+
   | `id_search`     | ``int``, auto increment, index |
   +-----------------+--------------------------------+
   | `id_entry`      | ``int``, key                   |
   +-----------------+--------------------------------+
   | `author`        | ``text``                       |
   +-----------------+--------------------------------+
   | `n_author`      | ``int``                        |
   +-----------------+--------------------------------+
   | `year`          | ``int``                        |
   +-----------------+--------------------------------+
   | `journal`       | ``text``                       |
   +-----------------+--------------------------------+



:mod:`bDatabase._generic` -- Abstract class an query object
-----------------------------------------------------------

.. automodule:: bDatabase._generic
   :members:

:mod:`bDatabase.mysql` -- Implementation for MySQL
--------------------------------------------------

.. automodule:: bDatabase.mysql
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

