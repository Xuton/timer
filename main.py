import datetime
import sqlite3

from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.popup import Popup


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

        self.btn_all = self.ids.btn_all
        self.btn_invoiced = self.ids.btn_invoiced
        self.btn_not_invoiced = self.ids.btn_not_invoiced
        self.grd_records = self.ids.grd_records

        # Filter is based on boolean field in times table
        # -1 == All
        # 0 == Invoiced False
        # 1 == Invoiced True
        self.filter = '0'

        self.checks = []  # Keeping a record of all the checkboxes so I don't need to loop over to find them
        self.popup = None
        self.mode = None

    def set_filter(self, btn):
        self.filter = btn
        self.populate_table()

    def on_enter(self):
        self.populate_table()

    def populate_table(self):
        self.grd_records.clear_widgets()

        self.grd_records.add_widget(self.get_label('Start time', font_size=24))
        self.grd_records.add_widget(self.get_label('Total Time', font_size=24))
        self.grd_records.add_widget(self.get_label('Comments', font_size=24))
        self.grd_records.add_widget(self.get_label('Invoiced', font_size=24))

        box = BoxLayout(spacing=5)
        box.add_widget(self.get_button(text='Delete', callback=self.btn_clicked))
        box.add_widget(self.get_button(text='Invoice', callback=self.btn_clicked))
        self.grd_records.add_widget(box)

        for record in db.get_records(self.filter):
            self.grd_records.add_widget(self.get_label(str(record[0])))
            self.grd_records.add_widget(self.get_label(str(record[1])))
            self.grd_records.add_widget(self.get_label(str(record[2])))
            self.grd_records.add_widget(self.get_label(str(bool(record[3]))))
            self.grd_records.add_widget(self.get_checkbox())

        self.grd_records.bind(minimum_height=self.grd_records.setter('height'))
        self.grd_records.height = (len(self.grd_records.children) / 4) * self.grd_records.row_default_height
        self.rel_records.height = self.grd_records.height

    def close_popup(self):
        if self.mode == 'delete':
            pass

        elif self.mode == 'invoice':
            pass

        self.popup.dismiss()
        self.populate_table()

        self.popup = None
        self.mode = None

    def btn_clicked(self, instance):
        checks = [c for c in self.checks if c.active]
        if checks:
            self.mode = instance.text.lower()
            title = 'Are you sure you want to {} the selected records?'.format(instance.text.lower())
            content = BoxLayout(spacing=5)
            content.add_widget(self.get_button(text='Yes', callback=self.close_popup))
            content.add_widget(self.xet_button(text='No', callback=self.close_popup))

            self.popup = Popup(title=title, content=content, size_hint=(.4, .2))
            self.popup.open()

    @staticmethod
    def get_button(**kwargs):
        btn = Button(
                text=kwargs['text'],
                border=(0, 0, 0, 0),
                background_normal='images/small_button.png',
                background_down='images/small_button_down.png',
                )
        btn.bind(on_press=kwargs['callback'])
        return btn

    def get_checkbox(self):
        chk = CheckBox(
                border=(0, 0, 0, 0),
                background_normal='images/del_button.png',
                background_down='images/del_button_down.png',
                # size_hint_x=.2,
                # width=1,
                )
        self.checks.append(chk)
        return chk

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

        if not self.c.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='times'").fetchone():
            self.c.execute('CREATE TABLE times (time_start TEXT, total_time TEXT, comments TEXT, invoiced INT)')

    def save_record(self, **kwargs):
        self.c.execute('INSERT INTO times VALUES (?, ?, ?, ?)',
                       (datetime.datetime.strftime(kwargs['timer_start'], "%Y-%m-%d %H:%M:%S"),
                        datetime.datetime.strftime(kwargs['timer_current'], "%H:%M:%S"),
                        kwargs['comments'],
                        kwargs['invoiced'])
                       )
        self.conn.commit()

    def get_records(self, filter):
        if int(filter) == -1:
            return self.c.execute('SELECT * FROM times')
        else:
            return self.c.execute('SELECT * FROM times WHERE invoiced=?', filter)


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
