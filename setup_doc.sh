#!/usr/bin/env bash

pip_modules=$(pip3 list)

if [[ ! ${pip_modules} =~ "pydoc-markdown" ]]
then
   pip install pydoc-markdown
   echo
fi

if [[ ! ${pip_modules} =~ "mkdocs" ]]
then
   pip install mkdocs
   echo
fi

if [[ ! ${pip_modules} =~ "mkdocs-gitbook" ]]
then
   pip install mkdocs-gitbook
   echo
fi

pydoc-markdown

cp module_overview.png build/docs/docs/

cd build/docs/

mkdocs serve