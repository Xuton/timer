import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen


class MenuScreen(Screen):
    btn_start = ObjectProperty()
    btn_pause = ObjectProperty()
    lbl_timer = ObjectProperty()

    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.timer_start = None
        self.timer_current = None
        self.timer_running = False

        self.btn_start = self.ids.btn_start

    def set_timer(self, time_increase):
        self.timer_running = True

        self.timer_current += datetime.timedelta(seconds=time_increase)
        self.lbl_timer.text = datetime.datetime.strftime(self.timer_current, "%H:%M:%S")

    def start_timer(self):
        if self.btn_start.text == 'Start Timer':
            self.btn_start.text = 'Stop Timer'
            self.timer_start = datetime.datetime.now()
            self.timer_current = datetime.datetime(year=2015, month=1, day=1)

            Clock.schedule_interval(self.set_timer, 1)
        else:
            Clock.unschedule(self.set_timer)
            self.btn_start.text = 'Start Timer'
            self.save_time()

    def save_time(self):
        pass


class StatsScreen(Screen):
    pass

Builder.load_file('main.kv')
sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
# sm.add_widget(StatsScreen(name='stats'))
sm.current = 'menu'


class TimerApp(App):
    def build(self):
        return sm


if __name__ == '__main__':
    TimerApp().run()
