Written by Hermes–GPT-6 (AI assistant)

# iw3 player enhancements fork

This is a public fork of [nagadomi/nunif](https://github.com/nagadomi/nunif).
The maintained customization branch is **`iw3-player-enhancements`**, based on
upstream **`dev`**. The upstream project and its licenses remain unchanged.

## Included changes

- Generate player HTTPS certificates with `cryptography`, replacing the removed
  pyOpenSSL `X509Extension` API. Existing certificate/key pairs are preserved.
- Compact playback-speed readout, opened by click, VR trigger or right-click.
- Popup-only slider, proportional +/- (multiply/divide by 1.1), 1x reset,
  restore-defaults icon, and live numeric Min/Max editing with a VR keypad or keyboard.
- Default range **0.1–16x**; configurable range **0.01–100x** with decimal inputs.
  Tapping Min/Max immediately selects that speed and opens its editor.
- Persist speed/range and reapply them when media changes. Unsupported native
  playback rates keep the previous actual speed and display a notification.

The user reports that the controls work in Quest Browser and is happy with the
result. This is not a guarantee of audio quality or browser support at every rate.
Browser limits still apply; extreme speeds can mute audio.

## Updates: upstream + these changes

Forks do **not** automatically incorporate upstream changes. In a clean development
checkout, merge upstream `dev` into the customization branch, test, then publish:

```sh
# Add once if missing:
git remote add upstream https://github.com/nagadomi/nunif.git

git switch iw3-player-enhancements
git fetch upstream
git merge upstream/dev
# Resolve any conflicts and run tests before pushing.
git push origin iw3-player-enhancements
```

An installation tracking `origin/iw3-player-enhancements` can then receive both
sets of changes. A normal upstream installation does not start tracking this fork
just because the fork exists. Back up and migrate its local changes deliberately
before switching remotes/branches; do not reset a working installation blindly.
This publication does **not** modify the existing installation or its updater.

**Windows updater warning:** the inherited `windows_package/update.bat` upgrades
Python packages and can run `git reset --hard` if pulling fails. Uncommitted local
fixes are not update-safe. This fork does not change that updater or provide a
separate Windows distribution. No automatic sync workflow is configured.

## Torch compiler workaround is separate

The previously investigated `vr must not be None for symbol q3` workaround patches
an installed **PyTorch** file, outside this repository. Matching Python developer
headers are also installation components. Neither is bundled here. Updating Torch
may overwrite its workaround; a fork of nunif cannot by itself prevent that.
See the [upstream discussion](https://github.com/nagadomi/nunif/discussions/731).
Do not treat the player changes as a fix for every Torch/compiler configuration.

## Verification

From `iw3/player`, using a modern Node.js version (22+):

```sh
npm test
# Or, without installing npm dependencies:
node --test
```

From the repository root, with `cryptography` installed:

```sh
python iw3/player/tests/test_player_cert.py
```

The Node tests exercise state, menu callbacks, persistence boundaries, numeric
editing, reset behavior, native-rate rejection and media replacement. UI/GPU/DB
boundaries are doubled in these portable tests. The certificate test extracts the
trusted local generator without importing GPU dependencies, checks real signatures,
SANs, TLS loading and preservation using temporary files and documentation/loopback
addresses only.

Additional agent-run local Chrome checks exercised real rendered pointer controls,
IndexedDB, native media-clock advancement with a synthetic muted clip, and full-app
startup. These local browser harnesses are not bundled as portable CI. No GitHub CI
pass or independent audio-quality verification is claimed.

Changes are kept in separate certificate and playback commits so they can later be
proposed upstream independently. Publishing this fork does not itself open a PR.
