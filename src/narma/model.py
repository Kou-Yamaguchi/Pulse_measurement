import numpy as np
from typing import Literal
from numpy.typing import NDArray

from ..database import append_record_narma_templetes, append_narma_input_array

def use_narma_input_array(use_database: bool, model: Literal["narma2", "narma10"], steps: int=None, input_range_bot: float=None, input_range_top: float=None) -> NDArray:
    """
    NARMAデータセットを使う

    Parameters
    ----------
    use_database: bool
        データベースから呼び出すかどうか
    model: 'narma2', 'narma10'
        モデル選択
    steps: int
        離散時間数
    input_range_bot: float
        入力値の下限
    input_range_top: float
        入力値の上限

    Returns
    -------
    u: NDArray
        入力配列
    y: NDArray
        出力配列
    """
    if use_database:
        return call_narma_dataset()

    return generate_narma_dataset(model, steps, input_range_bot, input_range_top)


def generate_narma2(u: NDArray[np.float64], steps: int) -> NDArray[np.float64]:
    y = np.zeros(steps)
    for t in range(10, steps):
        y[t] = 0.4 * y[t-1] + 0.4 * y[t-1] * y[t-2] + 0.6 * u[t-1] ** 3 + 0.1
    return y


def generate_narma10(u: NDArray[np.float64], steps: int) -> NDArray[np.float64]:
    y = np.zeros(steps)
    for t in range(10, steps):
        y[t] = 0.3 * y[t-1] + 0.05 * y[t-1] * sum(y[t-i-1] for i in range(10)) + 1.5 * u[t-10] * u[t-1] + 0.1
    return y


def generate_narma_dataset(model: Literal["narma2", "narma10"], steps: int, input_range_bot: float, input_range_top: float) -> NDArray:
    """
    NARMAデータセットを作成する

    Attributes
    ----------
    model: 'narma2', 'narma10'
        モデル選択
    steps: int
        離散時間数
    input_range_bot: float
        入力値の下限
    input_range_top: float
        入力値の上限

    Returns
    -------
    u: NDArray
        入力配列
    """
    if model not in ["narma2", "narma10"]:
        raise ValueError(f"Invalid model: {model}. Allowed values are 'narma2', 'narma10'.")
    
    narma_templete_id = append_record_narma_templetes(param=(steps, input_range_top, input_range_bot))

    u = np.random.uniform(input_range_bot, input_range_top, steps)

    # # NARMAデータの生成
    # if model == "narma2":
    #     y = generate_narma2(u, steps)

    # if model == "narma10":
    #     y = generate_narma10(u, steps)

    data = [(narma_templete_id, i, voltage) for i, voltage in enumerate(u)]
    append_narma_input_array(param=data)

    return u

def call_narma_dataset() -> tuple[NDArray, NDArray, NDArray, NDArray]:
    pass