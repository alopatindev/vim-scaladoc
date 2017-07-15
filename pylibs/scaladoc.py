#!/usr/bin/env python3
#
# Copyright 2012 Mike Dreves
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at:
#
#     http://opensource.org/licenses/eclipse-1.0.php
#
# By using this software in any fashion, you are agreeing to be bound
# by the terms of this license. You must not remove this notice, or any
# other, from this software. Unless required by applicable law or agreed
# to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.
#
# @author Mike Dreves

import errno
import glob
import hashlib
import json
import os
import re
import sys
import time
import urllib
import urllib.request
import webbrowser

DEFAULT_CACHE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'tmp'))

HREF_PATTERN = re.compile('href="([^ ><]*)"', re.I|re.U)

INDEX_PATTERN = re.compile('^Index\.PACKAGES\s*=\s*({.*});$', re.DOTALL)

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36'

INDEX_JS = 'index.js'

def Search(
    file_name, keywords, scaladoc_paths=[], scaladoc_urls=[], cache_dir=None, cache_ttl_days=15):
  """Searchs for scala doc files based on keywords (package/class names).

  Args:
    file_name: File search invoked from.
    keywords: List of keywords
    scaladoc_paths: Local directory paths to search for.
    scaladoc_urls: URLs to search for scaladocs.
    cache_dir: Directory to store index cache in.
    cache_ttl_days: Time between refreshes of official scaladoc lib. Note,
      local caches are updated based on changes to the local index.html file.

    Search('foo.scala', ['list'])  = ['scala/collection/immutable/List.html']
    Search('foo', ['im', 'queue']) = ['scala/collection/immutable/Queue.html']
    Search('foo' ['mu', 'queue'])  = ['scala/collection/mutable/Queue.html']
  """

  if not cache_dir:
    cache_dir = DEFAULT_CACHE_DIR

  if not os.path.exists(cache_dir):
    _mkdir_p(cache_dir)

  def _ComputeCacheId(path):
    data = path.encode('utf-8')
    hashsum = hashlib.sha1(data).hexdigest()
    return os.path.join(cache_dir, hashsum)

  _ClearStaleCacheEntries(cache_dir, cache_ttl_days)

  caches = dict()
  for url in scaladoc_urls:
    url = _StripPath(url)
    cache_id = _ComputeCacheId(url)
    caches[cache_id] = url
    _UpdateCacheFromNetwork(caches, cache_id, cache_ttl_days)

  # if docs local to file, add them to path
  api_path = _FindLocalDocs(file_name)
  if api_path and api_path not in scaladoc_paths:
    scaladoc_paths.append(api_path)

  # additional paths
  for api_path in scaladoc_paths:
    api_path = os.path.expanduser(_StripPath(api_path))
    cache_id = _ComputeCacheId(api_path)
    if _UpdateCacheFromDisk(cache_id, api_path):
      caches[cache_id] = 'file://' + api_path

  last_keyword = keywords[-1].strip('"').lower()
  prefix_pattern = '.*'  # skip main package (scala, etc)
  for keyword in keywords[:-1]:
    prefix_pattern += '/' + keyword.strip('"').lower() + '.*'

  # exact matches on last keyword (optional scala object matches)
  full_last_match = re.compile(
      prefix_pattern + '/' + last_keyword + '[$]?.html', re.I).match
  # matches that start with last keyword
  starts_with_last_match = re.compile(
      prefix_pattern + '/' + last_keyword + '.*.html', re.I).match

  matches_last = []  # exact matches on last keyword
  starts_with_last = []  # matches that start with last keyword

  for cache_file_name, url_prefix in caches.items():
    with open(cache_file_name, 'r') as cache:
      for line in cache:
        m = full_last_match(line)
        if m:
          matches_last.append(url_prefix + '/' + line)
        else:
          m = starts_with_last_match(line)
          if m:
            starts_with_last.append(url_prefix + '/' + line)

  return matches_last if matches_last else starts_with_last


def OpenUrl(url):
  """Opens URL in browser."""
  webbrowser.open(url)


def _UpdateCacheFromNetwork(caches_map, cache_id, cache_ttl_days):
  if os.path.exists(cache_id):
    update_cache = True
    last_modified = os.path.getmtime(cache_id)
    next_refresh = time.time() - (cache_ttl_days * 24 * 60 * 60)
    update_cache = (last_modified < next_refresh)
  else:
    update_cache = True
  
  if update_cache:
    url = caches_map[cache_id]
    raw_text = _HttpGet(url + '/' + INDEX_JS)
    cache = _ParseIndex(raw_text)
    with open(cache_id, 'w') as output:
      output.write(cache)


def _HttpGet(url):
  opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
  opener.addheaders = [('User-Agent', USER_AGENT)]
  return opener.open(url).read().decode('utf-8')


def _FindLocalDocs(path):
  if not path:
    return None

  while True:
    (path, tail) = os.path.split(path)
    if not tail:
      return None
    if tail == 'src':
      # found root of a project, search target for api docs
      target_path = os.path.join(path, 'target')
      if not os.path.exists(target_path):
        return None
      # search for scala-<version> dirs
      results = []
      for scala_path in glob.glob(os.path.join(target_path, 'scala-*')):
        api_path = os.path.join(scala_path, 'api')
        if os.path.exists(os.path.join(api_path, INDEX_JS)):
          results.append(api_path)
      if not results:
        return None
      return max(results)  # use latest scala version


def _UpdateCacheFromDisk(cache_id, api_path):
  api_index = None
  if api_path:
    api_index = os.path.join(api_path, INDEX_JS)
  if not api_index or not os.path.exists(api_index):
    # del local cache
    if os.path.exists(cache_id):
      os.remove(cache_id)
    return False

  update_cache = True
  if os.path.exists(cache_id):
    cache_last_modified = os.path.getmtime(cache_id)
    api_last_modified = os.path.getmtime(api_path)
    update_cache = (cache_last_modified < api_last_modified)

  if update_cache:
    with open(api_index, 'r') as f:
      raw_text = f.read()
      cache = _ParseIndex(raw_text)
      with open(cache_id, 'w') as output:
        output.write(cache)

  return True


def _ClearStaleCacheEntries(cache_dir, cache_ttl_days):
  for cache_id in glob.glob(os.path.join(cache_dir, '*')):
    last_modified = os.path.getmtime(cache_id)
    next_refresh = time.time() - (cache_ttl_days * 24 * 60 * 60)
    if last_modified < next_refresh:
      os.remove(cache_id)


def _StripPath(path):
  if path.endswith('/'):
    path = path[:-1]
  return path


def _ParseIndex(text):
  types = ('object', 'trait', 'class', 'case class')
  def dfs(node, result):
    for key, value in node.items():
      if key in types:
        result.add(value + '\n')
      elif type(value) is list:
        for child in value:
          dfs(child, result)

  result = set()
  try:
    document = INDEX_PATTERN.match(text).group(1)
    tree = json.loads(document)
    dfs(tree, result)
  except Exception as e:
    print(e) # FIXME: print as error

  sorted_result = sorted(result)
  return ''.join(sorted_result)


def _mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as e:
    if e.errno == errno.EEXIST:
      pass
    else:
      raise


def main():
  if len(sys.argv) <= 1:
    return 1

  docs = Search(os.getcwd(), sys.argv[1:])
  if not docs:
    return 1

  print(''.join(docs))
  return 0


if __name__ == "__main__":
  main()

# vim: set shiftwidth=2:softtabstop=2:tabstop=2
