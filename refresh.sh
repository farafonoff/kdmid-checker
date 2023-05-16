#!/bin/zsh

zip -u -r -0 captchas.zip captcha_images
git add captchas.zip
git commit -m "update capts"
git push
