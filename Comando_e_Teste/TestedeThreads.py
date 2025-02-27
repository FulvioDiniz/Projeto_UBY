import threading

def thread_func():
    while True:
        pass

threads = []
try:
    while True:
        t = threading.Thread(target=thread_func)
        t.start()
        threads.append(t)
        print(f"Threads ativas: {len(threads)}")
except RuntimeError as e:
    print(f"Erro ao criar thread: {e}")
