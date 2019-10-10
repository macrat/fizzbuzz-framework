""" FizzBuzzのフレームワーク

本気でFizzBuzzを作ったら、パイプライン処理のライブラリが出来た。


************************
このフレームワークの構造
************************

このフレームワークは、1個の入力に対して0個以上の出力を生成する :py:class:`Operator` というクラスを中心に構築されています。

この :py:class:`Operator` の派生として定義された :py:class:`数列を生成するクラス <SequenceGenerator>` や :py:class:`値を置換するクラス <ReplaceFilter>` 、:py:class:`結果をコンソールに表示するためのクラス <ConsolePrinter>` を組み合わせることでFizzBuzzを実現しています。


************
設計の考え方
************

FizzBuzzの処理を以下の3つの処理に分けて考えることにします。

1. 数列の生成
2. 値の処理
3. 結果の出力

ここで、この3つをそれぞれ *Generator* 、*Filter* 、*Printer* と呼ぶことにします。

もっとも基本的な形である *Filter* は、1個の入力に対して0個以上の出力を生成する処理であると定義出来ます。

単純な実装では、 *Generator* は入力を取らずに0個以上の出力を生成する処理として、 *Printer* は1個の入力に対して出力を持たない処理として定義することが出来ます。

しかしここで、 *Generator* は入力を無視する処理であると定義すると、3つの処理は全て *Filter* と同じシグネチャにすることが出来るようになります。
この共通のシグネチャを持った物を :py:class:`Operator` と呼び、このクラスから派生したクラスを組み合わせることでFizzBuzzの処理を実現しています。
"""

import sys
from typing import Any, List, Callable, TextIO


class EndOfList(Exception):
    """ 処理を終了したいときに送出する例外 """

    pass


class Operator:
    """ 値を生成したり、加工したり、出力したりするもの

    オペレータは1個の入力値を受け取り、0個以上の出力値を返す。
    もしくは、これ以上処理しないことを示す :py:class:`EndOfList` を送出する。

    複数のオペレータを :py:class:`OperatorChain` を使って繋ぐことで、プログラムの処理を表現する。
    """

    def execute(self, value: Any) -> List[Any]:
        """ 何らかの値を受け取り、何らかの値のリストを返す関数

        :param value: 上流のオペレータが作った入力値。無視しても良い。
        :returns: 下流のオペレータに渡される出力値のリスト。
        :raises EndOfList: 処理を終了させたい場合に送出する。
        """

        raise NotImplementedError()


class OperatorChain(Operator):
    """ 複数のオペレータを繋いで、一個のオペレータにしたもの

    :param operators: 繋ぎたいオペレータ。引数に与えた順番で実行される。


    一つのオペレータだけを与えた場合は、与えられたオペレータと同じ挙動になる。

    >>> class TestOperator(Operator):  # テスト用の値を倍にするオペレータ
    ...     def execute(self, x):
    ...         return [x * 2]
    >>> TestOperator().execute(2)
    [4]
    >>> OperatorChain(TestOperator()).execute(2)
    [4]

    二つ以上のオペレータを渡すと、与えられた順に実行した結果を返す。

    >>> OperatorChain(TestOperator(), TestOperator()).execute(2)
    [8]

    一つもオペレータが与えられなかった場合、入力をそのまま出力するオペレータになる。

    >>> OperatorChain().execute(2)
    [2]
    """

    def __init__(self, *operators: Operator) -> None:
        self.operators = operators

    def _unfoldExecute(self, operator: Operator, values: List[Any]) -> List[Any]:
        """ 複数の値の分だけオペレータを実行し、結果を結合して返す

        :param operator: 実行したいオペレータ。
        :param values: オペレータに渡したい引数のリスト。
        :returns: 全部の値についてオペレータを実行した結果を結合したリスト。


        >>> class TestOperator(Operator):  # テスト用の値を2回繰り返すオペレータ
        ...     def execute(self, x):
        ...         return [x, x]

        [1, 2, 3] を渡すと、それぞれの値が2回ずつ繰り返した物が返ってくる。

        >>> OperatorChain()._unfoldExecute(TestOperator(), [1, 2, 3])
        [1, 1, 2, 2, 3, 3]
        """

        result = []
        for v in values:
            r = operator.execute(v)
            try:
                result.extend(r)
            except TypeError:
                pass  # オペレータがリストを返さないのは許容してあげよう

        return result

    def execute(self, value: Any) -> List[Any]:
        """ 結合されたオペレータを実行する

        :param value: 入力値。
        :returns: 出力値のリスト。
        """

        val = [value]

        for o in self.operators:
            val = self._unfoldExecute(o, val)

        return val


def execute(*operators: Operator) -> None:
    """ オペレータを繋いで、 :py:class:`EndOfList` が送出されるまで繰り返し実行する

    :param operators: 実行したいオペレータのリスト


    最初のオペレータの入力は常に None になる。

    >>> class TestPrinter(Operator):  # テスト用の5回だけ入力を表示するオペレータ
    ...     def __init__(self):
    ...         self.count = 0
    ...     def execute(self, x):
    ...         self.count += 1
    ...         if self.count > 5:
    ...             raise EndOfList
    ...         print(x)
    >>> execute(TestPrinter())
    None
    None
    None
    None
    None
    """

    o = OperatorChain(*operators)

    while True:
        try:
            o.execute(None)
        except EndOfList:
            break


class SequenceGenerator(Operator):
    """ 無限の数列を作るジェネレータ

    :param from_: 最初に出力される数。省略すると0になる。
    :param step: 一回の呼び出しで変化する数。省略すると1ずつ増える。
    """

    def __init__(self, from_: float = 0, step: float = 1) -> None:
        self.current = from_ - step
        self.step = step

    def execute(self, value: Any) -> List[float]:
        """ 数列の次の値を取り出す

        :param value: 入力値だが、常に無視される。
        :returns: 昇順の数値。
        """

        self.current += self.step
        return [self.current]


class LimitFilter(Operator):
    """ 指定の回数で処理を停止させるフィルタ

    :param num: 停止するまでに処理する数。


    >>> execute(
    ...     SequenceGenerator(),  # 無限に数列を生成して、
    ...     LimitFilter(5),       # 先頭から5つだけ値を取り出し、
    ...     ConsolePrinter(),     # コンソールに表示する。
    ... )
    0
    1
    2
    3
    4
    """

    def __init__(self, num: int) -> None:
        self.ttl = num

    def execute(self, value: Any) -> List[Any]:
        """ 実行回数が上限を越えていないか確認して、入力をそのまま出力として出す

        :param value: 入力値。そのまま出力される。
        :returns: 出力値。入力されたものと同じ。
        :raises EndOfList: 実行回数が上限を越えると送出し、実行を停止させる。
        """

        if self.ttl <= 0:
            raise EndOfList()
        self.ttl -= 1
        return [value]


def RangeGenerator(from_: float, to: float, step: float = 1) -> OperatorChain:
    """ 指定の数値の間をカウントする数列を生成するジェネレータ

    中身は :py:class:`SequenceGenerator` と :py:class:`LimitFilter` を組み合わせただけのもの。

    :param from_: カウントを開始する値。
    :param to: カウントを終了する値。
    :param step: 一回の実行で増える数。


    >>> execute(
    ...     RangeGenerator(1, 8, 2),  # 1から8までの2刻みの数字を作って、
    ...     ConsolePrinter(),         # コンソールに表示する。
    ... )
    1
    3
    5
    7

    >>> execute(
    ...     RangeGenerator(3, 1, -1),  # 降順も作れる
    ...     ConsolePrinter(),
    ... )
    3
    2
    1
    """

    return OperatorChain(
        SequenceGenerator(from_, step),
        LimitFilter(int((max(from_, to) - min(from_, to)) // abs(step) + 1)),
    )


class ReplaceFilter(Operator):
    """ 特定の条件にマッチする値が入力されたら別の値に置換するフィルタ

    :param rule: 置換するかどうかを決める関数。Trueなら値を置きかえる。
    :param replace: どんな値に置換するか。


    >>> execute(
    ...     RangeGenerator(1, 5),
    ...     ReplaceFilter(lambda x: x == 2, "two"),
    ...     ConsolePrinter(),
    ... )
    1
    two
    3
    4
    5
    """

    def __init__(self, rule: Callable[[Any], bool], replace: Any) -> None:
        self.rule = rule
        self.replace = replace

    def execute(self, value: Any) -> List[Any]:
        """ 受け取った値をrule関数に渡し、Trueが返ってきたら置換する。

        :param value: 入力値。
        :returns: 置換された値、もしくは入力値そのものが入ったリスト。
        """

        if self.rule(value):
            return [self.replace]

        return [value]


def ModReplaceFilter(num: int, replace: Any) -> ReplaceFilter:
    """ 特定の値の倍数が入力されたら値を置換するフィルタ

    中身はReplaceFilter。ほぼFizzBuzz用。

    >>> execute(
    ...     RangeGenerator(1, 5),
    ...     ModReplaceFilter(2, "*"),
    ...     ConsolePrinter(),
    ... )
    1
    *
    3
    *
    5
    """

    return ReplaceFilter(lambda x: isinstance(x, int) and x % num == 0, replace)


class HTMLFilter(Operator):
    """ 入力をHTMLタグで囲って出力するフィルタ

    :param tag: 入力値を囲うのに使いたいタグ。


    >>> execute(
    ...     RangeGenerator(1, 5),
    ...     HTMLFilter(),
    ...     ConsolePrinter(),
    ... )
    <p>1</p>
    <p>2</p>
    <p>3</p>
    <p>4</p>
    <p>5</p>
    """

    def __init__(self, tag: str = "p") -> None:
        self.tag = tag

    def execute(self, value: Any) -> List[str]:
        """ 入力をタグで囲って出力する。

        :param value: 入力値。型は何でも良い。
        :returns: 入力値をタグで囲った文字列が入ったリスト。
        """

        return ["<{0}>{1}</{0}>".format(self.tag, value)]


class FilePrinter(Operator):
    r""" 入力値をFile like objectに出力するプリンタ

    :param file: 出力先となるファイルのインスタンス


    >>> import io
    >>> buf = io.StringIO()
    >>> execute(
    ...     RangeGenerator(1, 5),
    ...     FilePrinter(buf),
    ... )
    >>> buf.getvalue()
    '1\n2\n3\n4\n5\n'
    """

    def __init__(self, file: TextIO) -> None:
        self.file = file

    def execute(self, value: Any) -> List[Any]:
        """ 入力をファイルに出力し、そのまま出力値としても返す

        :param value: 入力値。
        :returns: 入力値が入った要素数が1のリスト。
        """

        print(value, file=self.file)

        return [value]


def ConsolePrinter() -> FilePrinter:
    """ 入力値をコンソールに出力するプリンタ

    出力先をstdoutにした :py:class:`FilePrinter` と同じもの。
    """

    return FilePrinter(sys.stdout)
