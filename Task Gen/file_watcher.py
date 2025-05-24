import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileWatcher:
    def __init__(self, directory, on_change_callback):
        self.directory = directory
        self.on_change_callback = on_change_callback
        self.event_handler = self._create_event_handler()
        self.observer = Observer()

    def _create_event_handler(self):
        class Handler(FileSystemEventHandler):
            def __init__(self, callback):
                super().__init__()
                self.callback = callback
            def on_created(self, event):
                if not event.is_directory:
                    self.callback('created', event.src_path)
            def on_deleted(self, event):
                if not event.is_directory:
                    self.callback('deleted', event.src_path)
            def on_moved(self, event):
                if not event.is_directory:
                    self.callback('moved', event.src_path, event.dest_path)
        return Handler(self.on_change_callback)

    def start(self):
        self.observer.schedule(self.event_handler, self.directory, recursive=False)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

if __name__ == "__main__":
    # Minimal test: print events in the TASKS directory
    def print_event(event_type, *paths):
        print(f"Event: {event_type}, Paths: {paths}")
    tasks_dir = os.path.join(os.path.dirname(__file__), '../shhh/tasks/TASKS')
    watcher = FileWatcher(tasks_dir, print_event)
    try:
        watcher.start()
        print(f"Watching {tasks_dir} for changes. Press Ctrl+C to exit.")
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop() 