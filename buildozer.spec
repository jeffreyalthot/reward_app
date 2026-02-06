[app]
title = RewardVideoApp
package.name = rewardvideo
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,pyjnius
orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 24
android.sdk = 33
android.ndk = 25b
android.accept_sdk_license = True

# IMPORTANT: ajoutez votre APP ID AdMob réel avant publication
# android.meta_data = com.google.android.gms.ads.APPLICATION_ID="ca-app-pub-xxxxxxxxxxxxxxxx~yyyyyyyyyy"

[buildozer]
log_level = 2
warn_on_root = 1
