import time
from datetime import datetime, timedelta
import sched
import threading
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode, Key


delay = 0.01
button = Button.left
start_stop_key = Key.caps_lock
exit_key = Key.esc
start_clicker_thread_key = Key.home


class ClickMouse(threading.Thread):
    def __init__(self, delay, button):
        super(ClickMouse, self).__init__()
        self.delay = delay
        self.button = button
        self.running = False
        self.program_running = True
        self.mouse = Controller()

    def start_clicking(self):
        self.running = True

    def stop_clicking(self):
        self.running = False

    def exit(self):
        self.stop_clicking()
        self.program_running = False

    def run(self):
        while self.program_running:
            while self.running:
                self.mouse.click(self.button)
                time.sleep(self.delay)


def on_press(key):
    print(f"{key} registered")
    if key == exit_key:
        print("------------\n| Clean Up |\n------------")
        if click_thread.is_alive():
            print("Stopping clicker thread")
            click_thread.exit()
        print("Empty scheduler")
        for event in scheduler.queue:
            print(f"Stopping scheduled event {event.time}:{event.action}")
            scheduler.cancel(event)
        print("Stopping button listener")
        listener.stop()
        print("Cleanup complete")
    elif not click_thread.is_alive():
        if key == start_clicker_thread_key:
            start_clicker(click_thread)
        else:
            print(
                f"clicker thread not yet active, enter {start_clicker_thread_key} to activate clicker"
            )
        return
    elif key == start_stop_key:
        if click_thread.running:
            click_thread.stop_clicking()
        else:
            click_thread.start_clicking()


def start_clicker(click_thread):
    if not click_thread.is_alive():
        print("starting clicker thread")
        click_thread.start()


def setup_scheduler_thread(scheduler):
    scheduler_thread = threading.Thread(
        target=run_scheduler, args=(scheduler,), daemon=True
    )
    scheduler_thread.start()
    return scheduler_thread


def print_time_till_clicking_loop():
    while 1:
        time_till_clicker = time_to_launch_clicker - datetime.now()
        days = time_till_clicker.days
        hours, remainder = divmod(time_till_clicker.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(
            f"Still {days} days and {hours}h {minutes}m {seconds}s to go before clicking"
        )
        time.sleep(60)


def run_scheduler(scheduler):
    scheduler.run()


def start_clicking(click_thread):
    print("start clicking")
    click_thread.start_clicking()


click_thread = ClickMouse(delay, button)
listener = None

print(f"It's currently {datetime.now()}\n")

dt = input(
    "Please tell me when to start clicking! Note: \n - I need 1 minute to setup beforehand\n - Format your datetime like so: %Y-%m-%d %H:%M:%S.\n\t - Example: 2022-2-14 18:00:00\n - Or if you want to trigger today, format your time like so: %H:%M:%S.\n\t - Example: 18:00:00\n - Enter 'default' without quotes to start at 2022-2-19 18:00:00.\n\nDatetime or time to start clicking: "
)
print("------------\n| Parsing |\n------------")
if dt == "default":
    dt = "2022-2-19 18:00:00"
elif dt == "test":
    dt = datetime.now() + timedelta(minutes=1, seconds=10)

# example time = "2022-2-14 18:00:00"
datetime_format = "%Y-%m-%d %H:%M:%S"
time_format = "%H:%M:%S"

try:
    time_to_launch_clicker = datetime.strptime(dt, datetime_format)
    print("Correct datetime format\n")
except ValueError as e:
    print("Not the correct datetime format")
    try:
        time_to_launch_clicker = datetime.combine(
            datetime.now(), datetime.strptime(dt, time_format).time()
        )
        print("Correct time format\n")
    except ValueError as e:
        print("Not the correct time format")
        raise e
print("------------\n| Info |\n------------")
print(f"Datetime to start clicking: {time_to_launch_clicker}")

time_delta = timedelta(minutes=1)
time_to_launch = time_to_launch_clicker - time_delta
print(f"Datetime to start preperation: {time_to_launch}\n")

if time_to_launch < datetime.now():
    raise ValueError("Scheduled time is already passed")
scheduler = sched.scheduler(time.time)
scheduler.enterabs(
    time_to_launch.timestamp(), 1, start_clicker, argument=(click_thread,)
)
scheduler.enterabs(
    time_to_launch_clicker.timestamp(), 2, start_clicking, argument=(click_thread,)
)

print("------------\n| Run Program |\n------------")
print("Starting schedule")
setup_scheduler_thread(scheduler)
print("Starting loop that prints 'time till clicking' every minute")
time_printing_thread = threading.Thread(
    target=print_time_till_clicking_loop, daemon=True
)
time_printing_thread.start()
print(
    f"Starting button listener, listens to:\n - ({exit_key}) to exit\n - ({start_stop_key}) to start/stop clicking\n"
)
with Listener(on_press=on_press) as listener:
    listener.join()

print("exiting")
