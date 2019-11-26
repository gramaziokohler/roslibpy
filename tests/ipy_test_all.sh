#!/bin/bash

mono /Library/Frameworks/IronPython.framework/Versions/2.7.9/bin/ipy.exe test_param.py
mono /Library/Frameworks/IronPython.framework/Versions/2.7.9/bin/ipy.exe test_rosapi.py
mono /Library/Frameworks/IronPython.framework/Versions/2.7.9/bin/ipy.exe test_service.py
mono /Library/Frameworks/IronPython.framework/Versions/2.7.9/bin/ipy.exe test_tf.py
mono /Library/Frameworks/IronPython.framework/Versions/2.7.9/bin/ipy.exe test_topic.py
