"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Copyright 2012 Mike Dreves
"
" All rights reserved. This program and the accompanying materials
" are made available under the terms of the Eclipse Public License v1.0
" which accompanies this distribution, and is available at:
"
"     http://opensource.org/licenses/eclipse-1.0.php
"
" By using this software in any fashion, you are agreeing to be bound
" by the terms of this license. You must not remove this notice, or any
" other, from this software. Unless required by applicable law or agreed
" to in writing, software distributed under the License is distributed
" on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
" either express or implied.
"
" @author Mike Dreves
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

" Check if loaded
if exists("g:loaded_scaladoc") || &cp
  finish
endif

" User disabled
if exists("g:scaladoc") && g:scaladoc == 0
 finish
endif

let g:loaded_scaladoc = 1

" Check python support
if !has('python3')
  echoerr expand("<sfile>:t") . " Vim must be compiled with +python."
  finish
endif

let s:pyfile_cmd = 'py3file'
let s:py_cmd = 'py3'

let s:keepcpo = &cpo
set cpo&vim

" Update python path
python3 << PYTHON_CODE
import os
import sys
import vim

cwd = vim.eval('getcwd()')
pylibs_path = os.path.join(os.path.dirname(os.path.dirname(
    vim.eval("expand('<sfile>:p')"))), 'pylibs')

sys.path = [pylibs_path, cwd] + sys.path
PYTHON_CODE

" Default variables
if !exists("g:scaladoc_cache_dir")
  let g:scaladoc_cache_dir = ''  " Use python default
endif
if !exists("g:scaladoc_cache_ttl_days")
  let g:scaladoc_cache_ttl_days = 15
endif
if !exists("g:scaladoc_paths")
  let g:scaladoc_paths = ''
endif
if !exists("g:scaladoc_urls")
  let g:scaladoc_urls = 'https://www.scala-lang.org/api/current'
endif

if !exists(":ScalaDoc")
  command -buffer -nargs=+ ScalaDoc :call scaladoc#Search('<f-args>')
endif

let &cpo = s:keepcpo
unlet s:keepcpo
