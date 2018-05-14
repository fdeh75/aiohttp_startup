#!/bin/bash
#1234
echo "# aiohttp_startup" >> README.md
git init
git add README.md
git commit -m "first commit"
git remote add origin git@github.com:fdeh75/aiohttp_startup.git
git push -u origin master
