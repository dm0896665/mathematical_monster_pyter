import inspect
import sys
import time
import traceback
from symtable import Function

from PySide6.QtCore import QObject, QRunnable, Signal, Slot, QTimer, QEvent, QThreadPool, QThread, \
    QEventLoop, QMutex, QWaitCondition
from PySide6.QtWidgets import QApplication


class WorkerSignals(QObject):
    """Signals from a running worker thread.

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc())

    result
        object data returned from processing, anything

    progress
        float indicating % progress
    """

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(float)

class Worker(QRunnable):
    """Worker thread.

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread.
                     Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.threadpool = QThreadPool()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.loop: QEventLoop = QEventLoop()
        # Add the callback to our kwargs
        self.kwargs["progress_callback"] = self.signals.progress
        self.setAutoDelete(True) # QThreadPool will delete it after run() finishes

    @Slot()
    def run(self):
        try:
            has_callback_parameter: bool = False
            for param in inspect.signature(self.fn).parameters.values():
                if param.name == "progress_callback":
                    has_callback_parameter = True

            if not has_callback_parameter:
                del self.kwargs["progress_callback"]

            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()
            self.loop.quit()

    def start(self):
        self.threadpool.start(self)
        self.threadpool.deleteLater()
        self.loop.exec_()

class UIRunner(QObject):

    def __init__(self):
        super().__init__()
        self.loop: QEventLoop = QEventLoop(self)
        self.signals = WorkerSignals()

    def customEvent(self, e):
        if e.is_wait:
            QTimer.singleShot(int(e.delay * 1000), lambda: self.run_and_wait(e.func))
            #self.loop.exec_()
        else:
            QTimer.singleShot(int(e.delay * 1000), e.func)
        print("potato" + str(e.is_wait))

    def event(self, e: QEvent):
        if e.type() == QEvent.Type.ChildAdded:
            return False

        if e.is_wait:
            QTimer.singleShot(int(e.delay * 1000), lambda: self.run_and_wait(e.func))
            #self.loop.exec_()
        else:
            QTimer.singleShot(int(e.delay * 1000), e.func)
        print("potato" + str(e.is_wait))
        return True

    def run_and_wait(self, func: Function):
        worker_thread = QThread()
        receiver = UIEventReceiver(func)
        receiver.moveToThread(worker_thread)
        worker_thread.start()

        e = QEvent(QEvent.User)
        QApplication.postEvent(receiver, e)

        # Synchronization objects
        mutex = QMutex()
        wait_condition = QWaitCondition()

        # 2. Lock the mutex and wait for the signal
        # This will block the main thread until the wait condition is met
        print("Main: Waiting for event to be processed...")
        mutex.lock()
        wait_condition.wait(mutex)
        mutex.unlock()
        print("Main: Wait finished. Event has been processed.")

        # Clean up
        worker_thread.quit()
        worker_thread.wait()
        # self.loop.exit(True)
        # self.loop.quit()
        self.signals.finished.emit()
        print("finished")


# Create a custom event type
class CustomEventType:
    Event = QEvent.registerEventType()

# Custom event class to hold synchronization objects
class CustomEvent(QEvent):
    def __init__(self, mutex, wait_condition, worker_thread):
        super().__init__(QEvent.Type.ThreadChange)
        self.mutex = mutex
        self.wait_condition = wait_condition
        self.worker_thread = worker_thread

# Object to handle the custom event
class UIEventReceiver(QObject):
    def __init__(self, func: Function):
        super().__init__()
        self.func = func

    def event(self, e):
        if e.type() == QEvent.Type.ThreadChange:
            print("Receiver: Event received. Starting local event loop...")

            # # The event handler will execute its own QEventLoop
            # local_loop = QEventLoop()
            #
            # # Use a QTimer to simulate work and eventually exit the loop
            # def stop_loop():
            #     print("Receiver: Stopping local event loop.")
            #     local_loop.quit()
            #
            # timer = QTimer()
            # timer.setSingleShot(True)
            # timer.timeout.connect(stop_loop)
            # timer.start(2000)  # Wait 2 seconds
            #
            # local_loop.exec()
            self.func()

            print("Receiver: Local event loop finished. Signaling main thread...")

            # Unlock the main thread using the mutex and wait condition
            e.mutex.lock()
            e.wait_condition.wakeAll()
            e.mutex.unlock()

            return True  # Mark the event as handled
        return super().event(e)

# Object to handle the custom event
class EventReceiver(QObject):
    def __init__(self, func: Function, delay = 0, is_wait = False, *args, **kwargs):
        super().__init__()
        self.func = lambda: func(*args, **kwargs)
        self.delay = delay
        self.is_wait = is_wait

    def event(self, e):
        if e.type() == QEvent.Type.ThreadChange:
            print("Receiver: Event received. Starting local event loop...")

            # # The event handler will execute its own QEventLoop
            # local_loop = QEventLoop()
            #
            # # Use a QTimer to simulate work and eventually exit the loop
            # def stop_loop():
            #     print("Receiver: Stopping local event loop.")
            #     local_loop.quit()
            #
            # timer = QTimer()
            # timer.setSingleShot(True)
            # timer.timeout.connect(stop_loop)
            # timer.start(2000)  # Wait 2 seconds
            #
            # local_loop.exec()
            self.func()

            print("Receiver: Local event loop finished. Signaling main thread...")

            # Unlock the main thread using the mutex and wait condition
            e.mutex.lock()
            e.wait_condition.wakeAll()
            e.mutex.unlock()

            return True  # Mark the event as handled
        return super().event(e)

class UiThreadUtil:
    _ui_runner: UIRunner = UIRunner()
    is_finished: bool = False
    loop: QEventLoop = QEventLoop()

    @staticmethod
    def run_on_ui(func: Function, delay = 0, is_wait = False, *args, **kwargs):
        e = QEvent(QEvent.User)
        e.is_wait = is_wait
        e.delay, e.func = delay, lambda: func(*args, **kwargs)
        QApplication.postEvent(UiThreadUtil._ui_runner, e)

        print("no please")

    @staticmethod
    def on_finished_wait():
        UiThreadUtil.is_finished = True
        if UiThreadUtil.loop.isRunning():
            UiThreadUtil.loop.exit(True)

    @staticmethod
    def run_on_ui_and_wait(func: Function, delay = 0, *args, **kwargs):
        UiThreadUtil.is_finished = False
        UiThreadUtil._ui_runner.signals.finished.connect(UiThreadUtil.on_finished_wait)
        UiThreadUtil.run_on_ui(func, delay, True, *args, **kwargs)
        # if not UiThreadUtil.is_on_ui_thread():
        #     while not UiThreadUtil.is_finished:
        #         QApplication.processEvents()
        #         QThread.msleep(10)
        #         print("hi")
        # else:
        UiThreadUtil.loop.exec_()

    @staticmethod
    def new_run_and_wait(func: Function, delay = 0, *args, **kwargs):
        main_thread = QThread.currentThread()

        # Create worker thread and event receiver object
        worker_thread = QThread()
        receiver = EventReceiver(func, delay, True, *args, **kwargs)
        receiver.moveToThread(worker_thread)
        worker_thread.start()

        # Synchronization objects
        mutex = QMutex()
        wait_condition = QWaitCondition()

        # 1. Post the custom event to the receiver object
        print("Main: Posting custom event...")
        event_to_post = CustomEvent(mutex, wait_condition, worker_thread)
        QApplication.postEvent(receiver, event_to_post)
        QApplication.processEvents()

        # 2. Lock the mutex and wait for the signal
        # This will block the main thread until the wait condition is met
        print("Main: Waiting for event to be processed...")
        mutex.lock()
        wait_condition.wait(mutex)
        mutex.unlock()
        print("Main: Wait finished. Event has been processed.")

        # Clean up
        worker_thread.quit()
        worker_thread.wait()

    @staticmethod
    def sleep(seconds: int):
        if seconds < 0:
            return

        if UiThreadUtil.is_on_ui_thread():
            milliseconds = seconds * 1000
            QTimer.singleShot(milliseconds, UiThreadUtil.loop.quit)
            UiThreadUtil.loop.exec_()
        else:
            i = 0
            deciseconds = seconds * 10
            while i < deciseconds:
                time.sleep(.1)
                QApplication.processEvents()
                i += 1

    @staticmethod
    def is_on_ui_thread():
        """
        Checks if the current execution is on the main UI thread.
        """
        app = QApplication.instance()
        if app is None:
            # No QApplication instance, likely not in a GUI context or app not started yet
            return False

        # The main application thread is typically the thread where QApplication was created
        # and where the event loop is running.
        # QThread.currentThread() returns the QThread object for the currently executing thread.
        return QThread.currentThread() == app.thread()