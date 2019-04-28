#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import flask

from app import frontend

APP = frontend.APP

if __name__ == '__main__':
	APP.run(host='127.0.0.1', port=8001)
