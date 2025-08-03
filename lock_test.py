# import sys
# import random
# import time
# from PySide6.QtCore import QObject, QThread, Signal, Slot, QMutexLocker, QMutex, QWaitCondition
# from PySide6.QtWidgets import QApplication

# # Shared buffer with thread-safe operations
# class Buffer(QObject):
#     itemProduced = Signal(int)
#     itemConsumed = Signal(int)

#     def __init__(self, max_size=5):
#         super().__init__()
#         self.buffer = []
#         self.lock = QMutex()
#         self.max_size = max_size

#     def produce(self, item):
#         if len(self.buffer) < self.max_size:
#             self.buffer.append(item)
#             self.itemProduced.emit(item)
#             return True
#         return False

#     def consume(self):
#         if self.buffer:
#             item = self.buffer.pop(0)
#             self.itemConsumed.emit(item)
#             return item
#         return None

# # Producer class
# class Producer(QObject):
#     finished = Signal()

#     def __init__(self, buffer, producer_id):
#         super().__init__()
#         self.buffer = buffer
#         self.producer_id = producer_id
#         self.running = True

#     @Slot()
#     def run(self):
#         while self.running:
#             item = random.randint(1, 100)
#             with QMutexLocker(self.buffer.lock):
#                 produced = self.buffer.produce(item)
#                 if not produced:
#                     print(f"Producer {self.producer_id}: Buffer full, waiting...")
#             if produced:
#                 print(f"Producer {self.producer_id} produced: {item}")
#             time.sleep(random.uniform(0.5, 1.5))
#         self.finished.emit()

#     def stop(self):
#         self.running = False

# # Consumer class
# class Consumer(QObject):
#     finished = Signal()

#     def __init__(self, buffer, consumer_id):
#         super().__init__()
#         self.buffer = buffer
#         self.consumer_id = consumer_id
#         self.running = True

#     @Slot()
#     def run(self):
#         while self.running:
#             with QMutexLocker(self.buffer.lock):
#                 item = self.buffer.consume()
#             if item is not None:
#                 print(f"Consumer {self.consumer_id} consumed: {item}")
#             else:
#                 print(f"Consumer {self.consumer_id}: Buffer empty, waiting...")
#             time.sleep(random.uniform(0.5, 1.5))
#         self.finished.emit()

#     def stop(self):
#         self.running = False

# # Main application
# def main():
#     app = QApplication(sys.argv)

#     # Create buffer
#     buffer = Buffer()

#     # Create threads and workers
#     producers = []
#     producer_threads = []
#     consumers = []
#     consumer_threads = []

#     # Start 3 producers
#     for i in range(3):
#         thread = QThread()
#         producer = Producer(buffer, i)
#         producer.moveToThread(thread)
#         thread.started.connect(producer.run)
#         producer.finished.connect(thread.quit)
#         thread.finished.connect(thread.deleteLater)
#         producer_threads.append(thread)
#         producers.append(producer)
#         thread.start()

#     # Start 5 consumers
#     for i in range(5):
#         thread = QThread()
#         consumer = Consumer(buffer, i)
#         consumer.moveToThread(thread)
#         thread.started.connect(consumer.run)
#         consumer.finished.connect(thread.quit)
#         thread.finished.connect(thread.deleteLater)
#         consumer_threads.append(thread)
#         consumers.append(consumer)
#         thread.start()

#     # Gracefully exit on app close
#     app.aboutToQuit.connect(lambda: [p.stop() for p in producers])
#     app.aboutToQuit.connect(lambda: [c.stop() for c in consumers])

#     sys.exit(app.exec())

# if __name__ == "__main__":
#     main()

import random
import sys
import time

from PySide6.QtCore import (
    QMutex,
    QMutexLocker,
    QObject,
    QThread,
    QWaitCondition,
    Signal,
    Slot,
)
from PySide6.QtWidgets import QApplication


# Shared buffer with QMutex and QWaitCondition
class Buffer(QObject):
    itemProduced = Signal(int)
    itemConsumed = Signal(int)

    def __init__(self, max_size=5):
        super().__init__()
        self.buffer = []
        self.max_size = max_size
        self.mutex = QMutex()
        self.notFull = QWaitCondition()
        self.notEmpty = QWaitCondition()

    def produce(self, item):
        with QMutexLocker(self.mutex):
            while len(self.buffer) >= self.max_size:
                print("Buffer full, producer waiting...")
                self.notFull.wait(self.mutex)

            self.buffer.append(item)
            self.itemProduced.emit(item)
            self.notEmpty.wakeAll()

    def consume(self):
        with QMutexLocker(self.mutex):
            while not self.buffer:
                print("Buffer empty, consumer waiting...")
                self.notEmpty.wait(self.mutex)

            item = self.buffer.pop(0)
            self.itemConsumed.emit(item)
            self.notFull.wakeAll()


# Producer class
class Producer(QObject):
    finished = Signal()

    def __init__(self, buffer, producer_id):
        super().__init__()
        self.buffer = buffer
        self.producer_id = producer_id
        self.running = True

    @Slot()
    def run(self):
        while self.running:
            item = random.randint(1, 100)
            self.buffer.produce(item)
            print(f"Producer {self.producer_id} produced: {item}")
            time.sleep(random.uniform(1.0, 2.0))
        self.finished.emit()

    def stop(self):
        self.running = False


# Consumer class
class Consumer(QObject):
    finished = Signal()

    def __init__(self, buffer, consumer_id):
        super().__init__()
        self.buffer = buffer
        self.consumer_id = consumer_id
        self.running = True

    @Slot()
    def run(self):
        while self.running:
            item = self.buffer.consume()
            if item is not None:
                print(f"Consumer {self.consumer_id} consumed: {item}")
            time.sleep(random.uniform(1.0, 2.0))
        self.finished.emit()

    def stop(self):
        self.running = False


# Main application
def main():
    app = QApplication(sys.argv)

    # Create buffer
    buffer = Buffer()

    # Create threads and workers
    producers = []
    producer_threads = []
    consumers = []
    consumer_threads = []

    # Start 3 producers
    for i in range(3):
        thread = QThread()
        producer = Producer(buffer, i)
        producer.moveToThread(thread)
        thread.started.connect(producer.run)
        producer.finished.connect(thread.quit)
        thread.finished.connect(thread.deleteLater)
        producer_threads.append(thread)
        producers.append(producer)
        thread.start()

    # Start 5 consumers
    for i in range(5):
        thread = QThread()
        consumer = Consumer(buffer, i)
        consumer.moveToThread(thread)
        thread.started.connect(consumer.run)
        consumer.finished.connect(thread.quit)
        thread.finished.connect(thread.deleteLater)
        consumer_threads.append(thread)
        consumers.append(consumer)
        thread.start()

    # Gracefully exit on app close
    app.aboutToQuit.connect(lambda: [p.stop() for p in producers])
    app.aboutToQuit.connect(lambda: [c.stop() for c in consumers])

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
