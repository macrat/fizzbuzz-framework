##################
FizzBuzz Framework
##################

.. toctree::
   :maxdepth: 2

   reference

.. automodule:: framework


**********
使い方の例
**********

FizzBuzz
========

単純に作るのであれば、 :py:class:`ModReplaceFilter` を用いれば実現出来ます。

.. code-block:: python

    execute(
        RangeGenerator(1, 30),
        ModReplaceFilter(15, "fizzbuzz"),
        ModReplaceFilter(3, "fizz"),
        ModReplaceFilter(5, "buzz"),
        ConsolePrinter(),
    )

FizzBuzzの処理をフィルタとして定義したい場合は、 :py:class:`ModReplaceFilter` を :py:class:`OperatorChain` で連結する関数を作成してください。

.. code-block:: python

    def FizzBuzzFilter():
        return OperatorChain(
            ModReplaceFilter(15, "fizzbuzz"),
            ModReplaceFilter(3, "fizz"),
            ModReplaceFilter(5, "buzz"),
        )

ここで作成したフィルタは、組み込みのフィルタと同じように使用することが出来ます。

.. code-block:: python

    execute(
        RangeGenerator(1, 30),
        FizzBuzzFilter(),
        ConsolePrinter(),
    )


階乗の計算
==========

階乗の計算は組み込みのフィルタで実現出来ないため、 :py:class:`Operator` を継承して新たにフィルタを作成します。

.. code-block:: python

    class FactorialFilter(Operator):
        def __init__(self):
            self.last_value = 1

        def execute(self, value):
            self.last_value = value * self.last_value

            return [self.last_value]  # 値を1つしか返さない場合でもリスト形式を取ることに注意してください。

使い方は通常のフィルタと同じです。

.. code-block:: python

    execute(
        RangeGenerator(1, 30),
        FactorialFilter(),
        ConsolePrinter(),
    )
