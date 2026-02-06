# Reward App (Kivy + AdMob Rewarded)

Application Android en **Kivy** avec un bouton pour regarder une vidéo reward et augmenter le solde de **0,02 €** par vidéo validée.

## Fichiers clés

- `main.py` : interface Kivy + logique de récompense + intégration AdMob Rewarded.
- `buildozer.spec` : configuration de build Android (Buildozer).

## Fonctionnement

- Le bouton **"Regarder une vidéo reward (+0,02 €)"** lance une vidéo reward.
- Quand l’utilisateur obtient la récompense (`onUserEarnedReward`), le solde monte de `0.02`.
- En dehors d’Android, l’app passe en **mode simulation** pour faciliter les tests.

## IDs AdMob

- L’app utilise l’ID test reward officiel Google dans `main.py`.
- Avant publication, remplacez:
  - l’`ad_unit_id` reward,
  - et ajoutez votre `APPLICATION_ID` AdMob dans `buildozer.spec` (`android.meta_data`).

## Build Android

```bash
pip install buildozer cython
buildozer android debug
```

APK généré dans `bin/`.

## Protocole réseau (découverte + relais)

- Une spécification de protocole pair-à-pair sûr est disponible dans `NETWORK_PROTOCOL.md`.
- Le design couvre la découverte des nœuds, le relais, le routage et la sécurité (mTLS, signatures, anti-rejeu).

