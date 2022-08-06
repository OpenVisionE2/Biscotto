# -*- coding: utf-8 -*-
from distutils.core import setup
import setup_translate

pkg = 'Extensions.KeyAdder'
setup(name='enigma2-plugin-extensions-keyadder',
       version='2.2',
       description='Add BISS, PowerVU, Irdeto and Tandberg keys to current service.',
       packages=[pkg],
       package_dir={pkg: 'plugin'},
       package_data={pkg: ['plugin.png', '*/*.png', 'locale/*/LC_MESSAGES/*.mo', 'VirtualKeyBoard_Icons/vkskin.xml', 'VirtualKeyBoard_Icons/*/*.png']},
       cmdclass=setup_translate.cmdclass, # for translation
      )
