#############
API Reference
#############

.. py:currentmodule:: framework


********************
基本的なクラスと関数
********************

.. autoclass:: Operator
    :members:

.. autoclass:: OperatorChain
    :members:

.. autofunction:: execute

.. autoclass:: EndOfList
    :members:


********************
組み込みのオペレータ
********************

ジェネレータ
============

.. autoclass:: SequenceGenerator
    :members:


.. autofunction:: RangeGenerator


フィルタ
========

.. autoclass:: LimitFilter
    :members:

.. autoclass:: ReplaceFilter
    :members:

.. autofunction:: ModReplaceFilter

.. autoclass:: HTMLFilter
    :members:


プリンタ
========

.. autoclass:: FilePrinter
    :members:

.. autofunction:: ConsolePrinter
