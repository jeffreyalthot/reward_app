from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

KV = '''
<RootWidget>:
    orientation: 'vertical'
    padding: dp(20)
    spacing: dp(16)

    Label:
        text: 'Application Rewarded Video'
        font_size: '24sp'
        bold: True
        size_hint_y: None
        height: self.texture_size[1]

    Label:
        text: root.balance_text
        font_size: '20sp'

    Button:
        text: root.button_text
        font_size: '18sp'
        size_hint_y: None
        height: dp(56)
        disabled: root.loading
        on_release: root.show_rewarded_video()

    Label:
        text: root.status_message
        color: 0.2, 0.2, 0.2, 1
        halign: 'center'
        text_size: self.size
'''


class RewardedAdManager:
    """Gestion AdMob Rewarded sous Android (avec mode simulation hors Android)."""

    def __init__(self, ad_unit_id, on_reward, on_status):
        self.ad_unit_id = ad_unit_id
        self.on_reward = on_reward
        self.on_status = on_status
        self._rewarded_ad = None
        self._android_ready = False

        if self._is_android():
            try:
                self._setup_android()
                self._android_ready = True
                self.load_ad()
            except Exception as exc:
                self.on_status(f"Erreur AdMob: {exc}")
        else:
            self.on_status("Mode simulation (non Android)")

    @staticmethod
    def _is_android():
        try:
            from kivy.utils import platform
            return platform == 'android'
        except Exception:
            return False

    def _setup_android(self):
        from android.runnable import run_on_ui_thread
        from jnius import autoclass, PythonJavaClass, java_method

        self.run_on_ui_thread = run_on_ui_thread
        self.PythonJavaClass = PythonJavaClass
        self.java_method = java_method
        self.autoclass = autoclass

        self.PythonActivity = autoclass('org.kivy.android.PythonActivity')
        self.MobileAds = autoclass('com.google.android.gms.ads.MobileAds')
        self.AdRequestBuilder = autoclass('com.google.android.gms.ads.AdRequest$Builder')
        self.RewardedAd = autoclass('com.google.android.gms.ads.rewarded.RewardedAd')

        self.activity = self.PythonActivity.mActivity

        @run_on_ui_thread
        def init_mobile_ads():
            self.MobileAds.initialize(self.activity)

        init_mobile_ads()

    def load_ad(self):
        if not self._android_ready:
            return

        @self.run_on_ui_thread
        def _load():
            manager = self

            class LoadCallback(manager.PythonJavaClass):
                __javaclass__ = 'com/google/android/gms/ads/rewarded/RewardedAdLoadCallback'
                __javacontext__ = 'app'

                @manager.java_method('(Lcom/google/android/gms/ads/LoadAdError;)V')
                def onAdFailedToLoad(self, load_ad_error):
                    manager._rewarded_ad = None
                    Clock.schedule_once(
                        lambda dt: manager.on_status(
                            f"Chargement échoué: {load_ad_error.getMessage()}"
                        )
                    )

                @manager.java_method('(Lcom/google/android/gms/ads/rewarded/RewardedAd;)V')
                def onAdLoaded(self, rewarded_ad):
                    manager._rewarded_ad = rewarded_ad
                    Clock.schedule_once(lambda dt: manager.on_status('Vidéo prête.'))

            ad_request = self.AdRequestBuilder().build()
            callback = LoadCallback()
            self.RewardedAd.load(
                self.activity,
                self.ad_unit_id,
                ad_request,
                callback,
            )

        _load()
        self.on_status('Chargement de la vidéo...')

    def show_ad(self):
        if not self._android_ready:
            Clock.schedule_once(lambda dt: self.on_reward())
            self.on_status('Récompense simulée (+0,02 €).')
            return

        if self._rewarded_ad is None:
            self.on_status('Aucune vidéo disponible, rechargement...')
            self.load_ad()
            return

        @self.run_on_ui_thread
        def _show():
            manager = self

            class RewardListener(manager.PythonJavaClass):
                __javaclass__ = 'com/google/android/gms/ads/OnUserEarnedRewardListener'
                __javacontext__ = 'app'

                @manager.java_method('(Lcom/google/android/gms/ads/rewarded/RewardItem;)V')
                def onUserEarnedReward(self, reward_item):
                    Clock.schedule_once(lambda dt: manager.on_reward())

            listener = RewardListener()
            self._rewarded_ad.show(self.activity, listener)
            self._rewarded_ad = None

        _show()
        self.on_status('Lecture de la vidéo reward...')
        self.load_ad()


class RootWidget(BoxLayout):
    balance = NumericProperty(0.0)
    loading = NumericProperty(0)
    status_message = StringProperty('Initialisation...')

    @property
    def balance_text(self):
        return f"Solde: {self.balance:.2f} €"

    @property
    def button_text(self):
        return 'Regarder une vidéo reward (+0,02 €)'

    def on_kv_post(self, base_widget):
        # ID test AdMob reward officiel. Remplacez en production.
        test_ad_unit = 'ca-app-pub-3940256099942544/5224354917'
        self.reward_manager = RewardedAdManager(
            ad_unit_id=test_ad_unit,
            on_reward=self.apply_reward,
            on_status=self.update_status,
        )

    def show_rewarded_video(self):
        self.loading = 1
        self.reward_manager.show_ad()
        Clock.schedule_once(lambda dt: setattr(self, 'loading', 0), 1)

    def apply_reward(self):
        self.balance += 0.02
        self.status_message = 'Récompense reçue ! +0,02 €'

    def update_status(self, message):
        self.status_message = message


class RewardVideoApp(App):
    def build(self):
        Builder.load_string(KV)
        return RootWidget()


if __name__ == '__main__':
    RewardVideoApp().run()
