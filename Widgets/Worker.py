from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

__all__ = [
    'Worker'
]

class Worker(QRunnable):
    class WorkerSignal(QObject):
        started = pyqtSignal()
        finished = pyqtSignal(object)

    # 2021-12-10 기준 Worker의 사용에서 args, kwargs가 사용되는 경우는 없으나
    # 혹시 추후에 필요할지 몰라서 일단 해놓기는 함.

    # 2022-03-03부터 쓰기 시작함. 천재냐, 2021-12-10의 나!
    # 2022-03-14: 근데 굳이 언패킹을 사용해야 할 지 잘 모르겠다는 이유로 언패킹을 없앴다.
    #             유념하기 바람.
    def __init__(self, fn, callback=None, args=(), kwargs={}):
        super().__init__()
        
        self._fn = fn
        self._callback = callback
        self._args = args
        self._kwargs = kwargs

        self.signal = self.WorkerSignal()

    def run(self):
        # ThreadPool이 종료될 때 RuntimeError가 발생하는 경우가 있음
        
        # 정확히는, ThreadPool 객체가 삭제될 때 self.signal의 C++ 객체가 삭제되어 
        # 그 result.emit()이 불가능해지는 것이 문제임.

        # 임시방편으로 try-except 문으로 Error 발생만을 막고 있는데, 
        # 추후 해결 방안이 떠오르면 속히 수정하기 바람.

        # 상기 문제는 종료 시 QThreadPool.waitForDone()을 호출하는 것으로 해결함.
        self.signal.started.emit()
        try:
            res = self._fn(*self._args, **self._kwargs)
        except Exception as e:
            if self._callback is not None: self._callback(e)
        else:
            self.signal.finished.emit(res)