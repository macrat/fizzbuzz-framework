""" FizzBuzzフレームワークの利用例 """

from typing import Any, List

import framework


def FizzBuzzFilter() -> framework.OperatorChain:
    """ 入力値に対してFizzBuzz変換掛けるフィルタ

    中身は単純に ModReplaceFilter を組み合わせただけ。
    """

    return framework.OperatorChain(
        framework.ModReplaceFilter(15, "fizzbuzz"),
        framework.ModReplaceFilter(3, "fizz"),
        framework.ModReplaceFilter(5, "buzz"),
    )


class FactorialFilter(framework.Operator):
    """ 階乗的な計算をするフィルタ

    前回の出力を記憶しておいて、新しい入力と掛けたものを次の出力とする。
    """

    def __init__(self) -> None:
        self.last_value: float = 1

    def execute(self, value: float) -> List[float]:
        """ 階乗的な計算をした結果を出力する

        :param value: 入力値。少なくともかけ算が出来る値である必要がある。
        :return: 階乗的な計算の結果。
        """

        self.last_value = value * self.last_value

        return [self.last_value]


if __name__ == "__main__":
    framework.execute(
        framework.RangeGenerator(1, 30),
        # FactorialFilter(),  # この行のコメントアウトを消すと階乗になる
        FizzBuzzFilter(),
        framework.ConsolePrinter(),
    )
