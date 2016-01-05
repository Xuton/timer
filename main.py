import datetime
import sqlite3

from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label


class MenuScreen(Screen):

    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.timer_start = None
        self.timer_current = None
        self.timer_running = False

        self.lbl_timer = self.ids.lbl_timer
        self.btn_start = self.ids.btn_start
        self.btn_pause = self.ids.btn_pause
        self.txt_comments = self.ids.txt_comments

    def set_timer(self, time_increase):
        self.timer_current += datetime.timedelta(seconds=time_increase)
        self.lbl_timer.text = datetime.datetime.strftime(self.timer_current, "%H:%M:%S")

    def start_timer(self):

        def anim_func(*args):
            # TODO gotta be a better way than this
            anim2.start(self.txt_comments)

        if self.btn_start.text == 'Resume Timer':
            self.resume_timer()

        elif self.btn_start.text == 'Start Timer':
            # Start the timer
            self.btn_start.text = 'Stop Timer'
            self.timer_start = datetime.datetime.now()
            self.timer_current = datetime.datetime(year=2015, month=1, day=1)

            # Start the timer
            Clock.schedule_interval(self.set_timer, 1)

            # Do the comments box animation
            anim = Animation(pos_hint={'x': 1.01, 'y': 1.32}, duration=.1)
            anim2 = Animation(size_hint=(.8, .38), pos_hint={'x': .8, 'y': 1.15}, duration=.5)
            Clock.schedule_once(anim_func, .2)

        else:
            # Stop the timer, save the item and reset screen
            Clock.unschedule(self.set_timer)
            self.save_time()
            self.btn_start.text = 'Start Timer'
            self.lbl_timer.text = '00:00:00'
            self.txt_comments.text = ''

            # Do the comments box animation
            anim = Animation(size_hint=(.4, .2), pos_hint={'x': 1.01, 'y': 1.32}, duration=.5)
            anim2 = Animation(pos_hint={'x': 1.01, 'y': 1.59}, duration=.1)
            Clock.schedule_once(anim_func, .6)

        anim.start(self.txt_comments)

    def resume_timer(self):
        Clock.schedule_interval(self.set_timer, 1)
        self.btn_start.text = 'Stop Timer'
        self.btn_pause.text = 'Pause Timer'

    def pause_timer(self):
        if self.btn_start.text == 'Stop Timer':
            self.btn_start.text = 'Resume Timer'
            self.btn_pause.text = 'Un-pause'
            Clock.unschedule(self.set_timer)

        elif self.btn_start.text == 'Resume Timer':
            self.resume_timer()

    def save_time(self):
        db.save_record(
                timer_start=self.timer_start,
                timer_current=self.timer_current,
                comments=self.txt_comments.text,
                invoiced=0
        )


class StatsScreen(Screen):
    def __init__(self, **kwargs):
        super(StatsScreen, self).__init__(**kwargs)
        self.grd_records = self.ids.grd_records

    def on_enter(self):
        self.grd_records.add_widget(self.get_label('Start time', font_size=24))
        self.grd_records.add_widget(self.get_label('Total Time', font_size=24))
        self.grd_records.add_widget(self.get_label('Comments', font_size=24))
        self.grd_records.add_widget(self.get_label('Invoiced', font_size=24))

        for record in db.get_records():
            self.grd_records.add_widget(self.get_label(str(record[0])))
            self.grd_records.add_widget(self.get_label(str(record[1])))
            self.grd_records.add_widget(self.get_label(str(record[2])))
            self.grd_records.add_widget(self.get_label(str(bool(record[3]))))

        self.grd_records.bind(minimum_height=self.grd_records.setter('height'))
        self.grd_records.height = (len(self.grd_records.children) / 4) * self.grd_records.row_default_height
        self.rel_records.height = self.grd_records.height

    @staticmethod
    def get_label(text, font_size=14):
        return Label(
                text=text,
                font_size=font_size,
                size_hint=(1, None),
                )


class DBAccess:
    def __init__(self):
        self.conn = sqlite3.connect('times.db')
        self.c = self.conn.cursor()

    def save_record(self, **kwargs):
        self.c.execute('INSERT INTO times VALUES (?, ?, ?, ?)',
                       (datetime.datetime.strftime(kwargs['timer_start'], "%Y-%m-%d %H:%M:%S"),
                        datetime.datetime.strftime(kwargs['timer_current'], "%H:%M:%S"),
                        kwargs['comments'],
                        kwargs['invoiced'])
                       )
        self.conn.commit()

    def get_records(self):
        return self.c.execute('SELECT * FROM times')

Builder.load_file('main.kv')
sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(StatsScreen(name='stats'))
sm.current = 'menu'

db = DBAccess()


class TimerApp(App):
    def build(self):
        Window.size = (800, 600)
        Window.set_icon('images/clock_icon.png')
        return sm


if __name__ == '__main__':
    TimerApp().run()
