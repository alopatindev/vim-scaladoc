This fork consists in adding the Spark scala doc in the index of ScalaDoc.

# Overview

The vim-scaladoc plug-in is for use with [Vim](http://www.vim.org/) - who
would have thought? It allows you to open scaladoc documentation in your
favorite browser based on keyword selection. By default the plugin will
search the following locations for documentation:

 * [Official Scala Documentation](http://www.scala-lang.org/api/current)
 * Local Project (target/scala-x.x.x/api)
 * User Specified Paths

The local project search is based on the current open file in VIM. If the file
contains a `src` directory in its path, then `target/scala-x.x.x/api` is
appended to the parent of this directory and added to the search path.

# Requirements

This plugin requires VIM be compiled with +python. The plugin has been tested
on Mac and Linux. If you are using Windows, go sit in the corner and think
about what you have done :)

# Installation

If you are using [pathogen](https://github.com/tpope/vim-pathogen), then
simply copy and paste:

    cd ~/.vim/bundle
    git clone git://github.com/mdreves/vim-scaladoc.git

Once help tags have been generated, you can view the manual with
`:help scaladoc`.

# Documentation

Documentation is available via VIM `:help`, but it's fairly simple:

    :ScalaDoc list

    http://www.scala-lang.org/api/current/scala/collection/immutable/List.html

    :ScalaDoc mu queue

    http://www.scala-lang.org/api/current/scala/collection/mutable/Queue.html

    :ScalaDoc im queue

    http://www.scala-lang.org/api/current/scala/collection/immutable/Queue.html

If multiple matches are found (e.g. `:ScalaDoc queue`), then a read-only
window will be opened to select a URL from.

Note: The first time `:ScalaDoc` is run it may be a bit slow as it downloads
and indexes the docs, but subsequent runs should be fast.

# Configuration

A few variables are available to customize settings:

    g:scaladoc            :  Enable (1) / Disable (0) plugin
                             (Default: 1)
    g:scaladoc_cache_dir  :  Directory to store index caches in
                             (Default: `tmp` dir of install directory)
    g:scaladoc_cache_ttl  :  TTL (days) for cached indexes
                             (Default: 15 days)
    g:scaladoc_paths      :  Local directory paths (comma sep) to search for
                             scaladocs (Default: '',
                             Example: '/helloworld/target/scala-2.11/api/')
    g:scaladoc_urls       :  URLs (comma sep) to search for scaladocs
                             (Default: 'https://www.scala-lang.org/api/current')

Note: The TTL applies to the official scaladoc site and to general cache
cleanup. Local API files are checked for modifications each time `:ScalaDoc` is
run in order to pickup changes from a local build.

There are no built-in mappings added for scaladoc, but it is simple enough to
add your own. For example:

    nnoremap <F1> :call scaladoc#Search(expand("<cword>"))<CR>

# License

Copyright 2012 Mike Dreves

All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at:

    http://opensource.org/licenses/eclipse-1.0.php

By using this software in any fashion, you are agreeing to be bound
by the terms of this license. You must not remove this notice, or any
other, from this software. Unless required by applicable law or agreed
to in writing, software distributed under the License is distributed
on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied.
